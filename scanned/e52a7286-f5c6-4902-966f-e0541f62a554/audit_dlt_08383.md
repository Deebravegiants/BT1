# [?] fix(baseapp): log correct panic value in ExtendVote recovery handler (#25604)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-11-29
Source: https://github.com/cosmos/cosmos-sdk/commit/9cd057b6d5cee066a947c8c50ba952dbbd648216
Type: security-commit

## Details
fix(baseapp): log correct panic value in ExtendVote recovery handler (#25604)

Co-authored-by: Alex | Cosmos Labs <alex@cosmoslabs.io>

## Patch
### baseapp/abci.go
```diff
@@ -627,7 +627,7 @@ func (app *BaseApp) ExtendVote(_ context.Context, req *abci.RequestExtendVote) (
 				"panic recovered in ExtendVote",
 				"height", req.Height,
 				"hash", fmt.Sprintf("%X", req.Hash),
-				"panic", err,
+				"panic", r,
 			)
 			err = fmt.Errorf("recovered application panic in ExtendVote: %v", r)
 		}
```

### baseapp/abci_test.go
```diff
@@ -376,6 +376,82 @@ func TestABCI_ExtendVote(t *testing.T) {
 	require.Equal(t, abci.ResponseVerifyVoteExtension_REJECT, vres.Status)
 }
 
+// TestABCI_ExtendVote_PanicRecovery tests that when ExtendVoteHandler panics,
+// the panic is recovered and the error contains the panic message.
+func TestABCI_ExtendVote_PanicRecovery(t *testing.T) {
+	name := t.Name()
+	db := dbm.NewMemDB()
+	app := baseapp.NewBaseApp(name, log.NewTestLogger(t), db, nil)
+
+	panicMsg := "test panic message for ExtendVote"
+	app.SetExtendVoteHandler(func(ctx sdk.Context, req *abci.RequestExtendVote) (*abci.ResponseExtendVote, error) {
+		panic(panicMsg)
+	})
+
+	app.SetVerifyVoteExtensionHandler(func(ctx sdk.Context, req *abci.RequestVerifyVoteExtension) (*abci.ResponseVerifyVoteExtension, error) {
+		return &abci.ResponseVerifyVoteExtension{Status: abci.ResponseVerifyVoteExtension_ACCEPT}, nil
+	})
+
+	app.SetParamStore(&paramStore{db: dbm.NewMemDB()})
+	_, err := app.InitChain(
+		&abci.RequestInitChain{
+			InitialHeight: 1,
+			ConsensusParams: &cmtproto.ConsensusParams{
+				Abci: &cmtproto.ABCIParams{
+					VoteExtensionsEnableHeight: 1,
+				},
+			},
+		},
+	)
+	require.NoError(t, err)
+
+	// Call ExtendVote which should panic and recover
+	_, err = app.ExtendVote(context.Background(), &abci.RequestExtendVote{Height: 1, Hash: []byte("thehash")})
+
+	// The error should contain the panic message
+	require.Error(t, err)
+	require.Contains(t, err.Error(), panicMsg)
+	require.Contains(t, err.Error(), "recovered application panic in ExtendVote")
+}
+
+// TestABCI_VerifyVoteExtension_PanicRecovery tests that when VerifyVoteExtensionHandler panics,
+// the panic is recovered and the error contains the panic message.
+func TestABCI_VerifyVoteExtension_PanicRecovery(t *testing.T) {
+	name := t.Name()
+	db := dbm.NewMemDB()
+	app := baseapp.NewBaseApp(name, log.NewTestLogger(t), db, nil)
+
+	panicMsg := "test panic message for VerifyVoteExtension"
+	app.SetExtendVoteHandler(func(ctx sdk.Context, req *abci.RequestExtendVote) (*abci.ResponseExtendVote, error) {
+		return &abci.ResponseExtendVote{VoteExtension: []byte("extension")}, nil
+	})
+
+	app.SetVerifyVoteExtensionHandler(func(ctx sdk.Context, req *abci.RequestVerifyVoteExtension) (*abci.ResponseVerifyVoteExtension, error) {
+		panic(panicMsg)
+	})
+
+	app.SetParamStore(&paramStore{db: dbm.NewMemDB()})
+	_, err := app.InitChain(
+		&abci.RequestInitChain{
+			InitialHeight: 1,
+			ConsensusParams: &cmtproto.ConsensusParams{
+				Abci: &cmtproto.ABCIParams{
+					VoteExtensionsEnableHeight: 1,
+				},
+			},
+		},
+	)
+	require.NoError(t, err)
+
+	// Call VerifyVoteExtension which should panic and recover
+	_, err = app.VerifyVoteExtension(&abci.RequestVerifyVoteExtension{Height: 1, Hash: []byte("thehash"), VoteExtension: []byte("extension")})
+
+	// The error should contain the panic message
+	require.Error(t, err)
+	require.Contains(t, err.Error(), panicMsg)
+	require.Contains(t, err.Error(), "recovered application panic in VerifyVoteExtension")
+}
+
 // TestABCI_OnlyVerifyVoteExtension makes sure we can call VerifyVoteExtension
 // without having called ExtendVote before.
 func TestABCI_OnlyVerifyVoteExtension(t *testing.T) {
```
