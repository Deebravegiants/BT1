# [M] Fees can be > 100%

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

A validator can be created with `feeRate > 1000` which would mean that the fee rate would be higher than 100%. Severity is not high because that validator will most likely be not whitelisted.

Also, 100%+ fees would still somehow work and not revert because of the absence of `SafeMath`.

#### Recommendation

Add sanity check for the input values in `registerValidator`, and do not allow adding a validator with a fee rate higher than 100%.
