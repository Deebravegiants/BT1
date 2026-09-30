# [?] fix: avoid panic if cdp debt > debt held by cdp account (#326)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-21
Source: https://github.com/Kava-Labs/kava/commit/bab798f50d02a2895b8cba5579e6b0e67dc39329
Type: security-commit

## Details
fix: avoid panic if cdp debt > debt held by cdp account (#326)

Co-authored-by: Kevin Davis <karzak@users.noreply.github.com>

## Patch
### x/cdp/abci_test.go
```diff
@@ -33,6 +33,32 @@ type liquidationTracker struct {
 }
 
 func (suite *ModuleTestSuite) SetupTest() {
+	tApp := app.NewTestApp()
+	ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: tmtime.Now()})
+	coins := []sdk.Coins{}
+	tracker := liquidationTracker{}
+
+	for j := 0; j < 100; j++ {
+		coins = append(coins, cs(c("btc", 100000000), c("xrp", 10000000000)))
+	}
+	_, addrs := app.GeneratePrivKeyAddressPairs(100)
+
+	authGS := app.NewAuthGenState(
+		addrs, coins)
+	tApp.InitializeFromGenesisStates(
+		authGS,
+		NewPricefeedGenStateMulti(),
+		NewCDPGenStateMulti(),
+	)
+	suite.ctx = ctx
+	suite.app = tApp
+	suite.keeper = tApp.GetCDPKeeper()
+	suite.cdps = cdp.CDPs{}
+	suite.addrs = addrs
+	suite.liquidations = tracker
+}
+
+func (suite *ModuleTestSuite) createCdps() {
 	tApp := app.NewTestApp()
 	ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: tmtime.Now()})
 	cdps := make(cdp.CDPs, 100)
@@ -96,6 +122,7 @@ func (suite *ModuleTestSuite) setPrice(price sdk.Dec, market string) {
 	suite.Equal(price, pp.Price)
 }
 func (suite *ModuleTestSuite) TestBeginBlock() {
+	suite.createCdps()
 	sk := suite.app.GetSupplyKeeper()
 	acc := sk.GetModuleAccount(suite.ctx, cdp.ModuleName)
 	originalXrpCollateral := acc.GetCoins().AmountOf("xrp")
@@ -122,6 +149,33 @@ func (suite *ModuleTestSuite) TestBeginBlock() {
 
 }
 
+func (suite *ModuleTestSuite) TestSeizeSingleCdpWithFees() {
+	err := suite.keeper.AddCdp(suite.ctx, suite.addrs[0], cs(c("xrp", 10000000000)), cs(c("usdx", 1000000000)))
+	suite.NoError(err)
+	suite.keeper.SetPreviousBlockTime(suite.ctx, suite.ctx.BlockTime())
+	previousBlockTime, _ := suite.keeper.GetPreviousBlockTime(suite.ctx)
+	suite.Equal(i(1000000000), suite.keeper.GetTotalPrincipal(suite.ctx, "xrp", "usdx"))
+	sk := suite.app.GetSupplyKeeper()
+	cdpMacc := sk.GetModuleAccount(suite.ctx, cdp.ModuleName)
+	suite.Equal(i(1000000000), cdpMacc.GetCoins().AmountOf("debt"))
+	for i := 0; i < 100; i++ {
+		suite.ctx = suite.ctx.WithBlockTime(suite.ctx.BlockTime().Add(time.Second * 6))
+		cdp.BeginBlocker(suite.ctx, abci.RequestBeginBlock{Header: suite.ctx.BlockHeader()}, suite.keeper)
+	}
+
+	cdpMacc = sk.GetModuleAccount(suite.ctx, cdp.ModuleName)
+	suite.Equal(i(1000000900), (cdpMacc.GetCoins().AmountOf("debt")))
+	cdp, _ := suite.keeper.GetCDP(suite.ctx, "xrp", 1)
+
+	timeElapsed := sdk.NewInt(suite.ctx.BlockTime().Unix() - previousBlockTime.Unix())
+
+	fees := suite.keeper.CalculateFees(suite.ctx, cdp.Principal, timeElapsed, "xrp")
+	suite.Equal(i(928), fees.AmountOf("usdx"))
+
+	err = suite.keeper.SeizeCollateral(suite.ctx, cdp)
+	suite.NoError(err)
+}
+
 func TestModuleTestSuite(t *testing.T) {
 	suite.Run(t, new(ModuleTestSuite))
 }
```

### x/cdp/integration_test.go
```diff
@@ -154,10 +154,10 @@ func NewCDPGenStateMulti() app.GenesisState {
 
 func cdps() (cdps cdp.CDPs) {
 	_, addrs := app.GeneratePrivKeyAddressPairs(3)
-	c1 := cdp.NewCDP(uint64(1), addrs[0], sdk.NewCoins(sdk.NewCoin("xrp", sdk.NewInt(10000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(8000000))), tmtime.Canonical(time.Now()))
+	c1 := cdp.NewCDP(uint64(1), addrs[0], sdk.NewCoins(sdk.NewCoin("xrp", sdk.NewInt(100000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(8000000))), tmtime.Canonical(time.Now()))
 	c2 := cdp.NewCDP(uint64(2), addrs[1], sdk.NewCoins(sdk.NewCoin("xrp", sdk.NewInt(100000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(10000000))), tmtime.Canonical(time.Now()))
 	c3 := cdp.NewCDP(uint64(3), addrs[1], sdk.NewCoins(sdk.NewCoin("btc", sdk.NewInt(1000000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(10000000))), tmtime.Canonical(time.Now()))
-	c4 := cdp.NewCDP(uint64(4), addrs[2], sdk.NewCoins(sdk.NewCoin("xrp", sdk.NewInt(1000000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(500000000))), tmtime.Canonical(time.Now()))
+	c4 := cdp.NewCDP(uint64(4), addrs[2], sdk.NewCoins(sdk.NewCoin("xrp", sdk.NewInt(1000000000))), sdk.NewCoins(sdk.NewCoin("usdx", sdk.NewInt(50000000))), tmtime.Canonical(time.Now()))
 	cdps = append(cdps, c1, c2, c3, c4)
 	return
 }
```

### x/cdp/keeper/seize.go
```diff
@@ -33,7 +33,10 @@ func (k Keeper) SeizeCollateral(ctx sdk.Context, cdp types.CDP) sdk.Error {
 	for _, dc := range cdp.AccumulatedFees {
 		debt = debt.Add(dc.Amount)
 	}
-
+	modAccountDebt := k.getModAccountDebt(ctx, types.ModuleName)
+	if modAccountDebt.LT(debt) {
+		debt = modAccountDebt
+	}
 	debtCoin := sdk.NewCoin(k.GetDebtDenom(ctx), debt)
 	err := k.supplyKeeper.SendCoinsFromModuleToModule(ctx, types.ModuleName, types.LiquidatorMacc, sdk.NewCoins(debtCoin))
 	if err != nil {
@@ -114,3 +117,8 @@ func (k Keeper) ApplyLiquidationPenalty(ctx sdk.Context, denom string, debt sdk.
 	penaltyAmount := sdk.NewDecFromInt(debt).Mul(penalty).RoundInt()
 	return penaltyAmount
 }
+
+func (k Keeper) getModAccountDebt(ctx sdk.Context, accountName string) sdk.Int {
+	macc := k.supplyKeeper.GetModuleAccount(ctx, accountName)
+	return macc.GetCoins().AmountOf(k.GetDebtDenom(ctx))
+}
```

### x/cdp/keeper/seize_test.go
```diff
@@ -34,6 +34,32 @@ type liquidationTracker struct {
 }
 
 func (suite *SeizeTestSuite) SetupTest() {
+	tApp := app.NewTestApp()
+	ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: tmtime.Now()})
+	coins := []sdk.Coins{}
+	tracker := liquidationTracker{}
+
+	for j := 0; j < 100; j++ {
+		coins = append(coins, cs(c("btc", 100000000), c("xrp", 10000000000)))
+	}
+	_, addrs := app.GeneratePrivKeyAddressPairs(100)
+
+	authGS := app.NewAuthGenState(
+		addrs, coins)
+	tApp.InitializeFromGenesisStates(
+		authGS,
+		NewPricefeedGenStateMulti(),
+		NewCDPGenStateMulti(),
+	)
+	suite.ctx = ctx
+	suite.app = tApp
+	suite.keeper = tApp.GetCDPKeeper()
+	suite.cdps = types.CDPs{}
+	suite.addrs = addrs
+	suite.liquidations = tracker
+}
+
+func (suite *SeizeTestSuite) createCdps() {
 	tApp := app.NewTestApp()
 	ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: tmtime.Now()})
 	cdps := make(types.CDPs, 100)
@@ -99,6 +125,7 @@ func (suite *SeizeTestSuite) setPrice(price sdk.Dec, market string) {
 }
 
 func (suite *SeizeTestSuite) TestSeizeCollateral() {
+	suite.createCdps()
 	sk := suite.app.GetSupplyKeeper()
 	cdp, _ := suite.keeper.GetCDP(suite.ctx, "xrp", uint64(2))
 	p := cdp.Principal[0].Amount
@@ -121,6 +148,7 @@ func (suite *SeizeTestSuite) TestSeizeCollateral() {
 }
 
 func (suite *SeizeTestSuite) TestSeizeCollateralMultiDeposit() {
+	suite.createCdps()
 	sk := suite.app.GetSupplyKeeper()
 	cdp, _ := suite.keeper.GetCDP(suite.ctx, "xrp", uint64(2))
 	err := suite.keeper.DepositCollateral(suite.ctx, suite.addrs[1], suite.addrs[0], cs(c("xrp", 6999000000)))
@@ -145,6 +173,7 @@ func (suite *SeizeTestSuite) TestSeizeCollateralMultiDeposit() {
 }
 
 func (suite *SeizeTestSuite) TestLiquidateCdps() {
+	suite.createCdps()
 	sk := suite.app.GetSupplyKeeper()
 	acc := sk.GetModuleAccount(suite.ctx, types.ModuleName)
 	originalXrpCollateral := acc.GetCoins().AmountOf("xrp")
@@ -159,6 +188,7 @@ func (suite *SeizeTestSuite) TestLiquidateCdps() {
 }
 
 func (suite *SeizeTestSuite) TestHandleNewDebt() {
+	suite.createCdps()
 	tpb := suite.keeper.GetTotalPrincipal(suite.ctx, "xrp", "usdx")
 	suite.keeper.HandleNewDebt(suite.ctx, "xrp", "usdx", i(31536000))
 	tpa := suite.keeper.GetTotalPrincipal(suite.ctx, "xrp", "usdx")
```
