# [M] MKTU-4 | Lack of Funding Fees When OI Is Stacked

## Summary
Severity: Medium
Contest weight: 0.1102
Dataset id: 17882
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing funding fees in the getNextFundingAmountPerSize function, the cache.oi.longOpenInterest == 0 || cache.oi.shortOpenInterest == 0 condition stipulates that when all of the open interest is stacked on one side no funding fees are charged to the users who have positions on the stacked side. This means there is a lack of disincentive for the users with stacked positions to switch sides. In such a case, the funding fees could be redirected to the poolAmount for the benefit of LPers. Exchanges like Binance have a minimum funding fee that is held at all times to properly disincentivize such imbalances.

## Recommendation
Consider whether or not funding fees should be charged when there is no opposing side open interest. If funding fees should in fact be charged when only one side has all of the open interest, refactor the existing logic to charge funding fees and optionally send them to the pool or an arbitrary fee receiver.
