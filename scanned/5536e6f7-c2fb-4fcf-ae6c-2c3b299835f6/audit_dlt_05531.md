# [?] Fix for underflow error when offchain price timestamp is bigger than current block timestamp (#2195)

## Summary
Severity: Unknown
Chain: Synthetix
Component: Synthetixio/synthetix-v3
Published: 2024-07-13
Source: https://github.com/Synthetixio/synthetix-v3/commit/2ac0fdfed5ff1ec687da9903d8fdc54394dada89
Type: security-commit

## Details
Fix for underflow error when offchain price timestamp is bigger than current block timestamp (#2195)

* Fix for underflow error when offchain price timestamp is bigger than current block timestamp

* Add a test for the price update from the future

* Simplified staleness check
