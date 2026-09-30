# [?] fix: race condition in baseapp states (#24655)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-05-13
Source: https://github.com/cosmos/cosmos-sdk/commit/b0466fd74f8ef58daf4baf997f14670d62e0a70c
Type: security-commit

## Details
fix: race condition in baseapp states (#24655)

Co-authored-by: beer-1 <beer-1@codingcats.xyz>
Co-authored-by: Tyler <48813565+technicallyty@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -38,8 +38,13 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ## [Unreleased]
 
+### Improvements
+
+* (baseapp) [#24655](https://github.com/cosmos/cosmos-sdk/pull/24655) Add mutex locks for `state` and make `lastCommitInfo` atomic to prevent race conditions between `Commit` and `CreateQueryContext`.
+
 ### Bug Fixes
 
+* (client, client/rpc, x/auth/tx) [#24551](https://github.com/cosmos/cosmos-sdk/pull/24551) Handle cancellation properly when supplying context to client methods.
 * (x/authz) [#24638](https://github.com/cosmos/cosmos-sdk/pull/24638) Fixed a minor bug where the grant key was cast as a string and dumped directly into the error message leading to an error string possibly containing invalid UTF-8.
 
 ### Deprecated
@@ -48,10 +53,6 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (x/group) [#24571](https://github.com/cosmos/cosmos-sdk/pull/24571) Deprecate the `x/group` module in the Cosmos SDK repository.  This module will not be maintained to the extent that our core modules will and will be kept in a [legacy repo](https://github.com/cosmos/cosmos-legacy).
 * (types) [#24664](https://github.com/cosmos/cosmos-sdk/pull/24664) Deprecate the `Invariant` type in the Cosmos SDK.
 
-### Bug Fixes
-
-* (client, client/rpc, x/auth/tx) [#24551](https://github.com/cosmos/cosmos-sdk/pull/24551) Handle cancellation properly when supplying context to client methods.
-
 ## [v0.53.0](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.53.0) - 2025-04-29
 
 ### Features
```

### baseapp/abci.go
```diff
@@ -20,6 +20,7 @@ import (
 	snapshottypes "cosmossdk.io/store/snapshots/types"
 	storetypes "cosmossdk.io/store/types"
 
+	"github.com/cosmos/cosmos-sdk/baseapp/state"
 	"github.com/cosmos/cosmos-sdk/codec"
 	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -62,14 +63,15 @@ func (app *BaseApp) InitChain(req *abci.RequestInitChain) (*abci.ResponseInitCha
 	}
 
 	// initialize states with a correct header
-	app.setState(execModeFinalize, initHeader)
-	app.setState(execModeCheck, initHeader)
+	app.stateManager.SetState(execModeFinalize, app.cms, initHeader, app.logger, app.streamingManager)
+	app.stateManager.SetState(execModeCheck, app.cms, initHeader, app.logger, app.streamingManager)
+	finalizeState := app.stateManager.GetState(execModeFinalize)
 
 	// Store the consensus params in the BaseApp's param store. Note, this must be
 	// done after the finalizeBlockState and context have been set as it's persisted
 	// to state.
 	if req.ConsensusParams != nil {
-		err := app.StoreConsensusParams(app.finalizeBlockState.Context(), *req.ConsensusParams)
+		err := app.StoreConsensusParams(finalizeState.Context(), *req.ConsensusParams)
 		if err != nil {
 			return nil, err
 		}
@@ -81,13 +83,14 @@ func (app *BaseApp) InitChain(req *abci.RequestInitChain) (*abci.ResponseInitCha
 		// handler, the block height is zero by default. However, after Commit is called
 		// the height needs to reflect the true block height.
 		initHeader.Height = req.InitialHeight
-		app.checkState.SetContext(app.checkState.Context().WithBlockHeader(initHeader).
+		checkState := app.stateManager.GetState(execModeCheck)
+		checkState.SetContext(checkState.Context().WithBlockHeader(initHeader).
 			WithHeaderInfo(coreheader.Info{
 				ChainID: req.ChainId,
 				Height:  req.InitialHeight,
 				Time:    req.Time,
 			}))
-		app.finalizeBlockState.SetContext(app.finalizeBlockState.Context().WithBlockHeader(initHeader).
+		finalizeState.SetContext(finalizeState.Context().WithBlockHeader(initHeader).
 			WithHeaderInfo(coreheader.Info{
 				ChainID: req.ChainId,
 				Height:  req.InitialHeight,
@@ -100,9 +103,9 @@ func (app *BaseApp) InitChain(req *abci.RequestInitChain) (*abci.ResponseInitCha
 	}
 
 	// add block gas meter for any genesis transactions (allow infinite gas)
-	app.finalizeBlockState.SetContext(app.finalizeBlockState.Context().WithBlockGasMeter(storetypes.NewInfiniteGasMeter()))
+	finalizeState.SetContext(finalizeState.Context().WithBlockGasMeter(storetypes.NewInfiniteGasMeter()))
 
-	res, err := app.abciHandlers.InitChainer(app.finalizeBlockState.Context(), req)
+	res, err := app.abciHandlers.InitChainer(finalizeState.Context(), req)
 	if err != nil {
 		return nil, err
 	}
@@ -336,9 +339,9 @@ func (app *BaseApp) ApplySnapshotChunk(req *abci.RequestApplySnapshotChunk) (*ab
 // and only the AnteHandler is executed. State is persisted to the BaseApp's
 // internal CheckTx state if the AnteHandler passes. Otherwise, the ResponseCheckTx
 // will contain relevant error information. Regardless of tx execution outcome,
-// the ResponseCheckTx will contain relevant gas execution context.
+// the ResponseCheckTx will contain the relevant gas execution context.
 func (app *BaseApp) CheckTx(req *abci.RequestCheckTx) (*abci.ResponseCheckTx, error) {
-	var mode execMode
+	var mode sdk.ExecMode
 
 	switch req.Type {
 	case abci.CheckTxType_New:
@@ -352,14 +355,14 @@ func (app *BaseApp) CheckTx(req *abci.RequestCheckTx) (*abci.ResponseCheckTx, er
 	}
 
 	if app.abciHandlers.CheckTxHandler == nil {
-		gInfo, result, anteEvents, err := app.runTx(mode, req.Tx, nil)
+		gasInfo, result, anteEvents, err := app.runTx(mode, req.Tx, nil)
 		if err != nil {
-			return sdkerrors.ResponseCheckTxWithEvents(err, gInfo.GasWanted, gInfo.GasUsed, anteEvents, app.trace), nil
+			return sdkerrors.ResponseCheckTxWithEvents(err, gasInfo.GasWanted, gasInfo.GasUsed, anteEvents, app.trace), nil
 		}
 
 		return &abci.ResponseCheckTx{
-			GasWanted: int64(gInfo.GasWanted), // TODO: Should type accept unsigned ints?
-			GasUsed:   int64(gInfo.GasUsed),   // TODO: Should type accept unsigned ints?
+			GasWanted: int64(gasInfo.GasWanted), // TODO: Should type accept unsigned ints?
+			GasUsed:   int64(gasInfo.GasUsed),   // TODO: Should type accept unsigned ints?
 			Log:       result.Log,
 			Data:      result.Data,
 			Events:    sdk.MarkEventsToIndex(result.Events, app.indexEvents),
@@ -402,7 +405,7 @@ func (app *BaseApp) PrepareProposal(req *abci.RequestPrepareProposal) (resp *abc
 		NextValidatorsHash: req.NextValidatorsHash,
 		AppHash:            app.LastCommitID().Hash,
 	}
-	app.setState(execModePrepareProposal, header)
+	app.stateManager.SetState(execModePrepareProposal, app.cms, header, app.logger, app.streamingManager)
 
 	// CometBFT must never call PrepareProposal with a height of 0.
 	//
@@ -411,7 +414,8 @@ func (app *BaseApp) PrepareProposal(req *abci.RequestPrepareProposal) (resp *abc
 		return nil, errors.New("PrepareProposal called with invalid height")
 	}
 
-	app.prepareProposalState.SetContext(app.getContextForProposal(app.prepareProposalState.Context(), req.Height).
+	prepareProposalState := app.stateManager.GetState(execModePrepareProposal)
+	prepareProposalState.SetContext(app.getContextForProposal(prepareProposalState.Context(), req.Height).
 		WithVoteInfos(toVoteInfo(req.LocalLastCommit.Votes)). // this is a set of votes that are not finalized yet, wait for commit
 		WithBlockHeight(req.Height).
 		WithBlockTime(req.Time).
@@ -424,9 +428,9 @@ func (app *BaseApp) PrepareProposal(req *abci.RequestPrepareProposal) (resp *abc
 			Time:    req.Time,
 		}))
 
-	app.prepareProposalState.SetContext(app.prepareProposalState.Context().
-		WithConsensusParams(app.GetConsensusParams(app.prepareProposalState.Context())).
-		WithBlockGasMeter(app.getBlockGasMeter(app.prepareProposalState.Context())))
+	prepareProposalState.SetContext(prepareProposalState.Context().
+		WithConsensusParams(app.GetConsensusParams(prepareProposalState.Context())).
+		WithBlockGasMeter(app.getBlockGasMeter(prepareProposalState.Context())))
 
 	defer func() {
 		if err := recover(); err != nil {
@@ -441,7 +445,7 @@ func (app *BaseApp) PrepareProposal(req *abci.RequestPrepareProposal) (resp *abc
 		}
 	}()
 
-	resp, err = app.abciHandlers.PrepareProposalHandler(app.prepareProposalState.Context(), req)
+	resp, err = app.abciHandlers.PrepareProposalHandler(prepareProposalState.Context(), req)
 	if err != nil {
 		app.logger.Error("failed to prepare proposal", "height", req.Height, "time", req.Time, "err", err)
 		return &abci.ResponsePrepareProposal{Txs: req.Txs}, nil
@@ -486,7 +490,7 @@ func (app *BaseApp) ProcessProposal(req *abci.RequestProcessProposal) (resp *abc
 		NextValidatorsHash: req.NextValidatorsHash,
 		AppHash:            app.LastCommitID().Hash,
 	}
-	app.setState(execModeProcessProposal, header)
+	app.stateManager.SetState(execModeProcessProposal, app.cms, header, app.logger, app.streamingManager)
 
 	// Since the application can get access to FinalizeBlock state and write to it,
 	// we must be sure to reset it in case ProcessProposal timeouts and is called
@@ -496,10 +500,11 @@ func (app *BaseApp) ProcessProposal(req *abci.RequestProcessProposal) (resp *abc
 	if req.Height > app.initialHeight {
 		// abort any running OE
 		app.optimisticExec.Abort()
-		app.setState(execModeFinalize, header)
+		app.stateManager.SetState(execModeFinalize, app.cms, header, app.logger, app.streamingManager)
 	}
 
-	app.processProposalState.SetContext(app.getContextForProposal(app.processProposalState.Context(), req.Height).
+	processProposalState := app.stateManager.GetState(execModeProcessProposal)
+	processProposalState.SetContext(app.getContextForProposal(processProposalState.Context(), req.Height).
 		WithVoteInfos(req.ProposedLastCommit.Votes). // this is a set of votes that are not finalized yet, wait for commit
 		WithBlockHeight(req.Height).
 		WithBlockTime(req.Time).
@@ -513,9 +518,9 @@ func (app *BaseApp) ProcessProposal(req *abci.RequestProcessProposal) (resp *abc
 			Time:    req.Time,
 		}))
 
-	app.processProposalState.SetContext(app.processProposalState.Context().
-		WithConsensusParams(app.GetConsensusParams(app.processProposalState.Context())).
-		WithBlockGasMeter(app.getBlockGasMeter(app.processProposalState.Context())))
+	processProposalState.SetContext(processProposalState.Context().
+		WithConsensusParams(app.GetConsensusParams(processProposalState.Context())).
+		WithBlockGasMeter(app.getBlockGasMeter(processProposalState.Context())))
 
 	defer func() {
 		if err := recover(); err != nil {
@@ -530,7 +535,7 @@ func (app *BaseApp) ProcessProposal(req *abci.RequestProcessProposal) (resp *abc
 		}
 	}()
 
-	resp, err = app.abciHandlers.ProcessProposalHandler(app.processProposalState.Context(), req)
+	resp, err = app.abciHandlers.ProcessProposalHandler(processProposalState.Context(), req)
 	if err != nil {
 		app.logger.Error("failed to process proposal", "height", req.Height, "time", req.Time, "hash", fmt.Sprintf("%X", req.Hash), "err", err)
 		return &abci.ResponseProcessProposal{Status: abci.ResponseProcessProposal_REJECT}, nil
@@ -570,7 +575,7 @@ func (app *BaseApp) ExtendVote(_ context.Context, req *abci.RequestExtendVote) (
 	// finalizeBlockState context, otherwise we don't get the uncommitted data
 	// from InitChain.
 	if req.Height == app.initialHeight {
-		ctx, _ = app.finalizeBlockState.Context().CacheContext()
+		ctx, _ = app.stateManager.GetState(execModeFinalize).Context().CacheContext()
 	} else {
 		emptyHeader := cmtproto.Header{ChainID: app.chainID, Height: req.Height}
 		ms := app.cms.CacheMultiStore()
@@ -645,7 +650,7 @@ func (app *BaseApp) VerifyVoteExtension(req *abci.RequestVerifyVoteExtension) (r
 	// finalizeBlockState context, otherwise we don't get the uncommitted data
 	// from InitChain.
 	if req.Height == app.initialHeight {
-		ctx, _ = app.finalizeBlockState.Context().CacheContext()
+		ctx, _ = app.stateManager.GetState(execModeFinalize).Context().CacheContext()
 	} else {
 		emptyHeader := cmtproto.Header{ChainID: app.chainID, Height: req.Height}
 		ms := app.cms.CacheMultiStore()
@@ -700,7 +705,7 @@ func (app *BaseApp) VerifyVoteExtension(req *abci.RequestVerifyVoteExtension) (r
 
 // internalFinalizeBlock executes the block, called by the Optimistic
 // Execution flow or by the FinalizeBlock ABCI method. The context received is
-// only used to handle early cancellation, for anything related to state app.finalizeBlockState.Context()
+// only used to handle early cancellation, for anything related to state app.stateManager.GetState(execModeFinalize).Context()
 // must be used.
 func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.RequestFinalizeBlock) (*abci.ResponseFinalizeBlock, error) {
 	var events []abci.Event
@@ -731,12 +736,14 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 	// finalizeBlockState should be set on InitChain or ProcessProposal. If it is
 	// nil, it means we are replaying this block and we need to set the state here
 	// given that during block replay ProcessProposal is not executed by CometBFT.
-	if app.finalizeBlockState == nil {
-		app.setState(execModeFinalize, header)
+	finalizeState := app.stateManager.GetState(execModeFinalize)
+	if finalizeState == nil {
+		app.stateManager.SetState(execModeFinalize, app.cms, header, app.logger, app.streamingManager)
+		finalizeState = app.stateManager.GetState(execModeFinalize)
 	}
 
 	// Context is now updated with Header information.
-	app.finalizeBlockState.SetContext(app.finalizeBlockState.Context().
+	finalizeState.SetContext(finalizeState.Context().
 		WithBlockHeader(header).
 		WithHeaderHash(req.Hash).
 		WithHeaderInfo(coreheader.Info{
@@ -746,7 +753,7 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 			Hash:    req.Hash,
 			AppHash: app.LastCommitID().Hash,
 		}).
-		WithConsensusParams(app.GetConsensusParams(app.finalizeBlockState.Context())).
+		WithConsensusParams(app.GetConsensusParams(finalizeState.Context())).
 		WithVoteInfos(req.DecidedLastCommit.Votes).
 		WithExecMode(sdk.ExecModeFinalize).
 		WithCometInfo(cometInfo{
@@ -757,11 +764,11 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 		}))
 
 	// GasMeter must be set after we get a context with updated consensus params.
-	gasMeter := app.getBlockGasMeter(app.finalizeBlockState.Context())
-	app.finalizeBlockState.SetContext(app.finalizeBlockState.Context().WithBlockGasMeter(gasMeter))
+	gasMeter := app.getBlockGasMeter(finalizeState.Context())
+	finalizeState.SetContext(finalizeState.Context().WithBlockGasMeter(gasMeter))
 
-	if app.checkState != nil {
-		app.checkState.SetContext(app.checkState.Context().
+	if checkState := app.stateManager.GetState(execModeCheck); checkState != nil {
+		checkState.SetContext(checkState.Context().
 			WithBlockGasMeter(gasMeter).
 			WithHeaderHash(req.Hash))
 	}
@@ -790,8 +797,8 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 	events = append(events, beginBlock.Events...)
 
 	// Reset the gas meter so that the AnteHandlers aren't required to
-	gasMeter = app.getBlockGasMeter(app.finalizeBlockState.Context())
-	app.finalizeBlockState.SetContext(app.finalizeBlockState.Context().WithBlockGasMeter(gasMeter))
+	gasMeter = app.getBlockGasMeter(finalizeState.Context())
+	finalizeState.SetContext(finalizeState.Context().WithBlockGasMeter(gasMeter))
 
 	// Iterate over all raw transactions in the proposal and attempt to execute
 	// them, gathering the execution results.
@@ -828,11 +835,11 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 		txResults = append(txResults, response)
 	}
 
-	if app.finalizeBlockState.ms.TracingEnabled() {
-		app.finalizeBlockState.ms = app.finalizeBlockState.ms.SetTracingContext(nil).(storetypes.CacheMultiStore)
+	if finalizeState.MultiStore.TracingEnabled() {
+		finalizeState.MultiStore = finalizeState.MultiStore.SetTracingContext(nil).(storetypes.CacheMultiStore)
 	}
 
-	endBlock, err := app.endBlock(app.finalizeBlockState.Context())
+	endBlock, err := app.endBlock(finalizeState.Context())
 	if err != nil {
 		return nil, err
 	}
@@ -846,7 +853,7 @@ func (app *BaseApp) internalFinalizeBlock(ctx context.Context, req *abci.Request
 	}
 
 	events = append(events, endBlock.Events...)
-	cp := app.GetConsensusParams(app.finalizeBlockState.Context())
+	cp := app.GetConsensusParams(finalizeState.Context())
 
 	return &abci.ResponseFinalizeBlock{
 		Events:                events,
@@ -873,7 +880,7 @@ func (app *BaseApp) FinalizeBlock(req *abci.RequestFinalizeBlock) (res *abci.Res
 		}
 		// call the streaming service hooks with the FinalizeBlock messages
 		for _, streamingListener := range app.streamingManager.ABCIListeners {
-			if err := streamingListener.ListenFinalizeBlock(app.finalizeBlockState.Context(), *req, *res); err != nil {
+			if err := streamingListener.ListenFinalizeBlock(app.stateManager.GetState(execModeFinalize).Context(), *req, *res); err != nil {
 				app.logger.Error("ListenFinalizeBlock listening hook failed", "height", req.Height, "err", err)
 			}
 		}
@@ -895,7 +902,7 @@ func (app *BaseApp) FinalizeBlock(req *abci.RequestFinalizeBlock) (res *abci.Res
 		}
 
 		// if it was aborted, we need to reset the state
-		app.finalizeBlockState = nil
+		app.stateManager.ClearState(execModeFinalize)
 		app.optimisticExec.Reset()
 	}
 
@@ -934,11 +941,12 @@ func (app *BaseApp) checkHalt(height int64, time time.Time) error {
 // against that height and gracefully halt if it matches the latest committed
 // height.
 func (app *BaseApp) Commit() (*abci.ResponseCommit, error) {
-	header := app.finalizeBlockState.Context().BlockHeader()
+	finalizeState := app.stateManager.GetState(execModeFinalize)
+	header := finalizeState.Context().BlockHeader()
 	retainHeight := app.GetBlockRetentionHeight(header.Height)
 
 	if app.abciHandlers.Precommiter != nil {
-		app.abciHandlers.Precommiter(app.finalizeBlockState.Context())
+		app.abciHandlers.Precommiter(finalizeState.Context())
 	}
 
 	rms, ok := app.cms.(*rootmulti.Store)
@@ -954,7 +962,7 @@ func (app *BaseApp) Commit() (*abci.ResponseCommit, error) {
 
 	abciListeners := app.streamingManager.ABCIListeners
 	if len(abciListeners) > 0 {
-		ctx := app.finalizeBlockState.Context()
+		ctx := finalizeState.Context()
 		blockHeight := ctx.BlockHeight()
 		changeSet := app.cms.PopStateCache()
 
@@ -969,12 +977,12 @@ func (app *BaseApp) Commit() (*abci.ResponseCommit, error) {
 	//
 	// NOTE: This is safe because CometBFT holds a lock on the mempool for
 	// Commit. Use the header from this latest block.
-	app.setState(execModeCheck, header)
+	app.stateManager.SetState(execModeCheck, app.cms, header, app.logger, app.streamingManager)
 
-	app.finalizeBlockState = nil
+	app.stateManager.ClearState(execModeFinalize)
 
 	if app.abciHandlers.PrepareCheckStater != nil {
-		app.abciHandlers.PrepareCheckStater(app.checkState.Context())
+		app.abciHandlers.PrepareCheckStater(app.stateManager.GetState(execModeCheck).Context())
 	}
 
 	// The SnapshotIfApplicable method will create the snapshot by starting the goroutine
@@ -992,7 +1000,7 @@ func (app *BaseApp) workingHash() []byte {
 	// Write the FinalizeBlock state into branched storage and commit the MultiStore.
 	// The write to the FinalizeBlock state writes all state transitions to the root
 	// MultiStore (app.cms) so when Commit() is called it persists those values.
-	app.finalizeBlockState.ms.Write()
+	app.stateManager.GetState(execModeFinalize).MultiStore.Write()
 
 	// Get the hash of all writes in order to return the apphash to the comet in finalizeBlock.
 	commitHash := app.cms.WorkingHash()
@@ -1139,7 +1147,7 @@ func (app *BaseApp) FilterPeerByID(info string) *abci.ResponseQuery {
 // access any state changes made in InitChain.
 func (app *BaseApp) getContextForProposal(ctx sdk.Context, height int64) sdk.Context {
 	if height == app.initialHeight {
-		ctx, _ = app.finalizeBlockState.Context().CacheContext()
+		ctx, _ = app.stateManager.GetState(execModeFinalize).Context().CacheContext()
 
 		// clear all context data set during InitChain to avoid inconsistent behavior
 		ctx = ctx.WithBlockHeader(cmtproto.Header{}).WithHeaderInfo(coreheader.Info{})
@@ -1199,26 +1207,26 @@ func checkNegativeHeight(height int64) error {
 
 // CreateQueryContext creates a new sdk.Context for a query, taking as args
 // the block height and whether the query needs a proof or not.
-func (app *BaseApp) CreateQueryContext(height int64, prove bool) (sdk.Context, error) {
-	return app.CreateQueryContextWithCheckHeader(height, prove, true)
+func (bapp *BaseApp) CreateQueryContext(height int64, prove bool) (sdk.Context, error) {
+	return bapp.CreateQueryContextWithCheckHeader(height, prove, true)
 }
 
 // CreateQueryContextWithCheckHeader creates a new sdk.Context for a query, taking as args
 // the block height, whether the query needs a proof or not, and whether to check the header or not.
-func (app *BaseApp) CreateQueryContextWithCheckHeader(height int64, prove, checkHeader bool) (sdk.Context, error) {
+func (bapp *BaseApp) CreateQueryContextWithCheckHeader(height int64, prove, checkHeader bool) (sdk.Context, error) {
 	if err := checkNegativeHeight(height); err != nil {
 		return sdk.Context{}, err
 	}
 
 	// use custom query multi-store if provided
-	qms := app.qms
+	qms := bapp.qms
 	if qms == nil {
-		qms = app.cms.(storetypes.MultiStore)
+		qms = bapp.cms.(storetypes.MultiStore)
 	}
 
 	lastBlockHeight := qms.LatestVersion()
 	if lastBlockHeight == 0 {
-		return sdk.Context{}, errorsmod.Wrapf(sdkerrors.ErrInvalidHeight, "%s is not ready; please wait for first block", app.Name())
+		return sdk.Context{}, errorsmod.Wrapf(sdkerrors.ErrInvalidHeight, "%s is not ready; please wait for first block", bapp.Name())
 	}
 
 	if height > lastBlockHeight {
@@ -1239,13 +1247,13 @@ func (app *BaseApp) CreateQueryContextWithCheckHeader(height int64, prove, check
 
 	var header *cmtproto.Header
 	isLatest := height == 0
-	for _, state := range []*state{
-		app.checkState,
-		app.finalizeBlockState,
+	for _, appState := range []*state.State{
+		bapp.stateManager.GetState(execModeCheck),
+		bapp.stateManager.GetState(execModeFinalize),
 	} {
-		if state != nil {
+		if appState != nil {
 			// branch the commit multi-store for safety
-			h := state.Context().BlockHeader()
+			h := appState.Context().BlockHeader()
 			if isLatest {
 				lastBlockHeight = qms.LatestVersion()
 			}
@@ -1279,14 +1287,14 @@ func (app *BaseApp) CreateQueryContextWithCheckHeader(height int64, prove, check
 	}
 
 	// branch the commit multi-store for safety
-	ctx := sdk.NewContext(cacheMS, *header, true, app.logger).
-		WithMinGasPrices(app.minGasPrices).
-		WithGasMeter(storetypes.NewGasMeter(app.queryGasLimit)).
+	ctx := sdk.NewContext(cacheMS, *header, true, bapp.logger).
+		WithMinGasPrices(bapp.gasConfig.MinGasPrices).
+		WithGasMeter(storetypes.NewGasMeter(bapp.gasConfig.QueryGasLimit)).
 		WithBlockHeader(*header).
 		WithBlockHeight(height)
 
 	if !isLatest {
-		rms, ok := app.cms.(*rootmulti.Store)
+		rms, ok := bapp.cms.(*rootmulti.Store)
 		if ok {
 			cInfo, err := rms.GetCommitInfo(height)
 			if cInfo != nil && err == nil {
@@ -1349,11 +1357,11 @@ func (app *BaseApp) GetBlockRetentionHeight(commitHeight int64) int64 {
 	var retentionHeight int64
 
 	// Define the number of blocks needed to protect against misbehaving validators
-	// which allows light clients to operate safely. Note, we piggy back of the
+	// which allows light clients to operate safely. Note, we piggyback of the
 	// evidence parameters instead of computing an estimated number of blocks based
 	// on the unbonding period and block commitment time as the two should be
 	// equivalent.
-	cp := app.GetConsensusParams(app.finalizeBlockState.Context())
+	cp := app.GetConsensusParams(app.stateManager.GetState(execModeFinalize).Context())
 	if cp.Evidence != nil && cp.Evidence.MaxAgeNumBlocks > 0 {
 		retentionHeight = commitHeight - cp.Evidence.MaxAgeNumBlocks
 	}
```

### baseapp/abci_test.go
```diff
@@ -11,6 +11,7 @@ import (
 	"math/rand"
 	"strconv"
 	"strings"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -2535,3 +2536,51 @@ func TestFinalizeBlockDeferResponseHandle(t *testing.T) {
 	require.Empty(t, res)
 	require.NotEmpty(t, err)
 }
+
+func TestABCI_Race_Commit_Query(t *testing.T) {
+	suite := NewBaseAppSuite(t, baseapp.SetChainID("test-chain-id"))
+	app := suite.baseApp
+
+	_, err := app.InitChain(&abci.RequestInitChain{
+		ChainId:         "test-chain-id",
+		ConsensusParams: &cmtproto.ConsensusParams{Block: &cmtproto.BlockParams{MaxGas: 5000000}},
+		InitialHeight:   1,
+	})
+	require.NoError(t, err)
+	_, err = app.Commit()
+	require.NoError(t, err)
+
+	counter := atomic.Uint64{}
+	counter.Store(0)
+
+	ctx, cancel := context.WithCancel(context.Background())
+	queryCreator := func() {
+		for {
+			select {
+			case <-ctx.Done():
+				return
+			default:
+				_, err := app.CreateQueryContextWithCheckHeader(0, false, false)
+				require.NoError(t, err)
+
+				counter.Add(1)
+			}
+		}
+	}
+
+	for i := 0; i < 100; i++ {
+		go queryCreator()
+	}
+
+	for i := 0; i < 1000; i++ {
+		_, err = app.FinalizeBlock(&abci.RequestFinalizeBlock{Height: app.LastBlockHeight() + 1})
+		require.NoError(t, err)
+
+		_, err = app.Commit()
+		require.NoError(t, err)
+	}
+
+	cancel()
+
+	require.Equal(t, int64(1001), app.GetContextForCheckTx(nil).BlockHeight())
+}
```

### baseapp/baseapp.go
```diff
@@ -17,15 +17,16 @@ import (
 	"github.com/cosmos/gogoproto/proto"
 	protov2 "google.golang.org/protobuf/proto"
 
-	"cosmossdk.io/core/header"
 	errorsmod "cosmossdk.io/errors"
 	"cosmossdk.io/log"
 	"cosmossdk.io/store"
 	storemetrics "cosmossdk.io/store/metrics"
 	"cosmossdk.io/store/snapshots"
 	storetypes "cosmossdk.io/store/types"
 
+	"github.com/cosmos/cosmos-sdk/baseapp/config"
 	"github.com/cosmos/cosmos-sdk/baseapp/oe"
+	"github.com/cosmos/cosmos-sdk/baseapp/state"
 	"github.com/cosmos/cosmos-sdk/codec"
 	codectypes "github.com/cosmos/cosmos-sdk/codec/types"
 	servertypes "github.com/cosmos/cosmos-sdk/server/types"
@@ -37,8 +38,6 @@ import (
 )
 
 type (
-	execMode uint8
-
 	// StoreLoader defines a customizable function to control how we load the
 	// CommitMultiStore from disk. This is useful for state migration, when
 	// loading a datastore written with an older version of the software. In
@@ -48,14 +47,14 @@ type (
 )
 
 const (
-	execModeCheck               execMode = iota // Check a transaction
-	execModeReCheck                             // Recheck a (pending) transaction after a commit
-	execModeSimulate                            // Simulate a transaction
-	execModePrepareProposal                     // Prepare a block proposal
-	execModeProcessProposal                     // Process a block proposal
-	execModeVoteExtension                       // Extend or verify a pre-commit vote
-	execModeVerifyVoteExtension                 // Verify a vote extension
-	execModeFinalize                            // Finalize a block proposal
+	execModeCheck               = sdk.ExecModeCheck               // Check a transaction
+	execModeReCheck             = sdk.ExecModeReCheck             // Recheck a (pending) transaction after a commit
+	execModeSimulate            = sdk.ExecModeSimulate            // Simulate a transaction
+	execModePrepareProposal     = sdk.ExecModePrepareProposal     // Prepare a block proposal
+	execModeProcessProposal     = sdk.ExecModeProcessProposal     // Process a block proposal
+	execModeVoteExtension       = sdk.ExecModeVoteExtension       // Extend or verify a pre-commit vote
+	execModeVerifyVoteExtension = sdk.ExecModeVerifyVoteExtension // Verify a vote extension
+	execModeFinalize            = sdk.ExecModeFinalize            // Finalize a block proposal
 )
 
 var _ servertypes.ABCI = (*BaseApp)(nil)
@@ -90,29 +89,7 @@ type BaseApp struct {
 	// manages snapshots, i.e. dumps of app state at certain intervals
 	snapshotManager *snapshots.Manager
 
-	// volatile states:
-	//
-	// - checkState is set on InitChain and reset on Commit
-	// - finalizeBlockState is set on InitChain and FinalizeBlock and set to nil
-	// on Commit.
-	//
-	// - checkState: Used for CheckTx, which is set based on the previous block's
-	// state. This state is never committed.
-	//
-	// - prepareProposalState: Used for PrepareProposal, which is set based on the
-	// previous block's state. This state is never committed. In case of multiple
-	// consensus rounds, the state is always reset to the previous block's state.
-	//
-	// - processProposalState: Used for ProcessProposal, which is set based on the
-	// the previous block's state. This state is never committed. In case of
-	// multiple rounds, the state is always reset to the previous block's state.
-	//
-	// - finalizeBlockState: Used for FinalizeBlock, which is set based on the
-	// previous block's state. This state is committed.
-	checkState           *state
-	prepareProposalState *state
-	processProposalState *state
-	finalizeBlockState   *state
+	stateManager *state.Manager
 
 	// An inter-block write-through cache provided to the context during the ABCI
 	// FinalizeBlock call.
@@ -122,12 +99,8 @@ type BaseApp struct {
 	// application parameter store.
 	paramStore ParamStore
 
-	// queryGasLimit defines the maximum gas for queries; unbounded if 0.
-	queryGasLimit uint64
-
-	// The minimum gas prices a validator is willing to accept for processing a
-	// transaction. This is mainly used for DoS and spam prevention.
-	minGasPrices sdk.DecCoins
+	// gasConfig contains node-level gas configuration.
+	gasConfig config.GasConfig
 
 	// initialHeight is the initial height at which we start the BaseApp
 	initialHeight int64
@@ -207,7 +180,7 @@ func NewBaseApp(
 		txDecoder:        txDecoder,
 		fauxMerkleMode:   false,
 		sigverifyTx:      true,
-		queryGasLimit:    math.MaxUint64,
+		gasConfig:        config.GasConfig{QueryGasLimit: math.MaxUint64},
 	}
 
 	for _, option := range options {
@@ -254,6 +227,8 @@ func NewBaseApp(
 		}
 	}
 
+	app.stateManager = state.NewManager(app.gasConfig)
+
 	return app
 }
 
@@ -431,17 +406,21 @@ func (app *BaseApp) Init() error {
 		return errors.New("commit multi-store must not be nil")
 	}
 
+	if app.stateManager == nil {
+		return errors.New("state manager must not be nil")
+	}
+
 	emptyHeader := cmtproto.Header{ChainID: app.chainID}
 
 	// needed for the export command which inits from store but never calls initchain
-	app.setState(execModeCheck, emptyHeader)
+	app.stateManager.SetState(execModeCheck, app.cms, emptyHeader, app.logger, app.streamingManager)
 	app.Seal()
 
 	return app.cms.GetPruning().Validate()
 }
 
 func (app *BaseApp) setMinGasPrices(gasPrices sdk.DecCoins) {
-	app.minGasPrices = gasPrices
+	app.gasConfig.MinGasPrices = gasPrices
 }
 
 func (app *BaseApp) setHaltHeight(haltHeight uint64) {
@@ -478,43 +457,6 @@ func (app *BaseApp) Seal() { app.sealed = true }
 // IsSealed returns true if the BaseApp is sealed and false otherwise.
 func (app *BaseApp) IsSealed() bool { return app.sealed }
 
-// setState sets the BaseApp's state for the corresponding mode with a branched
-// multi-store (i.e. a CacheMultiStore) and a new Context with the same
-// multi-store branch, and provided header.
-func (app *BaseApp) setState(mode execMode, h cmtproto.Header) {
-	ms := app.cms.CacheMultiStore()
-	headerInfo := header.Info{
-		Height:  h.Height,
-		Time:    h.Time,
-		ChainID: h.ChainID,
-		AppHash: h.AppHash,
-	}
-	baseState := &state{
-		ms: ms,
-		ctx: sdk.NewContext(ms, h, false, app.logger).
-			WithStreamingManager(app.streamingManager).
-			WithHeaderInfo(headerInfo),
-	}
-
-	switch mode {
-	case execModeCheck:
-		baseState.SetContext(baseState.Context().WithIsCheckTx(true).WithMinGasPrices(app.minGasPrices))
-		app.checkState = baseState
-
-	case execModePrepareProposal:
-		app.prepareProposalState = baseState
-
-	case execModeProcessProposal:
-		app.processProposalState = baseState
-
-	case execModeFinalize:
-		app.finalizeBlockState = baseState
-
-	default:
-		panic(fmt.Sprintf("invalid runTxMode for setState: %d", mode))
-	}
-}
-
 // SetCircuitBreaker sets the circuit breaker for the BaseApp.
 // The circuit breaker is checked on every message execution to verify if a transaction should be executed or not.
 func (app *BaseApp) SetCircuitBreaker(cb CircuitBreaker) {
@@ -635,22 +577,6 @@ func validateBasicTxMsgs(msgs []sdk.Msg) error {
 	return nil
 }
 
-func (app *BaseApp) getState(mode execMode) *state {
-	switch mode {
-	case execModeFinalize:
-		return app.finalizeBlockState
-
-	case execModePrepareProposal:
-		return app.prepareProposalState
-
-	case execModeProcessProposal:
-		return app.processProposalState
-
-	default:
-		return app.checkState
-	}
-}
-
 func (app *BaseApp) getBlockGasMeter(ctx sdk.Context) storetypes.GasMeter {
 	if app.disableBlockGasMeter {
 		return noopGasMeter{}
@@ -664,11 +590,11 @@ func (app *BaseApp) getBlockGasMeter(ctx sdk.Context) storetypes.GasMeter {
 }
 
 // retrieve the context for the tx w/ txBytes and other memoized values.
-func (app *BaseApp) getContextForTx(mode execMode, txBytes []byte) sdk.Context {
+func (app *BaseApp) getContextForTx(mode sdk.ExecMode, txBytes []byte) sdk.Context {
 	app.mu.Lock()
 	defer app.mu.Unlock()
 
-	modeState := app.getState(mode)
+	modeState := app.stateManager.GetState(mode)
 	if modeState == nil {
 		panic(fmt.Sprintf("state is nil for mode %v", mode))
 	}
@@ -687,7 +613,7 @@ func (app *BaseApp) getContextForTx(mode execMode, txBytes []byte) sdk.Context {
 
 	if mode == execModeSimulate {
 		ctx, _ = ctx.CacheContext()
-		ctx = ctx.WithExecMode(sdk.ExecMode(execModeSimulate))
+		ctx = ctx.WithExecMode(execModeSimulate)
 	}
 
 	return ctx
@@ -700,11 +626,9 @@ func (app *BaseApp) cacheTxContext(ctx sdk.Context, txBytes []byte) (sdk.Context
 	msCache := ms.CacheMultiStore()
 	if msCache.TracingEnabled() {
 		msCache = msCache.SetTracingContext(
-			storetypes.TraceContext(
-				map[string]any{
-					"txHash": fmt.Sprintf("%X", tmhash.Sum(txBytes)),
-				},
-			),
+			map[string]any{
+				"txHash": fmt.Sprintf("%X", tmhash.Sum(txBytes)),
+			},
 		).(storetypes.CacheMultiStore)
 	}
 
@@ -714,7 +638,8 @@ func (app *BaseApp) cacheTxContext(ctx sdk.Context, txBytes []byte) (sdk.Context
 func (app *BaseApp) preBlock(req *abci.RequestFinalizeBlock) ([]abci.Event, error) {
 	var events []abci.Event
 	if app.abciHandlers.PreBlocker != nil {
-		ctx := app.finalizeBlockState.Context().WithEventManager(sdk.NewEventManager())
+		finalizeState := app.stateManager.GetState(execModeFinalize)
+		ctx := finalizeState.Context().WithEventManager(sdk.NewEventManager())
 		rsp, err := app.abciHandlers.PreBlocker(ctx, req)
 		if err != nil {
 			return nil, err
@@ -726,7 +651,7 @@ func (app *BaseApp) preBlock(req *abci.RequestFinalizeBlock) ([]abci.Event, erro
 			// GasMeter must be set after we get a context with updated consensus params.
 			gasMeter := app.getBlockGasMeter(ctx)
 			ctx = ctx.WithBlockGasMeter(gasMeter)
-			app.finalizeBlockState.SetContext(ctx)
+			finalizeState.SetContext(ctx)
 		}
 		events = ctx.EventManager().ABCIEvents()
 	}
@@ -740,7 +665,7 @@ func (app *BaseApp) beginBlock(_ *abci.RequestFinalizeBlock) (sdk.BeginBlock, er
 	)
 
 	if app.abciHandlers.BeginBlocker != nil {
-		resp, err = app.abciHandlers.BeginBlocker(app.finalizeBlockState.Context())
+		resp, err = app.abciHandlers.BeginBlocker(app.stateManager.GetState(execModeFinalize).Context())
 		if err != nil {
 			return resp, err
 		}
@@ -802,7 +727,7 @@ func (app *BaseApp) endBlock(_ context.Context) (sdk.EndBlock, error) {
 	var endblock sdk.EndBlock
 
 	if app.abciHandlers.EndBlocker != nil {
-		eb, err := app.abciHandlers.EndBlocker(app.finalizeBlockState.Context())
+		eb, err := app.abciHandlers.EndBlocker(app.stateManager.GetState(execModeFinalize).Context())
 		if err != nil {
 			return endblock, err
 		}
@@ -831,7 +756,7 @@ func (app *BaseApp) endBlock(_ context.Context) (sdk.EndBlock, error) {
 // and execute successfully. An error is returned otherwise.
 // both txbytes and the decoded tx are passed to runTx to avoid the state machine encoding the tx and decoding the transaction twice
 // passing the decoded tx to runTX is optional, it will be decoded if the tx is nil
-func (app *BaseApp) runTx(mode execMode, txBytes []byte, tx sdk.Tx) (gInfo sdk.GasInfo, result *sdk.Result, anteEvents []abci.Event, err error) {
+func (app *BaseApp) runTx(mode sdk.ExecMode, txBytes []byte, tx sdk.Tx) (gInfo sdk.GasInfo, result *sdk.Result, anteEvents []abci.Event, err error) {
 	// NOTE: GasWanted should be returned by the AnteHandler. GasUsed is
 	// determined by the GasMeter. We need access to the context to get the gas
 	// meter, so we initialize upfront.
@@ -1020,7 +945,7 @@ func (app *BaseApp) runTx(mode execMode, txBytes []byte, tx sdk.Tx) (gInfo sdk.G
 // and DeliverTx. An error is returned if any single message fails or if a
 // Handler does not exist for a given message route. Otherwise, a reference to a
 // Result is returned. The caller must not commit state if an error is returned.
-func (app *BaseApp) runMsgs(ctx sdk.Context, msgs []sdk.Msg, msgsV2 []protov2.Message, mode execMode) (*sdk.Result, error) {
+func (app *BaseApp) runMsgs(ctx sdk.Context, msgs []sdk.Msg, msgsV2 []protov2.Message, mode sdk.ExecMode) (*sdk.Result, error) {
 	events := sdk.EmptyEvents()
 	var msgResponses []*codectypes.Any
 
```

### baseapp/baseapp_test.go
```diff
@@ -5,7 +5,9 @@ import (
 	"context"
 	"crypto/sha256"
 	"fmt"
+	"io"
 	"math/rand"
+	"os"
 	"testing"
 	"time"
 
@@ -48,10 +50,9 @@ var (
 
 type (
 	BaseAppSuite struct {
-		baseApp   *baseapp.BaseApp
-		cdc       *codec.ProtoCodec
-		txConfig  client.TxConfig
-		logBuffer *bytes.Buffer
+		baseApp  *baseapp.BaseApp
+		cdc      *codec.ProtoCodec
+		txConfig client.TxConfig
 	}
 
 	SnapshotsConfig struct {
@@ -71,8 +72,7 @@ func NewBaseAppSuite(t *testing.T, opts ...func(*baseapp.BaseApp)) *BaseAppSuite
 
 	txConfig := authtx.NewTxConfig(cdc, authtx.DefaultSignModes)
 	db := dbm.NewMemDB()
-	logBuffer := new(bytes.Buffer)
-	logger := log.NewLogger(logBuffer, log.ColorOption(false))
+	logger := log.NewLogger(os.Stdout, log.ColorOption(false))
 
 	app := baseapp.NewBaseApp(t.Name(), logger, db, txConfig.TxDecoder(), opts...)
 	require.Equal(t, t.Name(), app.Name())
@@ -88,10 +88,9 @@ func NewBaseAppSuite(t *testing.T, opts ...func(*baseapp.BaseApp)) *BaseAppSuite
 	require.Nil(t, app.LoadLatestVersion())
 
 	return &BaseAppSuite{
-		baseApp:   app,
-		cdc:       cdc,
-		txConfig:  txConfig,
-		logBuffer: logBuffer,
+		baseApp:  app,
+		cdc:      cdc,
+		txConfig: txConfig,
 	}
 }
 
@@ -687,9 +686,30 @@ func TestBaseAppPostHandler(t *testing.T) {
 	tx = wonkyMsg(t, suite.txConfig, tx)
 	txBytes, err = suite.txConfig.TxEncoder()(tx)
 	require.NoError(t, err)
-	_, err = suite.baseApp.FinalizeBlock(&abci.RequestFinalizeBlock{Height: 1, Txs: [][]byte{txBytes}})
+
+	output := captureStdout(t, func() {
+		_, err = suite.baseApp.FinalizeBlock(&abci.RequestFinalizeBlock{Height: 1, Txs: [][]byte{txBytes}})
+		require.NoError(t, err)
+	})
+	// Check the captured output
+	require.NotContains(t, output, "panic recovered in runTx")
+}
+
+func captureStdout(t *testing.T, fn func()) string {
+	t.Helper()
+	oldStdout := os.Stdout
+	r, w, _ := os.Pipe()
+	os.Stdout = w
+
+	fn()
+
+	w.Close()
+	os.Stdout = oldStdout
+
+	var buf bytes.Buffer
+	_, err := io.Copy(&buf, r)
 	require.NoError(t, err)
-	require.NotContains(t, suite.logBuffer.String(), "panic recovered in runTx")
+	return buf.String()
 }
 
 func TestBaseAppPostHandlerErrorHandling(t *testing.T) {
```

### baseapp/config/gas.go
```diff
@@ -0,0 +1,12 @@
+package config
+
+import sdk "github.com/cosmos/cosmos-sdk/types"
+
+type GasConfig struct {
+	// queryGasLimit defines the maximum gas for queries; unbounded if 0.
+	QueryGasLimit uint64
+
+	// The minimum gas prices a validator is willing to accept for processing a
+	// transaction. This is mainly used for DoS and spam prevention.
+	MinGasPrices sdk.DecCoins
+}
```

### baseapp/options.go
```diff
@@ -44,7 +44,7 @@ func SetQueryGasLimit(queryGasLimit uint64) func(*BaseApp) {
 		queryGasLimit = math.MaxUint64
 	}
 
-	return func(bapp *BaseApp) { bapp.queryGasLimit = queryGasLimit }
+	return func(bapp *BaseApp) { bapp.gasConfig.QueryGasLimit = queryGasLimit }
 }
 
 // SetHaltHeight returns a BaseApp option function that sets the halt block height.
```

### baseapp/regression_test.go
```diff
@@ -9,12 +9,16 @@ import (
 	"cosmossdk.io/log"
 	"cosmossdk.io/store"
 	storemetrics "cosmossdk.io/store/metrics"
+
+	"github.com/cosmos/cosmos-sdk/baseapp/config"
+	"github.com/cosmos/cosmos-sdk/baseapp/state"
 )
 
 // Ensures that error checks are performed before sealing the app.
 // Please see https://github.com/cosmos/cosmos-sdk/issues/18726
 func TestNilCmsCheckBeforeSeal(t *testing.T) {
 	app := new(BaseApp)
+	app.stateManager = state.NewManager(config.GasConfig{})
 
 	// 1. Invoking app.Init with a nil cms MUST not seal the app
 	// and should return an error firstly, which can later be reversed.
```

### baseapp/state/manager.go
```diff
@@ -0,0 +1,137 @@
+package state
+
+import (
+	"fmt"
+	"sync"
+
+	cmtproto "github.com/cometbft/cometbft/proto/tendermint/types"
+
+	"cosmossdk.io/core/header"
+	"cosmossdk.io/log"
+	storetypes "cosmossdk.io/store/types"
+
+	"github.com/cosmos/cosmos-sdk/baseapp/config"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+)
+
+type Manager struct {
+	// volatile states:
+	//
+	// - checkState is set on InitChain and reset on Commit
+	// - finalizeBlockState is set on InitChain and FinalizeBlock and set to nil
+	// on Commit.
+	//
+	// - checkState: Used for CheckTx, which is set based on the previous block's
+	// state. This state is never committed.
+	//
+	// - prepareProposalState: Used for PrepareProposal, which is set based on the
+	// previous block's state. This state is never committed. In case of multiple
+	// consensus rounds, the state is always reset to the previous block's state.
+	//
+	// - processProposalState: Used for ProcessProposal, which is set based on the
+	// the previous block's state. This state is never committed. In case of
+	// multiple rounds, the state is always reset to the previous block's state.
+	//
+	// - finalizeBlockState: Used for FinalizeBlock, which is set based on the
+	// previous block's state. This state is committed.
+	checkState           *State
+	prepareProposalState *State
+	processProposalState *State
+	finalizeBlockState   *State
+	stateMut             sync.RWMutex
+
+	gasConfig config.GasConfig
+}
+
+func NewManager(gasConfig config.GasConfig) *Manager {
+	return &Manager{
+		gasConfig: gasConfig,
+	}
+}
+
+func (mgr *Manager) GetState(mode sdk.ExecMode) *State {
+	mgr.stateMut.RLock()
+	defer mgr.stateMut.RUnlock()
+
+	switch mode {
+	case sdk.ExecModeFinalize:
+		return mgr.finalizeBlockState
+
+	case sdk.ExecModePrepareProposal:
+		return mgr.prepareProposalState
+
+	case sdk.ExecModeProcessProposal:
+		return mgr.processProposalState
+
+	default:
+		return mgr.checkState
+	}
+}
+
+// SetState sets the BaseApp's state for the corresponding mode with a branched
+// multi-store (i.e. a CacheMultiStore) and a new Context with the same
+// multi-store branch, and provided header.
+func (mgr *Manager) SetState(
+	mode sdk.ExecMode,
+	unbranchedStore storetypes.CommitMultiStore,
+	h cmtproto.Header,
+	logger log.Logger,
+	streamingManager storetypes.StreamingManager,
+) {
+	ms := unbranchedStore.CacheMultiStore()
+	headerInfo := header.Info{
+		Height:  h.Height,
+		Time:    h.Time,
+		ChainID: h.ChainID,
+		AppHash: h.AppHash,
+	}
+	baseState := NewState(
+		sdk.NewContext(ms, h, false, logger).
+			WithStreamingManager(streamingManager).
+			WithHeaderInfo(headerInfo),
+		ms,
+	)
+
+	mgr.stateMut.Lock()
+	defer mgr.stateMut.Unlock()
+
+	switch mode {
+	case sdk.ExecModeCheck:
+		baseState.SetContext(baseState.Context().WithIsCheckTx(true).WithMinGasPrices(mgr.gasConfig.MinGasPrices))
+		mgr.checkState = baseState
+
+	case sdk.ExecModePrepareProposal:
+		mgr.prepareProposalState = baseState
+
+	case sdk.ExecModeProcessProposal:
+		mgr.processProposalState = baseState
+
+	case sdk.ExecModeFinalize:
+		mgr.finalizeBlockState = baseState
+
+	default:
+		panic(fmt.Sprintf("invalid runTxMode for setState: %d", mode))
+	}
+}
+
+func (mgr *Manager) ClearState(mode sdk.ExecMode) {
+	mgr.stateMut.Lock()
+	defer mgr.stateMut.Unlock()
+
+	switch mode {
+	case sdk.ExecModeCheck:
+		mgr.checkState = nil
+
+	case sdk.ExecModePrepareProposal:
+		mgr.prepareProposalState = nil
+
+	case sdk.ExecModeProcessProposal:
+		mgr.processProposalState = nil
+
+	case sdk.ExecModeFinalize:
+		mgr.finalizeBlockState = nil
+
+	default:
+		panic(fmt.Sprintf("invalid runTxMode for clearState: %d", mode))
+	}
+}
```

### baseapp/state/state.go
```diff
@@ -1,4 +1,4 @@
-package baseapp
+package state
 
 import (
 	"sync"
@@ -8,28 +8,35 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
-type state struct {
-	ms storetypes.CacheMultiStore
+type State struct {
+	MultiStore storetypes.CacheMultiStore
 
 	mtx sync.RWMutex
 	ctx sdk.Context
 }
 
+func NewState(ctx sdk.Context, ms storetypes.CacheMultiStore) *State {
+	return &State{
+		MultiStore: ms,
+		ctx:        ctx,
+	}
+}
+
 // CacheMultiStore calls and returns a CacheMultiStore on the state's underling
 // CacheMultiStore.
-func (st *state) CacheMultiStore() storetypes.CacheMultiStore {
-	return st.ms.CacheMultiStore()
+func (st *State) CacheMultiStore() storetypes.CacheMultiStore {
+	return st.MultiStore.CacheMultiStore()
 }
 
 // SetContext updates the state's context to the context provided.
-func (st *state) SetContext(ctx sdk.Context) {
+func (st *State) SetContext(ctx sdk.Context) {
 	st.mtx.Lock()
 	defer st.mtx.Unlock()
 	st.ctx = ctx
 }
 
 // Context returns the Context of the state.
-func (st *state) Context() sdk.Context {
+func (st *State) Context() sdk.Context {
 	st.mtx.RLock()
 	defer st.mtx.RUnlock()
 	return st.ctx
```

### baseapp/test_helpers.go
```diff
@@ -54,17 +54,17 @@ func (app *BaseApp) SimTxFinalizeBlock(txEncoder sdk.TxEncoder, tx sdk.Tx) (sdk.
 // SimWriteState is an entrypoint for simulations only. They are not executed during the normal ABCI finalize
 // block step but later. Therefor an extra call to the root multi-store (app.cms) is required to write the changes.
 func (app *BaseApp) SimWriteState() {
-	app.finalizeBlockState.ms.Write()
+	app.stateManager.GetState(execModeFinalize).MultiStore.Write()
 }
 
 // NewContextLegacy returns a new sdk.Context with the provided header
 func (app *BaseApp) NewContextLegacy(isCheckTx bool, header cmtproto.Header) sdk.Context {
 	if isCheckTx {
-		return sdk.NewContext(app.checkState.ms, header, true, app.logger).
-			WithMinGasPrices(app.minGasPrices)
+		return sdk.NewContext(app.stateManager.GetState(execModeCheck).MultiStore, header, true, app.logger).
+			WithMinGasPrices(app.gasConfig.MinGasPrices)
 	}
 
-	return sdk.NewContext(app.finalizeBlockState.ms, header, false, app.logger)
+	return sdk.NewContext(app.stateManager.GetState(execModeFinalize).MultiStore, header, false, app.logger)
 }
 
 // NewContext returns a new sdk.Context with a empty header
```

### baseapp/utils_test.go
```diff
@@ -28,6 +28,7 @@ import (
 	storetypes "cosmossdk.io/store/types"
 
 	"github.com/cosmos/cosmos-sdk/baseapp"
+	"github.com/cosmos/cosmos-sdk/baseapp/state"
 	baseapptestutil "github.com/cosmos/cosmos-sdk/baseapp/testutil"
 	"github.com/cosmos/cosmos-sdk/client"
 	"github.com/cosmos/cosmos-sdk/codec"
@@ -323,18 +324,23 @@ func testLoadVersionHelper(t *testing.T, app *baseapp.BaseApp, expectedHeight in
 	require.Equal(t, expectedID, lastID)
 }
 
-func getCheckStateCtx(app *baseapp.BaseApp) sdk.Context {
+// note: we use reflection in this test because we do not want to make the baseapp state publicly available
+
+func reflectGetStateCtx(app *baseapp.BaseApp, mode sdk.ExecMode) sdk.Context {
 	v := reflect.ValueOf(app).Elem()
-	f := v.FieldByName("checkState")
+	f := v.FieldByName("stateManager")
 	rf := reflect.NewAt(f.Type(), unsafe.Pointer(f.UnsafeAddr())).Elem()
-	return rf.MethodByName("Context").Call(nil)[0].Interface().(sdk.Context)
+	arg := reflect.ValueOf(mode)
+	st := rf.MethodByName("GetState").Call([]reflect.Value{arg})[0].Interface().(*state.State)
+	return st.Context()
+}
+
+func getCheckStateCtx(app *baseapp.BaseApp) sdk.Context {
+	return reflectGetStateCtx(app, sdk.ExecModeCheck)
 }
 
 func getFinalizeBlockStateCtx(app *baseapp.BaseApp) sdk.Context {
-	v := reflect.ValueOf(app).Elem()
-	f := v.FieldByName("finalizeBlockState")
-	rf := reflect.NewAt(f.Type(), unsafe.Pointer(f.UnsafeAddr())).Elem()
-	return rf.MethodByName("Context").Call(nil)[0].Interface().(sdk.Context)
+	return reflectGetStateCtx(app, sdk.ExecModeFinalize)
 }
 
 func parseTxMemo(t *testing.T, tx sdk.Tx) (counter int64, failOnAnte bool) {
```
