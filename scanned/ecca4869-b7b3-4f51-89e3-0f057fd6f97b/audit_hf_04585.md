# [M] M-18 | Wrong Price Calculations If T0 Is baseToken

## Summary
Severity: Medium
Contest weight: 0.0566
Dataset id: 22188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the base token is one of the two tokens in the UNDERLYING_TKN_CL_POOL, it has to be token1. That's because _pricePTKNPerBase18 is calculated based on whether or not the base token is part of that pool by checking if it's token1. This means for pools where the base token is token0 the price will be wrongly flipped.

## Recommendation
If the base token is included in the pool pair, always make sure it's the token1.
