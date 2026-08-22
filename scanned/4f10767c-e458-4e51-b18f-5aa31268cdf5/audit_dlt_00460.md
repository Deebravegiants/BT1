# [?] Fix race condition in rebuildInMemorySorobanStateForTesting (#5351)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2026-07-16
Source: https://github.com/stellar/stellar-core/commit/3620e88f035e29c98bef76d01acd252a300c977f
Type: security-commit

## Details
Fix race condition in rebuildInMemorySorobanStateForTesting (#5351)

# Description

Fixes a flaky test I think I ran into on an unrelated
[PR](https://github.com/stellar/stellar-core/actions/runs/29378709185/job/87327140083?pr=5350).
It looks like we can call the test only module cache rebuild function
while a real, background module cache build is under way, causing an
assert failure. This just makes sure we finish any in-progress builds
before calling the test reset function.

# Checklist
- [x] Reviewed the
[contributing](https://github.com/stellar/stellar-core/blob/master/CONTRIBUTING.md#submitting-changes)
document
- [x] Rebased on top of master (no merge commits)
- [x] Ran `clang-format` v8.0.0 (via `make format` or the Visual Studio
extension)
- [x] Compiles
- [x] Ran all tests
- [ ] If change impacts performance, include supporting evidence per the
[performance
document](https://github.com/stellar/stellar-core/blob/master/performance-eval/performance-eval.md)
