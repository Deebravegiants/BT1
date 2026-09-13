# [?] [simulator] Fix race condition when creating LocalBeaconNode (#2137)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2021-01-14
Source: https://github.com/sigp/lighthouse/commit/e5b1a37110b72db03d5eea98a7c317b491157941
Type: security-commit

## Details
[simulator] Fix race condition when creating LocalBeaconNode (#2137)

## Issue Addressed

We have a race condition when counting the number of beacon nodes. The user could end up seeing a duplicated service name (node_N).

## Proposed Changes

I have updated to acquire write lock before counting the number of beacon nodes.
