'''
This file is part of an ICSE'18 submission that is currently under review.
For more information visit: https://github.com/icse18-FAST/FAST.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''


import random
import sys

import lsh


def get_signatures(test_cases, hashes, bbox=False, k=5):
    all_signatures = {}
    tc_id = 1
    for tc in test_cases:
        signatures = []
        if bbox:
            # shingling
            tc_ = tc
            tc_shingles = set()
            for i in range(len(tc_) - k + 1):
                tc_shingles.add(hash(tc_[i:i + k]))

            sig = lsh.tc_minhashing((tc_id, set(tc_shingles)), hashes)
        else:
            tc_ = tc[:-1].split()
            sig = lsh.tc_minhashing((tc_id, set(tc_)), hashes)
        for hash_ in sig:
            signatures.append(hash_)
        all_signatures[tc_id] = signatures
        tc_id += 1
    return all_signatures


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# lsh + pairwise comparison with candidate set
def fast_pw(test_cases1, r, b, bbox=False, k=5, B=0):
    """INPUT
    (list): compacted files
    (int)r: number of rows
    (int)b: number of bands
    (bool)bbox: True if BB prioritization
    (int)k: k-shingle size (for BB prioritization)
    (bool)memory: if True keep signature in memory and do not store them to file

    OUTPUT
    (list)P: prioritized test suite
    """
    n = r * b  # number of hash functions

    hashes = [lsh.hash_family(i) for i in range(n)]

    tcs_minhashes = get_signatures(test_cases1, hashes, bbox, k)
    tcs = set(tcs_minhashes.keys())

    # budget B modification
    if B == 0:
        B = len(tcs)

    BASE = 0.5
    SIZE = int(len(tcs)*BASE) + 1

    bucket = lsh.lsh_bucket(tcs_minhashes.items(), b, r, n)

    prioritized_tcs = [0]

    # First TC

    selected_tcs_minhash = lsh.tc_minhashing((0, set()), hashes)
    if len(test_cases1) > 0:
        first_tc = random.choice(list(tcs_minhashes.keys()))
        for i in range(n):
            if tcs_minhashes[first_tc][i] < selected_tcs_minhash[i]:
                selected_tcs_minhash[i] = tcs_minhashes[first_tc][i]
        prioritized_tcs.append(first_tc)
        tcs -= set([first_tc])
        del tcs_minhashes[first_tc]

        iteration, total = 0, float(len(tcs_minhashes))
        while len(tcs_minhashes) > 0:
            iteration += 1
            if iteration % 100 == 0:
                sys.stdout.write("  Progress: {}%\r".format(
                    round(100*iteration/total, 2)))
                sys.stdout.flush()

            if len(tcs_minhashes) < SIZE:
                bucket = lsh.lsh_bucket(tcs_minhashes.items(), b, r, n)
                SIZE = int(SIZE*BASE) + 1

            sim_cand = lsh.lsh_candidates(bucket, (0, selected_tcs_minhash),
                                          b, r, n)
            filtered_sim_cand = sim_cand.difference(prioritized_tcs)
            candidates = tcs - filtered_sim_cand

            if len(candidates) == 0:
                selected_tcs_minhash = lsh.tc_minhashing((0, set()), hashes)
                sim_cand = lsh.lsh_candidates(bucket, (0, selected_tcs_minhash),
                                              b, r, n)
                filtered_sim_cand = sim_cand.difference(prioritized_tcs)
                candidates = tcs - filtered_sim_cand
                if len(candidates) == 0:
                    candidates = tcs_minhashes.keys()

            selected_tc, max_dist = random.choice(tuple(candidates)), -1
            for candidate in tcs_minhashes:
                if candidate in candidates:
                    dist = lsh.j_distance_estimate(
                        selected_tcs_minhash, tcs_minhashes[candidate])
                    if dist > max_dist:
                        selected_tc, max_dist = candidate, dist

            for i in range(n):
                if tcs_minhashes[selected_tc][i] < selected_tcs_minhash[i]:
                    selected_tcs_minhash[i] = tcs_minhashes[selected_tc][i]

            prioritized_tcs.append(selected_tc)

            # select budget B
            if len(prioritized_tcs) >= B+1:
                break

            tcs -= set([selected_tc])
            del tcs_minhashes[selected_tc]

        prioritized_tcs.remove(0)
        return prioritized_tcs
    else:
        print("No java test files in this repository")
