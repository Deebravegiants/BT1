# [?] [DEC-2075] [fix-halt] Avoid overflow in vest and rewards stats (#530)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2023-10-09
Source: https://github.com/dydxprotocol/v4-chain/commit/6eceae2125b48e311e0bf3153abb45f4ecbc322c
Type: security-commit

## Details
[DEC-2075] [fix-halt] Avoid overflow in vest and rewards stats (#530)

* avoid int64 oerflow

* divide amount before casting, add test

* change log unit

* nit

* remove debug print

* use `GetMetricValueFromBigInt`

* nits

* also update how totalrewardweight is emitted

* nits

## Patch
### protocol/lib/metrics/util_test.go
```diff
@@ -1,13 +1,15 @@
 package metrics_test
 
 import (
-	gometrics "github.com/armon/go-metrics"
-	"github.com/dydxprotocol/v4-chain/protocol/lib/metrics"
 	"math"
 	"math/big"
 	"testing"
 	"time"
 
+	gometrics "github.com/armon/go-metrics"
+	"github.com/dydxprotocol/v4-chain/protocol/lib/metrics"
+	big_testutil "github.com/dydxprotocol/v4-chain/protocol/testutil/big"
+
 	"github.com/stretchr/testify/require"
 )
 
@@ -205,6 +207,10 @@ func TestGetMetricValueFromBigInt(t *testing.T) {
 			input:    new(big.Int).SetUint64(math.MaxUint64),
 			expected: float32(1.8446744e+19),
 		},
+		"overflow: 1234567 * 1e24": {
+			input:    big_testutil.Int64MulPow10(1234567, 24), // 1234567 * 1e24
+			expected: float32(1.234567e+30),
+		},
 	}
 	for name, tc := range tests {
 		t.Run(name, func(t *testing.T) {
```

### protocol/lib/quantums_test.go
```diff
@@ -1,10 +1,11 @@
-package lib
+package lib_test
 
 import (
 	"math"
 	"math/big"
 	"testing"
 
+	"github.com/dydxprotocol/v4-chain/protocol/lib"
 	big_testutil "github.com/dydxprotocol/v4-chain/protocol/testutil/big"
 )
 
@@ -89,7 +90,7 @@ func TestBaseToQuoteQuantums(t *testing.T) {
 	}
 	for name, tc := range tests {
 		t.Run(name, func(t *testing.T) {
-			quoteQuantums := BaseToQuoteQuantums(
+			quoteQuantums := lib.BaseToQuoteQuantums(
 				tc.bigBaseQuantums,
 				tc.baseCurrencyAtomicResolution,
 				tc.priceValue,
@@ -188,7 +189,7 @@ func TestQuoteToBaseQuantums(t *testing.T) {
 	}
 	for name, tc := range tests {
 		t.Run(name, func(t *testing.T) {
-			baseQuantums := QuoteToBaseQuantums(
+			baseQuantums := lib.QuoteToBaseQuantums(
 				tc.bigQuoteQuantums,
 				tc.baseCurrencyAtomicResolution,
 				tc.priceValue,
```

### protocol/testutil/big/big.go
```diff
@@ -3,6 +3,8 @@ package big
 
 import (
 	"math/big"
+
+	"github.com/dydxprotocol/v4-chain/protocol/lib"
 )
 
 // MustFirst is used for returning the first value of the SetString
@@ -13,3 +15,16 @@ func MustFirst[T *big.Int | *big.Rat](n T, success bool) T {
 	}
 	return n
 }
+
+// Int64MulPow10 returns the result of `val * 10^exponent`, in *big.Int.
+func Int64MulPow10(
+	val int64,
+	exponent uint64,
+) (
+	result *big.Int,
+) {
+	return new(big.Int).Mul(
+		big.NewInt(val),
+		lib.BigPow10(exponent),
+	)
+}
```

### protocol/testutil/big/big_test.go
```diff
@@ -0,0 +1,57 @@
+package big_test
+
+import (
+	"math/big"
+	"testing"
+
+	big_testutil "github.com/dydxprotocol/v4-chain/protocol/testutil/big"
+	"github.com/stretchr/testify/require"
+)
+
+func TestInt64MulPow10(t *testing.T) {
+	tests := map[string]struct {
+		val            int64
+		exponent       uint64
+		expectedResult string
+	}{
+		"Regular value and exponent": {
+			val:            215,
+			exponent:       4,
+			expectedResult: "2150000",
+		},
+		"Zero value": {
+			val:            0,
+			exponent:       3,
+			expectedResult: "0",
+		},
+		"Zero exponent": {
+			val:            2,
+			exponent:       0,
+			expectedResult: "2",
+		},
+		"(-2) * 1e3": {
+			val:            -2,
+			exponent:       3,
+			expectedResult: "-2000",
+		},
+		"123456789 * 1e10": {
+			val:            123456789,
+			exponent:       10,
+			expectedResult: "1234567890000000000",
+		},
+		"87654321 * 1e18": {
+			val:            87654321,
+			exponent:       18,
+			expectedResult: "87654321000000000000000000",
+		},
+	}
+
+	for name, tc := range tests {
+		t.Run(name, func(t *testing.T) {
+			result := big_testutil.Int64MulPow10(tc.val, tc.exponent)
+			bigExpected, valid := new(big.Int).SetString(tc.expectedResult, 10)
+			require.True(t, valid)
+			require.Equal(t, bigExpected, result)
+		})
+	}
+}
```

### protocol/x/rewards/keeper/keeper.go
```diff
@@ -247,7 +247,7 @@ func (k Keeper) ProcessRewardsForBlock(
 	allRewardShares, totalRewardWeight := k.getAllRewardSharesAndTotalWeight(ctx)
 	// Measure total reward weight.
 	telemetry.SetGauge(
-		float32(totalRewardWeight.Int64()),
+		metrics.GetMetricValueFromBigInt(totalRewardWeight),
 		types.ModuleName,
 		metrics.TotalRewardShareWeight,
 	)
@@ -274,7 +274,7 @@ func (k Keeper) ProcessRewardsForBlock(
 	tokensToDistribute := lib.BigMin(rewardTokenBalance.Amount.BigInt(), bigIntRewardTokenAmount)
 	// Measure distributed token amount.
 	telemetry.SetGauge(
-		float32(tokensToDistribute.Int64()),
+		metrics.GetMetricValueFromBigInt(tokensToDistribute),
 		types.ModuleName,
 		metrics.DistributedRewardTokens,
 	)
@@ -333,7 +333,7 @@ func (k Keeper) ProcessRewardsForBlock(
 		params.Denom,
 	)
 	telemetry.SetGauge(
-		float32(remainingTreasuryBalance.Amount.Int64()),
+		metrics.GetMetricValueFromBigInt(remainingTreasuryBalance.Amount.BigInt()),
 		types.ModuleName,
 		metrics.TreasuryBalanceAfterDistribution,
 	)
```

### protocol/x/rewards/keeper/keeper_test.go
```diff
@@ -11,6 +11,7 @@ import (
 	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
 	"github.com/dydxprotocol/v4-chain/protocol/dtypes"
 	testapp "github.com/dydxprotocol/v4-chain/protocol/testutil/app"
+	big_testutil "github.com/dydxprotocol/v4-chain/protocol/testutil/big"
 	feetierstypes "github.com/dydxprotocol/v4-chain/protocol/x/feetiers/types"
 	pricestypes "github.com/dydxprotocol/v4-chain/protocol/x/prices/types"
 	"github.com/dydxprotocol/v4-chain/protocol/x/rewards/types"
@@ -272,6 +273,7 @@ func TestAddRewardSharesForFill(t *testing.T) {
 func TestProcessRewardsForBlock(t *testing.T) {
 	testRewardTokenMarketId := uint32(33)
 	testRewardTokenMarket := "test-market"
+	// TODO(CORE-645): Update test to -18 denom for consistency with prod.
 	TestRewardTokenDenomExp := int32(-6)
 
 	tokenPrice2Usdc := pricestypes.MarketPrice{
@@ -408,51 +410,55 @@ func TestProcessRewardsForBlock(t *testing.T) {
 				ZeroTreasuryAccountBalance,
 			},
 		},
-		"three reward shares, enough treasury balance, fee multipler = 0.99": {
+		"three reward shares, enough treasury balance, fee multipler = 0.99, realistic numbers": {
 			rewardShares: []types.RewardShare{
 				{
 					Address: TestAddress1,
-					Weight:  dtypes.NewInt(1_000_000), // $1 weight of fee
+					Weight:  dtypes.NewInt(1_025_590_000), // $1025.59 weight of fee
 				},
 				{
 					Address: TestAddress2,
-					Weight:  dtypes.NewInt(2_000_000), // $2 weight of fee
+					Weight:  dtypes.NewInt(2_021_300_000), // $2021.3 weight of fee
 				},
 				{
 					Address: TestAddress3,
-					Weight:  dtypes.NewInt(3_000_000), // $3 weight of fee
+					Weight:  dtypes.NewInt(835_660_000), // $835.66 weight of fee
 				},
 			},
-			tokenPrice:             tokenPrice2Usdc,
-			treasuryAccountBalance: sdkmath.NewInt(1_000_000_000), // 1000 full coins
-			feeMultiplierPpm:       990_000,                       // 99%
+			tokenPrice: tokenPrice2Usdc,
+			treasuryAccountBalance: sdkmath.NewIntFromBigInt(
+				big_testutil.Int64MulPow10(2_000_123, 18), //~2_000_123 full coin.
+			), // 1000 full coins
+			feeMultiplierPpm: 990_000, // 99%
 			expectedBalances: []banktypes.Balance{
 				{
 					Address: TestAddress1,
 					Coins: []sdk.Coin{{
 						Denom:  TestRewardTokenDenom,
-						Amount: sdkmath.NewInt(495_000), // $1 weight / $2 price * 99% = 0.495 full coin
+						Amount: sdkmath.NewInt(507_667_050), // $1 weight / $2 price * 99% = 0.495 full coin
 					}},
 				},
 				{
 					Address: TestAddress2,
 					Coins: []sdk.Coin{{
 						Denom:  TestRewardTokenDenom,
-						Amount: sdkmath.NewInt(990_000), // $2 weight / $2 price * 99% = 0.99 full coin
+						Amount: sdkmath.NewInt(1_000_543_500), // $2021.3 weight / $2 price * 99% ~= 1000 full coin
 					}},
 				},
 				{
 					Address: TestAddress3,
 					Coins: []sdk.Coin{{
 						Denom:  TestRewardTokenDenom,
-						Amount: sdkmath.NewInt(1_485_000), // $3 weight / $2 price * 99% = 1.485 full coin
+						Amount: sdkmath.NewInt(413_651_700), // $835.66 weight / $2 price * 99% ~= 413 full coin
 					}},
 				},
 				{
 					Address: authtypes.NewModuleAddress(types.TreasuryAccountName).String(),
 					Coins: []sdk.Coin{{
-						Denom:  TestRewardTokenDenom,
-						Amount: sdkmath.NewInt(997_030_000), // 997.03 full coins
+						Denom: TestRewardTokenDenom,
+						Amount: sdkmath.NewIntFromBigInt(
+							big_testutil.MustFirst(new(big.Int).SetString("2000122999999998078137750", 10)),
+						), // ~2_000_122.9 full coins
 					}},
 				},
 			},
```

### protocol/x/vest/keeper/keeper.go
```diff
@@ -2,10 +2,11 @@ package keeper
 
 import (
 	"fmt"
-	"github.com/dydxprotocol/v4-chain/protocol/daemons/pricefeed/client/constants"
 	"math/big"
 	"time"
 
+	"github.com/dydxprotocol/v4-chain/protocol/daemons/pricefeed/client/constants"
+
 	errorsmod "cosmossdk.io/errors"
 
 	sdklog "cosmossdk.io/log"
@@ -148,14 +149,14 @@ func (k Keeper) ProcessVesting(ctx sdk.Context) {
 		// Report vest amount.
 		telemetry.SetGaugeWithLabels(
 			[]string{types.ModuleName, metrics.VestAmount},
-			float32(vestAmount.Int64()),
+			metrics.GetMetricValueFromBigInt(vestAmount.BigInt()),
 			[]gometrics.Label{metrics.GetLabelForStringValue(metrics.VesterAccount, entry.VesterAccount)},
 		)
 		// Report vester account balance after vest event.
 		balanceAfterVest := k.bankKeeper.GetBalance(ctx, authtypes.NewModuleAddress(entry.VesterAccount), entry.Denom)
 		telemetry.SetGaugeWithLabels(
 			[]string{types.ModuleName, metrics.BalanceAfterVestEvent},
-			float32(balanceAfterVest.Amount.Int64()),
+			metrics.GetMetricValueFromBigInt(balanceAfterVest.Amount.BigInt()),
 			[]gometrics.Label{metrics.GetLabelForStringValue(metrics.VesterAccount, entry.VesterAccount)},
 		)
 	}
```

### protocol/x/vest/keeper/keeper_test.go
```diff
@@ -1,6 +1,7 @@
 package keeper_test
 
 import (
+	"math/big"
 	"testing"
 	"time"
 
@@ -10,6 +11,7 @@ import (
 	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
 	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
 	testapp "github.com/dydxprotocol/v4-chain/protocol/testutil/app"
+	big_testutil "github.com/dydxprotocol/v4-chain/protocol/testutil/big"
 	blocktimetypes "github.com/dydxprotocol/v4-chain/protocol/x/blocktime/types"
 	rewardstypes "github.com/dydxprotocol/v4-chain/protocol/x/rewards/types"
 	"github.com/dydxprotocol/v4-chain/protocol/x/vest/types"
@@ -97,6 +99,8 @@ func TestProcessVesting(t *testing.T) {
 	testVestTokenDenom := "testdenom"
 	testVesterAccount := rewardstypes.VesterAccountName
 	testTreasuryAccount := rewardstypes.TreasuryAccountName
+	testPrevBlockTime := time.Date(2023, 11, 5, 8, 55, 20, 0, time.UTC).In(time.UTC)
+	testCurrBlockTime := time.Date(2023, 11, 5, 8, 55, 22, 0, time.UTC).In(time.UTC)
 
 	for name, tc := range map[string]struct {
 		vesterBalance           sdkmath.Int
@@ -150,6 +154,30 @@ func TestProcessVesting(t *testing.T) {
 			expectedTreasuryBalance: sdkmath.NewInt(2_000),
 			expectedVesterBalance:   sdkmath.NewInt(1_998_000),
 		},
+		"vesting in progress, realistic values, start_time < prev_block_time < block_time < end_time": {
+			vesterBalance: sdkmath.NewIntFromBigInt(
+				big_testutil.Int64MulPow10(20_000_000, 18), // 20 million full coin, 2e26 in base denom.
+			),
+			vestEntry: types.VestEntry{
+				VesterAccount:   testVesterAccount,
+				TreasuryAccount: testTreasuryAccount,
+				Denom:           testVestTokenDenom,
+				StartTime:       types.DefaultVestingStartTime,
+				EndTime:         types.DefaultVestingEndTime,
+			},
+			prevBlockTime: testPrevBlockTime,
+			blockTime:     testCurrBlockTime,
+			expectedTreasuryBalance: sdkmath.NewIntFromBigInt(
+				big_testutil.MustFirst(
+					new(big.Int).SetString("1095437830069111172", 10), // 1.09e18
+				),
+			),
+			expectedVesterBalance: sdkmath.NewIntFromBigInt(
+				big_testutil.MustFirst(
+					new(big.Int).SetString("19999998904562169930888828", 10), // 1.99e25
+				),
+			),
+		},
 		"vesting in progress, start_time < prev_block_time < block_time < end_time, rounds down": {
 			vesterBalance: sdkmath.NewInt(2_005_000),
 			vestEntry: types.VestEntry{
```
