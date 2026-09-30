# [C] IPU-1 | Rounding Leads To Risk Free Trade

## Summary
Severity: Critical
Contest weight: 0.2474
Dataset id: 18195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In increasePosition, the sizeDeltaInTokens is rounded down for long positions. An attacker can provide a sizeDeltaUsd that is 1 wei less than their triggerPrice and have their sizeDeltaInTokens rounded to 0. In this case a LimitIncrease would revert with the EmptyPosition error. The attacker can make a LimitIncrease long for a niche market with low open interest where it is easy to manipulate the price impact by controlling the open interest. The attacker can then manipulate the open interest such that their LimitIncrease long is positively price impacted, meaning their executionPrice is decreased. A reduction in the executionPrice would cause the sizeDeltaInTokens to no longer be rounded to 0, and the order to no longer revert with an EmptyPosition error. The attacker can leverage this with a large initialCollateralDeltaAmount and a swapPath that allows them to take advantage of outdated prices for a risk-free trade.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/IPU_1.ts

## Recommendation
Do not allow users to create position orders with any sizeDeltaUsd less than a particular value such as 1e30 e.g. $1.
