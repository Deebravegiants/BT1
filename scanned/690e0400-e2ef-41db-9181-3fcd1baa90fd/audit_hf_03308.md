# [C] MKTU-1 | Impact Pool Included In Pool Value

## Summary
Severity: Critical
Contest weight: 0.2209
Dataset id: 18154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getPoolValue function, the position impact pool value is added to the value of the pool. However the position impact pool is comprised of a notional value of synthetic index tokens, therefore it should not be added to the pool value. When a trader is negatively impacted, two things happen: indexTokens are taken from the trader and allocated to the position impact pool. The trader immediately experiences a loss on their PnL. This results in the pool accounting for this negative impact amount twice. Once for the indexTokens that are allocated to the position impact pool. And a second time for the negative PnL that the trader has just experienced. This double counting invalidates the market’s accounting system and does not allow depositors to withdraw all of their MarketTokens.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_1.ts

## Recommendation
Do not account the position impact pool as a part of the net poolValue.
