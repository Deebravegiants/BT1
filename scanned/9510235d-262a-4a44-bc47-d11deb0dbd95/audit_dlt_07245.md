# [?] fix(baseapp): ABCI Consensus Failure Fix (#16700)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-06-28
Source: https://github.com/cosmos/cosmos-sdk/commit/078e7cb4aeb1aa608951c2cf9abb931e9e81414c
Type: security-commit

## Details
fix(baseapp): ABCI Consensus Failure Fix (#16700)

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
Co-authored-by: Jeancarlo Barrios <JeancarloBarrios@users.noreply.github.com>
Co-authored-by: Julien Robert <julien@rbrt.fr>
Co-authored-by: Chill Validation <92176880+chillyvee@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -76,6 +76,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (baseapp) [#16613](https://github.com/cosmos/cosmos-sdk/pull/16613) Ensure each message in a transaction has a registered handler, otherwise `CheckTx` will fail.
 * (x/consensus) [#16713](https://github.com/cosmos/cosmos-sdk/pull/16713) Add missing ABCI param in MsgUpdateParams.
 * [#16639](https://github.com/cosmos/cosmos-sdk/pull/16639) Make sure we don't execute blocks beyond the halt height.
+* (baseapp) [#16700](https://github.com/cosmos/cosmos-sdk/pull/16700) Fix: Consensus Failure in returning no response to malformed transactions
 
 ## [v0.50.0-alpha.0](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.0-alpha.0) - 2023-06-07
 
```

### baseapp/abci.go
```diff
@@ -724,9 +724,24 @@ func (app *BaseApp) FinalizeBlock(req *abci.RequestFinalizeBlock) (*abci.Respons
 	// vote extensions, so skip those.
 	txResults := make([]*abci.ExecTxResult, 0, len(req.Txs))
 	for _, rawTx := range req.Txs {
+		var response *abci.ExecTxResult
+
 		if _, err := app.txDecoder(rawTx); err == nil {
-			txResults = append(txResults, app.deliverTx(rawTx))
+			response = app.deliverTx(rawTx)
+		} else {
+			// In the case where a transaction included in a block proposal is malformed,
+			// we still want to return a default response to comet. This is because comet
+			// expects a response for each transaction included in a block proposal.
+			response = sdkerrors.ResponseExecTxResultWithEvents(
+				sdkerrors.ErrTxDecode,
+				0,
+				0,
+				nil,
+				false,
+			)
 		}
+
+		txResults = append(txResults, response)
 	}
 
 	if app.finalizeBlockState.ms.TracingEnabled() {
```

### baseapp/abci_test.go
```diff
@@ -567,6 +567,19 @@ func TestABCI_InvalidTransaction(t *testing.T) {
 		Height: 1,
 	})
 
+	// malformed transaction bytes
+	{
+		bz := []byte("example vote extension")
+		result, err := suite.baseApp.FinalizeBlock(&abci.RequestFinalizeBlock{
+			Height: 1,
+			Txs:    [][]byte{bz},
+		})
+
+		require.EqualValues(t, sdkerrors.ErrTxDecode.Codespace(), result.TxResults[0].Codespace, err)
+		require.EqualValues(t, sdkerrors.ErrTxDecode.ABCICode(), result.TxResults[0].Code, err)
+		require.EqualValues(t, 0, result.TxResults[0].GasUsed, err)
+		require.EqualValues(t, 0, result.TxResults[0].GasWanted, err)
+	}
 	// transaction with no messages
 	{
 		emptyTx := suite.txConfig.NewTxBuilder().GetTx()
@@ -1231,6 +1244,69 @@ func TestABCI_Proposal_Read_State_PrepareProposal(t *testing.T) {
 	// })
 }
 
+func TestABCI_Proposals_WithVE(t *testing.T) {
+	someVoteExtension := []byte("some-vote-extension")
+
+	setInitChainerOpt := func(bapp *baseapp.BaseApp) {
+		bapp.SetInitChainer(func(ctx sdk.Context, req *abci.RequestInitChain) (*abci.ResponseInitChain, error) {
+			return &abci.ResponseInitChain{}, nil
+		})
+	}
+
+	prepareOpt := func(bapp *baseapp.BaseApp) {
+		bapp.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
+			// Inject the vote extension to the beginning of the proposal
+			txs := make([][]byte, len(req.Txs)+1)
+			txs[0] = someVoteExtension
+			copy(txs[1:], req.Txs)
+
+			return &abci.ResponsePrepareProposal{Txs: txs}, nil
+		})
+
+		bapp.SetProcessProposal(func(ctx sdk.Context, req *abci.RequestProcessProposal) (*abci.ResponseProcessProposal, error) {
+			// Check that the vote extension is still there
+			require.Equal(t, someVoteExtension, req.Txs[0])
+			return &abci.ResponseProcessProposal{Status: abci.ResponseProcessProposal_ACCEPT}, nil
+		})
+	}
+
+	suite := NewBaseAppSuite(t, setInitChainerOpt, prepareOpt)
+
+	suite.baseApp.InitChain(&abci.RequestInitChain{
+		InitialHeight:   1,
+		ConsensusParams: &cmtproto.ConsensusParams{},
+	})
+
+	reqPrepareProposal := abci.RequestPrepareProposal{
+		MaxTxBytes: 100000,
+		Height:     1, // this value can't be 0
+	}
+	resPrepareProposal, err := suite.baseApp.PrepareProposal(&reqPrepareProposal)
+	require.NoError(t, err)
+	require.Equal(t, 1, len(resPrepareProposal.Txs))
+
+	reqProcessProposal := abci.RequestProcessProposal{
+		Txs:    resPrepareProposal.Txs,
+		Height: reqPrepareProposal.Height,
+	}
+	resProcessProposal, err := suite.baseApp.ProcessProposal(&reqProcessProposal)
+	require.NoError(t, err)
+	require.Equal(t, abci.ResponseProcessProposal_ACCEPT, resProcessProposal.Status)
+
+	// Run finalize block and ensure that the vote extension is still there and that
+	// the proposal is accepted
+	result, err := suite.baseApp.FinalizeBlock(&abci.RequestFinalizeBlock{
+		Txs:    resPrepareProposal.Txs,
+		Height: reqPrepareProposal.Height,
+	})
+	require.NoError(t, err)
+	require.Equal(t, 1, len(result.TxResults))
+	require.EqualValues(t, sdkerrors.ErrTxDecode.Codespace(), result.TxResults[0].Codespace, err)
+	require.EqualValues(t, sdkerrors.ErrTxDecode.ABCICode(), result.TxResults[0].Code, err)
+	require.EqualValues(t, 0, result.TxResults[0].GasUsed, err)
+	require.EqualValues(t, 0, result.TxResults[0].GasWanted, err)
+}
+
 func TestABCI_PrepareProposal_ReachedMaxBytes(t *testing.T) {
 	anteKey := []byte("ante-key")
 	pool := mempool.NewSenderNonceMempool()
```
