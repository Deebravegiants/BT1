# [M] GMXC-6 | Unwieldy Collateral

## Summary
Severity: Medium
Contest weight: 0.0843
Dataset id: 130
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several characteristics of GM tokens that make them less than ideal as collateral. Firstly, liquidations may be somewhat unwieldy for the liquidator as there is currently no market to swap GM tokens and unwrapping the GM tokens cannot occur in a single liquidation transaction. Additionally, if the pnlToPoolFactor in the GMX system is above the MAX_PNL_FACTOR_FOR_WITHDRAWALS GM tokens cannot be redeemed for their backing longTokens or shortTokens.

## Recommendation
No changes may be necessary, simply be aware of this unwieldiness for liquidators, ensure that liquidators are still properly incentivized and consider this when determining the COLLATERIZATION_RATE for GM tokens.
