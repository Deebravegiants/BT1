# [M] M-33 | Funding Rate Affected By Updates

## Summary
Severity: Medium
Contest weight: 0.1353
Dataset id: 199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _fundingPerDay function the resulting _fundingPerDay value is a function of the current imbalance added to the existing EMA value. This resulting _fundingPerDay value is then factored into the EMA.
The additive nature of the current skew to the current EMA for the resulting _fundingPerDay value means that the more updates occur in a given timeframe the higher the funding will be.
In the attached PoC shows that in a week period the funding is 34% greater if there is an update every day versus if there are only updates at the beginning and end of the period.
This is unexpected as the amount of updates should not affect the funding amount paid or the funding rate and instead this should be based purely on the skew experienced and the time of imbalance.

## Recommendation
Consider refactoring the funding calculations such that the fundingPerDay portion that is based upon the current imbalance as represented by numerator^2 * _fundingSF / denominator^2 is simply factored into the EMA as the latest data point instead of adding it to the EMA for the resulting _fundingPerDay value.
The latest EMA computed this way including the most recent skew calculation can be used to compute the resulting funding value.
