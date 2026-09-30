# [M] MKTU-3 | Shorts Arbitrarily Pay Stable Funding To Longs

## Summary
Severity: Medium
Contest weight: 0.1208
Dataset id: 18866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event that OI is balanced for longs/shorts, shorts will arbitrarily pay longs because of the definition of result.longsPayShorts: result.longsPayShorts = cache.longOpenInterest > cache.shortOpenInterest. Normally, the fundingUsd would be 0 in this case as the resulting fundingFactorPerSecond is 0 when the OI is balanced. However when there is a stable funding factor configured the fundingFactorPerSecond will be nonzero when the OI is balanced. Therefore when there is a stable funding factor configured, shorts will arbitrarily pay longs the stable funding factor. This causes an incentive to stop shorting and join the long side to collect funding fees rather than pay them. Even though OI is already balanced, which undermines the point of funding fees.

## Recommendation
Skip the update per size delta logic when there is a stable funding factor present and the long open interest is equivalent to the short open interest.
