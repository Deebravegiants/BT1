# [H] Wrong validation in toggleCollateralActiveState()

## Summary
Severity: High
Contest weight: 0.5851
Dataset id: 8386
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The active state of the collateral can be toggled using toggleCollateralActiveState(), which will set isActive for the specified collateral index. This allows the governance to disable specified collateral when required and prevent opening of new trades using that collateral.
However, toggleCollateralActiveState() has an error in the validation check. It reverts when collateral.precision > 0, which would occur for all existing collateral as precision is set upon added.
This will prevent governance from disabling the collateral for trading when required in an emergency situation such as depegging of the stablecoin collateral.
```solidity
function toggleCollateralActiveState(uint8 _collateralIndex) internal {
    ITradingStorage.TradingStorage storage s = _getStorage();
    ITradingStorage.Collateral storage collateral = s.collaterals[_collateralIndex];
    //@audit this will revert as precision is > 0 for existing collaterals
    if (collateral.precision > 0) {
        revert IGeneralErrors.DoesntExist();
    }
    bool toggled = !collateral.isActive;
    collateral.isActive = toggled;
    emit ITradingStorageUtils.CollateralUpdated(_collateralIndex, toggled);
}
```

## Recommendation
Change the check to collateral.precision == 0.
