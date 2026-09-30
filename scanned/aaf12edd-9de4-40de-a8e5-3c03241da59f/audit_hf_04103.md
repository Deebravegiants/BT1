# [M] DATA-3 | Changing Market Settings Applies Fees Retroactively

## Summary
Severity: Medium
Contest weight: 0.1389
Dataset id: 20559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Changing market settings, by calling the setMaximumOi or setBorrowingCurveConfig functions from the DataFabric contract, creates an issue regarding fee updates. Fees are updated and deducted whenever any protocol operation is settled with the current value applied for the entire time since the last fee update. Neither of the two functions call the _updateCumulativeFees function to update fees up to that point before influencing the fees. Consider a situation when there are no operations for 3 hours, in which, after 2 hours the maximum OI was decreased. The next operation will commit all fees during those 3 hours with the new OI taken into consideration for fee calculation. This results in a higher than intended fee being paid by users since only 1 hrs of those 3 hrs was spent in the market with the new, higher fees.

## Recommendation
Consider allowing a grace period when configuring these market values so that users have a time limit to modify/cancel their current positions. Call _updateCumulativeFees before setting new configuration value as to not impact fees since the last checkpoint. _updateCumulativeFees must not be called in a paused market as to not accumulate fees for users if paused.
