# [?] fix(abci): fix deadlock when response callback re-enters the client (#5850)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-12
Source: https://github.com/cometbft/cometbft/commit/2eeb81ae552dc8348f4c892fe33020808ef049da
Type: security-commit

## Details
fix(abci): fix deadlock when response callback re-enters the client (#5850)

`resCb` and `InvokeCallback` were called while holding `cli.mtx` in both
`socketClient` and `grpcClient`. Any callback that re-enters the client
(e.g. calls `Error()` or any ABCI method) would deadlock on the same
mutex.

Snapshot `cli.resCb` under the lock, then release the lock before
invoking
both `resCb` and `reqres.InvokeCallback()`. In `grpcClient` this also
eliminates the inner `callCb` closure, moving the unlock inline for
clarity.
Add `TestResponseCallbackNoDeadlock` and
`TestGRPCResponseCallbackNoDeadlock`
to prevent regression.

To run the tests:
  go test ./abci/client/... -run TestResponseCallbackNoDeadlock -race -v
go test ./abci/client/... -run TestGRPCResponseCallbackNoDeadlock -race
-v

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -33,6 +33,8 @@
   ([\#5839](https://github.com/cometbft/cometbft/pull/5839))
 - `[mempool]` fix setRecheckFull/setDone race causing spurious ErrRecheckFull.
   ([\#5837](https://github.com/cometbft/cometbft/pull/5837))
+- `[abci]` fix deadlock when response callback re-enters the client.
+  ([\#5850](https://github.com/cometbft/cometbft/pull/5850))
 - `[node]` close partial listeners on startRPC failure
   ([\#5869](https://github.com/cometbft/cometbft/pull/5869))
 - `[consensus]` release cs.mtx before sending to statsMsgQueue
```

### abci/client/grpc_client.go
```diff
@@ -61,28 +61,22 @@ func (cli *grpcClient) OnStart() error {
 	// This processes asynchronous request/response messages and dispatches
 	// them to callbacks.
 	go func() {
-		// Use a separate function to use defer for mutex unlocks (this handles panics)
-		callCb := func(reqres *ReqRes) {
-			cli.mtx.Lock()
-			defer cli.mtx.Unlock()
+		for reqres := range cli.chReqRes {
+			if reqres == nil {
+				cli.Logger.Error("Received nil reqres")
+				continue
+			}
 
+			cli.mtx.Lock()
 			reqres.Done()
+			resCb := cli.resCb
+			cli.mtx.Unlock()
 
-			// Notify client listener if set
-			if cli.resCb != nil {
-				cli.resCb(reqres.Request, reqres.Response)
+			if resCb != nil {
+				resCb(reqres.Request, reqres.Response)
 			}
-
-			// Notify reqRes listener if set
 			reqres.InvokeCallback()
 		}
-		for reqres := range cli.chReqRes {
-			if reqres != nil {
-				callCb(reqres)
-			} else {
-				cli.Logger.Error("Received nil reqres")
-			}
-		}
 	}()
 
 RETRY_LOOP:
```

### abci/client/grpc_client_test.go
```diff
@@ -2,20 +2,105 @@ package abcicli_test
 
 import (
 	"context"
+	"errors"
 	"fmt"
 	"math/rand"
 	"os"
+	"sync"
 	"testing"
+	"time"
 
 	"github.com/stretchr/testify/require"
 	"google.golang.org/grpc"
 	"google.golang.org/grpc/credentials/insecure"
 
+	abcicli "github.com/cometbft/cometbft/abci/client"
 	abciserver "github.com/cometbft/cometbft/abci/server"
 	"github.com/cometbft/cometbft/abci/types"
 	"github.com/cometbft/cometbft/libs/log"
 )
 
+func TestGRPCResponseCallbackNoDeadlock(t *testing.T) {
+	socketFile := fmt.Sprintf("/tmp/test-%08x.sock", rand.Int31n(1<<30))
+	defer os.Remove(socketFile)
+	socket := fmt.Sprintf("unix://%v", socketFile)
+
+	server := abciserver.NewGRPCServer(socket, types.NewBaseApplication())
+	server.SetLogger(log.TestingLogger().With("module", "abci-server"))
+	require.NoError(t, server.Start())
+	t.Cleanup(func() { _ = server.Stop() })
+
+	c := abcicli.NewGRPCClient(socket, true)
+	require.NoError(t, c.Start())
+	t.Cleanup(func() { _ = c.Stop() })
+
+	var once sync.Once
+	done := make(chan struct{})
+	c.SetResponseCallback(func(_ *types.Request, _ *types.Response) {
+		_ = c.Error() // re-enters cli.mtx; deadlocks without the fix
+		once.Do(func() { close(done) })
+	})
+
+	_, err := c.CheckTxAsync(context.Background(), &types.RequestCheckTx{})
+	require.NoError(t, err)
+
+	select {
+	case <-done:
+	case <-time.After(5 * time.Second):
+		t.Fatal("deadlock: response callback did not complete")
+	}
+}
+
+func TestGRPCResponseCallbackSeesErrorState(t *testing.T) {
+	socketFile := fmt.Sprintf("/tmp/test-%08x.sock", rand.Int31n(1<<30))
+	defer os.Remove(socketFile)
+	socket := fmt.Sprintf("unix://%v", socketFile)
+
+	server := abciserver.NewGRPCServer(socket, types.NewBaseApplication())
+	server.SetLogger(log.TestingLogger().With("module", "abci-server"))
+	require.NoError(t, server.Start())
+	t.Cleanup(func() { _ = server.Stop() })
+
+	c := abcicli.NewGRPCClient(socket, true)
+	require.NoError(t, c.Start())
+	t.Cleanup(func() { _ = c.Stop() })
+
+	inCallback := make(chan struct{})
+	proceed := make(chan struct{})
+	cbErrCh := make(chan error, 1)
+	var once sync.Once
+
+	c.SetResponseCallback(func(_ *types.Request, _ *types.Response) {
+		once.Do(func() {
+			close(inCallback)
+			<-proceed
+			cbErrCh <- c.Error()
+		})
+	})
+
+	_, err := c.CheckTxAsync(context.Background(), &types.RequestCheckTx{})
+	require.NoError(t, err)
+
+	select {
+	case <-inCallback:
+	case <-time.After(5 * time.Second):
+		t.Fatal("callback did not start")
+	}
+
+	type errorSetter interface{ StopForError(error) }
+	injected := errors.New("injected test error")
+	c.(errorSetter).StopForError(injected)
+
+	close(proceed)
+
+	select {
+	case cbErr := <-cbErrCh:
+		require.ErrorIs(t, cbErr, injected)
+	case <-time.After(5 * time.Second):
+		t.Fatal("callback did not complete")
+	}
+}
+
 func TestGRPC(t *testing.T) {
 	app := types.NewBaseApplication()
 	numCheckTxs := 2000
```

### abci/client/socket_client.go
```diff
@@ -138,15 +138,15 @@ func (cli *socketClient) sendRequestsRoutine(conn io.Writer) {
 
 			err := types.WriteMessage(reqres.Request, w)
 			if err != nil {
-				cli.stopForError(fmt.Errorf("write to buffer: %w", err))
+				cli.StopForError(fmt.Errorf("write to buffer: %w", err))
 				return
 			}
 
 			// If it's a flush request, flush the current buffer.
 			if _, ok := reqres.Request.Value.(*types.Request_Flush); ok {
 				err = w.Flush()
 				if err != nil {
-					cli.stopForError(fmt.Errorf("flush buffer: %w", err))
+					cli.StopForError(fmt.Errorf("flush buffer: %w", err))
 					return
 				}
 			}
@@ -172,19 +172,19 @@ func (cli *socketClient) recvResponseRoutine(conn io.Reader) {
 		res := &types.Response{}
 		err := types.ReadMessage(r, res)
 		if err != nil {
-			cli.stopForError(fmt.Errorf("read message: %w", err))
+			cli.StopForError(fmt.Errorf("read message: %w", err))
 			return
 		}
 
 		switch r := res.Value.(type) {
 		case *types.Response_Exception: // app responded with error
 			// XXX After setting cli.err, release waiters (e.g. reqres.Done())
-			cli.stopForError(errors.New(r.Exception.Error))
+			cli.StopForError(errors.New(r.Exception.Error))
 			return
 		default:
 			err := cli.didRecvResponse(res)
 			if err != nil {
-				cli.stopForError(err)
+				cli.StopForError(err)
 				return
 			}
 		}
@@ -205,26 +205,29 @@ func (cli *socketClient) trackRequest(reqres *ReqRes) {
 
 func (cli *socketClient) didRecvResponse(res *types.Response) error {
 	cli.mtx.Lock()
-	defer cli.mtx.Unlock()
 
 	// Get the first ReqRes.
 	next := cli.reqSent.Front()
 	if next == nil {
+		cli.mtx.Unlock()
 		return ErrUnexpectedResponse{Response: *res, Reason: "no call was made"}
 	}
 
 	reqres := next.Value.(*ReqRes)
 	if !resMatchesReq(reqres.Request, res) {
+		cli.mtx.Unlock()
 		return ErrUnexpectedResponse{Response: *res, Reason: fmt.Sprintf("unexpected response to the request %T", reqres.Request.Value)}
 	}
 
 	reqres.Response = res
 	reqres.Done()            // release waiters
 	cli.reqSent.Remove(next) // pop first item from linked list
+	resCb := cli.resCb
+	cli.mtx.Unlock()
 
 	// Notify client listener if set (global callback).
-	if cli.resCb != nil {
-		cli.resCb(reqres.Request, res)
+	if resCb != nil {
+		resCb(reqres.Request, res)
 	}
 
 	// Notify reqRes listener if set (request specific callback).
@@ -519,7 +522,7 @@ func resMatchesReq(req *types.Request, res *types.Response) (ok bool) {
 	return ok
 }
 
-func (cli *socketClient) stopForError(err error) {
+func (cli *socketClient) StopForError(err error) {
 	if !cli.IsRunning() {
 		return
 	}
```

### abci/client/socket_client_test.go
```diff
@@ -2,6 +2,7 @@ package abcicli_test
 
 import (
 	"context"
+	"errors"
 	"fmt"
 	"math/rand"
 	"os"
@@ -203,6 +204,67 @@ func (b blockedABCIApplication) CheckTxAsync(ctx context.Context, r *types.Reque
 	return b.CheckTx(ctx, r)
 }
 
+func TestResponseCallbackNoDeadlock(t *testing.T) {
+	ctx := t.Context()
+	_, c := setupClientServer(t, types.BaseApplication{})
+
+	var once sync.Once
+	done := make(chan struct{})
+	c.SetResponseCallback(func(_ *types.Request, _ *types.Response) {
+		_ = c.Error() // re-enters cli.mtx; deadlocks without the fix
+		once.Do(func() { close(done) })
+	})
+
+	_, err := c.CheckTxAsync(ctx, &types.RequestCheckTx{})
+	require.NoError(t, err)
+
+	select {
+	case <-done:
+	case <-time.After(5 * time.Second):
+		t.Fatal("deadlock: response callback did not complete")
+	}
+}
+
+func TestResponseCallbackSeesErrorState(t *testing.T) {
+	ctx := t.Context()
+	_, c := setupClientServer(t, types.BaseApplication{})
+
+	inCallback := make(chan struct{})
+	proceed := make(chan struct{})
+	cbErrCh := make(chan error, 1)
+	var once sync.Once
+
+	c.SetResponseCallback(func(_ *types.Request, _ *types.Response) {
+		once.Do(func() {
+			close(inCallback)
+			<-proceed
+			cbErrCh <- c.Error()
+		})
+	})
+
+	_, err := c.CheckTxAsync(ctx, &types.RequestCheckTx{})
+	require.NoError(t, err)
+
+	select {
+	case <-inCallback:
+	case <-time.After(5 * time.Second):
+		t.Fatal("callback did not start")
+	}
+
+	type errorSetter interface{ StopForError(error) }
+	injected := errors.New("injected test error")
+	c.(errorSetter).StopForError(injected)
+
+	close(proceed)
+
+	select {
+	case cbErr := <-cbErrCh:
+		require.ErrorIs(t, cbErr, injected)
+	case <-time.After(5 * time.Second):
+		t.Fatal("callback did not complete")
+	}
+}
+
 // TestCallbackInvokedWhenSetEarly ensures that the callback is invoked when
 // set before the client completes the call into the app.
 func TestCallbackInvokedWhenSetEarly(t *testing.T) {
```
