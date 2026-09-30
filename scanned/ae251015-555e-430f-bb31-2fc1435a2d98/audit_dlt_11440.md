# [?] fix error scope to avoid data race (#13642)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-06-21
Source: https://github.com/smartcontractkit/ccip/commit/b584df5c4f99a9e2c8734959a40cf730bbb1435a
Type: security-commit

## Details
fix error scope to avoid data race (#13642)

* fix error scope to avoid data race

* fix another instance, and local scope other errors

* MERC-5697: reinstate test in CI

## Patch
### core/services/ocr2/plugins/mercury/integration_test.go
```diff
@@ -126,7 +126,6 @@ func setupBlockchain(t *testing.T) (*bind.TransactOpts, *backends.SimulatedBacke
 }
 
 func TestIntegration_MercuryV1(t *testing.T) {
-	testutils.SkipFlakey(t, "https://smartcontract-it.atlassian.net/browse/MERC-5697")
 	t.Parallel()
 
 	integration_MercuryV1(t)
@@ -228,22 +227,22 @@ func integration_MercuryV1(t *testing.T) {
 
 	createBridge := func(name string, i int, p *big.Int, borm bridges.ORM) (bridgeName string) {
 		bridge := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
-			b, err := io.ReadAll(req.Body)
-			require.NoError(t, err)
+			b, herr := io.ReadAll(req.Body)
+			require.NoError(t, herr)
 			require.Equal(t, `{"data":{"from":"ETH","to":"USD"}}`, string(b))
 
 			r := rand.Int63n(101)
 			if r > pError.Load() {
 				res.WriteHeader(http.StatusOK)
 				val := decimal.NewFromBigInt(p, 0).Div(decimal.NewFromInt(multiplier)).Add(decimal.NewFromInt(int64(i)).Div(decimal.NewFromInt(100))).String()
 				resp := fmt.Sprintf(`{"result": %s}`, val)
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			} else {
 				res.WriteHeader(http.StatusInternalServerError)
 				resp := `{"error": "pError test error"}`
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			}
 		}))
 		t.Cleanup(bridge.Close)
@@ -330,7 +329,7 @@ func integration_MercuryV1(t *testing.T) {
 			"offchainConfig", offchainConfig,
 		)
 
-		_, err = verifier.SetConfig(
+		_, ferr := verifier.SetConfig(
 			steve,
 			feed.id,
 			signerAddresses,
@@ -341,7 +340,7 @@ func integration_MercuryV1(t *testing.T) {
 			offchainConfig,
 			nil,
 		)
-		require.NoError(t, err)
+		require.NoError(t, ferr)
 		backend.Commit()
 	}
 
@@ -582,23 +581,22 @@ func integration_MercuryV2(t *testing.T) {
 
 	createBridge := func(name string, i int, p *big.Int, borm bridges.ORM) (bridgeName string) {
 		bridge := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
-			var b []byte
-			b, err = io.ReadAll(req.Body)
-			require.NoError(t, err)
+			b, herr := io.ReadAll(req.Body)
+			require.NoError(t, herr)
 			require.Equal(t, `{"data":{"from":"ETH","to":"USD"}}`, string(b))
 
 			r := rand.Int63n(101)
 			if r > pError.Load() {
 				res.WriteHeader(http.StatusOK)
 				val := decimal.NewFromBigInt(p, 0).Div(decimal.NewFromInt(multiplier)).Add(decimal.NewFromInt(int64(i)).Div(decimal.NewFromInt(100))).String()
 				resp := fmt.Sprintf(`{"result": %s}`, val)
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			} else {
 				res.WriteHeader(http.StatusInternalServerError)
 				resp := `{"error": "pError test error"}`
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			}
 		}))
 		t.Cleanup(bridge.Close)
@@ -670,7 +668,7 @@ func integration_MercuryV2(t *testing.T) {
 	}
 
 	for _, feed := range feeds {
-		_, err = verifier.SetConfig(
+		_, ferr := verifier.SetConfig(
 			steve,
 			feed.id,
 			signerAddresses,
@@ -681,7 +679,7 @@ func integration_MercuryV2(t *testing.T) {
 			offchainConfig,
 			nil,
 		)
-		require.NoError(t, err)
+		require.NoError(t, ferr)
 		backend.Commit()
 	}
 
@@ -872,23 +870,22 @@ func integration_MercuryV3(t *testing.T) {
 
 	createBridge := func(name string, i int, p *big.Int, borm bridges.ORM) (bridgeName string) {
 		bridge := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
-			var b []byte
-			b, err = io.ReadAll(req.Body)
-			require.NoError(t, err)
+			b, herr := io.ReadAll(req.Body)
+			require.NoError(t, herr)
 			require.Equal(t, `{"data":{"from":"ETH","to":"USD"}}`, string(b))
 
 			r := rand.Int63n(101)
 			if r > pError.Load() {
 				res.WriteHeader(http.StatusOK)
 				val := decimal.NewFromBigInt(p, 0).Div(decimal.NewFromInt(multiplier)).Add(decimal.NewFromInt(int64(i)).Div(decimal.NewFromInt(100))).String()
 				resp := fmt.Sprintf(`{"result": %s}`, val)
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			} else {
 				res.WriteHeader(http.StatusInternalServerError)
 				resp := `{"error": "pError test error"}`
-				_, err = res.Write([]byte(resp))
-				require.NoError(t, err)
+				_, herr = res.Write([]byte(resp))
+				require.NoError(t, herr)
 			}
 		}))
 		t.Cleanup(bridge.Close)
@@ -963,7 +960,7 @@ func integration_MercuryV3(t *testing.T) {
 	}
 
 	for _, feed := range feeds {
-		_, err = verifier.SetConfig(
+		_, ferr := verifier.SetConfig(
 			steve,
 			feed.id,
 			signerAddresses,
@@ -974,7 +971,7 @@ func integration_MercuryV3(t *testing.T) {
 			offchainConfig,
 			nil,
 		)
-		require.NoError(t, err)
+		require.NoError(t, ferr)
 		backend.Commit()
 	}
 
```
