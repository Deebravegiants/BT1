# [M] M-08 | Collateral Can Be Stuck After Closing Position

## Summary
Severity: Medium
Contest weight: 0.1224
Dataset id: 22064
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling modifyTraderPosition to close a position the system will not automatically withdraw all collateral of the position and instead withdraw based on the given collateralAmount. This means when a trader makes the mistake of providing a positive collateralAmount to the modifyTraderPosition when closing the position, the closed position will still own collateral. The user can't call the function again with a 0 tokenAmount and 0 collateralAmount to withdraw the remaining collateral, as this will call _closePosition again and perform a 0 token swap which will revert. Therefore there are only two ways to withdraw the remaining collateral:
• Wait till the epoch is settled (which could take up to a month)
• Call modifyTraderPosition to open a new position and close it again (which costs trading fees)

## Recommendation
Automatically withdraw all remaining collateral when closing a position.
