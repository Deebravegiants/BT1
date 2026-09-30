# [?] fix(bug): fix data race in common/cmd module. (#220)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2023-01-11
Source: https://github.com/scroll-tech/scroll/commit/a44956a05fc6cd7675b6165af3f9a6c90c25b17a
Type: security-commit

## Details
fix(bug): fix data race in common/cmd module. (#220)

## Patch
### bridge/cmd/app/app_test.go
```diff
@@ -15,5 +15,5 @@ func TestRunBridge(t *testing.T) {
 
 	// wait result
 	bridge.ExpectWithTimeout(true, time.Second*3, fmt.Sprintf("bridge version %s", version.Version))
-	bridge.RunApp(false)
+	bridge.RunApp(nil)
 }
```

### common/cmd/cmd.go
```diff
@@ -1,17 +1,13 @@
 package cmd
 
 import (
-	"fmt"
 	"os"
 	"os/exec"
 	"strings"
 	"sync"
 	"testing"
-	"time"
 
-	"github.com/docker/docker/pkg/reexec"
 	cmap "github.com/orcaman/concurrent-map"
-	"github.com/stretchr/testify/assert"
 )
 
 var verbose bool
@@ -51,48 +47,6 @@ func NewCmd(t *testing.T, name string, args ...string) *Cmd {
 	}
 }
 
-// RunApp exec's the current binary using name as argv[0] which will trigger the
-// reexec init function for that name (e.g. "geth-test" in cmd/geth/run_test.go)
-func (t *Cmd) RunApp(parallel bool) {
-	t.Log("cmd: ", append([]string{t.name}, t.args...))
-	cmd := &exec.Cmd{
-		Path:   reexec.Self(),
-		Args:   append([]string{t.name}, t.args...),
-		Stderr: t,
-		Stdout: t,
-	}
-	if parallel {
-		go func() {
-			_ = cmd.Run()
-		}()
-	} else {
-		_ = cmd.Run()
-	}
-	t.mu.Lock()
-	t.cmd = cmd
-	t.mu.Unlock()
-}
-
-// WaitExit wait util process exit.
-func (t *Cmd) WaitExit() {
-	// Wait all the check funcs are finished or test status is failed.
-	for !(t.Failed() || t.checkFuncs.IsEmpty()) {
-		<-time.After(time.Millisecond * 500)
-	}
-
-	// Send interrupt signal.
-	t.mu.Lock()
-	_ = t.cmd.Process.Signal(os.Interrupt)
-	t.mu.Unlock()
-}
-
-// Interrupt send interrupt signal.
-func (t *Cmd) Interrupt() {
-	t.mu.Lock()
-	t.Err = t.cmd.Process.Signal(os.Interrupt)
-	t.mu.Unlock()
-}
-
 // RegistFunc register check func
 func (t *Cmd) RegistFunc(key string, check checkFunc) {
 	t.checkFuncs.Set(key, check)
@@ -103,39 +57,6 @@ func (t *Cmd) UnRegistFunc(key string) {
 	t.checkFuncs.Pop(key)
 }
 
-// ExpectWithTimeout wait result during timeout time.
-func (t *Cmd) ExpectWithTimeout(parallel bool, timeout time.Duration, keyword string) {
-	if keyword == "" {
-		return
-	}
-	okCh := make(chan struct{}, 1)
-	t.RegistFunc(keyword, func(buf string) {
-		if strings.Contains(buf, keyword) {
-			select {
-			case okCh <- struct{}{}:
-			default:
-				return
-			}
-		}
-	})
-
-	waitResult := func() {
-		defer t.UnRegistFunc(keyword)
-		select {
-		case <-okCh:
-			return
-		case <-time.After(timeout):
-			assert.Fail(t, fmt.Sprintf("didn't get the desired result before timeout, keyword: %s", keyword))
-		}
-	}
-
-	if parallel {
-		go waitResult()
-	} else {
-		waitResult()
-	}
-}
-
 func (t *Cmd) runCmd() {
 	cmd := exec.Command(t.args[0], t.args[1:]...) //nolint:gosec
 	cmd.Stdout = t
```

### common/cmd/cmd_app.go
```diff
@@ -0,0 +1,114 @@
+package cmd
+
+import (
+	"fmt"
+	"os"
+	"os/exec"
+	"strings"
+	"time"
+
+	"github.com/docker/docker/pkg/reexec"
+	"github.com/stretchr/testify/assert"
+)
+
+// RunApp exec's the current binary using name as argv[0] which will trigger the
+// reexec init function for that name (e.g. "geth-test" in cmd/geth/run_test.go)
+func (t *Cmd) RunApp(waitResult func() bool) {
+	t.Log("cmd: ", append([]string{t.name}, t.args...))
+	cmd := &exec.Cmd{
+		Path:   reexec.Self(),
+		Args:   append([]string{t.name}, t.args...),
+		Stderr: t,
+		Stdout: t,
+	}
+	if waitResult != nil {
+		go func() {
+			_ = cmd.Run()
+		}()
+		waitResult()
+	} else {
+		_ = cmd.Run()
+	}
+
+	t.mu.Lock()
+	t.cmd = cmd
+	t.mu.Unlock()
+}
+
+// WaitExit wait util process exit.
+func (t *Cmd) WaitExit() {
+	// Wait all the check funcs are finished or test status is failed.
+	for !(t.Failed() || t.checkFuncs.IsEmpty()) {
+		<-time.After(time.Millisecond * 500)
+	}
+
+	// Send interrupt signal.
+	t.mu.Lock()
+	_ = t.cmd.Process.Signal(os.Interrupt)
+	t.mu.Unlock()
+}
+
+// Interrupt send interrupt signal.
+func (t *Cmd) Interrupt() {
+	t.mu.Lock()
+	t.Err = t.cmd.Process.Signal(os.Interrupt)
+	t.mu.Unlock()
+}
+
+// WaitResult return true when get the keyword during timeout.
+func (t *Cmd) WaitResult(timeout time.Duration, keyword string) bool {
+	if keyword == "" {
+		return false
+	}
+	okCh := make(chan struct{}, 1)
+	t.RegistFunc(keyword, func(buf string) {
+		if strings.Contains(buf, keyword) {
+			select {
+			case okCh <- struct{}{}:
+			default:
+				return
+			}
+		}
+	})
+	defer t.UnRegistFunc(keyword)
+	select {
+	case <-okCh:
+		return true
+	case <-time.After(timeout):
+		assert.Fail(t, fmt.Sprintf("didn't get the desired result before timeout, keyword: %s", keyword))
+	}
+	return false
+}
+
+// ExpectWithTimeout wait result during timeout time.
+func (t *Cmd) ExpectWithTimeout(parallel bool, timeout time.Duration, keyword string) {
+	if keyword == "" {
+		return
+	}
+	okCh := make(chan struct{}, 1)
+	t.RegistFunc(keyword, func(buf string) {
+		if strings.Contains(buf, keyword) {
+			select {
+			case okCh <- struct{}{}:
+			default:
+				return
+			}
+		}
+	})
+
+	waitResult := func() {
+		defer t.UnRegistFunc(keyword)
+		select {
+		case <-okCh:
+			return
+		case <-time.After(timeout):
+			assert.Fail(t, fmt.Sprintf("didn't get the desired result before timeout, keyword: %s", keyword))
+		}
+	}
+
+	if parallel {
+		go waitResult()
+	} else {
+		waitResult()
+	}
+}
```

### coordinator/cmd/app/app_test.go
```diff
@@ -15,5 +15,5 @@ func TestRunCoordinator(t *testing.T) {
 
 	// wait result
 	coordinator.ExpectWithTimeout(true, time.Second*3, fmt.Sprintf("coordinator version %s", version.Version))
-	coordinator.RunApp(false)
+	coordinator.RunApp(nil)
 }
```

### database/cmd/app/app_test.go
```diff
@@ -15,5 +15,5 @@ func TestRunDatabase(t *testing.T) {
 
 	// wait result
 	bridge.ExpectWithTimeout(true, time.Second*3, fmt.Sprintf("db_cli version %s", version.Version))
-	bridge.RunApp(false)
+	bridge.RunApp(nil)
 }
```

### roller/cmd/app/app_test.go
```diff
@@ -15,5 +15,5 @@ func TestRunRoller(t *testing.T) {
 
 	// wait result
 	roller.ExpectWithTimeout(true, time.Second*3, fmt.Sprintf("roller version %s", version.Version))
-	roller.RunApp(false)
+	roller.RunApp(nil)
 }
```

### tests/integration-test/common.go
```diff
@@ -80,7 +80,8 @@ func free(t *testing.T) {
 }
 
 type appAPI interface {
-	RunApp(parallel bool)
+	WaitResult(timeout time.Duration, keyword string) bool
+	RunApp(waitResult func() bool)
 	WaitExit()
 	ExpectWithTimeout(parallel bool, timeout time.Duration, keyword string)
 }
@@ -103,7 +104,7 @@ func runDBCliApp(t *testing.T, option, keyword string) {
 
 	// Wait expect result.
 	app.ExpectWithTimeout(true, time.Second*3, keyword)
-	app.RunApp(false)
+	app.RunApp(nil)
 }
 
 func runRollerApp(t *testing.T, args ...string) appAPI {
```

### tests/integration-test/integration_test.go
```diff
@@ -28,19 +28,16 @@ func testStartProcess(t *testing.T) {
 
 	// Start bridge process.
 	bridgeCmd := runBridgeApp(t)
-	bridgeCmd.ExpectWithTimeout(true, time.Second*20, "Start bridge successfully")
-	bridgeCmd.RunApp(true)
+	bridgeCmd.RunApp(func() bool { return bridgeCmd.WaitResult(time.Second*20, "Start bridge successfully") })
 
 	// Start coordinator process.
 	coordinatorCmd := runCoordinatorApp(t, "--ws", "--ws.port", "8391")
-	coordinatorCmd.ExpectWithTimeout(true, time.Second*20, "Start coordinator successfully")
-	coordinatorCmd.RunApp(true)
+	coordinatorCmd.RunApp(func() bool { return coordinatorCmd.WaitResult(time.Second*20, "Start coordinator successfully") })
 
 	// Start roller process.
 	rollerCmd := runRollerApp(t)
-	rollerCmd.ExpectWithTimeout(true, time.Second*40, "roller start successfully")
 	rollerCmd.ExpectWithTimeout(true, time.Second*60, "register to coordinator successfully!")
-	rollerCmd.RunApp(true)
+	rollerCmd.RunApp(func() bool { return rollerCmd.WaitResult(time.Second*40, "roller start successfully") })
 
 	rollerCmd.WaitExit()
 	bridgeCmd.WaitExit()
```
