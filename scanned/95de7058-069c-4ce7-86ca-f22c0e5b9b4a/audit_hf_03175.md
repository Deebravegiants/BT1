# [M] Extension logic incorrectly extends the auc-

## Summary
Severity: Medium
Contest weight: 0.0909
Dataset id: 17737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect auction extension logic extends the auction by an additional amount of the previous duration instead of extending it by 15 minutes. The calculation of newDuration incorrectly adds duration in the auction extension logic. This causes the new duration to be extended by an additional amount of the existing duration, instead of an additional 15 minutes (timeBuffer), when a bid is created in the last 15 mins of the existing auction duration. Delayed payout of funds/collateral upon auction completion only after the newly extended duration.

## Recommendation
Change the calculation to uint64 newDuration = uint256(block.timestamp + timeBuffer - firstBidTime).safeCastTo64();
