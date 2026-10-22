# [H] PositionManager#setLiquidationManager fails to give allowances to new liquidation manager

## Summary
Severity: High
Contest weight: 0.7630
Dataset id: 2729
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function registerVault(address _vaultAddress, uint256 _mcr, uint256 _minDebt, bytes memory _registerData)
    external
    onlyOwner
    returns (uint8)
{
    uint8 index = lastVaultIndex;

    VaultData memory data;
    data.addr = _vaultAddress;
    data.MCR = _mcr;
    data.asset = IVault(_vaultAddress).asset();
    data.interestIndex = INTEREST_PRECISION;
    data.lastInterestIndexUpdate = block.timestamp;
    data.debtCap = type(uint256).max;
    data.minDebt = _minDebt;

    vaults[index] = data;
    lastVaultIndex = index + 1;

    IVault(_vaultAddress).approve(address(liquidationManager), type(uint256).max);
    IERC20(data.asset).approve(_vaultAddress, type(uint256).max);

    interestRateStrategy.registerVault(index, _registerData);

    return index;
}
```

When vaults are registered to the PositionManager, it grants max approval to the liquidation manager for the vault asset. This is essential for the liquidation manager to function.

```solidity
function setLiquidationManager(address _newLiquidationManager) external onlyOwner {
    emit NewLiquidationManager(liquidationManager, _newLiquidationManager);

    liquidationManager = _newLiquidationManager;
}
```

We notice above that when a new manager is set, no approvals are granted. As a result the new liquidation manager will be unable to functions. This will lead to bad debt that will damage the entire system.

## Recommendation
`setLiquidationManager` should grant approval to new `LiquidationManager`
