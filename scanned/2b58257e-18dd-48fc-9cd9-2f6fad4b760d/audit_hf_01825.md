# [M] Consider implementing timelock for onlyPoolAdmin functions

## Summary
Severity: Medium
Contest weight: 0.0731
Dataset id: 10129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MasterchefAtoken.sol, the PoolAdmin can call setRewardFeeAddress which changes the setRewardFeeRate function can be called and the fees can be changed to 100%. This will have a direct financial or trust impact on users who should be given an opportunity to react to them by exiting / engaging without being surprised when changes initiated by such functions are made.

## Recommendation
A timelock provides more guarantees and reduces the level of trust required, thus decreasing risk for users. It also indicates that the project is legitimate. Consider adding a timelock to both setRewardFeeAddress and setRewardFeeRate.
