# [M] Failing liquidation

## Summary
Severity: Medium
Contest weight: 0.3836
Dataset id: 8971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the setLiquidationManager() function of the PositionManager contract, when the liquidationManager address is changed, the new contract is not granted approval on the share tokens for all registered vaults. This results in the failure of liquidation for these vaults when the liquidationManager attempts to redeem assets to pay for the liquidator:
```solidity
function setLiquidationManager(address _newLiquidationManager) external onlyOwner {
    emit NewLiquidationManager(liquidationManager, _newLiquidationManager);
    liquidationManager = _newLiquidationManager;
```

## Recommendation
Implement a mechanism to grant the new liquidationManager address approval on all registered vaults shares.
