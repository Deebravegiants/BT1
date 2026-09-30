# [?] Fix a data race in Basic Catchpoint Catchup Test

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2020-07-13
Source: https://github.com/algorand/go-algorand/commit/627f1089e1d3e94af2c52fe221b2e0ac6e30099c
Type: security-commit

## Details
Fix a data race in Basic Catchpoint Catchup Test

Fix a data race in Basic Catchpoint Catchup Test

## Patch
### test/e2e-go/features/catchup/catchpointCatchup_test.go
```diff
@@ -17,6 +17,7 @@
 package catchup
 
 import (
+	"fmt"
 	"net/http"
 	"os"
 	"os/exec"
@@ -26,6 +27,7 @@ import (
 	"testing"
 	"time"
 
+	"github.com/algorand/go-deadlock"
 	"github.com/stretchr/testify/require"
 
 	"github.com/algorand/go-algorand/config"
@@ -36,20 +38,45 @@ import (
 	"github.com/algorand/go-algorand/test/framework/fixtures"
 )
 
-func nodeExitWithError(t *testing.T, nc *nodecontrol.NodeController, err error) {
+type nodeExitErrorCollector struct {
+	errors   []error
+	messages []string
+	mu       deadlock.Mutex
+	t        *testing.T
+}
+
+func (ec *nodeExitErrorCollector) nodeExitWithError(nc *nodecontrol.NodeController, err error) {
 	if err == nil {
 		return
 	}
 
 	exitError, ok := err.(*exec.ExitError)
 	if !ok {
-		require.NoError(t, err, "Node at %s has terminated with an error", nc.GetDataDir())
+		if err != nil {
+			ec.mu.Lock()
+			ec.errors = append(ec.errors, err)
+			ec.messages = append(ec.messages, "Node at %s has terminated with an error", nc.GetDataDir())
+			ec.mu.Unlock()
+		}
 		return
 	}
 	ws := exitError.Sys().(syscall.WaitStatus)
 	exitCode := ws.ExitStatus()
 
-	require.NoError(t, err, "Node at %s has terminated with error code %d", nc.GetDataDir(), exitCode)
+	if err != nil {
+		ec.mu.Lock()
+		ec.errors = append(ec.errors, err)
+		ec.messages = append(ec.messages, fmt.Sprintf("Node at %s has terminated with error code %d", nc.GetDataDir(), exitCode))
+		ec.mu.Unlock()
+	}
+}
+
+func (ec *nodeExitErrorCollector) Print() {
+	ec.mu.Lock()
+	defer ec.mu.Unlock()
+	for i, err := range ec.errors {
+		require.NoError(ec.t, err, ec.messages[i])
+	}
 }
 
 func TestBasicCatchpointCatchup(t *testing.T) {
@@ -87,11 +114,14 @@ func TestBasicCatchpointCatchup(t *testing.T) {
 
 	var fixture fixtures.RestClientFixture
 	fixture.SetConsensus(consensus)
+
+	errorsCollector := nodeExitErrorCollector{t: t}
+	defer errorsCollector.Print()
+
 	// Give the second node (which starts up last) all the stake so that its proposal always has better credentials,
 	// and so that its proposal isn't dropped. Otherwise the test burns 17s to recover. We don't care about stake
 	// distribution for catchup so this is fine.
 	fixture.SetupNoStart(t, filepath.Join("nettemplates", "CatchpointCatchupTestNetwork.json"))
-	//defer fixture.Shutdown()
 
 	// Get primary node
 	primaryNode, err := fixture.GetNodeController("Primary")
@@ -118,7 +148,7 @@ func TestBasicCatchpointCatchup(t *testing.T) {
 		RedirectOutput:    true,
 		RunUnderHost:      false,
 		TelemetryOverride: "",
-		ExitErrorCallback: func(nc *nodecontrol.NodeController, err error) { nodeExitWithError(t, nc, err) },
+		ExitErrorCallback: errorsCollector.nodeExitWithError,
 	})
 	a.NoError(err)
 
@@ -160,7 +190,7 @@ func TestBasicCatchpointCatchup(t *testing.T) {
 		RedirectOutput:    true,
 		RunUnderHost:      false,
 		TelemetryOverride: "",
-		ExitErrorCallback: func(nc *nodecontrol.NodeController, err error) { nodeExitWithError(t, nc, err) },
+		ExitErrorCallback: errorsCollector.nodeExitWithError,
 	})
 	a.NoError(err)
 
```
