# [H] H-10 | DoS In _withdrawToVault Due To Underflow

## Summary
Severity: High
Contest weight: 0.2415
Dataset id: 22168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the Fraxlend pair does not have enough assets to lend, necessary amounts are transferred from the LendingAssetVault(LAV), and Frax shares are minted to LAV. The opposite occurs when removing leverage: Frax shares are burned from the LAV, and assets are transferred back to the vault. The share amounts to mint and burn are always in favor of the protocol. Frax shares that the LAV receives during borrowing are rounded down in _depositFromVault, while Frax shares burned during repayment are rounded up in _withdrawToVault, as expected. In the _repayAsset function, the _withdrawToVault is called with the asset amounts to repay. However, this causes DoS in certain situations. When attempting to transfer the entire utilized amount back (_extAmount == _externalAssetsToWithdraw), the share amount is rounded up in _withdrawToVault, causing the function to revert due to the insufficient balance error, as the LAV holds 1 fewer shares.

## Recommendation
Check the share balance of the LAV before burning, and burn shares up to LAV balance.
