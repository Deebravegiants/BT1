# [H] MJR-1 Excess reserve amount

## Summary
Severity: High
Contest weight: 0.0362
Dataset id: 6968
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At lines CCapableErc20.sol#L250-L252 contract increases internalCash and totalReserves values, but it's so strange that internalCash increased by totalFee and totalReserves increased by reservesFee so we totally increased assets amount by reservesFee + totalFee however user paid only totalFee . It seems there are some uncollateralized reservesFee . May be there totalFee paid by user should be splitted to internalCash and totalReserves ?

## Recommendation
We recommend to double check that place
