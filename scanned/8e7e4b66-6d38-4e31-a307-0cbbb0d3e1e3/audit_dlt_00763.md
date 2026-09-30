# [?] fix(abci): prevent panic on unlock in socket server panic recovery (#5593)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-04-24
Source: https://github.com/cometbft/cometbft/commit/320e79ef982a69a5e32ec98a49ef6b6db1ad9c4f
Type: security-commit

## Details
fix(abci): prevent panic on unlock in socket server panic recovery (#5593)

---

#### PR checklist
Fix a bug in handleRequests where the panic recovery defer function
would attempt to unlock appMtx even when the lock was never acquired.
- [x] Tests written/updated
- [x] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: Alex | Cosmos Labs <alex@cosmoslabs.io>
Co-authored-by: Dmitry S <11892559+swift1337@users.noreply.github.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -167,6 +167,8 @@
   ([\#4783](https://github.com/cometbft/cometbft/issues/4783))
 - `[cli]` Prevent inadvertent rollover of IPs in `cometbft testnet` config generator
   ([\#5541](https://github.com/cometbft/cometbft/pull/5541))
+- `[abci]` fix(abci): prevent panic on unlock in socket server panic recovery
+  ([\#5593](https://github.com/cometbft/cometbft/pull/5593))
 
 ### API-BREAKING
 
```

### abci/server/socket_server.go
```diff
@@ -163,6 +163,8 @@ func (s *SocketServer) waitForClose(closeConn chan error, connID int) {
 func (s *SocketServer) handleRequests(closeConn chan error, conn io.Reader, responses chan<- *types.Response) {
 	bufReader := bufio.NewReader(conn)
 
+	locked := false // true only while appMtx is held inside the loop
+
 	defer func() {
 		// make sure to recover from any app-related panics to allow proper socket cleanup.
 		// In the case of a panic, we do not notify the client by passing an exception so
@@ -177,6 +179,8 @@ func (s *SocketServer) handleRequests(closeConn chan error, conn io.Reader, resp
 				fmt.Fprintln(os.Stderr, err)
 			}
 			closeConn <- err
+		}
+		if locked {
 			s.appMtx.Unlock()
 		}
 	}()
@@ -194,6 +198,7 @@ func (s *SocketServer) handleRequests(closeConn chan error, conn io.Reader, resp
 			return
 		}
 		s.appMtx.Lock()
+		locked = true
 		resp, err := s.handleRequest(context.TODO(), req)
 		if err != nil {
 			// any error either from the application or because of an unknown request
@@ -204,6 +209,7 @@ func (s *SocketServer) handleRequests(closeConn chan error, conn io.Reader, resp
 			responses <- resp
 		}
 		s.appMtx.Unlock()
+		locked = false
 	}
 }
 
```

### abci/server/socket_server_test.go
```diff
@@ -0,0 +1,40 @@
+package server
+
+import (
+	"testing"
+	"time"
+
+	"github.com/cometbft/cometbft/abci/types"
+)
+
+type panicReader struct{}
+
+func (panicReader) Read(_ []byte) (int, error) {
+	panic("boom")
+}
+
+// TestHandleRequestsPanicBeforeLock ensures the panic recovery block does not
+// attempt to unlock appMtx when the lock was never acquired.
+func TestHandleRequestsPanicBeforeLock(t *testing.T) {
+	s := &SocketServer{}
+	closeConn := make(chan error, 1)
+	responses := make(chan *types.Response, 1)
+	done := make(chan struct{})
+
+	go func() {
+		defer close(done)
+		s.handleRequests(closeConn, panicReader{}, responses)
+	}()
+
+	select {
+	case <-closeConn:
+	case <-time.After(time.Second):
+		t.Fatal("closeConn not signaled")
+	}
+
+	select {
+	case <-done:
+	case <-time.After(time.Second):
+		t.Fatal("handleRequests did not exit")
+	}
+}
```
