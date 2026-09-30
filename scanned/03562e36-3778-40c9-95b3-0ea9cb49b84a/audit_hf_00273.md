# [M] Wrong comment in `getFee`

## Summary
Severity: Medium
Contest weight: 0.0911
Dataset id: 1393
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `ThreePieceWiseLinearPriceCurve.getFee` comment states that the total + the input must be less than the cap:

If dollarCap == 0, then it is not capped. Otherwise, **then the total + the total input** must be less than the cap.

The code only checks if the input is less than the cap:
    
    // @param _collateralVCInput is how much collateral is being input by the user into the system
    if (dollarCap != 0) {
        require(_collateralVCInput <= dollarCap, "Collateral input exceeds cap");
    }

## Recommendation
Clarify the desired behavior and reconcile the code with the comments.

This was an issue also found by one of our independent economic auditors. Good find. Is actually more like a medium (severity 2) issue.

Fixed in line 92
