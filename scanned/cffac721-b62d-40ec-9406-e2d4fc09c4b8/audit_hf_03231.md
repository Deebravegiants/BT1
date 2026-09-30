# [C] MKTU-2 | Incorrect Funding Per Size Calculation

## Summary
Severity: Critical
Contest weight: 0.1303
Dataset id: 17850
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
shortCollateralFundingPerSizeForLongs is being both added to and subtracted in the same branch which not only misrepresents the true value of shortCollateralFundingPerSizeForLongs, but also leaves the longCollateralFundingPerSizeForShorts uninitialized. This negatively impacts the purpose of the funding fee which is to incentivize long and short balance in the pool.

## Recommendation
Change line 655 to cache.fps.longCollateralFundingPerSizeForShorts -= cache.fps.fundingAmountPerSizeForLongCollateralForShorts.toInt256(); Change line 661 to cache.fps.longCollateralFundingPerSizeForShorts += cache.fps.fundingAmountPerSizeForLongCollateralForShorts.toInt256();
