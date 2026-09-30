# [M] M-05 | Negative New Margin Is Not Recognized

## Summary
Severity: Medium
Contest weight: 0.1239
Dataset id: 2262
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an order is impacted positively or negatively the price impact is applied to the rest of the existing position when computing the newMarginUsd. Because the newMarginUsd cannot go below 0, this behavior can potentially allow traders to erase losses from their position. In the case of lower minimum margin conﬁgurations, the effect from the new entry price based on the ﬁll price could create a situation which zeroes out sUSD collateral and then should create a new debtUSD amount but it does not because the newMarginUSD is not allowed to be negative in this case.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs/pull/6/files

## Recommendation
Consider reverting when the marginUsdForNextMarginUsd is negative or less than the orderFee + keeperFee. Otherwise, to allow orders that would reach this edge case to be settled, consider refactoring the settlement logic such that the PnL of the entire new position relative to the current market price is realized instead of just the existing position to the ﬁllPrice. Such a refactor would also require updates to the way the debtCorrection is handled as well.
