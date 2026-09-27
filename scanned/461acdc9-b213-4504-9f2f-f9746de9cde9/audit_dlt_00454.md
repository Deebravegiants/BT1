# [?] progcache: fix rec lock underflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-27
Source: https://github.com/firedancer-io/firedancer/commit/8b4e864b3d30230dd40d08cf26556f21eb1af7df
Type: security-commit

## Details
progcache: fix rec lock underflow

Fixes a race between search_chain recovery (unread after map_chain
seqlock failure) and record allocation (resets lock to 0), thus
underflowing rec lock to USHORT_MAX and causing a deadlock.
