# [H] Proper Asset Price in GenericLogic::calculateUserAccountData()

## Summary
Severity: High
Contest weight: 0.6366
Dataset id: 11567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For any lending protocol, there is a need to reliably and accurately measure the borrower's debt position and provide necessary means to liquidate underwater positions. The Aave protocol is no exception. While reviewing the implementation to measure the debt position, we notice the key function calculateUserAccountData() needs to be improved.
To illustrate, we show below this function. As the name indicates, the function is dedicated to calculate the user data across the reserves. For this end, it requires the total liquidity/collateral/borrow balances in the base currency used by the price feed, as well as the average loan to value (LVT), the average liquidation ratio, and the health factor. However, it misuses the eModeAssetPrice as the price for each iterated reserve (lines 134-136), which leads to erroneous calculation of collateral value and borrow power. This issue is possibly introduced to support the eMode feature, but has been mistakenly used to consider all reserve assets to be part of the same eMode category.
```solidity
function calculateUserAccountData(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reserves,
    mapping(uint8 => DataTypes.EModeCategory) storage eModeCategories,
    DataTypes.CalculateUserAccountDataParams memory params
) internal view returns (
    uint256,
    uint256,
    uint256,
    uint256,
    uint256,
    bool
) {
    if (params.userConfig.isEmpty()) {
        return (0, 0, 0, 0, type(uint256).max, false);
    }
    CalculateUserAccountDataVars memory vars;
    if (params.userEModeCategory != 0) {
        vars.eModePriceSource = eModeCategories[params.userEModeCategory].priceSource;
        vars.eModeLtv = eModeCategories[params.userEModeCategory].ltv;
        vars.eModeLiqThreshold = eModeCategories[params.userEModeCategory]
        .liquidationThreshold;
        if (vars.eModePriceSource != address(0)) {
            vars.eModeAssetPrice = IPriceOracleGetter(params.oracle).getAssetPrice(
                vars.eModePriceSource
            );
        }
    }
    while (vars.i < params.reservesCount) {
        if (!params.userConfig.isUsingAsCollateralOrBorrowing(vars.i)) {
            unchecked {
                ++vars.i;
                continue;
            }
        }
        vars.currentReserveAddress = reserves[vars.i];
        if (vars.currentReserveAddress == address(0)) {
            unchecked {
                ++vars.i;
                continue;
            }
        }
        DataTypes.ReserveData storage currentReserve = reservesData[
            vars.currentReserveAddress
        ];
        (vars.ltv,
        vars.liquidationThreshold,
        vars.decimals,
        vars.eModeAssetCategory
        ) = currentReserve.configuration.getParams();
        unchecked {
            vars.assetUnit = 10**vars.decimals;
            vars.assetPrice = vars.eModeAssetPrice > 0
            ? vars.eModeAssetPrice
            : IPriceOracleGetter(params.oracle).getAssetPrice(vars.currentReserveAddress);
        }
    }
    // ... rest of function omitted for brevity
}
```

## Recommendation
Apply the right price oracle in the above calculateUserAccountData() routine to compute the user account data.
