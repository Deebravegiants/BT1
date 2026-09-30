# [M] MKTU-3 | nextSavedFundingFactorPerSecond Cycling

## Summary
Severity: Medium
Contest weight: 0.1100
Dataset id: 19215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The nextSavedFundingFactorPerSecond can be decreased to 0 in the event that the
cache.savedFundingFactorPerSecondMagnitude == decreaseValue.
This can result in the funding side increasing rather than decreasing since it isn’t set to 1 or -1:
Long OI < short OI
Original nextSavedFundingFactorPerSecond = -10
Original longsPayShorts = false
decreaseValue = 10
nextSavedFundingFactorPerSecond = 0
Long OI < Short OI
nextSavedFundingFactorPerSecond = 0
isSkewTheSameDirectionAsFunding = false
increaseValue = 13
nextSavedFundingFactorPerSecond = -13
Therefore the fundingFactorPerSecond was meant to decrease in magnitude but increased instead.

## Recommendation
Avoid this cycling by assigning the nextSavedFundingFactorPerSecond to 1 or -1 in the if case on line
1316 by changing the cache.savedFundingFactorPerSecondMagnitude < decreaseValue to
cache.savedFundingFactorPerSecondMagnitude <= decreaseValue.
