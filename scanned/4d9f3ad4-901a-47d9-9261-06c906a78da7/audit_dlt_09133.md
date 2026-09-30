# [?] cre-4300: fix panic masking and error handling in CCIP load tests (#22409)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-05-12
Source: https://github.com/smartcontractkit/chainlink/commit/6779d66b26876f03a6f3bcc83971861826c53098
Type: security-commit

## Details
cre-4300: fix panic masking and error handling in CCIP load tests (#22409)

## Patch
### integration-tests/load/ccip/ccip_chaos_test.go
```diff
@@ -10,6 +10,7 @@ import (
 	"github.com/rs/zerolog"
 	"github.com/rs/zerolog/log"
 	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
 
 	"github.com/smartcontractkit/chainlink-testing-framework/framework"
 	"github.com/smartcontractkit/chainlink-testing-framework/framework/rpc"
@@ -35,15 +36,16 @@ func a(ns, text string, dashboardUIDs []string, from, to *time.Time) framework.A
 }
 
 func prepareChaos(t *testing.T) (*ccip.Config, *havoc.NamespaceScopedChaosRunner, *framework.GrafanaClient) {
+	t.Helper()
 	l := log.Output(zerolog.ConsoleWriter{Out: os.Stderr}).Level(zerolog.DebugLevel)
 	c, err := havoc.NewChaosMeshClient()
 	if err != nil {
-		t.Error("Failed to create chaos mesh client", err)
+		t.Fatalf("Failed to create chaos mesh client: %v", err)
 	}
 
 	config, err := tc.GetConfig([]string{"Load"}, tc.CCIP)
 	if err != nil {
-		t.Error("Failed to get config", err)
+		t.Fatalf("Failed to get config: %v", err)
 	}
 	cfg := config.CCIP
 	cr := havoc.NewNamespaceRunner(l, c, false)
@@ -108,10 +110,12 @@ type cribNetworkConfig []struct {
 }
 
 func readCRIBConfig(t *testing.T, cfg *ccip.Config) cribNetworkConfig {
-	f, _ := os.ReadFile(*cfg.Load.CribEnvDirectory + "/ccip-v2-scripts-chains-details.json")
+	t.Helper()
+	f, err := os.ReadFile(*cfg.Load.CribEnvDirectory + "/ccip-v2-scripts-chains-details.json")
+	require.NoError(t, err, "Failed to read CRIB config file")
 	var cribConfig cribNetworkConfig
-	err := json.Unmarshal(f, &cribConfig)
-	assert.NoError(t, err)
+	err = json.Unmarshal(f, &cribConfig)
+	require.NoError(t, err, "Failed to unmarshal CRIB config")
 	return cribConfig
 }
 
```

### integration-tests/load/ccip/ccip_test.go
```diff
@@ -50,21 +50,23 @@ const (
 	aptosTestKey    = "0x906b8a983b434318ca67b7eff7300f91b02744c84f87d243d2fbc3e528414366"
 )
 
-func runSafely(ops ...func()) {
+func runSafely(ops ...func()) (errs []error) {
 	for _, op := range ops {
 		func() {
 			defer func() {
 				if r := recover(); r != nil {
-					fmt.Printf("Recovered from panic: %v\n", r)
+					errs = append(errs, fmt.Errorf("panic recovered: %v", r))
 				}
 			}()
 			op()
 		}()
 	}
+	return
 }
 
-func SetProgramIDsSafe(state solState.CCIPChainState) {
-	runSafely(
+func SetProgramIDsSafe(t *testing.T, state solState.CCIPChainState) {
+	t.Helper()
+	errs := runSafely(
 		func() {
 			ccip_router.SetProgramID(state.Router)
 		},
@@ -85,6 +87,7 @@ func SetProgramIDsSafe(state solState.CCIPChainState) {
 			}
 		},
 	)
+	require.Empty(t, errs, "SetProgramID operations failed")
 }
 
 // step 1: setup
@@ -157,7 +160,7 @@ func TestCCIPLoad_RPS(t *testing.T) {
 	require.NoError(t, err)
 
 	for chainSel := range state.SolChains {
-		SetProgramIDsSafe(state.SolChains[chainSel])
+		SetProgramIDsSafe(t, state.SolChains[chainSel])
 		err := prepSolAccount(
 			ctx,
 			t,
```
