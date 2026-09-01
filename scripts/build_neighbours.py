"""Derive the top-N nearest neighbours for every movie from similarity.pkl.

The app only ever needs the *ranking* of similar movies, never the raw cosine
scores, so shipping the full 4809x4809 float64 matrix (185 MB) to the runtime is
wasteful. This collapses it to a (4809, 20) int16 index table -- about 188 KB --
which is what app.py loads.

similarity.pkl is kept in the repo as the documented model artifact; it is simply
no longer read at runtime.

Run from the project root:  python scripts/build_neighbours.py
"""

import pickle
import numpy as np

TOP_N = 20
CHUNK = 500  # rows at a time; a full-matrix argsort would peak around 370 MB


def build(similarity, top_n=TOP_N, chunk=CHUNK):
    n = similarity.shape[0]
    if n - 1 < top_n:
        raise ValueError(f"need more than {top_n} movies, got {n}")

    neighbours = np.empty((n, top_n), dtype=np.int16)

    for start in range(0, n, chunk):
        block = similarity[start:start + chunk]
        # A stable sort breaks ties by ascending index, which is exactly what
        # Python's stable sorted(..., reverse=True) did in the original code.
        # Ties at equal cosine scores are common, so this is what keeps the
        # precomputed rankings byte-identical to the old runtime sort.
        ranked = np.argsort(-block, axis=1, kind='stable')[:, :top_n + 1]

        # Drop the movie itself rather than assuming it sits at column 0, so a
        # tie at 1.0 can never silently shift the window by one.
        for r, self_idx in enumerate(range(start, start + block.shape[0])):
            row = ranked[r]
            neighbours[start + r] = row[row != self_idx][:top_n]

    return neighbours


def main():
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)

    print(f"loaded similarity {similarity.shape} {similarity.dtype} "
          f"({similarity.nbytes / 1e6:.1f} MB)")

    if similarity.shape[0] > np.iinfo(np.int16).max:
        raise ValueError("too many movies for int16 indices")

    neighbours = build(similarity)

    with open('neighbours.pkl', 'wb') as f:
        pickle.dump(neighbours, f, protocol=4)

    print(f"wrote neighbours.pkl {neighbours.shape} {neighbours.dtype} "
          f"({neighbours.nbytes / 1024:.0f} KB)")


if __name__ == '__main__':
    main()
