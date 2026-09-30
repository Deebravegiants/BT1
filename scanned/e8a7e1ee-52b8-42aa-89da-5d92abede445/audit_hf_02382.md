# [M] Trading Fee Discrepancy In PancakeGoblin And EspAddStrategy

## Summary
Severity: Medium
Contest weight: 0.4154
Dataset id: 12848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Rabbit protocol, a number of situations require the real-time swap of one token to another. For example, the StrategyAddTwoSidesOptimal strategy takes one underlying token and converts some portion of it to another underlying token so that their ratio matches the current swap price in the PancakeSwap pool. Note that in PancakeSwap, if you make a token swap or trade on the exchange, you will need to pay a 0.25% trading fee, which is broken down into two parts. The first part of 0.17% is returned to liquidity pools in the form of a fee reward for liquidity providers, the 0.03% is sent to the PancakeSwap Treasury, and the remaining 0.05% is used towards CAKE buyback and burn. To elaborate, we show below the getMktSellAmount() routine in PancakeGoblin. It is interesting to note that PancakeGoblin has implicitly assumed the trading fee is 0.3%, instead of 0.25%. The difference in the built-in trading fee with the actual PancakeSwap may skew the optimal allocation of assets in the developed strategies, including StrategyAddTwoSidesOptimal.
```solidity
/// @dev Return maximum output given the input amount and the
```

## Recommendation
Make the built-in trading fee consistent with the actual trading fee in PancakeSwap and Ellipsis.
