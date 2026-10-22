# [M] Important setter functions are not constrained

## Summary
Severity: Medium
Contest weight: 0.0886
Dataset id: 16654
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are couple of methods in ZKTBase.sol that don't have input validations, checking if the arguments value are too big or too small. A malicious/compromised admin, or one that does a "fat-finger", can input a huge number as those methods' argument, which will messed up the protocol's logic as some of these functions are doing important maths regarding fee calculation or wrong calculation of the conversion from unitAmount to nativeAmount for example. These functions are:
setBurnFeeStrategy()
setTransferFeeStrategy()
setEpochBase()
setEpochLength()
setUnit()
ZKT_Tsunami.md

## Recommendation
Add reasonable constrains for these methods
