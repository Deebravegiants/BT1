# [?] fix: Add panic recovery to ProcessProposalHandler goroutine (#2345)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-10-01
Source: https://github.com/sei-protocol/sei-chain/commit/caebdeaa5e06c7c1fe07b8556ef8637a7a4e204e
Type: security-commit

## Details
fix: Add panic recovery to ProcessProposalHandler goroutine (#2345)

* fix: Add panic recovery to ProcessProposalHandler goroutine

## Patch
### app/antedecorators/gasless.go
```diff
@@ -2,6 +2,7 @@ package antedecorators
 
 import (
 	"encoding/hex"
+	"fmt"
 
 	storetypes "github.com/cosmos/cosmos-sdk/store/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -111,7 +112,15 @@ func (gd GaslessDecorator) AnteDeps(txDeps []sdkacltypes.AccessOperation, tx sdk
 	return next(append(txDeps, deps...), tx, txIndex)
 }
 
-func IsTxGasless(tx sdk.Tx, ctx sdk.Context, oracleKeeper oraclekeeper.Keeper, evmKeeper *evmkeeper.Keeper) (bool, error) {
+func IsTxGasless(tx sdk.Tx, ctx sdk.Context, oracleKeeper oraclekeeper.Keeper, evmKeeper *evmkeeper.Keeper) (isGasless bool, err error) {
+	defer func() {
+		if r := recover(); r != nil {
+			ctx.Logger().Error("panic recovered in IsTxGasless", "panic", r)
+			err = fmt.Errorf("panic in IsTxGasless: %v", r)
+			isGasless = false
+		}
+	}()
+
 	if len(tx.GetMsgs()) == 0 {
 		// empty TX shouldn't be gasless
 		return false, nil
```

### app/app.go
```diff
@@ -11,6 +11,7 @@ import (
 	"net/http"
 	"os"
 	"path/filepath"
+	"regexp"
 	"strings"
 	"sync"
 	"time"
@@ -180,6 +181,13 @@ var (
 	// DefaultNodeHome default home directories for the application daemon
 	DefaultNodeHome string
 
+	// upgradePanicRe matches upgrade panic messages using Cosmovisor-compatible regex
+	// Matches multiple upgrade-related panic patterns:
+	// 1. UPGRADE "name" NEEDED at height: 123 (or height123)
+	// 2. Wrong app version X, upgrade handler is missing for name upgrade plan
+	// 3. BINARY UPDATED BEFORE TRIGGER! UPGRADE "name"
+	upgradePanicRe = regexp.MustCompile(`^(UPGRADE "[^"]+" NEEDED at height:?\s*\d+|Wrong app version \d+, upgrade handler is missing for .+ upgrade plan|BINARY UPDATED BEFORE TRIGGER! UPGRADE "[^"]+")`)
+
 	// ModuleBasics defines the module BasicManager is in charge of setting up basic,
 	// non-dependant module elements, such as codec registration
 	// and genesis verification.
@@ -1133,7 +1141,7 @@ func (app *App) ClearOptimisticProcessingInfo() {
 	app.optimisticProcessingInfo = OptimisticProcessingInfo{}
 }
 
-func (app *App) ProcessProposalHandler(ctx sdk.Context, req *abci.RequestProcessProposal) (*abci.ResponseProcessProposal, error) {
+func (app *App) ProcessProposalHandler(ctx sdk.Context, req *abci.RequestProcessProposal) (resp *abci.ResponseProcessProposal, err error) {
 	// TODO: this check decodes transactions which is redone in subsequent processing. We might be able to optimize performance
 	// by recording the decoding results and avoid decoding again later on.
 
@@ -1143,45 +1151,64 @@ func (app *App) ProcessProposalHandler(ctx sdk.Context, req *abci.RequestProcess
 			Status: abci.ResponseProcessProposal_REJECT,
 		}, nil
 	}
-	if app.GetOptimisticProcessingInfo().Completion == nil {
+
+	app.optimisticProcessingInfoMutex.Lock()
+	shouldStartOptimisticProcessing := app.optimisticProcessingInfo.Completion == nil
+	if shouldStartOptimisticProcessing {
 		completionSignal := make(chan struct{}, 1)
-		optimisticProcessingInfo := OptimisticProcessingInfo{
+		app.optimisticProcessingInfo = OptimisticProcessingInfo{
 			Height:     req.Height,
 			Hash:       req.Hash,
 			Completion: completionSignal,
 		}
-		app.optimisticProcessingInfoMutex.Lock()
-		app.optimisticProcessingInfo = optimisticProcessingInfo
-		app.optimisticProcessingInfoMutex.Unlock()
+	}
+	app.optimisticProcessingInfoMutex.Unlock()
 
+	if shouldStartOptimisticProcessing {
 		plan, found := app.UpgradeKeeper.GetUpgradePlan(ctx)
 		if found && plan.ShouldExecute(ctx) {
-			app.Logger().Info(fmt.Sprintf("Potential upgrade planned for height=%d skipping optimistic processing", plan.Height))
+			app.Logger().Info("Potential upgrade planned; skipping optimistic processing", "height", plan.Height)
 			app.optimisticProcessingInfoMutex.Lock()
 			app.optimisticProcessingInfo.Aborted = true
 			completion := app.optimisticProcessingInfo.Completion
 			app.optimisticProcessingInfoMutex.Unlock()
 			completion <- struct{}{}
 		} else {
 			go func() {
-				events, txResults, endBlockResp, _ := app.ProcessBlock(ctx, req.Txs, req, req.ProposedLastCommit, false)
+				// ProcessBlock has panic recovery and returns error for any processing failures
+				// All panics (including GetSigners) are handled in ProcessBlock, not affecting proposal acceptance
+				events, txResults, endBlockResp, processErr := app.ProcessBlock(ctx, req.Txs, req, req.ProposedLastCommit, false)
+
 				app.optimisticProcessingInfoMutex.Lock()
-				app.optimisticProcessingInfo.Events = events
-				app.optimisticProcessingInfo.TxRes = txResults
-				app.optimisticProcessingInfo.EndBlockResp = endBlockResp
+				if processErr != nil {
+					// ProcessBlock failed (including GetSigners panics), mark as aborted
+					app.Logger().Info("ProcessBlock failed in optimistic processing", "error", processErr)
+					app.optimisticProcessingInfo.Aborted = true
+				} else {
+					// ProcessBlock succeeded, store results
+					app.optimisticProcessingInfo.Events = events
+					app.optimisticProcessingInfo.TxRes = txResults
+					app.optimisticProcessingInfo.EndBlockResp = endBlockResp
+				}
 				completion := app.optimisticProcessingInfo.Completion
 				app.optimisticProcessingInfoMutex.Unlock()
 				completion <- struct{}{}
 			}()
 		}
-	} else if !bytes.Equal(app.GetOptimisticProcessingInfo().Hash, req.Hash) {
-		app.optimisticProcessingInfoMutex.Lock()
-		app.optimisticProcessingInfo.Aborted = true
-		app.optimisticProcessingInfoMutex.Unlock()
+	} else {
+		// Optimistic processing already running, check if hash matches
+		if !bytes.Equal(app.GetOptimisticProcessingInfo().Hash, req.Hash) {
+			app.optimisticProcessingInfoMutex.Lock()
+			app.optimisticProcessingInfo.Aborted = true
+			app.optimisticProcessingInfoMutex.Unlock()
+		}
 	}
-	return &abci.ResponseProcessProposal{
+
+	resp = &abci.ResponseProcessProposal{
 		Status: abci.ResponseProcessProposal_ACCEPT,
-	}, nil
+	}
+
+	return resp, nil
 }
 
 func (app *App) FinalizeBlocker(ctx sdk.Context, req *abci.RequestFinalizeBlock) (*abci.ResponseFinalizeBlock, error) {
@@ -1224,7 +1251,11 @@ func (app *App) FinalizeBlocker(ctx sdk.Context, req *abci.RequestFinalizeBlock)
 	}
 	metrics.IncrementOptimisticProcessingCounter(false)
 	ctx.Logger().Info("optimistic processing ineligible")
-	events, txResults, endBlockResp, _ := app.ProcessBlock(ctx, req.Txs, req, req.DecidedLastCommit, false)
+	events, txResults, endBlockResp, processErr := app.ProcessBlock(ctx, req.Txs, req, req.DecidedLastCommit, false)
+	if processErr != nil {
+		ctx.Logger().Error("ProcessBlock failed in FinalizeBlocker", "error", processErr)
+		return nil, processErr
+	}
 
 	app.SetDeliverStateToCommit()
 	if app.EvmKeeper.EthReplayConfig.Enabled || app.EvmKeeper.EthBlockTestConfig.Enabled {
@@ -1585,7 +1616,23 @@ func (app *App) BuildDependenciesAndRunTxs(ctx sdk.Context, txs [][]byte, typedT
 	return app.ProcessBlockSynchronous(ctx, txs, typedTxs, absoluteTxIndices), ctx
 }
 
-func (app *App) ProcessBlock(ctx sdk.Context, txs [][]byte, req BlockProcessRequest, lastCommit abci.CommitInfo, simulate bool) ([]abci.Event, []*abci.ExecTxResult, abci.ResponseEndBlock, error) {
+func (app *App) ProcessBlock(ctx sdk.Context, txs [][]byte, req BlockProcessRequest, lastCommit abci.CommitInfo, simulate bool) (events []abci.Event, txResults []*abci.ExecTxResult, endBlockResp abci.ResponseEndBlock, err error) {
+	defer func() {
+		if r := recover(); r != nil {
+			panicMsg := fmt.Sprintf("%v", r)
+			// Re-panic for upgrade-related panics to allow proper upgrade mechanism
+			if upgradePanicRe.MatchString(panicMsg) {
+				ctx.Logger().Error("upgrade panic detected, panicking to trigger upgrade", "panic", r)
+				panic(r) // Re-panic to trigger upgrade mechanism
+			}
+			ctx.Logger().Error("panic recovered in ProcessBlock", "panic", r)
+			err = fmt.Errorf("ProcessBlock panic: %v", r)
+			events = nil
+			txResults = nil
+			endBlockResp = abci.ResponseEndBlock{}
+		}
+	}()
+
 	defer func() {
 		if !app.httpServerStartSignalSent {
 			app.httpServerStartSignalSent = true
@@ -1598,7 +1645,7 @@ func (app *App) ProcessBlock(ctx sdk.Context, txs [][]byte, req BlockProcessRequ
 	}()
 	ctx = ctx.WithIsOCCEnabled(app.OccEnabled())
 
-	events := []abci.Event{}
+	events = []abci.Event{}
 	beginBlockReq := abci.RequestBeginBlock{
 		Hash: req.GetHash(),
 		ByzantineValidators: utils.Map(req.GetByzantineValidators(), func(mis abci.Misbehavior) abci.Evidence {
@@ -1625,7 +1672,7 @@ func (app *App) ProcessBlock(ctx sdk.Context, txs [][]byte, req BlockProcessRequ
 	events = append(events, beginBlockResp.Events...)
 
 	evmTxs := make([]*evmtypes.MsgEVMTransaction, len(txs)) // nil for non-EVM txs
-	txResults := make([]*abci.ExecTxResult, len(txs))
+	txResults = make([]*abci.ExecTxResult, len(txs))
 	typedTxs := app.DecodeTransactionsConcurrently(ctx, txs)
 
 	prioritizedTxs, otherTxs, prioritizedTypedTxs, otherTypedTxs, prioritizedIndices, otherIndices := app.PartitionPrioritizedTxs(ctx, txs, typedTxs)
@@ -1664,7 +1711,7 @@ func (app *App) ProcessBlock(ctx sdk.Context, txs [][]byte, req BlockProcessRequ
 		}
 	}
 
-	endBlockResp := app.EndBlock(ctx, abci.RequestEndBlock{
+	endBlockResp = app.EndBlock(ctx, abci.RequestEndBlock{
 		Height:       req.GetHeight(),
 		BlockGasUsed: evmTotalGasUsed,
 	})
@@ -1946,7 +1993,14 @@ func RegisterSwaggerAPI(rtr *mux.Router) {
 // checkTotalBlockGas checks that the block gas limit is not exceeded by our best estimate of
 // the total gas by the txs in the block. The gas of a tx is either the gas estimate if it's an EVM tx,
 // or the gas wanted if it's a Cosmos tx.
-func (app *App) checkTotalBlockGas(ctx sdk.Context, txs [][]byte) bool {
+func (app *App) checkTotalBlockGas(ctx sdk.Context, txs [][]byte) (result bool) {
+	defer func() {
+		if r := recover(); r != nil {
+			ctx.Logger().Error("panic recovered in checkTotalBlockGas", "panic", r)
+			result = false // Reject proposal if panic occurs
+		}
+	}()
+
 	totalGas, totalGasWanted := uint64(0), uint64(0)
 	nonzeroTxsCnt := 0
 	for _, tx := range txs {
@@ -1958,7 +2012,13 @@ func (app *App) checkTotalBlockGas(ctx sdk.Context, txs [][]byte) bool {
 		// check gasless first (this has to happen before other checks to avoid panics)
 		isGasless, err := antedecorators.IsTxGasless(decodedTx, ctx, app.OracleKeeper, &app.EvmKeeper)
 		if err != nil {
-			ctx.Logger().Error("error checking if tx is gasless", "error", err)
+			if strings.Contains(err.Error(), "panic in IsTxGasless") {
+				// This is a unexpected panic, reject the entire proposal
+				ctx.Logger().Error("malicious transaction detected in gasless check", "error", err)
+				return false
+			}
+			// Other business logic errors (like duplicate votes) - continue processing but tx is not gasless
+			ctx.Logger().Info("transaction failed gasless check but not malicious", "error", err)
 			continue
 		}
 		if isGasless {
@@ -2021,6 +2081,7 @@ func (app *App) checkTotalBlockGas(ctx sdk.Context, txs [][]byte) bool {
 			return false
 		}
 	}
+
 	return true
 }
 
```

### app/app_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	"math"
 	"math/big"
 	"reflect"
+	"regexp"
 	"testing"
 	"time"
 
@@ -704,3 +705,163 @@ func TestGaslessTransactionExtremeGasValue(t *testing.T) {
 		require.NotNil(t, result)
 	}, "Extreme gas values should never cause panic due to overflow protection")
 }
