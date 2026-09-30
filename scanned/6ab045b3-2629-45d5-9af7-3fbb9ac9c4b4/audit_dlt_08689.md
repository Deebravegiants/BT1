# [?] Merge pull request #4604 from OffchainLabs/fix/stopwaiter-rlock-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-04-09
Source: https://github.com/OffchainLabs/nitro/commit/5cb076303609b2661b36f63378682e6c722abb99
Type: security-commit

## Details
Merge pull request #4604 from OffchainLabs/fix/stopwaiter-rlock-deadlock

fix: release RLock before waitChan in stopAndWaitImpl to prevent deadlock

## Patch
### changelog/jcolvin-fix-stopwaiter-deadlock.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+- Fix deadlock in `StopWaiterSafe.stopAndWaitImpl` by releasing `RLock` before blocking on `waitChan`.
```

### util/stopwaiter/stopwaiter.go
```diff
@@ -8,6 +8,7 @@ import (
 	"errors"
 	"reflect"
 	"runtime"
+	"runtime/debug"
 	"strings"
 	"sync"
 	"time"
@@ -175,8 +176,9 @@ func (s *StopWaiterSafe) stopAndWaitImpl(warningTimeout time.Duration) error {
 	case <-timer.C:
 		traces := getAllStackTraces()
 		st := s.RLock()
-		defer s.RUnlock()
-		log.Warn("taking too long to stop", "name", st.Name, "delay[s]", warningTimeout.Seconds())
+		name := st.Name
+		s.RUnlock()
+		log.Warn("taking too long to stop", "name", name, "delay[s]", warningTimeout.Seconds())
 		log.Warn(traces)
 	case <-waitChan:
 		timer.Stop()
@@ -220,7 +222,7 @@ func (s *StopWaiterSafe) LaunchThreadSafe(foo func(context.Context)) error {
 	s.wg.Go(func() {
 		defer func() {
 			if r := recover(); r != nil {
-				log.Error("Thread crashed", "name", name, "message", r)
+				log.Error("Thread crashed", "name", name, "message", r, "stack", string(debug.Stack()))
 			}
 		}()
 		foo(ctx)
```

### util/stopwaiter/stopwaiter_test.go
```diff
@@ -339,6 +339,73 @@ func TestStopOnlyThenStopAndWaitIndependentGoroutine(t *testing.T) {
 	}
 }
 
+// Before the fix, stopAndWaitImpl held an RLock across <-waitChan, so any
+// goroutine that needed the write lock (StopOnly or StopAndWait) would deadlock.
+func TestStopAndWaitNoDeadlockWhenGoroutineNeedsLock(t *testing.T) {
+	t.Parallel()
+	for _, tc := range []struct {
+		name   string
+		stopFn func(*StopWaiter)
+	}{
+		{"StopOnly", (*StopWaiter).StopOnly},
+		{"StopAndWait", (*StopWaiter).StopAndWait},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			t.Parallel()
+			parent := StopWaiter{}
+			parent.Start(context.Background(), &TestStruct{})
+
+			child := StopWaiter{}
+			child.Start(parent.GetContext(), &TestStruct{})
+			parent.TrackChild(&child)
+
+			stopFn := tc.stopFn
+			parent.LaunchThread(func(ctx context.Context) {
+				time.Sleep(testStopDelayWarningTimeout + 200*time.Millisecond)
+				stopFn(&child)
+			})
+
+			done := make(chan struct{})
+			var stopErr error
+			go func() {
+				stopErr = parent.stopAndWaitImpl(testStopDelayWarningTimeout)
+				close(done)
+			}()
+
+			select {
+			case <-done:
+				if stopErr != nil {
+					t.Errorf("stopAndWaitImpl returned unexpected error: %v", stopErr)
+				}
+			case <-time.After(5 * time.Second):
+				t.Fatalf("stopAndWaitImpl deadlocked: goroutine calling %s could not acquire lock", tc.name)
+			}
+		})
+	}
+}
+
+func TestLaunchThreadSafePanicRecovery(t *testing.T) {
+	logHandler := testhelpers.InitTestLog(t, log.LvlTrace)
+	sw := StopWaiter{}
+	sw.Start(context.Background(), &TestStruct{})
+
+	sw.LaunchThread(func(ctx context.Context) {
+		panic("test panic message")
+	})
+
+	sw.StopAndWait()
+
+	if !logHandler.WasLogged("Thread crashed") {
+		t.Error("expected 'Thread crashed' log entry after panicking goroutine")
+	}
+	if !logHandler.WasLoggedWithAttr("Thread crashed", "message", "test panic message") {
+		t.Error("expected panic message in 'Thread crashed' log entry")
+	}
+	if !logHandler.WasLoggedWithAttr("Thread crashed", "stack", "stopwaiter_test.go") {
+		t.Error("expected stack trace in 'Thread crashed' log entry")
+	}
+}
+
 func TestStopOnlyThenStopAndWaitWaitsForChildGoroutines(t *testing.T) {
 	t.Parallel()
 	parent := StopWaiter{}
```

### util/testhelpers/testhelpers.go
```diff
@@ -12,6 +12,7 @@ import (
 	"os"
 	"regexp"
 	"runtime/debug"
+	"strings"
 	"sync"
 	"testing"
 
@@ -136,6 +137,32 @@ func (h *LogHandler) wasLoggedWithFilter(pattern string, lvl *slog.Level) bool {
 	return false
 }
 
+// WasLoggedWithAttr checks whether a log record matching msgPattern has an
+// attribute whose key equals attrKey and whose string value contains attrSubstr.
+func (h *LogHandler) WasLoggedWithAttr(msgPattern, attrKey, attrSubstr string) bool {
+	msgRe, err := regexp.Compile(msgPattern)
+	RequireImpl(h.t, err)
+	h.mutex.Lock()
+	defer h.mutex.Unlock()
+	for _, record := range h.records {
+		if !msgRe.MatchString(record.Message) {
+			continue
+		}
+		found := false
+		record.Attrs(func(a slog.Attr) bool {
+			if a.Key == attrKey && strings.Contains(a.Value.String(), attrSubstr) {
+				found = true
+				return false
+			}
+			return true
+		})
+		if found {
+			return true
+		}
+	}
+	return false
+}
+
 func newLogHandler(t *testing.T) *LogHandler {
 	return &LogHandler{
 		t:               t,
```
