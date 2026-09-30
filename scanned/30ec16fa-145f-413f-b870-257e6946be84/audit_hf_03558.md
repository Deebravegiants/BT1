# [M] ATPH-3 | Average Entry Can Be Rounded In User’s Favor

## Summary
Severity: Medium
Contest weight: 0.1081
Dataset id: 19360
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When rounding operations are performed, it is safer for the protocol to round against the users so that there is a smaller likelihood of needing to use the insurance fund or ADL. The average entry price is calculated using position.averageEntryPrice = halfDown16_8(-openingCost, currentHolding).toUint128() which rounds up if the fractional part is greater than half, and down otherwise. When a trader is long, it is possible for the entry price to round down which would provide the user a superior entry as they want to buy as low as possible. When a trader is short, it is possible for the entry price to round up which would provide the user a superior entry as they want to sell as high as possible.

## Recommendation
Round against the user depending on their trade direction.
