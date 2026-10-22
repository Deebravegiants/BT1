# [M] LGR-4 | Large Withdrawals Can Fail

## Summary
Severity: Medium
Contest weight: 0.0981
Dataset id: 19364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the executeWithdrawAction function, there is a check to ensure that the withdraw.fee is less than the maxWithdrawFee. However the maxWithdrawFee is a fixed value that will be used for all withdrawals. While the withdraw.fee will be a percentage based on the size of the individual withdraw. Because the two are inherently misaligned, there is a risk that large withdraws will fail as their withdraw.fee will be greater than the maxWithdrawFee. Users in this scenario will need to break up their withdrawals into multiple smaller withdrawals leading to operational inefficiency.

## Recommendation
Make maxFee percentage based so that the fee is never more than X percentage of the amount being withdrawn. This will ensure that all valid withdrawals are still possible.
