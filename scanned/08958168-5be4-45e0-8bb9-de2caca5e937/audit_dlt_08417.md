# [?] fix: panic recovery in PrepareProposal and ProcessProposal Handlers (#14381)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2022-12-21
Source: https://github.com/cosmos/cosmos-sdk/commit/1152e5b0b5ed90da3665aa1b987a874208b6fcfa
Type: security-commit

## Details
fix: panic recovery in PrepareProposal and ProcessProposal Handlers (#14381)

## Patch
### baseapp/abci.go
```diff
@@ -247,12 +247,26 @@ func (app *BaseApp) EndBlock(req abci.RequestEndBlock) (res abci.ResponseEndBloc
 //
 // Ref: https://github.com/cosmos/cosmos-sdk/blob/main/docs/architecture/adr-060-abci-1.0.md
 // Ref: https://github.com/tendermint/tendermint/blob/main/spec/abci/abci%2B%2B_basic_concepts.md
-func (app *BaseApp) PrepareProposal(req abci.RequestPrepareProposal) abci.ResponsePrepareProposal {
+func (app *BaseApp) PrepareProposal(req abci.RequestPrepareProposal) (resp abci.ResponsePrepareProposal) {
 	ctx := app.getContextForTx(runTxPrepareProposal, []byte{})
 	if app.prepareProposal == nil {
 		panic("PrepareProposal method not set")
 	}
-	return app.prepareProposal(ctx, req)
+
+	defer func() {
+		if err := recover(); err != nil {
+			app.logger.Error(
+				"panic recovered in PrepareProposal",
+				"height", req.Height,
+				"time", req.Time,
+				"panic", err,
+			)
+			resp = abci.ResponsePrepareProposal{Txs: req.Txs}
+		}
+	}()
+
+	resp = app.prepareProposal(ctx, req)
+	return resp
 }
 
 // ProcessProposal implements the ProcessProposal ABCI method and returns a
@@ -265,9 +279,12 @@ func (app *BaseApp) PrepareProposal(req abci.RequestPrepareProposal) abci.Respon
 // to implement optimizations such as executing the entire proposed block
 // immediately. It may even execute the block in parallel.
 //
+// If a panic is detected during execution of an application's ProcessProposal
+// handler, it will be recovered and we will reject the proposal.
+//
 // Ref: https://github.com/cosmos/cosmos-sdk/blob/main/docs/architecture/adr-060-abci-1.0.md
 // Ref: https://github.com/tendermint/tendermint/blob/main/spec/abci/abci%2B%2B_basic_concepts.md
-func (app *BaseApp) ProcessProposal(req abci.RequestProcessProposal) abci.ResponseProcessProposal {
+func (app *BaseApp) ProcessProposal(req abci.RequestProcessProposal) (resp abci.ResponseProcessProposal) {
 	if app.processProposal == nil {
 		panic("app.ProcessProposal is not set")
 	}
@@ -280,7 +297,21 @@ func (app *BaseApp) ProcessProposal(req abci.RequestProcessProposal) abci.Respon
 		WithProposer(req.ProposerAddress).
 		WithConsensusParams(app.GetConsensusParams(app.processProposalState.ctx))
 
-	return app.processProposal(ctx, req)
+	defer func() {
+		if err := recover(); err != nil {
+			app.logger.Error(
+				"panic recovered in ProcessProposal",
+				"height", req.Height,
+				"time", req.Time,
+				"hash", fmt.Sprintf("%X", req.Hash),
+				"panic", err,
+			)
+			resp = abci.ResponseProcessProposal{Status: abci.ResponseProcessProposal_REJECT}
+		}
+	}()
+
+	resp = app.processProposal(ctx, req)
+	return resp
 }
 
 // CheckTx implements the ABCI interface and executes a tx in CheckTx mode. In
```

### baseapp/abci_test.go
```diff
@@ -2,6 +2,7 @@ package baseapp_test
 
 import (
 	"bytes"
+	"errors"
 	"fmt"
 	"strings"
 	"testing"
@@ -1452,3 +1453,43 @@ func TestABCI_PrepareProposal_Failures(t *testing.T) {
 	res := suite.baseApp.PrepareProposal(req)
 	require.Equal(t, 1, len(res.Txs))
 }
+
+func TestABCI_PrepareProposal_PanicRecovery(t *testing.T) {
+	prepareOpt := func(app *baseapp.BaseApp) {
+		app.SetPrepareProposal(func(ctx sdk.Context, rpp abci.RequestPrepareProposal) abci.ResponsePrepareProposal {
+			panic(errors.New("test"))
+		})
+	}
+	suite := NewBaseAppSuite(t, prepareOpt)
+
+	suite.baseApp.InitChain(abci.RequestInitChain{
+		ConsensusParams: &tmproto.ConsensusParams{},
+	})
+
+	req := abci.RequestPrepareProposal{
+		MaxTxBytes: 1000,
+	}
+
+	require.NotPanics(t, func() {
+		res := suite.baseApp.PrepareProposal(req)
+		require.Equal(t, req.Txs, res.Txs)
+	})
+}
+
+func TestABCI_ProcessProposal_PanicRecovery(t *testing.T) {
+	processOpt := func(app *baseapp.BaseApp) {
+		app.SetProcessProposal(func(ctx sdk.Context, rpp abci.RequestProcessProposal) abci.ResponseProcessProposal {
+			panic(errors.New("test"))
+		})
+	}
+	suite := NewBaseAppSuite(t, processOpt)
+
+	suite.baseApp.InitChain(abci.RequestInitChain{
+		ConsensusParams: &tmproto.ConsensusParams{},
+	})
+
+	require.NotPanics(t, func() {
+		res := suite.baseApp.ProcessProposal(abci.RequestProcessProposal{})
+		require.Equal(t, res.Status, abci.ResponseProcessProposal_REJECT)
+	})
+}
```
