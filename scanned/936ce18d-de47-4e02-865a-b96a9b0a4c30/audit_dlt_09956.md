# [?] Fix: Avoid panics when adding cdp collaterals via governance (#329)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-23
Source: https://github.com/Kava-Labs/kava/commit/535094df96ace59c97214305360a8c2d38c4c792
Type: security-commit

## Details
Fix: Avoid panics when adding cdp collaterals via governance (#329)

* fix: remove unnecessary accumulator key

* fix: correct test comment

* fix: avoid panic when cdp collateral type added

## Patch
### x/cdp/alias.go
```diff
@@ -120,7 +120,6 @@ var (
 	GovDenomKey                = types.GovDenomKey
 	DepositKeyPrefix           = types.DepositKeyPrefix
 	PrincipalKeyPrefix         = types.PrincipalKeyPrefix
-	AccumulatorKeyPrefix       = types.AccumulatorKeyPrefix
 	PreviousBlockTimeKey       = types.PreviousBlockTimeKey
 	KeyGlobalDebtLimit         = types.KeyGlobalDebtLimit
 	KeyCollateralParams        = types.KeyCollateralParams
```

### x/cdp/genesis.go
```diff
@@ -34,7 +34,6 @@ func InitGenesis(ctx sdk.Context, k Keeper, pk PricefeedKeeper, gs GenesisState)
 		for _, dp := range gs.Params.DebtParams {
 			k.SetTotalPrincipal(ctx, cp.Denom, dp.Denom, sdk.ZeroInt())
 		}
-		k.SetFeeRate(ctx, cp.Denom, cp.StabilityFee)
 	}
 
 	// add cdps
```

### x/cdp/integration_test.go
```diff
@@ -210,7 +210,7 @@ func badGenStates() []badGenState {
 	return []badGenState{
 		badGenState{Genesis: g1, Reason: "duplicate collateral denom"},
 		badGenState{Genesis: g2, Reason: "duplicate collateral prefix"},
-		badGenState{Genesis: g3, Reason: "duplicate collateral prefix"},
+		badGenState{Genesis: g3, Reason: "invalid debt limit"},
 		badGenState{Genesis: g4, Reason: "single collateral exceeds debt limit"},
 		badGenState{Genesis: g5, Reason: "combined collateral exceeds debt limit"},
 		badGenState{Genesis: g6, Reason: "duplicate debt denom"},
```

### x/cdp/keeper/fees.go
```diff
@@ -1,7 +1,6 @@
 package keeper
 
 import (
-	"fmt"
 	"time"
 
 	"github.com/cosmos/cosmos-sdk/store/prefix"
@@ -17,7 +16,7 @@ func (k Keeper) CalculateFees(ctx sdk.Context, principal sdk.Coins, periods sdk.
 		// how fees are calculated:
 		// feesAccumulated = (outstandingDebt * (feeRate^periods)) - outstandingDebt
 		// Note that since we can't do x^y using sdk.Decimal, we are converting to int and using RelativePow
-		feePerSecond := k.GetFeeRate(ctx, denom)
+		feePerSecond := k.getFeeRate(ctx, denom)
 		scalar := sdk.NewInt(1000000000000000000)
 		feeRateInt := feePerSecond.Mul(sdk.NewDecFromInt(scalar)).TruncateInt()
 		accumulator := sdk.NewDecFromInt(types.RelativePow(feeRateInt, periods, scalar)).Mul(sdk.SmallestDec())
@@ -55,7 +54,8 @@ func (k Keeper) GetTotalPrincipal(ctx sdk.Context, collateralDenom string, princ
 	store := prefix.NewStore(ctx.KVStore(k.key), types.PrincipalKeyPrefix)
 	bz := store.Get([]byte(collateralDenom + principalDenom))
 	if bz == nil {
-		panic(fmt.Sprintf("total principal of %s for %s collateral not set in genesis", principalDenom, collateralDenom))
+		k.SetTotalPrincipal(ctx, collateralDenom, principalDenom, sdk.ZeroInt())
+		return sdk.ZeroInt()
 	}
 	k.cdc.MustUnmarshalBinaryLengthPrefixed(bz, &total)
 	return total
@@ -67,23 +67,6 @@ func (k Keeper) SetTotalPrincipal(ctx sdk.Context, collateralDenom string, princ
 	store.Set([]byte(collateralDenom+principalDenom), k.cdc.MustMarshalBinaryLengthPrefixed(total))
 }
 
-// GetFeeRate returns the per second fee rate for the input denom
-func (k Keeper) GetFeeRate(ctx sdk.Context, denom string) (fee sdk.Dec) {
-	store := prefix.NewStore(ctx.KVStore(k.key), types.AccumulatorKeyPrefix)
-	bz := store.Get([]byte(denom))
-	if bz == nil {
-		panic(fmt.Sprintf("fee rate for %s not set in genesis", denom))
-	}
-	k.cdc.MustUnmarshalBinaryLengthPrefixed(bz, &fee)
-	return fee
-}
-
-// SetFeeRate sets the per second fee rate for the input denom
-func (k Keeper) SetFeeRate(ctx sdk.Context, denom string, fee sdk.Dec) {
-	store := prefix.NewStore(ctx.KVStore(k.key), types.AccumulatorKeyPrefix)
-	store.Set([]byte(denom), k.cdc.MustMarshalBinaryLengthPrefixed(fee))
-}
-
 // GetPreviousBlockTime get the blocktime for the previous block
 func (k Keeper) GetPreviousBlockTime(ctx sdk.Context) (blockTime time.Time, found bool) {
 	store := prefix.NewStore(ctx.KVStore(k.key), types.PreviousBlockTimeKey)
```

### x/cdp/keeper/params.go
```diff
@@ -94,3 +94,12 @@ func (k Keeper) getAuctionSize(ctx sdk.Context, denom string) sdk.Int {
 	}
 	return cp.AuctionSize
 }
+
+// GetFeeRate returns the per second fee rate for the input denom
+func (k Keeper) getFeeRate(ctx sdk.Context, denom string) (fee sdk.Dec) {
+	collalateralParam, found := k.GetCollateral(ctx, denom)
+	if !found {
+		panic(fmt.Sprintf("could not get fee rate for %s, collateral not found", denom))
+	}
+	return collalateralParam.StabilityFee
+}
```

### x/cdp/types/keys.go
```diff
@@ -54,8 +54,7 @@ var (
 	GovDenomKey                = []byte{0x05}
 	DepositKeyPrefix           = []byte{0x06}
 	PrincipalKeyPrefix         = []byte{0x07}
-	AccumulatorKeyPrefix       = []byte{0x08}
-	PreviousBlockTimeKey       = []byte{0x09}
+	PreviousBlockTimeKey       = []byte{0x08}
 )
 
 var lenPositiveDec = len(SortableDecBytes(sdk.OneDec()))
```
