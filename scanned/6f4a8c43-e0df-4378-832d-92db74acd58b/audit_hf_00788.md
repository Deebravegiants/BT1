# [H] H-09 | Util Ratio Calculation Is Incorrect

## Summary
Severity: High
Contest weight: 0.2101
Dataset id: 2524
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LinearRateModel calculates the totalAssets amount by summing up the totalBorrows and the idleAssetAmt. But the idleAssetAmt already is the totalAssets amount (pool.totalAssets.assets from the BasePool). This leads to an incorrect calculation of the utilization ratio.
For example:
Unborrowed Amount = 500
Borrowed Amount = 500
Therefore util ratio = 50%
Calculation in the LinearRateModel:
idleAssetAmt = pool.totalAssets.assets = 1000
totalAssets = totalBorrows + idleAssetAmt = 500 + 1000 = 1500
util = totalBorrows / totalAssets = 500 / 1500 = 33.33%
Therefore the calculated utilization ratio is 33.33% when 50% of the funds are borrowed. As the utilization ratio is smaller than it should be the lender receives less interest than they should.

## Recommendation
Do not calculate the totalAssets amount as the idleAssetAmt already is the totalAssets amount.
