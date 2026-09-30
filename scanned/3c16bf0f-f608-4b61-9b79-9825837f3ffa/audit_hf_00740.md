# [M] M-04 | Owner Cannot Trigger disputeMarket

## Summary
Severity: Medium
Contest weight: 0.0927
Dataset id: 2296
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Many operations inside TruthMarketManagerV2 that change the market state can be manually
triggered by the owner. This is needed in cases where markets are paused, as only the owner can
initiate market state transitions, including disputeMarket.
However, disputeMarket uses the onlyOracleCouncil modifier, which restricts the function to being
called only by the oracle council. This is despite the function logic including a check allowing the
owner to trigger disputeMarket when markets are paused.
As a result, disputeMarket cannot be manually called by the owner when markets are paused.

## Recommendation
Consider to use onlyOracleCouncilAndOwner instead.