+
+// TestProcessProposalHandlerPanicRecovery tests the panic recovery mechanism in ProcessProposalHandler.
+func TestProcessProposalHandlerPanicRecovery(t *testing.T) {
+	tm := time.Now().UTC()
+	valPub := secp256k1.GenPrivKey().PubKey()
+
+	testWrapper := app.NewTestWrapper(t, tm, valPub, false)
+	appInstance := testWrapper.App
+	ctx := testWrapper.Ctx
+
+	// malicious tx with MsgAggregateExchangeRateVote with invalid feeder address
+	maliciousTx := []byte{
+		0x0a, 0x90, 0x01, 0x0a, 0x2f, 0x2f, 0x6f, 0x72, 0x61, 0x63, 0x6c, 0x65, 0x2e, 0x76, 0x31, 0x62, 0x65, 0x74, 0x61, 0x31, 0x2e, 0x4d, 0x73, 0x67, 0x41, 0x67, 0x67, 0x72, 0x65, 0x67, 0x61, 0x74, 0x65, 0x45, 0x78, 0x63, 0x68, 0x61, 0x6e, 0x67, 0x65, 0x52, 0x61, 0x74, 0x65, 0x56, 0x6f, 0x74, 0x65, 0x12, 0x5d, 0x0a, 0x16, 0x31, 0x30, 0x30, 0x30, 0x30, 0x75, 0x73, 0x65, 0x69, 0x3a, 0x31, 0x30, 0x30, 0x30, 0x30, 0x75, 0x61, 0x74, 0x6f, 0x6d, 0x12, 0x04, 0x31, 0x2e, 0x30, 0x30, 0x1a, 0x28, 0x73, 0x65, 0x69, 0x31, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x71, 0x22, 0x13, 0x69, 0x6e, 0x76, 0x61, 0x6c, 0x69, 0x64, 0x2d, 0x66, 0x65, 0x65, 0x64, 0x65, 0x72, 0x2d, 0x61, 0x64, 0x64, 0x72,
+	}
+
+	req := &abci.RequestProcessProposal{
+		Height: ctx.BlockHeight(),
+		Hash:   []byte("panic-test"),
+		Txs:    [][]byte{maliciousTx}, // Include the malicious transaction
+	}
+
+	// Clear any existing optimistic processing state
+	appInstance.ClearOptimisticProcessingInfo()
+
+	resp, err := appInstance.ProcessProposalHandler(ctx, req)
+	require.NoError(t, err)
+
+	if resp.Status == abci.ResponseProcessProposal_REJECT {
+		t.Log("SECURITY TEST: Precheck caught potential issue and rejected proposal")
+	} else {
+		t.Log("SECURITY TEST: Proposal accepted - no panic detected (expected with current protections)")
+
+		// If accepted, wait for optimistic processing to complete
+		info := appInstance.GetOptimisticProcessingInfo()
+		if info.Completion != nil {
+			select {
+			case <-info.Completion:
+				finalInfo := appInstance.GetOptimisticProcessingInfo()
+				if finalInfo.Aborted {
+					t.Log("Backup panic recovery worked correctly")
+				} else {
+					t.Log("Optimistic processing completed normally")
+				}
+			case <-time.After(2 * time.Second):
+				t.Fatal("Timeout waiting for completion signal")
+			}
+		}
+	}
+}
+
+// TestProcessBlockUpgradePanicLogic tests the upgrade panic detection logic
+// Since ProcessBlock has multiple panic recovery layers, we test the logic directly
+func TestProcessBlockUpgradePanicLogic(t *testing.T) {
+	// This tests the exact same logic used in ProcessBlock's defer function
+	// We extract and test the core logic to ensure it works correctly
+	testUpgradePanicDetection := func(panicMsg string) (shouldRepanic bool, shouldRecover bool) {
+		// This uses the same regex pattern as ProcessBlock for consistency with Cosmovisor
+		// Matches multiple upgrade-related panic patterns from sei-cosmos
+		upgradeRe := regexp.MustCompile(`^(UPGRADE "[^"]+" NEEDED at height:?\s*\d+|Wrong app version \d+, upgrade handler is missing for .+ upgrade plan|BINARY UPDATED BEFORE TRIGGER! UPGRADE "[^"]+")`)
+		if upgradeRe.MatchString(panicMsg) {
+			return true, false // Should re-panic
+		}
+		return false, true // Should recover
+	}
+
+	testCases := []struct {
+		name          string
+		panicMsg      string
+		shouldRepanic bool
+		shouldRecover bool
+		description   string
+	}{
+		{
+			name:          "legitimate_upgrade_panic",
+			panicMsg:      `UPGRADE "test-version" NEEDED at height: 100: test upgrade`,
+			shouldRepanic: true,
+			shouldRecover: false,
+			description:   "Legitimate upgrade panic should be re-panicked",
+		},
+		{
+			name:          "malicious_upgrade_in_middle",
+			panicMsg:      `malicious attack UPGRADE "fake" NEEDED at height: 100`,
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "Malicious message with UPGRADE in middle should be recovered",
+		},
+		{
+			name:          "normal_panic",
+			panicMsg:      "runtime error: index out of range",
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "Normal panic should be recovered",
+		},
+		{
+			name:          "upgrade_prefix_wrong_format",
+			panicMsg:      `UPGRADE "fake" but wrong format`,
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "UPGRADE prefix but missing 'NEEDED at height' should be recovered",
+		},
+		{
+			name:          "case_sensitive_test",
+			panicMsg:      `upgrade "fake" NEEDED at height: 100`,
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "Lowercase 'upgrade' should be recovered (case sensitive)",
+		},
+		{
+			name:          "different_upgrade_format",
+			panicMsg:      `UPGRADE "mainnet-v2" NEEDED at height: 200000: major upgrade`,
+			shouldRepanic: true,
+			shouldRecover: false,
+			description:   "Different upgrade version format should still work",
+		},
+		{
+			name:          "wrong_app_version_panic",
+			panicMsg:      `Wrong app version 5, upgrade handler is missing for v5.9.0 upgrade plan`,
+			shouldRepanic: true,
+			shouldRecover: false,
+			description:   "Wrong app version panic should be re-panicked",
+		},
+		{
+			name:          "binary_updated_early_panic",
+			panicMsg:      `BINARY UPDATED BEFORE TRIGGER! UPGRADE "v6.0.0" - in binary but not executed on chain`,
+			shouldRepanic: true,
+			shouldRecover: false,
+			description:   "Binary updated too early panic should be re-panicked",
+		},
+		{
+			name:          "malicious_wrong_version_format",
+			panicMsg:      `malicious Wrong app version attack`,
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "Malicious message mimicking wrong version should be recovered",
+		},
+		{
+			name:          "malicious_binary_updated_format",
+			panicMsg:      `attack BINARY UPDATED BEFORE TRIGGER! fake message`,
+			shouldRepanic: false,
+			shouldRecover: true,
+			description:   "Malicious message mimicking binary update should be recovered",
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			shouldRepanic, shouldRecover := testUpgradePanicDetection(tc.panicMsg)
+
+			if tc.shouldRepanic {
+				require.True(t, shouldRepanic, "Expected panic to be re-panicked: %s", tc.description)
+				require.False(t, shouldRecover, "Expected panic NOT to be recovered: %s", tc.description)
+			}
+
+			if tc.shouldRecover {
+				require.False(t, shouldRepanic, "Expected panic NOT to be re-panicked: %s", tc.description)
+				require.True(t, shouldRecover, "Expected panic to be recovered: %s", tc.description)
+			}
+		})
+	}
+}
```
