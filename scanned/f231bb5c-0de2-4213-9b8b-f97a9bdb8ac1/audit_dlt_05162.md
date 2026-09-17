# [?] Fix: Out of bounds error with user defined `TrancheId` (#595)

## Summary
Severity: Unknown
Chain: Centrifuge
Component: centrifuge/centrifuge-chain
Published: 2022-01-19
Source: https://github.com/centrifuge/centrifuge-chain/commit/48aff40f50b565716a878968e48d330b4c45f00c
Type: security-commit

## Details
Fix: Out of bounds error with user defined `TrancheId` (#595)

* Refactor and ensure tranche-id not our of bounds

* Earlier error for no pool, expect msg enhanced

* Unified formating

* Cover invalid tranche-id with test-case

* Address review
