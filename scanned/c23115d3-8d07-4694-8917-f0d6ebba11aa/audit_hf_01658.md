# [M] Incorrect decimal handling

## Summary
Severity: Medium
Contest weight: 0.4554
Dataset id: 8980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PositionManager and LiquidationManager contracts incorrectly handles decimals when calculating across various processes. The issue stems from assuming all values are 18 decimals when performing calculations, while vault shares inherit decimals from their underlying token through Vault.decimals(). Therefore, for the vault supported assets with decimals != 18, or the decimal offset > 0, the current process will treat the share amount as 18 decimals despite the fact that the collateralSnapshots are stored with vault decimals (@1>).
```solidity
//File: src/core/PositionManager.sol
function deposit(uint8 _index, uint256 _amountToDeposit) external {
    --- SNIPPED ---
    asset.transferFrom(msg.sender, address(this), _amountToDeposit);
    @1> uint256 shares = vault.deposit(_amountToDeposit, address(this));
    _accruePositionDebt(_index, vaultData, positionData);
    @1> vaultData.collateralSnapshot += shares;
    @1> positionData.collateralSnapshot += shares;
    emit Deposit(vaultData.addr, msg.sender, _amountToDeposit);
```
This causes:
1. Incorrect value to calculate CR for the position across the PositionManager and LiquidationManager contracts:
   PositionManager._checkCR()
   PositionManager.accountCr()
   LiquidationManager._getLiquidationValues()
   LiquidationManager._calculateCr()
   This can both bypass the CR checks (for > 18 decimals) or always present the CR less than MCR (for < 18 decimals) that will cause position to present as always liquidatable.
2. Incorrect value to calculate requiredCollateral in the LiquidationManager._getLiquidationValues() as it always present the 18 decimals, when it compares and processes with the liquidatedCollateral ( _positionData.collateralSnapshot ) the value is wrong in that process.
Note that the WBTC asset with 8 decimals value is potentially to be used as per the documentation.

## Recommendation
Correctly normalize the decimals in the PositionManager and LiquidationManager contracts for the vaults with decimals != 18 when handling those values in both calculation, comparison, and validation processes.
