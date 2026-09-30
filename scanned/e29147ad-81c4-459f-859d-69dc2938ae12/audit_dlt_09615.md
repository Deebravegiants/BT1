# [?] Merge pull request from GHSA-354m-4qv6-x846

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2023-07-18
Source: https://github.com/cosmos/gaia/commit/a759409c9da2780663244308b430a7847b95139b
Type: security-commit

## Details
Merge pull request from GHSA-354m-4qv6-x846

## Patch
### ante/gov_ante.go
```diff
@@ -50,7 +50,7 @@ func (g GovPreventSpamDecorator) ValidateGovMsgs(ctx sdk.Context, msgs []sdk.Msg
 			// prevent messages with insufficient initial deposit amount
 			depositParams := g.govKeeper.GetDepositParams(ctx)
 			minInitialDeposit := g.calcMinInitialDeposit(depositParams.MinDeposit)
-			if msg.InitialDeposit.IsAllLT(minInitialDeposit) {
+			if !msg.InitialDeposit.IsAllGTE(minInitialDeposit) {
 				return errorsmod.Wrapf(gaiaerrors.ErrInsufficientFunds, "insufficient initial deposit amount - required: %v", minInitialDeposit)
 			}
 		}
```

### ante/gov_ante_test.go
```diff
@@ -20,10 +20,16 @@ import (
 )
 
 var (
-	insufficientCoins = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 100))
-	minCoins          = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 1000000))
-	moreThanMinCoins  = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 2500000))
-	testAddr          = sdk.AccAddress("test1")
+	insufficientCoins           = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 100))
+	insufficientMultiDenomCoins = sdk.NewCoins(
+		sdk.NewInt64Coin(sdk.DefaultBondDenom, 100),
+		sdk.NewInt64Coin("ibc/example", 100))
+	minCoins                   = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 1000000))
+	moreThanMinCoins           = sdk.NewCoins(sdk.NewInt64Coin(sdk.DefaultBondDenom, 2500000))
+	moreThanMinMultiDenomCoins = sdk.NewCoins(
+		sdk.NewInt64Coin(sdk.DefaultBondDenom, 1000000),
+		sdk.NewInt64Coin("ibc/example", 100))
+	testAddr = sdk.AccAddress("test1")
 )
 
 type GovAnteHandlerTestSuite struct {
@@ -66,7 +72,9 @@ func (s *GovAnteHandlerTestSuite) TestGlobalFeeMinimumGasFeeAnteHandler() {
 	}{
 		{"Passing proposal 1", "the purpose of this proposal is to pass", govtypes.ProposalTypeText, testAddr, minCoins, true},
 		{"Passing proposal 2", "the purpose of this proposal is to pass with more coins than minimum", govtypes.ProposalTypeText, testAddr, moreThanMinCoins, true},
-		{"Failing proposal", "the purpose of this proposal is to fail", govtypes.ProposalTypeText, testAddr, insufficientCoins, false},
+		{"Passing proposal 3", "the purpose of this proposal is to pass with multi denom coins", govtypes.ProposalTypeText, testAddr, moreThanMinMultiDenomCoins, true},
+		{"Failing proposal 1", "the purpose of this proposal is to fail", govtypes.ProposalTypeText, testAddr, insufficientCoins, false},
+		{"Failing proposal 2", "the purpose of this proposal is to fail with multi denom coins", govtypes.ProposalTypeText, testAddr, insufficientMultiDenomCoins, false},
 	}
 
 	decorator := ante.NewGovPreventSpamDecorator(s.app.AppCodec(), &s.app.GovKeeper)
```
