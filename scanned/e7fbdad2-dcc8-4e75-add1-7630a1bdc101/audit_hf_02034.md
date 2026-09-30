# [M] Proper And Consistent Collateral Enabling

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 11575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Aave protocol supports dynamic updates on the set of assets that are considered as collateral.
This is important as these collateral assets directly determine the borrowing power of the respective users. In addition, these collateral assets have profound implications on the new features on eMode and isolation mode. While reviewing the logic to enable a collateral, we observe unnecessary inconsistency that may introduce unwanted confusion and errors.
To elaborate, we show below the executeSupply() function from the SupplyLogic library. To turn on the collateral, the logic requires (!isolationModeActive && (reserveCache.reserveConfiguration.getDebtCeiling()== 0)) or !userConfig.isUsingAsCollateralAny() (lines 72–73).
```solidity
function executeSupply(
    mapping(address => DataTypes.ReserveData) storage reserves,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ExecuteSupplyParams memory params
) external {
    DataTypes.ReserveData storage reserve = reserves[params.asset];
    DataTypes.ReserveCache memory reserveCache = reserve.cache();
    reserve.updateState(reserveCache);
    ValidationLogic.validateSupply(reserveCache, params.amount);
    reserve.updateInterestRates(reserveCache, params.asset, params.amount, 0);
    IERC20(params.asset).safeTransferFrom(msg.sender, reserveCache.aTokenAddress, params.amount);
    bool isFirstSupply = IAToken(reserveCache.aTokenAddress).mint(
        params.onBehalfOf,
        params.amount,
        reserveCache.nextLiquidityIndex
    );
    if (isFirstSupply) {
        (bool isolationModeActive, , ) = userConfig.getIsolationModeState(reserves, reservesList);
        if (
            ((!isolationModeActive && (reserveCache.reserveConfiguration.getDebtCeiling() == 0)) ||
            !userConfig.isUsingAsCollateralAny())
        ) {
            userConfig.setUsingAsCollateral(reserve.id, true);
            emit ReserveUsedAsCollateralEnabled(params.asset, params.onBehalfOf);
        }
    }
    emit Supply(params.asset, msg.sender, params.onBehalfOf, params.amount, params.referralCode);
}
```
However, if we examine another function mintUnbacked() from the BorrowLogic library, the logic simply requires it is the isFirstSupply.
The inconsistency on the same collateral-enabling logic among current libraries SupplyLogic, BridgeLogic, and LiquidationLogic needs to be resolved before production deployment.
```solidity
function mintUnbacked(
    DataTypes.ReserveData storage reserve,
    DataTypes.UserConfigurationMap storage userConfig,
    address asset,
    uint256 amount,
    address onBehalfOf,
    uint16 referralCode
) external {
    DataTypes.ReserveCache memory reserveCache = reserve.cache();
    reserve.updateState(reserveCache);
    ValidationLogic.validateSupply(reserveCache, amount);
    uint256 unbackedMintCap = reserveCache.reserveConfiguration.getUnbackedMintCap();
    uint256 reserveDecimals = reserveCache.reserveConfiguration.getDecimals();
    uint256 unbacked = reserve.unbacked = reserve.unbacked + Helpers.castUint128(amount);
    require(
        unbackedMintCap > 0 && unbacked / (10**reserveDecimals) < unbackedMintCap,
        Errors.VL_UNBACKED_MINT_CAP_EXCEEDED
    );
    reserve.updateInterestRates(reserveCache, asset, 0, 0);
    bool isFirstSupply = IAToken(reserveCache.aTokenAddress).mint(
        onBehalfOf,
        amount,
        reserveCache.nextLiquidityIndex
    );
    if (isFirstSupply) {
        userConfig.setUsingAsCollateral(reserve.id, true);
        emit ReserveUsedAsCollateralEnabled(asset, onBehalfOf);
    }
    emit MintUnbacked(asset, msg.sender, onBehalfOf, amount, referralCode);
}
```

## Recommendation
Revise the above functions to be consistent on the enabling of a specific asset as collateral.
