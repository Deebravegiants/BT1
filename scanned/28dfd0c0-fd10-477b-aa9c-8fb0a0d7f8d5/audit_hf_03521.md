# [M] MKTU-5 | Funding Factor Spikes To Max

## Summary
Severity: Medium
Contest weight: 0.0892
Dataset id: 19231
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because the increaseValue is dependent on durationInSeconds, when a period of time goes by without updates the cache.nextSavedFundingFactorPerSecond can spike to the maximum bound. This can occur when the skew changes, causing an increase to a large fundingFactorPerSecond regardless of the new OI diff. The situation also may arise if the savedFundingFactorPerSecond is at 0 and the duration is large, regardless of whether the previous fundingRateChangeType was an increase or no change.

## Recommendation
It's crucial to track the min/max limits and make adjustments as needed. Additionally, consider refactoring the funding such that these spikes do not occur when the skew is switching sides or the savedFundingFactorPerSecond is 0.
