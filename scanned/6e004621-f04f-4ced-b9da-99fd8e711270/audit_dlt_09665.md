# [?] fix(migration): changed default values for incentive creation to protect against dos (#1653)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2024-12-14
Source: https://github.com/dymensionxyz/dymension/commit/887a5472c3ed40e221d27a1abb401d26a4916a8f
Type: security-commit

## Details
fix(migration): changed default values for incentive creation to protect against dos (#1653)

## Patch
### app/upgrades/v4/upgrade.go
```diff
@@ -5,6 +5,7 @@ import (
 	"strings"
 
 	errorsmod "cosmossdk.io/errors"
+	"cosmossdk.io/math"
 	"github.com/cometbft/cometbft/crypto"
 	"github.com/cosmos/cosmos-sdk/baseapp"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -285,7 +286,11 @@ func ReformatFinalizationQueue(queue rollapptypes.BlockHeightToFinalizationQueue
 }
 
 func migrateIncentivesParams(ctx sdk.Context, ik *incentiveskeeper.Keeper) {
+	DYM := math.NewIntWithDecimal(1, 18)
 	params := incentivestypes.DefaultParams()
+	params.CreateGaugeBaseFee = DYM.MulRaw(10)
+	params.AddToGaugeBaseFee = DYM.MulRaw(10)
+	params.AddDenomFee = DYM.MulRaw(10)
 	params.DistrEpochIdentifier = "day"
 	ik.SetParams(ctx, params)
 }
```
