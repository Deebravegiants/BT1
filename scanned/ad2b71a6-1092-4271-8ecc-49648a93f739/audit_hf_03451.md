# [M] EDPU-2 | Subsequent Mints Cause Market Token Inflation

## Summary
Severity: Medium
Contest weight: 0.1632
Dataset id: 18861
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the usdToMarketTokenAmount function when the supply of market tokens is 0 and the poolValue is nonzero, the resulting market token amount is the poolValue + usdValue. However in the _executeDeposit function, the marketTokensSupply and poolValue variables are cached and passed to the usdToMarketTokenAmount function twice in a row when there is positive impact. When the supply of market tokens is zero and there is some dust leftover in the poolAmount it is possible to be positively impacted and end up with: 2 * poolValue + (positiveImpactAmount.toUint256() * _params.tokenOutPrice.max) + (fees.amountAfterFees * params.tokenInPrice.min) market tokens. Thus resulting in a market token amount that double counts the poolValue. The case where this market token amount inflation occurs is rare and there is no immediate financial loss or gain. However, this market token inflation is unexpected and goes against the documented goal of a 1 USD value per market token in the usdToMarketTokenAmount function. This unexpected and undocumented behavior could be used to exploit systems building on top of GMX V2.

## Recommendation
Consider re-calculating the updated poolValue and market token supply after the positive impact application if the initial market token supply was 0. Otherwise document this unexpected behavior.
