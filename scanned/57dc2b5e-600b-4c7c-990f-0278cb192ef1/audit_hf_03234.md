# [C] ORDH-1 | Risk Free Trades From Empty Positions

## Summary
Severity: Critical
Contest weight: 0.1766
Dataset id: 17853
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The custom handling for the Keys.EMPTY_POSITION_ERROR_KEY allows users to create MarketDecrease orders that continue to revert and be retried until the user creates a position. The MarketDecrease order would then be executed at the prices of the block in which the decrease order was created. This way a user can submit a long MarketDecrease for an empty position, and wait until the price of the index token decreases before submitting a MarketIncrease order and realizing risk-free profits from the exchange.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L116

## Recommendation
Do not revert and retry on Keys.EMPTY_POSITION_ERROR_KEY.
