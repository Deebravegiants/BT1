# [M] M-21 | ADL Is Triggered Per Pool

## Summary
Severity: Medium
Contest weight: 0.0836
Dataset id: 2122
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When fillADLOrder is called, it validates that the position is viable for an auto deleverage. This is accomplished in isDeleverageAllowed function when it checks if any of the pools that the user has their position in is above the trigger PnL threshold. The issue is that a user could have a position, in its entirety, not exceed the trigger threshold, but has exceeded the threshold in a singular pool. This will cause the entire position to be auto deleverage, even if their position has negative PnL.

## Recommendation
Validate that the entire position is in a profitable enough state to trigger the auto deleverage.
