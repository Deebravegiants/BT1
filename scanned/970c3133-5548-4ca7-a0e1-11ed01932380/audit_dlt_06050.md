# [?] Prevent panic-causing param values (#875)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2021-03-15
Source: https://github.com/Kava-Labs/kava/commit/20b3fa53e30ca8789571ef925f583f53a842362d
Type: security-commit

## Details
Prevent panic-causing param values (#875)

* prevent cdp liquidation ratio being 0.0

* fix linter warning

* prevent hard conversin factor being < 1

* add liquidation tests for different keeper rewards

## Patch
### x/cdp/keeper/cdp.go
```diff
@@ -615,7 +615,7 @@ type pricefeedType string
 
 const (
 	spot        pricefeedType = "spot"
-	liquidation               = "liquidation"
+	liquidation pricefeedType = "liquidation"
 )
 
 func (pft pricefeedType) IsValid() error {
```

### x/cdp/types/params.go
```diff
@@ -362,6 +362,10 @@ func validateCollateralParams(i interface{}) error {
 			return fmt.Errorf("debt limit for all collaterals should be positive, is %s for %s", cp.DebtLimit, cp.Denom)
 		}
 
+		if cp.LiquidationRatio.IsNil() || !cp.LiquidationRatio.IsPositive() {
+			return fmt.Errorf("liquidation ratio must be > 0")
+		}
+
 		if cp.LiquidationPenalty.LT(sdk.ZeroDec()) || cp.LiquidationPenalty.GT(sdk.OneDec()) {
 			return fmt.Errorf("liquidation penalty should be between 0 and 1, is %s for %s", cp.LiquidationPenalty, cp.Denom)
 		}
```

### x/cdp/types/params_test.go
```diff
@@ -1,7 +1,6 @@
 package types_test
 
 import (
-	"strings"
 	"testing"
 
 	"github.com/stretchr/testify/suite"
@@ -715,6 +714,39 @@ func (suite *ParamsTestSuite) TestParamValidation() {
 				contains:   "stability fee must be ≥ 1.0",
 			},
 		},
+		{
+			name: "invalid collateral params zero liquidation ratio",
+			args: args{
+				globalDebtLimit: sdk.NewInt64Coin("usdx", 2000000000000),
+				collateralParams: types.CollateralParams{
+					{
+						Denom:                            "bnb",
+						Type:                             "bnb-a",
+						LiquidationRatio:                 sdk.MustNewDecFromStr("0.0"),
+						DebtLimit:                        sdk.NewInt64Coin("usdx", 1_000_000_000_000),
+						StabilityFee:                     sdk.MustNewDecFromStr("1.1"),
+						LiquidationPenalty:               sdk.MustNewDecFromStr("0.05"),
+						AuctionSize:                      sdk.NewInt(50_000_000_000),
+						Prefix:                           0x20,
+						SpotMarketID:                     "bnb:usd",
+						LiquidationMarketID:              "bnb:usd",
+						KeeperRewardPercentage:           sdk.MustNewDecFromStr("0.01"),
+						ConversionFactor:                 sdk.NewInt(8),
+						CheckCollateralizationIndexCount: sdk.NewInt(10),
+					},
+				},
+				debtParam:        types.DefaultDebtParam,
+				surplusThreshold: types.DefaultSurplusThreshold,
+				surplusLot:       types.DefaultSurplusLot,
+				debtThreshold:    types.DefaultDebtThreshold,
+				debtLot:          types.DefaultDebtLot,
+				breaker:          types.DefaultCircuitBreaker,
+			},
+			errArgs: errArgs{
+				expectPass: false,
+				contains:   "liquidation ratio must be > 0",
+			},
+		},
 		{
 			name: "invalid debt param empty denom",
 			args: args{
@@ -847,7 +879,7 @@ func (suite *ParamsTestSuite) TestParamValidation() {
 				suite.Require().NoError(err)
 			} else {
 				suite.Require().Error(err)
-				suite.Require().True(strings.Contains(err.Error(), tc.errArgs.contains))
+				suite.Require().Contains(err.Error(), tc.errArgs.contains)
 			}
 		})
 	}
```

### x/hard/keeper/liquidation.go
```diff
@@ -113,7 +113,13 @@ func (k Keeper) SeizeDeposits(ctx sdk.Context, keeper sdk.AccAddress, deposit ty
 	}
 
 	// Loan-to-Value ratio after sending keeper their reward
-	ltv := borrowCoinValues.Sum().Quo(depositCoinValues.Sum())
+	depositUsdValue := depositCoinValues.Sum()
+	if depositUsdValue.IsZero() {
+		// Deposit value can be zero if params.KeeperRewardPercent is 1.0, or all deposit asset prices are zero.
+		// In this case the full deposit will be sent to the keeper and no auctions started.
+		return nil
+	}
+	ltv := borrowCoinValues.Sum().Quo(depositUsdValue)
 
 	liquidatedCoins, err := k.StartAuctions(ctx, deposit.Depositor, borrow.Amount, aucDeposits, depositCoinValues, borrowCoinValues, ltv, liqMap)
 	// If some coins were liquidated and sent to auction prior to error, still need to emit liquidation event
```

### x/hard/keeper/liquidation_test.go
```diff
@@ -7,7 +7,6 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	abci "github.com/tendermint/tendermint/abci/types"
 	"github.com/tendermint/tendermint/crypto"
-	tmtime "github.com/tendermint/tendermint/types/time"
 
 	"github.com/kava-labs/kava/app"
 	auctypes "github.com/kava-labs/kava/x/auction/types"
@@ -26,7 +25,7 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 		initialKeeperCoins         sdk.Coins
 		depositCoins               []sdk.Coin
 		borrowCoins                sdk.Coins
-		liquidateAfter             int64
+		liquidateAfter             time.Duration
 		expectedTotalSuppliedCoins sdk.Coins
 		expectedTotalBorrowedCoins sdk.Coins
 		expectedKeeperCoins        sdk.Coins         // coins keeper address should have after successfully liquidating position
@@ -48,7 +47,7 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 	// Set up test constants
 	model := types.NewInterestRateModel(sdk.MustNewDecFromStr("0"), sdk.MustNewDecFromStr("0.1"), sdk.MustNewDecFromStr("0.8"), sdk.MustNewDecFromStr("0.5"))
 	reserveFactor := sdk.MustNewDecFromStr("0.05")
-	oneMonthInSeconds := int64(2592000)
+	oneMonthInSeconds := time.Second * 30 * 24 * 3600
 	borrower := sdk.AccAddress(crypto.AddressHash([]byte("testborrower")))
 	keeper := sdk.AccAddress(crypto.AddressHash([]byte("testkeeper")))
 
@@ -99,6 +98,68 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 				contains:   "",
 			},
 		},
+		{
+			"valid: 0% keeper rewards",
+			args{
+				borrower:                   borrower,
+				keeper:                     keeper,
+				keeperRewardPercent:        sdk.MustNewDecFromStr("0.0"),
+				initialModuleCoins:         sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				initialBorrowerCoins:       sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				initialKeeperCoins:         sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				depositCoins:               sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(10*KAVA_CF))),
+				borrowCoins:                sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(8*KAVA_CF))),
+				liquidateAfter:             oneMonthInSeconds,
+				expectedTotalSuppliedCoins: sdk.NewCoins(sdk.NewInt64Coin("ukava", 100_004_117)),
+				expectedTotalBorrowedCoins: sdk.NewCoins(sdk.NewInt64Coin("ukava", 1)),
+				expectedKeeperCoins:        sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				expectedBorrowerCoins:      sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(98*KAVA_CF))), // initial - deposit + borrow + liquidation leftovers
+				expectedAuctions: auctypes.Auctions{
+					auctypes.CollateralAuction{
+						BaseAuction: auctypes.BaseAuction{
+							ID:              1,
+							Initiator:       "hard",
+							Lot:             sdk.NewInt64Coin("ukava", 10000411),
+							Bidder:          nil,
+							Bid:             sdk.NewInt64Coin("ukava", 0),
+							HasReceivedBids: false,
+							EndTime:         endTime,
+							MaxEndTime:      endTime,
+						},
+						CorrespondingDebt: sdk.NewInt64Coin("debt", 0),
+						MaxBid:            sdk.NewInt64Coin("ukava", 8004765),
+						LotReturns:        lotReturns,
+					},
+				},
+			},
+			errArgs{
+				expectPass: true,
+				contains:   "",
+			},
+		},
+		{
+			"valid: 100% keeper reward",
+			args{
+				borrower:                   borrower,
+				keeper:                     keeper,
+				keeperRewardPercent:        sdk.MustNewDecFromStr("1.0"),
+				initialModuleCoins:         sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				initialBorrowerCoins:       sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				initialKeeperCoins:         sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(100*KAVA_CF))),
+				depositCoins:               sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(10*KAVA_CF))),
+				borrowCoins:                sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(8*KAVA_CF))),
+				liquidateAfter:             oneMonthInSeconds,
+				expectedTotalSuppliedCoins: sdk.NewCoins(sdk.NewInt64Coin("ukava", 100_004_117)),
+				expectedTotalBorrowedCoins: sdk.NewCoins(sdk.NewInt64Coin("ukava", 8_004_766)),
+				expectedKeeperCoins:        sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(110_000_411))),
+				expectedBorrowerCoins:      sdk.NewCoins(sdk.NewCoin("ukava", sdk.NewInt(98*KAVA_CF))), // initial - deposit + borrow + liquidation leftovers
+				expectedAuctions:           nil,
+			},
+			errArgs{
+				expectPass: true,
+				contains:   "",
+			},
+		},
 		{
 			"valid: single deposit, multiple borrows",
 			args{
@@ -467,7 +528,7 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 		suite.Run(tc.name, func() {
 			// Initialize test app and set context
 			tApp := app.NewTestApp()
-			ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: tmtime.Now()})
+			ctx := tApp.NewContext(true, abci.Header{Height: 1, Time: time.Date(1998, 1, 1, 0, 0, 0, 0, time.UTC)})
 
 			// account which will deposit "initial module account coins"
 			depositor := sdk.AccAddress(crypto.AddressHash([]byte("testdepositor")))
@@ -626,7 +687,7 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 			suite.Require().NoError(err)
 
 			// Set up liquidation chain context and run begin blocker
-			runAtTime := time.Unix(suite.ctx.BlockTime().Unix()+(tc.args.liquidateAfter), 0)
+			runAtTime := suite.ctx.BlockTime().Add(tc.args.liquidateAfter)
 			liqCtx := suite.ctx.WithBlockTime(runAtTime)
 			hard.BeginBlocker(liqCtx, suite.keeper)
 
@@ -665,7 +726,6 @@ func (suite *KeeperTestSuite) TestKeeperLiquidation() {
 
 				// Check that the expected auctions have been created
 				auctions := suite.auctionKeeper.GetAllAuctions(liqCtx)
-				suite.Require().True(len(auctions) > 0)
 				suite.Require().Equal(tc.args.expectedAuctions, auctions)
 
 				// Check that supplied and borrowed coins have been updated post-liquidation
```

### x/hard/types/params.go
```diff
@@ -109,6 +109,10 @@ func (mm MoneyMarket) Validate() error {
 		return err
 	}
 
+	if mm.ConversionFactor.IsNil() || mm.ConversionFactor.LT(sdk.OneInt()) {
+		return fmt.Errorf("conversion '%s' factor must be ≥ one", mm.ConversionFactor)
+	}
+
 	if err := mm.InterestRateModel.Validate(); err != nil {
 		return err
 	}
```

### x/hard/types/params_test.go
```diff
@@ -1,7 +1,6 @@
 package types_test
 
 import (
-	"strings"
 	"testing"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -34,6 +33,29 @@ func (suite *ParamTestSuite) TestParamValidation() {
 			expectPass:  true,
 			expectedErr: "",
 		},
+		{
+			name: "invalid: conversion factor < one",
+			args: args{
+				minBorrowVal: types.DefaultMinimumBorrowUSDValue,
+				mms: types.MoneyMarkets{
+					{
+						Denom: "btcb",
+						BorrowLimit: types.NewBorrowLimit(
+							false,
+							sdk.MustNewDecFromStr("100000000000"),
+							sdk.MustNewDecFromStr("0.5"),
+						),
+						SpotMarketID:           "btc:usd",
+						ConversionFactor:       sdk.NewInt(0),
+						InterestRateModel:      types.InterestRateModel{},
+						ReserveFactor:          sdk.MustNewDecFromStr("0.05"),
+						KeeperRewardPercentage: sdk.MustNewDecFromStr("0.05"),
+					},
+				},
+			},
+			expectPass:  false,
+			expectedErr: "conversion '0' factor must be ≥ one",
+		},
 	}
 	for _, tc := range testCases {
 		suite.Run(tc.name, func() {
@@ -43,7 +65,7 @@ func (suite *ParamTestSuite) TestParamValidation() {
 				suite.NoError(err)
 			} else {
 				suite.Error(err)
-				suite.Require().True(strings.Contains(err.Error(), tc.expectedErr))
+				suite.Require().Contains(err.Error(), tc.expectedErr)
 			}
 		})
 	}
```
