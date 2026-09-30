# [H] User can close a vault that should be liquidated

## Summary
Severity: High
Contest weight: 0.5906
Dataset id: 9276
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The closeVault function closes a vault and returns the collateral to the user. The problem occurs because the function does not check if the vault that is to be closed is eligible for liquidation as seen below.
Keiko_audit.md
```solidity
(uint256 collateralAmount, uint256 debtAmount,) =
manageDebtInterest(vaultCollateral, msg.sender);
require(collateralAmount != 0, "Vault doesnt exists");
totalCollateral[vaultCollateral] -= collateralAmount;
totalDebt[vaultCollateral] -= debtAmount;
totalProtocolDebt -= debtAmount;
activeVaults -= 1;
lastDebtUpdateTime[msg.sender][vaultCollateral] == 0;
IVaultManager(vaultManager).adjustVaultData(vaultCollateral,
msg.sender, 0, 0, 0);
IVaultSorter(vaultSorter).removeVault(vaultCollateral,
msg.sender);
IERC20(debtToken).burn(msg.sender, debtAmount);
IERC20(vaultCollateral).transfer(msg.sender, collateralAmount);
emit VaultClosed(msg.sender, collateralAmount, debtAmount);
```

This means that when the user goes to close the vault, he will leave the protocol with bad debt and increase the chance that the protocol will become insolvent.
This will also allow the user to bypass liquidations by front running the liquidation call with closing the vault.

## Recommendation
It is important to not allow vaults who are not eligible for liquidation to close vaults, users should increase collateral and achieve the MCR in order to close said vault.
