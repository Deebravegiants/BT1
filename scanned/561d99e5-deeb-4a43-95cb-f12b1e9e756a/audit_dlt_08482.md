# [?] fix: method handler crash due to nil min fee per gas (#1982)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2024-12-09
Source: https://github.com/sei-protocol/sei-chain/commit/cb56268ce69a32c2ceb39e0c9fee912d23af0809
Type: security-commit

## Details
fix: method handler crash due to nil min fee per gas (#1982)

* fix: method handler crash due to nil min fee per gas

* unit test

## Patch
### x/evm/keeper/fee.go
```diff
@@ -63,7 +63,11 @@ func (k *Keeper) GetDynamicBaseFeePerGas(ctx sdk.Context) sdk.Dec {
 	store := ctx.KVStore(k.storeKey)
 	bz := store.Get(types.BaseFeePerGasPrefix)
 	if bz == nil {
-		return k.GetMinimumFeePerGas(ctx)
+		minFeePerGas := k.GetMinimumFeePerGas(ctx)
+		if minFeePerGas.IsNil() {
+			minFeePerGas = types.DefaultParams().MinimumFeePerGas
+		}
+		return minFeePerGas
 	}
 	d := sdk.Dec{}
 	err := d.UnmarshalJSON(bz)
```

### x/evm/keeper/fee_test.go
```diff
@@ -5,6 +5,7 @@ import (
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	testkeeper "github.com/sei-protocol/sei-chain/testutil/keeper"
+	"github.com/sei-protocol/sei-chain/x/evm/types"
 	"github.com/stretchr/testify/require"
 	tmproto "github.com/tendermint/tendermint/proto/tendermint/types"
 )
@@ -177,3 +178,24 @@ func TestAdjustBaseFeePerGas(t *testing.T) {
 		})
 	}
 }
+
+func TestGetDynamicBaseFeePerGasWithNilMinFee(t *testing.T) {
+	k, ctx := testkeeper.MockEVMKeeper()
+
+	// Test case 1: When dynamic base fee doesn't exist and minimum fee is nil
+	store := ctx.KVStore(k.GetStoreKey())
+	store.Delete(types.BaseFeePerGasPrefix)
+
+	// Clear the dynamic base fee from store
+	fee := k.GetDynamicBaseFeePerGas(ctx)
+	require.Equal(t, types.DefaultParams().MinimumFeePerGas, fee)
+	require.False(t, fee.IsNil())
+
+	// Test case 2: When dynamic base fee exists
+	expectedFee := sdk.NewDec(100)
+	k.SetDynamicBaseFeePerGas(ctx, expectedFee)
+
+	fee = k.GetDynamicBaseFeePerGas(ctx)
+	require.Equal(t, expectedFee, fee)
+	require.False(t, fee.IsNil())
+}
```
