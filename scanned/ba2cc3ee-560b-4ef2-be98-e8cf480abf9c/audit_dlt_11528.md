# [?] fix: stop panicking in PrepareProposalHandler (#5460)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-08-07
Source: https://github.com/celestiaorg/celestia-app/commit/982ba669ad8043d112b84877325fc8e7810c7d62
Type: security-commit

## Details
fix: stop panicking in PrepareProposalHandler (#5460)

Closes https://github.com/celestiaorg/celestia-app/issues/4992
Reopen #5047 
fixed golanci lint, also fixed comment to match the current logic

## Patch
### app/prepare_proposal.go
```diff
@@ -1,6 +1,7 @@
 package app
 
 import (
+	"fmt"
 	"time"
 
 	"github.com/celestiaorg/celestia-app/v6/app/ante"
@@ -14,9 +15,8 @@ import (
 
 // PrepareProposalHandler fulfills the celestia-core version of the ABCI interface by
 // preparing the proposal block data. This method generates the data root for
-// the proposal block and passes it back to tendermint via the BlockData. Panics
-// indicate a developer error and should immediately halt the node for
-// visibility and so they can be quickly resolved.
+// the proposal block and passes it back to tendermint via the BlockData. Errors
+// are returned instead of panicking to improve error handling and reduce attack surface.
 func (app *App) PrepareProposalHandler(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
 	defer telemetry.MeasureSince(time.Now(), "prepare_proposal")
 	// Create a context using a branch of the state.
@@ -40,15 +40,15 @@ func (app *App) PrepareProposalHandler(ctx sdk.Context, req *abci.RequestPrepare
 		appconsts.SubtreeRootThreshold,
 	)
 	if err != nil {
-		panic(err)
+		return nil, fmt.Errorf("failed to create FilteredSquareBuilder: %w", err)
 	}
 
 	txs := fsb.Fill(ctx, req.Txs)
 
 	// Build the square from the set of valid and prioritised transactions.
 	dataSquare, err := fsb.Build()
 	if err != nil {
-		panic(err)
+		return nil, fmt.Errorf("failed to build data square: %w", err)
 	}
 
 	// Erasure encode the data square to create the extended data square (eds).
@@ -57,13 +57,13 @@ func (app *App) PrepareProposalHandler(ctx sdk.Context, req *abci.RequestPrepare
 	eds, err := da.ExtendShares(share.ToBytes(dataSquare))
 	if err != nil {
 		app.Logger().Error("failure to erasure the data square while creating a proposal block", "error", err.Error())
-		panic(err)
+		return nil, fmt.Errorf("failure to erasure the data square while creating a proposal block: %w", err)
 	}
 
 	dah, err := da.NewDataAvailabilityHeader(eds)
 	if err != nil {
 		app.Logger().Error("failure to create new data availability header", "error", err.Error())
-		panic(err)
+		return nil, fmt.Errorf("failure to create new data availability header: %w", err)
 	}
 
 	// Tendermint doesn't need to use any of the erasure data because only the
```
