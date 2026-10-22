# [M] A malicious admin can steal all users collat- eral

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 20447
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to Taurus contest details, all roles, including the admin Multisig, should
not be able to drain users collateral.
2. Multisig. Trusted with essentially everything but user collateral.
admin to update price feed without any restriction, such as timelock. This leads to
an attack vector that a malicious admin can steal all users collateral.
As shown of updateWrapper() function of PriceOracleManager.sol, the admin
(onlyOwner) can update any price oracle _wrapperAddress for any _underlying
collateral without any restrictions (such as timelock).
File: taurus-contracts\contracts\Oracle\PriceOracleManager.sol
36:
```solidity
function updateWrapper(address _underlying, address _wrapperAddress)
external override onlyOwner {
    if (!_wrapperAddress.isContract()) revert notContract();
    if (wrapperAddressMap[_underlying] == address(0)) revert
    wrapperNotRegistered(_wrapperAddress);
    wrapperAddressMap[_underlying] = _wrapperAddress;
    emit WrapperUpdated(_underlying, _wrapperAddress);
}
```
Hence, admin can set a malicious price oracle like
```solidity
contract AttackOracleWrapper is IOracleWrapper, Ownable {
    address public attacker;
    IGLPManager public glpManager;
    constructor(address _attacker, address glp) {
        attacker = _attacker;
        glpManager = IGLPManager(glp);
    }
    function getExternalPrice(
        address _underlying,
        bytes calldata _flags
    ) external view returns (uint256 price, uint8 decimals, bool success) {
        if (tx.origin == attacker) {
            // liquidation of all positions
        } else {
            uint256 price = glpManager.getPrice();
            return (price, 18, true);
        }
    }
}
```
Then call liquidate() to drain out users collateral with negligible $TAU cost.
File: taurus-contracts\contracts\Vault\BaseVault.sol
342:
```solidity
function liquidate(
    address _account,
    uint256 _debtAmount,
    uint256 _minExchangeRate
) external onlyLiquidator whenNotPaused updateReward(_account) returns
(bool) {
    if (_debtAmount == 0) revert wrongLiquidationAmount();
    UserDetails memory accDetails = userDetails[_account];
    // Since Taurus accounts' debt continuously decreases, liquidators
    // may pass in an arbitrarily large number in order to
    // request to liquidate the entire account.
    if (_debtAmount > accDetails.debt) {
        _debtAmount = accDetails.debt;
    }
    // Get total fee charged to the user for this liquidation.
    // Collateral equal to (liquidated taurus debt value * feeMultiplier) will be
    // deducted from the user's account.
    // This call reverts if the account is healthy or if the
    // liquidation amount is too large.
    (uint256 collateralToLiquidate, uint256 liquidationSurcharge) =
    _calcLiquidation(
        accDetails.collateral,
        accDetails.debt,
        _debtAmount
    );
    // Check that collateral received is sufficient for liquidator
    uint256 collateralToLiquidator = collateralToLiquidate -
    liquidationSurcharge;
    if (collateralToLiquidator < (_debtAmount * _minExchangeRate) /
    Constants.PRECISION) {
        revert insufficientCollateralLiquidated(_debtAmount,
        collateralToLiquidator);
    }
    // Update user info
    userDetails[_account].collateral = accDetails.collateral -
    collateralToLiquidate;
    userDetails[_account].debt = accDetails.debt - _debtAmount;
    // Burn liquidator's Tau
    TAU(tau).burnFrom(msg.sender, _debtAmount);
    // Transfer part of _debtAmount to liquidator and Taurus as fees
    // for liquidation
    IERC20(collateralToken).safeTransfer(msg.sender,
    collateralToLiquidator);
    IERC20(collateralToken).safeTransfer(
        Controller(controller).addressMapper(Constants.FEE_SPLITTER),
        liquidationSurcharge
    );
    emit AccountLiquidated(msg.sender, _account, collateralToLiquidate,
    liquidationSurcharge);
    return true;
}
```
A malicious admin can steal all users collateral

## Recommendation
update of price oracle should be restricted with a timelock.
