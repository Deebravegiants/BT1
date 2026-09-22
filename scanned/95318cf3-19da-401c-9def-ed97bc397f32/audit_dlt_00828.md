# [?] [SEC-615] Reject malformed weight proof segments with overflow block at index 0 (#20747)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-04-02
Source: https://github.com/Chia-Network/chia-blockchain/commit/2fcaf4520c3b66c1db602f5df638ce9c9661ffe6
Type: security-commit

## Details
[SEC-615] Reject malformed weight proof segments with overflow block at index 0 (#20747)

* Reject malformed weight proof segments with overflow block at index 0

Add a bounds check in __validate_pospace before accessing
segment.sub_slots[idx - 1] on the overflow path. When idx == 0,
Python's negative indexing silently reads the last element instead of a
predecessor slot. This mirrors the existing guard in
_get_challenge_block_vdfs and returns None (same pattern as other
validation failures in this function).

* Add test for overflow block at sub-slot index 0 rejection

Exercises the new idx < 1 guard in __validate_pospace to achieve 100%
diff coverage on the defensive bounds check.
