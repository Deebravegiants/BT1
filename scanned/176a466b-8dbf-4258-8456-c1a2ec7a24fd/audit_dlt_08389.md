# [?] fix(test): avoid panic of SetStreamingManager() on sealed BaseApp (backport #24109) (#24110)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-03-24
Source: https://github.com/cosmos/cosmos-sdk/commit/ddce50f42e416a389c48ca5b48a7a2868810ff33
Type: security-commit

## Details
fix(test): avoid panic of SetStreamingManager() on sealed BaseApp (backport #24109) (#24110)

Co-authored-by: mmsqe <mavis@crypto.com>

## Patch
### baseapp/abci_test.go
```diff
@@ -2509,11 +2509,12 @@ func TestABCI_Proposal_FailReCheckTx(t *testing.T) {
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
 
 	res, err := suite.baseApp.FinalizeBlock(&abci.RequestFinalizeBlock{
```
