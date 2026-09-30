# [M] M-09 | Preview Functions In SuperPool Are Not Accurate

## Summary
Severity: Medium
Contest weight: 0.1841
Dataset id: 2544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SuperPool is a contract that is compatible with ERC4626. It includes multiple preview functions that, in the end, call internal functions _convertToShares or _convertToAssets.
These internal functions utilize the lastTotalAssets variable in their calculations. However, lastTotalAssets does not represent the most updated asset amount, as it does not account for accrued interest since the last update. Therefore, the results of the preview functions are not accurate.
Some more examples of non-compliance include:
• previewDeposit does not simulate accrue, so deposit might mint less shares than previewed.
• previewMint does not simulate accrue, so mint might consume more assets than previewed.
• previewRedeem does not simulate accrue, so redeem might withdraw less assets than previewed.
• previewWithdraw does not simulate accrue, so withdraw might burn more shares than previewed.
• maxDeposit/maxMint do not correctly return the amount that can be deposited, as the cap can be bypassed.
• maxDeposit/maxMint do not return 0 if pools are paused for deposits
• maxWithdraw/maxRedeem return more assets than the real amount available, as pool.getLiquidityOf adds interest accrued.
• deposit should revert if all of assets cannot be deposited (due to poolCap limit)

## Recommendation
To ensure accurate preview calculations, it is suggested to call the simulateAccrue function and utilize the returned newTotalAssets value. This will provide a more precise calculation of assets including accrued interest. Furthermore, consider making the Superpool EIP-4626 compliant.
