# [?] [stableswap]: Cap number of assets and post-scaled asset amounts to ensure pools never overflow (#3055)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2022-10-24
Source: https://github.com/osmosis-labs/osmosis/commit/ced84c1c8a656c66b4e54baf2a271d456b25a119
Type: security-commit

## Details
[stableswap]: Cap number of assets and post-scaled asset amounts to ensure pools never overflow (#3055)

* add tests for 10-asset pools with 10B per asset

* add max post-scaled asset check and create pool tests

* add sanity tests for new swap guardrails

* move max scaled asset amt to constant

* add join-pool-internal tests for new functionality

## Patch
### x/gamm/pool-models/stableswap/amm.go
```diff
@@ -377,11 +377,14 @@ func (p *Pool) calcSingleAssetJoinShares(tokenIn sdk.Coin, swapFee sdk.Dec) (sdk
 // We can mutate pa here
 // TODO: some day switch this to a COW wrapped pa, for better perf
 func (p *Pool) joinPoolSharesInternal(ctx sdk.Context, tokensIn sdk.Coins, swapFee sdk.Dec) (numShares sdk.Int, newLiquidity sdk.Coins, err error) {
-	if len(tokensIn) == 1 {
+	if !tokensIn.DenomsSubsetOf(p.GetTotalPoolLiquidity(ctx)) {
+		return sdk.ZeroInt(), sdk.NewCoins(), errors.New("attempted joining pool with assets that do not exist in pool")
+	}
+	if len(tokensIn) == 1 && tokensIn[0].Amount.GT(sdk.OneInt()) {
 		numShares, err = p.calcSingleAssetJoinShares(tokensIn[0], swapFee)
 		newLiquidity = tokensIn
 		return numShares, newLiquidity, err
-	} else if len(tokensIn) != p.NumAssets() || !tokensIn.DenomsSubsetOf(p.GetTotalPoolLiquidity(ctx)) {
+	} else if len(tokensIn) != p.NumAssets() {
 		return sdk.ZeroInt(), sdk.NewCoins(), errors.New(
 			"stableswap pool only supports LP'ing with one asset, or all assets in pool")
 	}
@@ -393,15 +396,24 @@ func (p *Pool) joinPoolSharesInternal(ctx sdk.Context, tokensIn sdk.Coins, swapF
 	}
 	p.updatePoolForJoin(tokensIn.Sub(remCoins), numShares)
 
+	tokensJoined := tokensIn
 	for _, coin := range remCoins {
 		// TODO: Perhaps add a method to skip if this is too small.
-		newShare, err := p.calcSingleAssetJoinShares(coin, swapFee)
-		if err != nil {
-			return sdk.ZeroInt(), sdk.NewCoins(), err
+		if coin.Amount.GT(sdk.OneInt()) {
+			newShare, err := p.calcSingleAssetJoinShares(coin, swapFee)
+			if err != nil {
+				return sdk.ZeroInt(), sdk.NewCoins(), err
+			}
+			p.updatePoolForJoin(sdk.NewCoins(coin), newShare)
+			numShares = numShares.Add(newShare)
+		} else {
+			tokensJoined = tokensJoined.Sub(sdk.NewCoins(coin))
 		}
-		p.updatePoolForJoin(sdk.NewCoins(coin), newShare)
-		numShares = numShares.Add(newShare)
 	}
 
-	return numShares, tokensIn, nil
+	if err = validatePoolAssets(p.PoolLiquidity, p.ScalingFactor); err != nil {
+		return sdk.ZeroInt(), sdk.NewCoins(), err
+	}
+
+	return numShares, tokensJoined, nil
 }
```

### x/gamm/pool-models/stableswap/amm_test.go
```diff
@@ -224,16 +224,38 @@ var (
 			yIn:         osmomath.NewBigDec(1),
 			expectPanic: false,
 		},
-		/* TODO: increase BigDec precision (36 -> 72) to be able to accommodate this
-		"even 4-asset large pool, small input": {
+		"even 4-asset large pool (100M each), small input": {
 			xReserve: osmomath.NewBigDec(100000000),
 			yReserve: osmomath.NewBigDec(100000000),
 			// represents a 4-asset pool with 100M in each reserve
 			remReserves: []osmomath.BigDec{osmomath.NewBigDec(100000000), osmomath.NewBigDec(100000000)},
-			yIn: osmomath.NewBigDec(100),
+			yIn:         osmomath.NewBigDec(100),
+			expectPanic: false,
+		},
+		"even 4-asset pool (10B each post-scaled), small input": {
+			xReserve: osmomath.NewBigDec(10000000000),
+			yReserve: osmomath.NewBigDec(10000000000),
+			// represents a 4-asset pool with 10B in each reserve
+			remReserves: []osmomath.BigDec{osmomath.NewBigDec(10000000000), osmomath.NewBigDec(10000000000)},
+			yIn:         osmomath.NewBigDec(100000000),
+			expectPanic: false,
+		},
+		"even 10-asset pool (10B each post-scaled), small input": {
+			xReserve: osmomath.NewBigDec(10_000_000_000),
+			yReserve: osmomath.NewBigDec(10_000_000_000),
+			// represents a 10-asset pool with 10B in each reserve
+			remReserves: []osmomath.BigDec{osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000), osmomath.NewBigDec(10_000_000_000)},
+			yIn:         osmomath.NewBigDec(100),
+			expectPanic: false,
+		},
+		"even 10-asset pool (100B each post-scaled), large input": {
+			xReserve: osmomath.NewBigDec(100_000_000_000),
+			yReserve: osmomath.NewBigDec(100_000_000_000),
+			// represents a 10-asset pool with 100B in each reserve
+			remReserves: []osmomath.BigDec{osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000), osmomath.NewBigDec(100_000_000_000)},
+			yIn:         osmomath.NewBigDec(10_000_000_000),
 			expectPanic: false,
 		},
-		*/
 
 		// uneven pools
 		"uneven 3-asset pool, even swap assets as pool minority": {
@@ -790,8 +812,6 @@ func TestCalcSingleAssetJoinShares(t *testing.T) {
 			swapFee:        sdk.MustNewDecFromStr("0.03"),
 			expectedOut:    sdk.NewInt(100 - 3),
 		},
-
-		// TODO: increase BigDec precision further to be able to accommodate 5-asset pool tests
 	}
 
 	for name, tc := range tests {
@@ -815,3 +835,117 @@ func TestCalcSingleAssetJoinShares(t *testing.T) {
 		})
 	}
 }
+
+func TestJoinPoolSharesInternal(t *testing.T) {
+	tenPercentOfTwoPoolRaw := int64(1000000000 / 10)
+	tenPercentOfTwoPoolCoins := sdk.NewCoins(sdk.NewCoin("foo", sdk.NewInt(int64(1000000000/10))), sdk.NewCoin("bar", sdk.NewInt(int64(1000000000/10))))
+	twoAssetPlusTenPercent := twoEvenStablePoolAssets.Add(tenPercentOfTwoPoolCoins...)
+	type testcase struct {
+		tokensIn        sdk.Coins
+		poolAssets      sdk.Coins
+		scalingFactors  []uint64
+		swapFee         sdk.Dec
+		expNumShare     sdk.Int
+		expTokensJoined sdk.Coins
+		expPoolAssets   sdk.Coins
+		expectPass      bool
+	}
+
+	tests := map[string]testcase{
+		"even two asset pool, same tokenIn ratio": {
+			tokensIn:        tenPercentOfTwoPoolCoins,
+			poolAssets:      twoEvenStablePoolAssets,
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			swapFee:         sdk.ZeroDec(),
+			expNumShare:     sdk.NewIntFromUint64(10000000000000000000),
+			expTokensJoined: tenPercentOfTwoPoolCoins,
+			expPoolAssets:   twoAssetPlusTenPercent,
+			expectPass:      true,
+		},
+		"even two asset pool, different tokenIn ratio with pool": {
+			tokensIn:        sdk.NewCoins(sdk.NewCoin("foo", sdk.NewInt(tenPercentOfTwoPoolRaw)), sdk.NewCoin("bar", sdk.NewInt(10+tenPercentOfTwoPoolRaw))),
+			poolAssets:      twoEvenStablePoolAssets,
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			swapFee:         sdk.ZeroDec(),
+			expNumShare:     sdk.NewIntFromUint64(10000000500000000000),
+			expTokensJoined: sdk.NewCoins(sdk.NewCoin("foo", sdk.NewInt(tenPercentOfTwoPoolRaw)), sdk.NewCoin("bar", sdk.NewInt(10+tenPercentOfTwoPoolRaw))),
+			expPoolAssets:   twoAssetPlusTenPercent.Add(sdk.NewCoin("bar", sdk.NewInt(10))),
+			expectPass:      true,
+		},
+		"all-asset pool join attempt exceeds max scaled asset amount": {
+			tokensIn: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 1),
+				sdk.NewInt64Coin("bar", 1),
+			),
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			swapFee:         sdk.ZeroDec(),
+			expNumShare:     sdk.ZeroInt(),
+			expTokensJoined: sdk.Coins{},
+			expPoolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			expectPass: false,
+		},
+		"single-asset pool join exceeds hits max scaled asset amount": {
+			tokensIn: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 1),
+			),
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			swapFee:         sdk.ZeroDec(),
+			expNumShare:     sdk.ZeroInt(),
+			expTokensJoined: sdk.Coins{},
+			expPoolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			expectPass: false,
+		},
+		"all-asset pool join attempt exactly hits max scaled asset amount": {
+			tokensIn: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 1),
+				sdk.NewInt64Coin("bar", 1),
+			),
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 9_999_999_999),
+				sdk.NewInt64Coin("bar", 9_999_999_999),
+			),
+			scalingFactors: defaultTwoAssetScalingFactors,
+			swapFee:        sdk.ZeroDec(),
+			expNumShare:    sdk.NewInt(10000000000),
+			expTokensJoined: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 1),
+				sdk.NewInt64Coin("bar", 1),
+			),
+			expPoolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			expectPass: true,
+		},
+	}
+
+	for name, tc := range tests {
+		t.Run(name, func(t *testing.T) {
+			ctx := sdk.Context{}
+			p := poolStructFromAssets(tc.poolAssets, tc.scalingFactors)
+
+			shares, joinedLiquidity, err := p.joinPoolSharesInternal(ctx, tc.tokensIn, tc.swapFee)
+
+			if tc.expectPass {
+				require.Equal(t, tc.expNumShare, shares)
+				require.Equal(t, tc.expTokensJoined, joinedLiquidity)
+				require.Equal(t, tc.expPoolAssets, p.PoolLiquidity)
+			}
+			osmoassert.ConditionalError(t, !tc.expectPass, err)
+		})
+	}
+}
```

### x/gamm/pool-models/stableswap/msgs.go
```diff
@@ -46,13 +46,6 @@ func (msg MsgCreateStableswapPool) ValidateBasic() error {
 		return err
 	}
 
-	// validation for pool initial liquidity
-	if len(msg.InitialPoolLiquidity) < 2 {
-		return types.ErrTooFewPoolAssets
-	} else if len(msg.InitialPoolLiquidity) > 8 {
-		return types.ErrTooManyPoolAssets
-	}
-
 	// validation for scaling factors
 	// The message's scaling factors must be empty or a valid set of scaling factors
 	if len(msg.ScalingFactors) != 0 {
@@ -61,6 +54,12 @@ func (msg MsgCreateStableswapPool) ValidateBasic() error {
 		}
 	}
 
+	// validation for pool initial liquidity
+	// The message's pool liquidity must have between 2 and 8 assets with at most 10B post-scaled units in each
+	if err = validatePoolAssets(msg.InitialPoolLiquidity, msg.ScalingFactors); err != nil {
+		return err
+	}
+
 	// validation for scaling factor owner
 	if err = validateScalingFactorController(msg.ScalingFactorController); err != nil {
 		return err
```

### x/gamm/pool-models/stableswap/msgs_test.go
```diff
@@ -209,6 +209,60 @@ func TestMsgCreateStableswapPool(t *testing.T) {
 			}),
 			expectPass: true,
 		},
+		{
+			name: "max asset amounts",
+			msg: createMsg(func(msg stableswap.MsgCreateStableswapPool) stableswap.MsgCreateStableswapPool {
+				msg.InitialPoolLiquidity = sdk.Coins{
+					sdk.NewCoin("osmo", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("atom", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("usdt", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("usdc", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("juno", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("akt", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("regen", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("band", sdk.NewInt(10_000_000_000)),
+				}
+				msg.ScalingFactors = []uint64{1, 1, 1, 1, 1, 1, 1, 1}
+				return msg
+			}),
+			expectPass: true,
+		},
+		{
+			name: "greater than max post-scaled amount with regular scaling factors",
+			msg: createMsg(func(msg stableswap.MsgCreateStableswapPool) stableswap.MsgCreateStableswapPool {
+				msg.InitialPoolLiquidity = sdk.Coins{
+					sdk.NewCoin("osmo", sdk.NewInt(1+10_000_000_000)),
+					sdk.NewCoin("atom", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("usdt", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("usdc", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("juno", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("akt", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("regen", sdk.NewInt(10_000_000_000)),
+					sdk.NewCoin("band", sdk.NewInt(10_000_000_000)),
+				}
+				msg.ScalingFactors = []uint64{1, 1, 1, 1, 1, 1, 1, 1}
+				return msg
+			}),
+			expectPass: false,
+		},
+		{
+			name: "100B token 8-asset pool using large scaling factors",
+			msg: createMsg(func(msg stableswap.MsgCreateStableswapPool) stableswap.MsgCreateStableswapPool {
+				msg.InitialPoolLiquidity = sdk.Coins{
+					sdk.NewCoin("osmo", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("atom", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("usdt", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("usdc", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("juno", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("akt", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("regen", sdk.NewInt(100_000_000_000_000_000)),
+					sdk.NewCoin("band", sdk.NewInt(100_000_000_000_000_000)),
+				}
+				msg.ScalingFactors = []uint64{10000000, 10000000, 10000000, 10000000, 10000000, 10000000, 10000000, 10000000}
+				return msg
+			}),
+			expectPass: true,
+		},
 	}
 
 	for _, test := range tests {
```

### x/gamm/pool-models/stableswap/pool.go
```diff
@@ -36,6 +36,10 @@ func NewStableswapPool(poolId uint64,
 		return Pool{}, err
 	}
 
+	if err := validatePoolAssets(initialLiquidity, scalingFactors); err != nil {
+		return Pool{}, err
+	}
+
 	pool := Pool{
 		Address:                 types.NewPoolAddress(poolId).String(),
 		Id:                      poolId,
@@ -229,6 +233,10 @@ func (p Pool) CalcOutAmtGivenIn(ctx sdk.Context, tokenIn sdk.Coins, tokenOutDeno
 }
 
 func (p *Pool) SwapOutAmtGivenIn(ctx sdk.Context, tokenIn sdk.Coins, tokenOutDenom string, swapFee sdk.Dec) (tokenOut sdk.Coin, err error) {
+	if err = validatePoolAssets(p.PoolLiquidity.Add(tokenIn...), p.ScalingFactor); err != nil {
+		return sdk.Coin{}, err
+	}
+
 	tokenOut, err = p.CalcOutAmtGivenIn(ctx, tokenIn, tokenOutDenom, swapFee)
 	if err != nil {
 		return sdk.Coin{}, err
@@ -265,6 +273,10 @@ func (p *Pool) SwapInAmtGivenOut(ctx sdk.Context, tokenOut sdk.Coins, tokenInDen
 		return sdk.Coin{}, err
 	}
 
+	if err = validatePoolAssets(p.PoolLiquidity.Add(tokenIn), p.ScalingFactor); err != nil {
+		return sdk.Coin{}, err
+	}
+
 	p.updatePoolLiquidityForSwap(sdk.NewCoins(tokenIn), tokenOut)
 
 	return tokenIn, nil
@@ -328,6 +340,10 @@ func (p *Pool) SetStableSwapScalingFactors(ctx sdk.Context, scalingFactors []uin
 		return err
 	}
 
+	if err := validatePoolAssets(p.PoolLiquidity, scalingFactors); err != nil {
+		return err
+	}
+
 	p.ScalingFactor = scalingFactors
 	return nil
 }
@@ -353,3 +369,19 @@ func validateScalingFactors(scalingFactors []uint64, numAssets int) error {
 
 	return nil
 }
+
+func validatePoolAssets(initialAssets sdk.Coins, scalingFactors []uint64) error {
+	if len(initialAssets) < types.MinPoolAssets {
+		return types.ErrTooFewPoolAssets
+	} else if len(initialAssets) > types.MaxPoolAssets {
+		return types.ErrTooManyPoolAssets
+	}
+
+	for i, asset := range initialAssets {
+		if asset.Amount.Quo(sdk.NewInt(int64(scalingFactors[i]))).GT(sdk.NewInt(types.StableswapMaxScaledAmtPerAsset)) {
+			return types.ErrHitMaxScaledAssets
+		}
+	}
+
+	return nil
+}
```

### x/gamm/pool-models/stableswap/pool_test.go
```diff
@@ -505,3 +505,137 @@ func TestScaleCoin(t *testing.T) {
 		})
 	}
 }
+
+func TestSwapOutAmtGivenIn(t *testing.T) {
+	tests := map[string]struct {
+		poolAssets            sdk.Coins
+		scalingFactors        []uint64
+		tokenIn               sdk.Coins
+		expectedTokenOut      sdk.Coin
+		expectedPoolLiquidity sdk.Coins
+		swapFee               sdk.Dec
+		expError              bool
+	}{
+		"even pool basic trade": {
+			poolAssets:     twoEvenStablePoolAssets,
+			scalingFactors: defaultTwoAssetScalingFactors,
+			tokenIn:        sdk.NewCoins(sdk.NewInt64Coin("foo", 100)),
+			// we expect at least a 1 token difference since output is truncated
+			expectedTokenOut:      sdk.NewInt64Coin("bar", 99),
+			expectedPoolLiquidity: twoEvenStablePoolAssets.Add(sdk.NewInt64Coin("foo", 100)).Sub(sdk.NewCoins(sdk.NewInt64Coin("bar", 99))),
+			swapFee:               sdk.ZeroDec(),
+			expError:              false,
+		},
+		"trade hits max pool capacity for asset": {
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 9_999_999_998),
+				sdk.NewInt64Coin("bar", 9_999_999_999),
+			),
+			scalingFactors:   defaultTwoAssetScalingFactors,
+			tokenIn:          sdk.NewCoins(sdk.NewInt64Coin("foo", 1)),
+			expectedTokenOut: sdk.NewInt64Coin("bar", 1),
+			expectedPoolLiquidity: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 9_999_999_999),
+				sdk.NewInt64Coin("bar", 9_999_999_998),
+			),
+			swapFee:  sdk.ZeroDec(),
+			expError: false,
+		},
+		"trade exceeds max pool capacity for asset": {
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			scalingFactors:   defaultTwoAssetScalingFactors,
+			tokenIn:          sdk.NewCoins(sdk.NewInt64Coin("foo", 1)),
+			expectedTokenOut: sdk.Coin{},
+			expectedPoolLiquidity: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			swapFee:  sdk.ZeroDec(),
+			expError: true,
+		},
+	}
+
+	for name, tc := range tests {
+		t.Run(name, func(t *testing.T) {
+			ctx := sdk.Context{}
+			p := poolStructFromAssets(tc.poolAssets, tc.scalingFactors)
+
+			tokenOut, err := p.SwapOutAmtGivenIn(ctx, tc.tokenIn, tc.expectedTokenOut.Denom, tc.swapFee)
+			if !tc.expError {
+				require.Equal(t, tc.expectedTokenOut, tokenOut)
+				require.Equal(t, tc.expectedPoolLiquidity, p.PoolLiquidity)
+			}
+			osmoassert.ConditionalError(t, tc.expError, err)
+		})
+	}
+}
+
+func TestSwapInAmtGivenOut(t *testing.T) {
+	tests := map[string]struct {
+		poolAssets            sdk.Coins
+		scalingFactors        []uint64
+		tokenOut              sdk.Coins
+		expectedTokenIn       sdk.Coin
+		expectedPoolLiquidity sdk.Coins
+		swapFee               sdk.Dec
+		expError              bool
+	}{
+		"even pool basic trade": {
+			poolAssets:     twoEvenStablePoolAssets,
+			scalingFactors: defaultTwoAssetScalingFactors,
+			tokenOut:       sdk.NewCoins(sdk.NewInt64Coin("bar", 99)),
+			// we expect at least a 1 token difference from our true expected output since it is truncated
+			expectedTokenIn:       sdk.NewInt64Coin("foo", 99),
+			expectedPoolLiquidity: twoEvenStablePoolAssets.Add(sdk.NewInt64Coin("foo", 99)).Sub(sdk.NewCoins(sdk.NewInt64Coin("bar", 99))),
+			swapFee:               sdk.ZeroDec(),
+			expError:              false,
+		},
+		"trade hits max pool capacity for asset": {
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 9_999_999_998),
+				sdk.NewInt64Coin("bar", 9_999_999_999),
+			),
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			tokenOut:        sdk.NewCoins(sdk.NewInt64Coin("bar", 1)),
+			expectedTokenIn: sdk.NewInt64Coin("foo", 1),
+			expectedPoolLiquidity: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 9_999_999_999),
+				sdk.NewInt64Coin("bar", 9_999_999_998),
+			),
+			swapFee:  sdk.ZeroDec(),
+			expError: false,
+		},
+		"trade exceeds max pool capacity for asset": {
+			poolAssets: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			scalingFactors:  defaultTwoAssetScalingFactors,
+			tokenOut:        sdk.NewCoins(sdk.NewInt64Coin("bar", 1)),
+			expectedTokenIn: sdk.Coin{},
+			expectedPoolLiquidity: sdk.NewCoins(
+				sdk.NewInt64Coin("foo", 10_000_000_000),
+				sdk.NewInt64Coin("bar", 10_000_000_000),
+			),
+			swapFee:  sdk.ZeroDec(),
+			expError: true,
+		},
+	}
+
+	for name, tc := range tests {
+		t.Run(name, func(t *testing.T) {
+			ctx := sdk.Context{}
+			p := poolStructFromAssets(tc.poolAssets, tc.scalingFactors)
+
+			tokenIn, err := p.SwapInAmtGivenOut(ctx, tc.tokenOut, tc.expectedTokenIn.Denom, tc.swapFee)
+			if !tc.expError {
+				require.Equal(t, tc.expectedTokenIn, tokenIn)
+				require.Equal(t, tc.expectedPoolLiquidity, p.PoolLiquidity)
+			}
+			osmoassert.ConditionalError(t, tc.expError, err)
+		})
+	}
+}
```

### x/gamm/types/constants.go
```diff
@@ -13,6 +13,8 @@ const (
 	// i.e. SigFigExponent = 8 is 10^8 which is 100000000. This gives 8 significant figures.
 	SigFigsExponent       = 8
 	BalancerGasFeeForSwap = 10_000
+
+	StableswapMaxScaledAmtPerAsset = 10_000_000_000
 )
 
 var (
```

### x/gamm/types/errors.go
```diff
@@ -20,7 +20,7 @@ var (
 	ErrPoolAlreadyExist    = sdkerrors.Register(ModuleName, 2, "pool already exist")
 	ErrPoolLocked          = sdkerrors.Register(ModuleName, 3, "pool is locked")
 	ErrTooFewPoolAssets    = sdkerrors.Register(ModuleName, 4, "pool should have at least 2 assets, as they must be swapping between at least two assets")
-	ErrTooManyPoolAssets   = sdkerrors.Register(ModuleName, 5, "pool has too many assets (currently capped at 8 assets per balancer pool and 2 per stableswap)")
+	ErrTooManyPoolAssets   = sdkerrors.Register(ModuleName, 5, "pool has too many assets (currently capped at 8 assets per pool)")
 	ErrLimitMaxAmount      = sdkerrors.Register(ModuleName, 6, "calculated amount is larger than max amount")
 	ErrLimitMinAmount      = sdkerrors.Register(ModuleName, 7, "calculated amount is lesser than min amount")
 	ErrInvalidMathApprox   = sdkerrors.Register(ModuleName, 8, "invalid calculated result")
@@ -52,4 +52,5 @@ var (
 	ErrInvalidStableswapScalingFactors = sdkerrors.Register(ModuleName, 62, "length between liquidity and scaling factors mismatch")
 	ErrNotScalingFactorGovernor        = sdkerrors.Register(ModuleName, 63, "not scaling factor governor")
 	ErrInvalidScalingFactors           = sdkerrors.Register(ModuleName, 64, "invalid scaling factor")
+	ErrHitMaxScaledAssets              = sdkerrors.Register(ModuleName, 65, "post-scaled pool assets can not exceed 10B")
 )
```
