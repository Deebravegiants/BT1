# [?] fix(x/auth/tx): avoid panic from newWrapperFromDecodedTx (#23170)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-01-09
Source: https://github.com/cosmos/cosmos-sdk/commit/517839bc9686c6651dabdcf6d43dcb2aeb740586
Type: security-commit

## Details
fix(x/auth/tx): avoid panic from newWrapperFromDecodedTx (#23170)

Co-authored-by: Alex | Skip <alex@djinntek.world>
Co-authored-by: Alex | Interchain Labs <alex@skip.money>

## Patch
### CHANGELOG.md
```diff
@@ -53,6 +53,7 @@ Every module contains its own CHANGELOG.md. Please refer to the module you are i
 ### Bug Fixes
 
 * (query) [23002](https://github.com/cosmos/cosmos-sdk/pull/23002) Fix collection filtered pagination.
+* (x/auth/tx) [#23170](https://github.com/cosmos/cosmos-sdk/pull/23170) Avoid panic from newWrapperFromDecodedTx when AuthInfo.Fee is optional in decodedTx.
 * (x/auth/tx) [23144](https://github.com/cosmos/cosmos-sdk/pull/23144) Add missing CacheWithValue for ExtensionOptions.
 * (x/auth/tx) [#23148](https://github.com/cosmos/cosmos-sdk/pull/23148) Avoid panic from intoAnyV2 when v1.PublicKey is optional.
 
```

### x/auth/tx/gogotx.go
```diff
@@ -33,44 +33,46 @@ func newWrapperFromDecodedTx(
 	addrCodec address.Codec, cdc codec.BinaryCodec, decodedTx *decode.DecodedTx,
 ) (*gogoTxWrapper, error) {
 	var (
-		fees = sdk.Coins{} // decodedTx.Tx.AuthInfo.Fee.Amount might be nil
-		err  error
+		fees                 = sdk.Coins{} // decodedTx.Tx.AuthInfo.Fee.Amount might be nil
+		err                  error
+		feePayer, feeGranter []byte
 	)
-	for i, fee := range decodedTx.Tx.AuthInfo.Fee.Amount {
-		amtInt, ok := math.NewIntFromString(fee.Amount)
-		if !ok {
-			return nil, fmt.Errorf("invalid fee coin amount at index %d: %s", i, fee.Amount)
+	if decodedTx.Tx.AuthInfo.Fee != nil {
+		for i, fee := range decodedTx.Tx.AuthInfo.Fee.Amount {
+			amtInt, ok := math.NewIntFromString(fee.Amount)
+			if !ok {
+				return nil, fmt.Errorf("invalid fee coin amount at index %d: %s", i, fee.Amount)
+			}
+			if err = sdk.ValidateDenom(fee.Denom); err != nil {
+				return nil, fmt.Errorf("invalid fee coin denom at index %d: %w", i, err)
+			}
+
+			fees = fees.Add(sdk.Coin{
+				Denom:  fee.Denom,
+				Amount: amtInt,
+			})
 		}
-		if err = sdk.ValidateDenom(fee.Denom); err != nil {
-			return nil, fmt.Errorf("invalid fee coin denom at index %d: %w", i, err)
+		if !fees.IsSorted() {
+			return nil, fmt.Errorf("invalid not sorted tx fees: %s", fees.String())
 		}
 
-		fees = fees.Add(sdk.Coin{
-			Denom:  fee.Denom,
-			Amount: amtInt,
-		})
-	}
-	if !fees.IsSorted() {
-		return nil, fmt.Errorf("invalid not sorted tx fees: %s", fees.String())
-	}
-	// set fee payer
-	var feePayer []byte
-	if len(decodedTx.Signers) != 0 {
-		feePayer = decodedTx.Signers[0]
-		if decodedTx.Tx.AuthInfo.Fee.Payer != "" {
-			feePayer, err = addrCodec.StringToBytes(decodedTx.Tx.AuthInfo.Fee.Payer)
-			if err != nil {
-				return nil, err
+		// set fee payer
+		if len(decodedTx.Signers) != 0 {
+			feePayer = decodedTx.Signers[0]
+			if decodedTx.Tx.AuthInfo.Fee.Payer != "" {
+				feePayer, err = addrCodec.StringToBytes(decodedTx.Tx.AuthInfo.Fee.Payer)
+				if err != nil {
+					return nil, err
+				}
 			}
 		}
-	}
 
-	// fee granter
-	var feeGranter []byte
-	if decodedTx.Tx.AuthInfo.Fee.Granter != "" {
-		feeGranter, err = addrCodec.StringToBytes(decodedTx.Tx.AuthInfo.Fee.Granter)
-		if err != nil {
-			return nil, err
+		// fee granter
+		if decodedTx.Tx.AuthInfo.Fee.Granter != "" {
+			feeGranter, err = addrCodec.StringToBytes(decodedTx.Tx.AuthInfo.Fee.Granter)
+			if err != nil {
+				return nil, err
+			}
 		}
 	}
 
```

### x/auth/tx/gogotx_test.go
```diff
@@ -0,0 +1,26 @@
+package tx
+
+import (
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	v1beta1 "cosmossdk.io/api/cosmos/tx/v1beta1"
+	"cosmossdk.io/x/tx/decode"
+
+	"github.com/cosmos/cosmos-sdk/codec"
+	addresscodec "github.com/cosmos/cosmos-sdk/codec/address"
+	codectestutil "github.com/cosmos/cosmos-sdk/codec/testutil"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+)
+
+func TestNewWrapperFromDecodedTxAllowsNilFee(t *testing.T) {
+	addrCodec := addresscodec.NewBech32Codec(sdk.GetConfig().GetBech32AccountAddrPrefix())
+	cdc := codec.NewProtoCodec(codectestutil.CodecOptions{}.NewInterfaceRegistry())
+	_, err := newWrapperFromDecodedTx(addrCodec, cdc, &decode.DecodedTx{
+		Tx: &v1beta1.Tx{
+			AuthInfo: &v1beta1.AuthInfo{},
+		},
+	})
+	require.Nil(t, err)
+}
```
