# [?] fix: overflow in horizon computation (#15332)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-03-06
Source: https://github.com/near/nearcore/commit/49a520b36c5463ae626ea4376c71c3c48b00acfc
Type: security-commit

## Details
fix: overflow in horizon computation (#15332)

- rewrote height_within_front_horizon and height_within_rear_horizon in
chain/chunks/src/chunk_cache.rs to avoid integer overflow when
largest_seen_height or height is near u64::MAX.
- added test_height_within_horizon_no_overflow covering normal ranges,
largest_seen_height = 0, and largest_seen_height = u64::MAX.
