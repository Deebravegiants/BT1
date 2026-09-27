# [?] Fix race condition in seen caches (#1937)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-11-22
Source: https://github.com/sigp/lighthouse/commit/426b3001e06daacfad3d68e6ba27bb07ef442444
Type: security-commit

## Details
Fix race condition in seen caches (#1937)

## Issue Addressed

Closes #1719

## Proposed Changes

Lift the internal `RwLock`s and `Mutex`es from the `Observed*` data structures to resolve the race conditions described in #1719.

Most of this work was done by @paulhauner on his `lift-locks` branch, I merely updated it for the current `master` and checked over it.

## Additional Info

I think it would be prudent to test this on a testnet or two before mainnet launch, just to be sure that the extra lock contention doesn't negatively impact performance.
