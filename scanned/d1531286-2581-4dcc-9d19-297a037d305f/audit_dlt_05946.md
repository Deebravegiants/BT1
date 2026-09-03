# [?] Merge pull request from GHSA-vxmm-cwh2-q762

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-05-19
Source: https://github.com/vyperlang/vyper/commit/903727006c1e5ebef99fa9fd5d51d62bd33d72a9
Type: security-commit

## Details
Merge pull request from GHSA-vxmm-cwh2-q762

on <=0.3.7, the batch payable check was broken. this was fixed due to
the removal of the global calldatasize check in 02339dfda0. this commit
adds a test to prevent regression
