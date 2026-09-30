# [M] the DEFAULTVALIDATOR cannot be changed

## Summary
Severity: Medium
Contest weight: 0.0658
Dataset id: 22953
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DEFAULTVALIDATOR can not alter the default staking validator staking contract. But in reality, validator-staking does not have a function related to setDEFAULTVALIDATOR. The only way to modify DEFAULTVALIDATOR is to call instantiate and reinstantiate a new validator-staking. This contradicts the documentation, so I consider this a Medium issue. the default staking validator cannot be changed.

## Recommendation
Add and modify related functions of DEFAULTVALIDATOR.
