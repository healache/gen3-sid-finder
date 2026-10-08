#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: © 2026 healache <healache@posteo.org>
# SPDX-FileCopyrightText: © 2026 sakura151 <sakurakazama151@yahoo.com>
# SPDX-License-Identifier: BSD-3-Clause

"""
Find your trainer's SID for GBA ports on Switch.

The GBA ports have modern game IDs, so receiving games display their
TID in G7TID format (last 6 decimal digits of the 32-bit ID) instead
of the traditional 5-digit TID. This leaks enough information to
constrain the 32-bit ID to at most 5 candidates, letting us enumerate
possible SIDs without CFW or hunting a shiny.

Usage:
    python find_sid.py <tid> <g7tid>
"""

import sys

if sys.version_info < (3, 8):
    sys.exit("error: Python {}.{} is less than 3.8".format(*sys.version_info))

import math


def sidtid_candidates(tid: int, g7tid: int) -> range:
    """
    Return all u32 SIDTID values consistent with the given TID and G7TID.

    The 32-bit SIDTID must satisfy:
      - SIDTID ≡ g7tid (mod 10⁶)  [last 6 digits]
      - SIDTID ≡ tid (mod 2¹⁶)    [low 16 bits]

    Using CRT with step size: lcm(10⁶, 2¹⁶) = 1,024,000,000
    """
    mod_tid = 0x10000
    mod_g7 = 1_000_000

    if not (0 <= tid < mod_tid and 0 <= g7tid < mod_g7):
        message = f"tid must be 0-{mod_tid - 1}; g7tid must be 0-{mod_g7 - 1}"
        raise ValueError(message)

    g = math.gcd(mod_g7, mod_tid)
    if (tid - g7tid) % g:
        message = "tid and g7tid are inconsistent"
        raise ValueError(message)

    lcm = mod_g7 * mod_tid // g
    inv = pow(mod_g7 // g, -1, mod_tid // g)
    t = ((tid - g7tid) // g * inv) % (mod_tid // g)
    sidtid0 = (g7tid + mod_g7 * t) % lcm

    return range(sidtid0, 2**32, lcm)


if __name__ == "__main__":
    try:
        tid, g7tid = map(int, sys.argv[1:])
    except ValueError:
        sys.exit("usage: python find_sid.py <tid> <g7tid>")

    try:
        for sidtid in sidtid_candidates(tid=tid, g7tid=g7tid):
            print(sidtid >> 16)
    except ValueError as e:
        sys.exit(f"error: {e}")
