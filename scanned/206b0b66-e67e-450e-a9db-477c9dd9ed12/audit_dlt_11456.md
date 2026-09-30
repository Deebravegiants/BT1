# [?] Fix TestIntegration_VRF_WithBHS race condition (#9953)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-07-27
Source: https://github.com/smartcontractkit/ccip/commit/0922ee153cef13f539ba6813e4cc90969cb2e536
Type: security-commit

## Details
Fix TestIntegration_VRF_WithBHS race condition (#9953)

* Fix TestIntegration_VRF_WithBHS race condition

* Fix potential raciness in TestIntegration_VRF_JPV2

## Patch
### core/services/vrf/v1/integration_test.go
```diff
@@ -89,6 +89,10 @@ func TestIntegration_VRF_JPV2(t *testing.T) {
 			assert.NotNil(t, 0, runs[0].Outputs.Val)
 			assert.NotNil(t, 0, runs[1].Outputs.Val)
 
+			// stop jobs as to not cause a race condition in geth simulated backend
+			// between job creating new tx and fulfillment logs polling below
+			require.NoError(t, app.JobSpawner().DeleteJob(jb.ID))
+
 			// Ensure the eth transaction gets confirmed on chain.
 			gomega.NewWithT(t).Eventually(func() bool {
 				orm := txmgr.NewTxStore(app.GetSqlxDB(), app.GetLogger(), app.GetConfig().Database())
@@ -142,7 +146,7 @@ func TestIntegration_VRF_WithBHS(t *testing.T) {
 	sendingKeys := []string{key.Address.String()}
 
 	// Create BHS Job and start it
-	_ = vrftesthelpers.CreateAndStartBHSJob(t, sendingKeys, app, cu.BHSContractAddress.String(),
+	bhsJob := vrftesthelpers.CreateAndStartBHSJob(t, sendingKeys, app, cu.BHSContractAddress.String(),
 		cu.RootContractAddress.String(), "", "")
 
 	// Ensure log poller is ready and has all logs.
@@ -200,6 +204,11 @@ func TestIntegration_VRF_WithBHS(t *testing.T) {
 	assert.Equal(t, 4, len(runs[0].PipelineTaskRuns))
 	assert.NotNil(t, 0, runs[0].Outputs.Val)
 
+	// stop jobs as to not cause a race condition in geth simulated backend
+	// between job creating new tx and fulfillment logs polling below
+	require.NoError(t, app.JobSpawner().DeleteJob(jb.ID))
+	require.NoError(t, app.JobSpawner().DeleteJob(bhsJob.ID))
+
 	// Ensure the eth transaction gets confirmed on chain.
 	gomega.NewWithT(t).Eventually(func() bool {
 		orm := txmgr.NewTxStore(app.GetSqlxDB(), app.GetLogger(), app.GetConfig().Database())
```
