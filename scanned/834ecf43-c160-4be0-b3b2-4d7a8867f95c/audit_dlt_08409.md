# [?] fix: keep behavior from v0.47 in PrepareProposal panic recovery (#17930)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-10-10
Source: https://github.com/cosmos/cosmos-sdk/commit/223e179f2b6f8351f2d674ab7526b710fbbcb874
Type: security-commit

## Details
fix: keep behavior from v0.47 in PrepareProposal panic recovery (#17930)

## Patch
### baseapp/abci.go
```diff
@@ -453,14 +453,14 @@ func (app *BaseApp) PrepareProposal(req *abci.RequestPrepareProposal) (resp *abc
 				"panic", err,
 			)
 
-			resp = &abci.ResponsePrepareProposal{}
+			resp = &abci.ResponsePrepareProposal{Txs: req.Txs}
 		}
 	}()
 
 	resp, err = app.prepareProposal(app.prepareProposalState.ctx, req)
 	if err != nil {
 		app.logger.Error("failed to prepare proposal", "height", req.Height, "time", req.Time, "err", err)
-		return &abci.ResponsePrepareProposal{}, nil
+		return &abci.ResponsePrepareProposal{Txs: req.Txs}, nil
 	}
 
 	return resp, nil
```

### baseapp/abci_test.go
```diff
@@ -2296,6 +2296,43 @@ func TestBaseApp_VoteExtensions(t *testing.T) {
 	require.Equal(t, avgPrice, committedAvgPrice)
 }
 
+func TestABCI_PrepareProposal_Panic(t *testing.T) {
+	prepareOpt := func(bapp *baseapp.BaseApp) {
+		bapp.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
+			if len(req.Txs) == 3 {
+				panic("i don't like number 3, panic")
+			}
+			// return empty if no panic
+			return &abci.ResponsePrepareProposal{}, nil
+		})
+	}
+
+	suite := NewBaseAppSuite(t, prepareOpt)
+
+	_, err := suite.baseApp.InitChain(&abci.RequestInitChain{
+		InitialHeight:   1,
+		ConsensusParams: &cmtproto.ConsensusParams{},
+	})
+	require.NoError(t, err)
+
+	txs := [][]byte{{1}, {2}}
+	reqPrepareProposal := abci.RequestPrepareProposal{
+		MaxTxBytes: 1000,
+		Height:     1, // this value can't be 0
+		Txs:        txs,
+	}
+	resPrepareProposal, err := suite.baseApp.PrepareProposal(&reqPrepareProposal)
+	require.NoError(t, err)
+	require.Equal(t, 0, len(resPrepareProposal.Txs))
+
+	// make it panic, and check if it returns 3 txs (because of panic recovery)
+	txs = [][]byte{{1}, {2}, {3}}
+	reqPrepareProposal.Txs = txs
+	resPrepareProposal, err = suite.baseApp.PrepareProposal(&reqPrepareProposal)
+	require.NoError(t, err)
+	require.Equal(t, 3, len(resPrepareProposal.Txs))
+}
+
 func TestOptimisticExecution(t *testing.T) {
 	suite := NewBaseAppSuite(t, baseapp.SetOptimisticExecution())
 
```
