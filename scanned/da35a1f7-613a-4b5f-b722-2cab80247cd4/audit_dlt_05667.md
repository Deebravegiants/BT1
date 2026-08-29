# [?] Fix genesis state download panic when running in debug mode (#4753)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-09-21
Source: https://github.com/sigp/lighthouse/commit/a0478da99087e5f8f727864e055d179b9618c374
Type: security-commit

## Details
Fix genesis state download panic when running in debug mode (#4753)

## Issue Addressed

#4738 

## Proposed Changes

See the above issue for details. Went with option #2 to use the async reqwest client in `Eth2NetworkConfig` and propagate the async-ness.
