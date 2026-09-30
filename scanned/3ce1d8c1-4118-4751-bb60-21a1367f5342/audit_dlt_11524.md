# [?] fix: return error instead of panicking on unknown CheckTxType (#6721)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-05
Source: https://github.com/celestiaorg/celestia-app/commit/16392cbec2579aff21a695ad927537a116721fda
Type: security-commit

## Details
fix: return error instead of panicking on unknown CheckTxType (#6721)

## Summary
- Replace `panic` with error response in `handleBlobCheckTx` when
receiving an unknown `RequestCheckTx` type, preventing node crashes from
unexpected `CheckTxType` values.
- Add `TestCheckTx_UnknownRequestType` test covering `CheckTxType`
values 2, 99, and -1.

## Details
The `default` branch in `handleBlobCheckTx` (`app/check_tx.go:67`)
previously called `panic()` on any `CheckTxType` other than `New` or
`Recheck`. While CometBFT currently only sends these two types,
defensive programming dictates returning an error rather than
terminating the node process. The fix returns an error response via
`responseCheckTxWithEvents`, consistent with how other validation
failures are handled in the same function.

## Test plan
- [x] `TestCheckTx_UnknownRequestType` passes — verifies no panic and
correct error response for unknown types
- [x] All existing `TestCheckTx` subtests still pass
- [x] `make build-standalone` succeeds

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### app/check_tx.go
```diff
@@ -64,7 +64,8 @@ func (app *App) handleBlobCheckTx(req *abci.RequestCheckTx, btx *blobtx.BlobTx)
 	case abci.CheckTxType_Recheck:
 		// no need to re-validate a blob
 	default:
-		panic(fmt.Sprintf("unknown RequestCheckTx type: %s", req.Type))
+		err := fmt.Errorf("unknown RequestCheckTx type: %s", req.Type)
+		return responseCheckTxWithEvents(err, 0, 0, []abci.Event{}, false), err
 	}
 
 	sdkTx, err := app.encodingConfig.TxConfig.TxDecoder()(baseReq.Tx)
```

### app/test/check_tx_test.go
```diff
@@ -308,6 +308,41 @@ func TestCheckTx(t *testing.T) {
 	}
 }
 
+// TestCheckTx_UnknownRequestType verifies that an unknown CheckTxType returns
+// an error response instead of panicking.
+func TestCheckTx_UnknownRequestType(t *testing.T) {
+	encodingConfig := encoding.MakeConfig(app.ModuleEncodingRegisters...)
+	namespace1, err := share.NewV0Namespace(bytes.Repeat([]byte{1}, share.NamespaceVersionZeroIDSize))
+	require.NoError(t, err)
+
+	accounts := []string{"a"}
+	testApp, kr := testutil.SetupTestAppWithGenesisValSet(app.DefaultConsensusParams(), accounts...)
+	fetchedAcc := testutil.DirectQueryAccount(testApp, testfactory.GetAddress(kr, "a"))
+	signer := createSigner(t, kr, "a", encodingConfig.TxConfig, fetchedAcc.GetAccountNumber())
+
+	// Create a valid blob transaction.
+	blobTxBytes := blobfactory.RandBlobTxsWithNamespacesAndSigner(
+		signer,
+		[]share.Namespace{namespace1},
+		[]int{100},
+	)[0]
+
+	unknownCheckTxTypes := []abci.CheckTxType{2, 99, -1}
+	for _, unknownType := range unknownCheckTxTypes {
+		t.Run(unknownType.String(), func(t *testing.T) {
+			assert.NotPanics(t, func() {
+				resp, err := testApp.CheckTx(&abci.RequestCheckTx{
+					Type: unknownType,
+					Tx:   blobTxBytes,
+				})
+				require.Error(t, err)
+				assert.NotEqual(t, abci.CodeTypeOK, resp.Code)
+				assert.Contains(t, resp.Log, "unknown RequestCheckTx type")
+			})
+		})
+	}
+}
+
 func createSigner(t *testing.T, kr keyring.Keyring, accountName string, enc client.TxConfig, accNum uint64) *user.Signer {
 	t.Helper()
 
```
