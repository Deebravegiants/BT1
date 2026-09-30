# [?] fix/non-determinism-in-ocr-happy-path-test (#21875)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-04-07
Source: https://github.com/smartcontractkit/chainlink/commit/779e0327048153d1398886b859b9dcabe9234fed
Type: security-commit

## Details
fix/non-determinism-in-ocr-happy-path-test (#21875)

## Patch
### core/cmd/shell_remote_test.go
```diff
@@ -549,9 +549,11 @@ func TestShell_ConfigV2(t *testing.T) {
 }
 
 func TestShell_RunOCRJob_HappyPath(t *testing.T) {
-	t.Parallel()
+	// Serial: full app + OCR + synchronous pipeline run; avoid parallel scheduling
+	// starving the test deadline and keep bridge traffic on local httptest only.
 	ctx := testutils.Context(t)
 	app := startNewApplicationV2(t, func(c *chainlink.Config, s *chainlink.Secrets) {
+		c.JobPipeline.HTTPRequest.DefaultTimeout = commonconfig.MustNewDuration(2 * time.Second)
 		c.EVM[0].Enabled = ptr(true)
 		c.OCR.Enabled = ptr(true)
 		c.P2P.V2.Enabled = ptr(true)
@@ -565,11 +567,18 @@ func TestShell_RunOCRJob_HappyPath(t *testing.T) {
 
 	require.NoError(t, app.KeyStore.OCR().Add(ctx, cltest.DefaultOCRKey))
 
-	_, bridge := cltest.MustCreateBridge(t, app.GetDB(), cltest.BridgeOpts{})
-	_, bridge2 := cltest.MustCreateBridge(t, app.GetDB(), cltest.BridgeOpts{})
+	// Local mock adapters only: TriggerPipelineRun executes the observation pipeline synchronously.
+	mockDS1 := cltest.NewHTTPMockServer(t, 200, "POST", `{"one":{"two": 10}}`)
+	mockDS2 := cltest.NewHTTPMockServer(t, 200, "POST", `{"three":{"four": 20}}`)
+	_, bridge := cltest.MustCreateBridge(t, app.GetDB(), cltest.BridgeOpts{URL: mockDS1.URL})
+	_, bridge2 := cltest.MustCreateBridge(t, app.GetDB(), cltest.BridgeOpts{URL: mockDS2.URL})
 
 	var jb job.Job
-	ocrspec := testspecs.GenerateOCRSpec(testspecs.OCRSpecParams{DS1BridgeName: bridge.Name.String(), DS2BridgeName: bridge2.Name.String()})
+	ocrspec := testspecs.GenerateOCRSpec(testspecs.OCRSpecParams{
+		DS1BridgeName: bridge.Name.String(),
+		DS2BridgeName: bridge2.Name.String(),
+		EVMChainID:    testutils.FixtureChainID.String(),
+	})
 	err := toml.Unmarshal([]byte(ocrspec.Toml()), &jb)
 	require.NoError(t, err)
 	var ocrSpec job.OCROracleSpec
```

### core/testdata/testspecs/v2_specs.go
```diff
@@ -608,7 +608,46 @@ func GenerateOCRSpec(params OCRSpecParams) OCRSpec {
 	if params.EVMChainID != "" {
 		evmChainID = params.EVMChainID
 	}
-	template := `
+
+	// When both bridge names are supplied by the caller, use bridges for both observation
+	// paths so tests that execute the pipeline do not depend on external HTTP (chain.link).
+	explicitBridgeDataSources := params.DS1BridgeName != "" && params.DS2BridgeName != ""
+	var observationBlock string
+	if explicitBridgeDataSources {
+		observationBlock = fmt.Sprintf(`    // data source 1
+    ds1          [type=bridge name="%s"];
+    ds1_parse    [type=jsonparse path="one,two"];
+    ds1_multiply [type=multiply times=1.23];
+
+    // data source 2
+    ds2          [type=bridge name="%s"];
+    ds2_parse    [type=jsonparse path="three,four"];
+    ds2_multiply [type=multiply times=4.56];
+
+    ds1 -> ds1_parse -> ds1_multiply -> answer1;
+    ds2 -> ds2_parse -> ds2_multiply -> answer1;
+
+    answer1 [type=median                      index=0];
+    answer2 [type=bridge name="%s" index=1];`, ds1BridgeName, ds2BridgeName, ds2BridgeName)
+	} else {
+		observationBlock = fmt.Sprintf(`    // data source 1
+    ds1          [type=bridge name="%s"];
+    ds1_parse    [type=jsonparse path="one,two"];
+    ds1_multiply [type=multiply times=1.23];
+
+    // data source 2
+    ds2          [type=http method=GET url="https://chain.link/voter_turnout/USA-2020" requestData="{\\"hi\\": \\"hello\\"}"];
+    ds2_parse    [type=jsonparse path="three,four"];
+    ds2_multiply [type=multiply times=4.56];
+
+    ds1 -> ds1_parse -> ds1_multiply -> answer1;
+    ds2 -> ds2_parse -> ds2_multiply -> answer1;
+
+    answer1 [type=median                      index=0];
+    answer2 [type=bridge name="%s" index=1];`, ds1BridgeName, ds2BridgeName)
+	}
+
+	header := `
 type               = "offchainreporting"
 schemaVersion      = 1
 name               = "%s"
@@ -627,21 +666,7 @@ contractConfigTrackerSubscribeInterval = "2m"
 contractConfigTrackerPollInterval = "1m"
 contractConfigConfirmations = 3
 observationSource = """
-    // data source 1
-    ds1          [type=bridge name="%s"];
-    ds1_parse    [type=jsonparse path="one,two"];
-    ds1_multiply [type=multiply times=1.23];
-
-    // data source 2
-    ds2          [type=http method=GET url="https://chain.link/voter_turnout/USA-2020" requestData="{\\"hi\\": \\"hello\\"}"];
-    ds2_parse    [type=jsonparse path="three,four"];
-    ds2_multiply [type=multiply times=4.56];
-
-    ds1 -> ds1_parse -> ds1_multiply -> answer1;
-    ds2 -> ds2_parse -> ds2_multiply -> answer1;
-
-    answer1 [type=median                      index=0];
-    answer2 [type=bridge name="%s" index=1];
+%s
 """
 `
 	return OCRSpec{OCRSpecParams: OCRSpecParams{
@@ -650,7 +675,7 @@ observationSource = """
 		TransmitterAddress: transmitterAddress,
 		DS1BridgeName:      ds1BridgeName,
 		DS2BridgeName:      ds2BridgeName,
-	}, toml: fmt.Sprintf(template, name, contractAddress, evmChainID, jobID, transmitterAddress, ds1BridgeName, ds2BridgeName)}
+	}, toml: fmt.Sprintf(header, name, contractAddress, evmChainID, jobID, transmitterAddress, observationBlock)}
 }
 
 type WebhookSpecParams struct {
```
