# [M] PORT-5 | Liquidation Can Fail Due to Rounding

## Summary
Severity: Medium
Contest weight: 0.0619
Dataset id: 116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the removeMargin function, the amountToRemove rounds up when being transferred. The issue with this is that by rounding up, it is possible for amountToRemove to be greater than the available balance. This will cause the transfer to revert and potentially prevent liquidations via the removeMargin function when the effective margin of the asset is at 100%.

## Recommendation
When converting from the price amount to the token amount, do not round up.
