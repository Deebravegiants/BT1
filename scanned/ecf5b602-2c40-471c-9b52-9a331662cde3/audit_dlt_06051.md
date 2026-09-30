# [?] Fix withdraw panic (#315)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-22
Source: https://github.com/Kava-Labs/kava/commit/58deb49e5553f99d059dc90fe2cdc2c6271b724d
Type: security-commit

## Details
Fix withdraw panic (#315)

* fix: remove redundant debt limit param

* wip: test pricefeed genesis

* fix: pricefeed querier

* fix: comments, naming

* fix: query path

* fix: store methods

* fix: query methods

* feat: Liquidation Penalty

* feat: enforce debt floor on repayment

* fix: don't panic if withdrawing full amount

* fix: remove debt from liquidation penalty

## Patch
### x/cdp/keeper/cdp.go
```diff
@@ -412,6 +412,9 @@ func (k Keeper) CalculateCollateralToDebtRatio(ctx sdk.Context, collateral sdk.C
 
 // CalculateCollateralizationRatio returns the collateralization ratio of the input collateral to the input debt plus fees
 func (k Keeper) CalculateCollateralizationRatio(ctx sdk.Context, collateral sdk.Coins, principal sdk.Coins, fees sdk.Coins) (sdk.Dec, sdk.Error) {
+	if collateral.IsZero() {
+		return sdk.ZeroDec(), nil
+	}
 	marketID := k.getMarketID(ctx, collateral[0].Denom)
 	price, err := k.pricefeedKeeper.GetCurrentPrice(ctx, marketID)
 	if err != nil {
```

### x/cdp/keeper/deposit_test.go
```diff
@@ -93,7 +93,9 @@ func (suite *DepositTestSuite) TestDepositCollateral() {
 }
 
 func (suite *DepositTestSuite) TestWithdrawCollateral() {
-	err := suite.keeper.WithdrawCollateral(suite.ctx, suite.addrs[0], suite.addrs[0], cs(c("xrp", 321000000)))
+	err := suite.keeper.WithdrawCollateral(suite.ctx, suite.addrs[0], suite.addrs[0], cs(c("xrp", 400000000)))
+	suite.Equal(types.CodeInvalidCollateralRatio, err.Result().Code)
+	err = suite.keeper.WithdrawCollateral(suite.ctx, suite.addrs[0], suite.addrs[0], cs(c("xrp", 321000000)))
 	suite.Equal(types.CodeInvalidCollateralRatio, err.Result().Code)
 	err = suite.keeper.WithdrawCollateral(suite.ctx, suite.addrs[1], suite.addrs[0], cs(c("xrp", 10000000)))
 	suite.Equal(types.CodeCdpNotFound, err.Result().Code)
```
