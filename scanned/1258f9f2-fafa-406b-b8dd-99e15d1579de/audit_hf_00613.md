# [M] M-12 | Borrowing State Not Updated Before Config Change

## Summary
Severity: Medium
Contest weight: 0.0871
Dataset id: 2112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Borrowing params such as baseApy can be changed by admin in FacetManagement.setConfig. However, when borrowing params are changed, it affects the interest accrued by users since the last update time. For example, if baseApy was increased, users will be unfairly charged the higher rate since the last update. Consider this scenario:
T0 (last updated timestamp):
• baseApy = 1%
T5:
• Admin updates baseApy to 2%
T10:
• Trader closes position, borrowing rate is based on baseApy 2%, when it should have been 1% from T0 - T5 and 2% from T5-T10

## Recommendation
Call pool.updateMarketBorrowing before changing any borrowing params.
