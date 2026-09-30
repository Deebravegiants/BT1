# [H] MJR-3 No validation of the value of the variable msg.value

## Summary
Severity: High
Contest weight: 0.2306
Dataset id: 181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the lines ClipperRouter.sol#L57-L68 processing of the input data is done before the exchange procedure.
ETH is not required to work with WETH and regular tokens. But the user can inadvertently transfer it.
In this case, the user will lose these ETH.
To prevent this from happening, you need to add checks before lines 60 and 67:
```solidity
require(msg.value == 0, "CL1IN: wrong msg.value");
```

## Recommendation
Additional checks need to be added.
