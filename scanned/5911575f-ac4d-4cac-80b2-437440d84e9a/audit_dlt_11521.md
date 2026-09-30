# [?] fix: prevent uint32 overflow in blobSize * GasPerBlobByte calculation (#6779)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-11
Source: https://github.com/celestiaorg/celestia-app/commit/1c4bbabd0954f665e887b38ba893ce2b327b0419
Type: security-commit

## Details
fix: prevent uint32 overflow in blobSize * GasPerBlobByte calculation (#6779)

## Summary
- Widen both `uint32` operands to `uint64` before multiplying in
`calculatePaymentAmount` to prevent silent overflow when the product
exceeds `math.MaxUint32` (~4.2B).
- Use `math.NewIntFromUint64` instead of an `int64` cast to avoid a
secondary overflow when the product exceeds `math.MaxInt64`.
- Extract a `calculatePaymentCoin` helper and reuse it in
`validatePaymentPromiseStatefulInternal` to deduplicate the payment
calculation and replace a hardcoded `"utia"` with `appconsts.BondDenom`.
- Add tests covering zero, normal, overflow, and large-value cases.

Closes #6715

## Test plan
- [x] `TestCalculatePaymentCoin/zero_blob_size` — verifies zero input
produces a zero coin
- [x] `TestCalculatePaymentCoin/zero_gas_per_blob_byte` — verifies zero
input produces a zero coin
- [x] `TestCalculatePaymentCoin/normal_case` — verifies correct result
for small values
- [x] `TestCalculatePaymentCoin/overflow_case` — verifies `8_388_608 *
1000 = 8_388_608_000` (would overflow uint32)
- [x] `TestCalculatePaymentCoin/large_values_near_uint32_max` — verifies
`MaxUint32 * 2`
- [x]
`TestCalculatePaymentCoin/max_uint32_*_max_uint32_does_not_overflow` —
verifies `MaxUint32 * MaxUint32` (would overflow int64)
- [x] All existing `x/fibre/keeper` tests pass

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### x/fibre/keeper/calculate_payment_test.go
```diff
@@ -0,0 +1,64 @@
+package keeper
+
+import (
+	"math"
+	"testing"
+
+	sdkmath "cosmossdk.io/math"
+	"github.com/celestiaorg/celestia-app/v8/pkg/appconsts"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/stretchr/testify/assert"
+)
+
+func TestCalculatePaymentCoin(t *testing.T) {
+	tests := []struct {
+		name           string
+		blobSize       uint32
+		gasPerBlobByte uint32
+		want           sdk.Coin
+	}{
+		{
+			name:           "zero blob size",
+			blobSize:       0,
+			gasPerBlobByte: 8,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewInt(0)),
+		},
+		{
+			name:           "zero gas per blob byte",
+			blobSize:       1000,
+			gasPerBlobByte: 0,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewInt(0)),
+		},
+		{
+			name:           "normal case",
+			blobSize:       1000,
+			gasPerBlobByte: 8,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewInt(8000)),
+		},
+		{
+			name:           "overflow case: product exceeds uint32 max",
+			blobSize:       8_388_608, // 8 MiB
+			gasPerBlobByte: 1000,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewInt(8_388_608_000)),
+		},
+		{
+			name:           "large values near uint32 max",
+			blobSize:       math.MaxUint32,
+			gasPerBlobByte: 2,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewIntFromUint64(2*uint64(math.MaxUint32))),
+		},
+		{
+			name:           "max uint32 * max uint32 does not overflow",
+			blobSize:       math.MaxUint32,
+			gasPerBlobByte: math.MaxUint32,
+			want:           sdk.NewCoin(appconsts.BondDenom, sdkmath.NewIntFromUint64(uint64(math.MaxUint32)*uint64(math.MaxUint32))),
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			got := calculatePaymentCoin(tt.blobSize, tt.gasPerBlobByte)
+			assert.Equal(t, tt.want, got)
+		})
+	}
+}
```

### x/fibre/keeper/keeper.go
```diff
@@ -5,7 +5,6 @@ import (
 	"time"
 
 	"cosmossdk.io/log"
-	"cosmossdk.io/math"
 	storetypes "cosmossdk.io/store/types"
 	"github.com/celestiaorg/celestia-app/v8/fibre"
 	"github.com/celestiaorg/celestia-app/v8/x/fibre/types"
@@ -359,11 +358,9 @@ func (k Keeper) validatePaymentPromiseStatefulInternal(ctx sdk.Context, promise
 	}
 
 	// Check sufficient available balance
-	gasRequired := uint64(promise.BlobSize) * uint64(params.GasPerBlobByte)
-
 	// TODO: This assumes 1 gas = 1 utia but the minimum gas price could be
 	// different.
-	requiredAmount := sdk.NewCoin("utia", math.NewInt(int64(gasRequired)))
+	requiredAmount := calculatePaymentCoin(promise.BlobSize, params.GasPerBlobByte)
 
 	hasSufficientBalance := escrowAccount.AvailableBalance.IsGTE(requiredAmount)
 	if !hasSufficientBalance {
```

### x/fibre/keeper/msg_server.go
```diff
@@ -298,7 +298,14 @@ func (ms msgServer) UpdateFibreParams(goCtx context.Context, msg *types.MsgUpdat
 func (ms msgServer) calculatePaymentAmount(ctx sdk.Context, blobSize uint32) sdk.Coin {
 	params := ms.GetParams(ctx)
 	// TODO: this assumes 1 utia per gas which may not be correct.
-	return sdk.NewInt64Coin(appconsts.BondDenom, int64(blobSize*params.GasPerBlobByte))
+	return calculatePaymentCoin(blobSize, params.GasPerBlobByte)
+}
+
+// calculatePaymentCoin computes the payment coin from blobSize and gasPerBlobByte.
+// Both operands are widened to uint64 before multiplication to prevent uint32 overflow.
+func calculatePaymentCoin(blobSize, gasPerBlobByte uint32) sdk.Coin {
+	result := uint64(blobSize) * uint64(gasPerBlobByte)
+	return sdk.NewCoin(appconsts.BondDenom, math.NewIntFromUint64(result))
 }
 
 // validateValidatorSignatures validates validator signatures using the existing SignatureSet infrastructure
```
