# [M] Revised Borrow/Supply Value Calculation in Liquidation::_getTargetMarkets()

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 12406
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LineaBank protocol, the Liquidation contract performs as a liquidation bot to liquidate the borrower's debt and send the earns to the rebate distributor. Specially, it provides an autoLiquidate() function that chooses the market with the maximum borrow value to liquidate and the market with the maximum supply value in return. While examining the calculation of the borrow/supply values in a market, we notice it does not take the token decimal into consideration. In the following, we show the code snippet of the Liquidation::_getTargetMarkets() routine, which is used to choose the market with the maximum borrow value and the market with the maximum supply value. For each market, the borrow/supply values are calculated per the borrow/supply balances of the borrower and the underlying prices (lines 223-224). However, it comes to our attention that it does not take the underlying token decimal into consideration. As a result, it does not remove the underlying token decimal from the calculated values and the chosen markets are not accurate. With that, we suggest to remove the underlying token decimal from the calculated values.
```solidity
function _getTargetMarkets(address account) private view returns (address gTokenBorrowed, address gTokenCollateral) {
    uint256 maxSupplied;
    uint256 maxBorrowed;
    address[] memory markets = core.marketListOf(account);
    uint256[] memory prices = priceCalculator.getUnderlyingPrices(markets);
    for (uint256 i = 0; i < markets.length; i++) {
        uint256 borrowValue = ILToken(markets[i]).borrowBalanceOf(account).mul(prices[i]).div(1e18);
        uint256 supplyValue = ILToken(markets[i]).underlyingBalanceOf(account).mul(prices[i]).div(1e18);
        if (borrowValue > 0 && borrowValue > maxBorrowed) {
            maxBorrowed = borrowValue;
            gTokenBorrowed = markets[i];
            uint256 collateralFactor = core.marketInfoOf(markets[i]).collateralFactor;
            if (collateralFactor > 0 && supplyValue > 0 && supplyValue > maxSupplied) {
                maxSupplied = supplyValue;
                gTokenCollateral = markets[i];
            }
        }
    }
    return (gTokenBorrowed, gTokenCollateral);
}
```

## Recommendation
Properly take the underlying token decimal into consideration to calculate the borrow/supply values of the borrower.
