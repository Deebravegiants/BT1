# [?] fix - prevent race condition in reconstructing witness (#13794)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-06-27
Source: https://github.com/near/nearcore/commit/d4c7a74f9c555bf48219538c25beb7087036eb59
Type: security-commit

## Details
fix - prevent race condition in reconstructing witness (#13794)

We must check `processed_witnesses` under lock, to avoid some race
condition that can lead to process twice the same SW.

Note that the race conditions happen only if SW parts distribution is
changed in a way that multiple parts are delivered by multiple nodes at
very low latencies.
