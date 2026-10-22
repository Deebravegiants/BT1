# [M] PositionManager#setInterestRateStrategy fails to re-register existing vaults with the new strategy

## Summary
Severity: Medium
Contest weight: 0.5707
Dataset id: 2745
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function registerVault(uint8 _vaultId, bytes memory _registerData) external {
    _onlyPositionManager();

    (uint256 targetUtilization) = abi.decode(_registerData, (uint256));

    AdaptiveIRMStorage storage adaptiveIRM = AdaptiveIRM.getStorage();

    IPositionManager.VaultData memory vaultData = IPositionManager(positionManagerAddress).getVault(_vaultId);

    adaptiveIRM.setTargetUtilization(_vaultId, targetUtilization);

    (, int256 end) = adaptiveIRM.interestRate(_vaultId, 0, 0, vaultData.MCR);

    adaptiveIRM.updateInterestRateAtTarget(_vaultId, end);

    emit VaultRegistered(_vaultId, _registerData);
}
```

We see above that when vaults are registered, essential information about the vaults such as target utilization is communicated with the interest rate strategy.

```solidity
function setInterestRateStrategy(address _newInterestRateStrategy) external onlyOwner {
    if (_newInterestRateStrategy == address(0)) {
        revert ZeroAddress();
    }

    emit NewInterestRateStrategy(address(interestRateStrategy), address(_newInterestRateStrategy));

    interestRateStrategy = IInterestRateStrategy(_newInterestRateStrategy);
}
```

When switching interest rate strategies, notice that this is not done for any of the existing vaults. As a result the new interestRateStrategy will be unable to function correctly.

## Recommendation
All existing vaults should be re-registered with the new interest rate strategy
