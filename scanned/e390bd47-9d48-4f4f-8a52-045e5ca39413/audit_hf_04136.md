# [M] ADAP-4 | Lack Of Reusability

## Summary
Severity: Medium
Contest weight: 0.0692
Dataset id: 20596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Many of the functions in the Adapter are copies of functions in the OrderManager or have slight variations e.g. getProfitOrLossInCollateral. Furthermore, functions such as getAvgPriceWithDeviation and getPriceWithDeviation in the Adapter perform the exact same calculations where the only difference is the deltaSize parameter.

## Recommendation
Extract common components into a single library. This will help prevent any discrepancy between Adapter and OrderManager readings. Furthermore, any functions that are duplicative (e.g. getAvgPriceWithDeviation) should be calling helpers with common functionality extracted.
