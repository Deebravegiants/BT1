# [?] fix(test): avoid panic of SetStreamingManager() on sealed BaseApp (#24109)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-03-24
Source: https://github.com/cosmos/cosmos-sdk/commit/da5a74da3b5731d00b1ba62744d6530310488698
Type: security-commit

## Details
fix(test): avoid panic of SetStreamingManager() on sealed BaseApp (#24109)

## Patch
### baseapp/abci_test.go
```diff
@@ -2781,11 +2781,12 @@ func TestABCI_Proposal_FailReCheckTx(t *testing.T) {
 }
 
 func TestFinalizeBlockDeferResponseHandle(t *testing.T) {
-	suite := NewBaseAppSuite(t, baseapp.SetHaltHeight(1))
-	suite.baseApp.SetStreamingManager(storetypes.StreamingManager{
-		ABCIListeners: []storetypes.ABCIListener{
-			&mockABCIListener{},
-		},
+	suite := NewBaseAppSuite(t, baseapp.SetHaltHeight(1), func(ba *baseapp.BaseApp) {
+		ba.SetStreamingManager(storetypes.StreamingManager{
+			ABCIListeners: []storetypes.ABCIListener{
+				&mockABCIListener{},
+			},
+		})
 	})
 
 	res, err := suite.baseApp.FinalizeBlock(&abci.FinalizeBlockRequest{
```
