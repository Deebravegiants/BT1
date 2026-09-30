# [M] Vests can be denied

## Summary
Severity: Medium
Contest weight: 0.0717
Dataset id: 1246
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `LinearVesting.vestFor` function (which is called by `Converter`) reverts if there already exists a vest for the user:
    
require(
    vest[user].amount == 0,
    "LinearVesting::selfVest: Already a vester"
);

There’s an attack where a griefer frontruns the `vestFor` call and instead vests the smallest unit of VADER for the `user`. The original transaction will then revert and the vest will be denied

## Recommendation
There are several ways to mitigate this. The most involved one would be to allow several separate vestings per user.
