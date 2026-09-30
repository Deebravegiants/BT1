# [?] fix(mempool): panic when the app returns error on CheckTx request (#2894)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-04-26
Source: https://github.com/cometbft/cometbft/commit/98983fc64308843e07282f82b72e6b82fff7a573
Type: security-commit

## Details
fix(mempool): panic when the app returns error on CheckTx request (#2894)

Closes #2225

If the app returns an error on an ABCI call (in particular CheckTx),
CometBFT should stop, because the error is unrecoverable.

---

#### PR checklist

- [X] Tests written/updated
- [X] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [X] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

## Patch
### .changelog/unreleased/bug-fixes/2225-fix-checktx-request-returns-error.md
```diff
@@ -0,0 +1,2 @@
+- [`mempool`] Panic when a CheckTx request to the app returns an error
+  ([\#2225](https://github.com/cometbft/cometbft/pull/2225))
```

### mempool/clist_mempool.go
```diff
@@ -278,22 +278,19 @@ func (mem *CListMempool) CheckTx(tx types.Tx) (*abcicli.ReqRes, error) {
 	}
 
 	if added := mem.addToCache(tx); !added {
-		mem.logger.Debug("Not cached", "tx", tx.Hash())
 		mem.metrics.AlreadyReceivedTxs.Add(1)
 		// TODO: consider punishing peer for dups,
 		// its non-trivial since invalid txs can become valid,
 		// but they can spam the same tx with little cost to them atm.
 		return nil, ErrTxInCache
 	}
-	mem.logger.Debug("Cached", "tx", tx.Hash())
 
 	reqRes, err := mem.proxyAppConn.CheckTxAsync(context.TODO(), &abci.CheckTxRequest{
 		Tx:   tx,
 		Type: abci.CHECK_TX_TYPE_CHECK,
 	})
 	if err != nil {
-		mem.logger.Error("RequestCheckTx", "err", err)
-		return nil, ErrCheckTxAsync{Err: err}
+		panic(fmt.Errorf("CheckTx request for tx %s failed: %w", log.NewLazySprintf("%v", tx.Hash()), err))
 	}
 
 	return reqRes, nil
@@ -666,8 +663,7 @@ func (mem *CListMempool) recheckTxs() {
 			Type: abci.CHECK_TX_TYPE_RECHECK,
 		})
 		if err != nil {
-			mem.logger.Error("recheckTx", "err", err)
-			return
+			panic(fmt.Errorf("(re-)CheckTx request for tx %s failed: %w", log.NewLazySprintf("%v", memTx.tx.Hash()), err))
 		}
 	}
 
```

### mempool/clist_mempool_test.go
```diff
@@ -3,6 +3,7 @@ package mempool
 import (
 	"context"
 	"encoding/binary"
+	"errors"
 	"fmt"
 	mrand "math/rand"
 	"os"
@@ -805,6 +806,76 @@ func TestMempoolNotifyTxsAvailable(t *testing.T) {
 	require.False(t, mp.notifiedTxsAvailable.Load())
 }
 
+// Test that adding a transaction panics when the CheckTx request fails.
+func TestMempoolSyncCheckTxReturnError(t *testing.T) {
+	mockClient := new(abciclimocks.Client)
+	mockClient.On("Start").Return(nil)
+	mockClient.On("SetLogger", mock.Anything)
+	mockClient.On("SetResponseCallback", mock.Anything)
+
+	mp, cleanup := newMempoolWithAppMock(mockClient)
+	defer cleanup()
+
+	// The app will return an error on a CheckTx request.
+	tx := []byte{0x01}
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, errors.New("")).Once()
+
+	// Adding the transaction should panic when the call to the app returns an error.
+	defer func() {
+		if r := recover(); r == nil {
+			t.Errorf("CheckTx did not panic")
+		}
+	}()
+	_, err := mp.CheckTx(tx)
+	require.NoError(t, err)
+}
+
+// Test that rechecking panics when a CheckTx request fails, when using a sync ABCI client.
+func TestMempoolSyncRecheckTxReturnError(t *testing.T) {
+	var callback abciclient.Callback
+	mockClient := new(abciclimocks.Client)
+	mockClient.On("Start").Return(nil)
+	mockClient.On("SetLogger", mock.Anything)
+	mockClient.On("SetResponseCallback", mock.MatchedBy(func(cb abciclient.Callback) bool { callback = cb; return true }))
+
+	mp, cleanup := newMempoolWithAppMock(mockClient)
+	defer cleanup()
+
+	// First we add a two transactions to the mempool.
+	txs := []types.Tx{[]byte{0x01}, []byte{0x02}}
+	for _, tx := range txs {
+		// Mock a sync client, which will call the callback just after the response from the app.
+		mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
+			req := args.Get(1).(*abci.CheckTxRequest)
+			reqRes := newReqRes(req.Tx, abci.CodeTypeOK, abci.CHECK_TX_TYPE_CHECK)
+			callback(reqRes.Request, reqRes.Response)
+		}).Return(nil, nil).Once()
+		mockClient.On("Error").Return(nil)
+
+		_, err := mp.CheckTx(tx)
+		require.NoError(t, err)
+	}
+	require.Len(t, txs, mp.Size())
+
+	// The first tx is valid when rechecking and the client will call the callback right after the
+	// response from the app and before returning.
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Run(func(_ mock.Arguments) {
+		reqRes := newReqRes(txs[0], abci.CodeTypeOK, abci.CHECK_TX_TYPE_RECHECK)
+		callback(reqRes.Request, reqRes.Response)
+	}).Return(nil, nil).Once()
+
+	// On the second CheckTx request, the app returns an error.
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, errors.New("")).Once()
+
+	// Rechecking should panic when the call to the app returns an error.
+	defer func() {
+		if r := recover(); r == nil {
+			t.Errorf("recheckTxs did not panic")
+		}
+	}()
+	mp.recheckTxs()
+}
+
 // caller must close server.
 func newRemoteApp(t *testing.T, addr string, app abci.Application) service.Service {
 	t.Helper()
@@ -821,7 +892,7 @@ func newRemoteApp(t *testing.T, addr string, app abci.Application) service.Servi
 	return server
 }
 
-func newReqRes(tx types.Tx, code uint32, requestType abci.CheckTxType) *abciclient.ReqRes {
+func newReqRes(tx types.Tx, code uint32, requestType abci.CheckTxType) *abciclient.ReqRes { //nolint: unparam
 	reqRes := abciclient.NewReqRes(abci.ToCheckTxRequest(&abci.CheckTxRequest{Tx: tx, Type: requestType}))
 	reqRes.Response = abci.ToCheckTxResponse(&abci.CheckTxResponse{Code: code})
 	return reqRes
```

### mempool/errors.go
```diff
@@ -59,18 +59,6 @@ func IsPreCheckError(err error) bool {
 	return errors.As(err, &ErrPreCheck{})
 }
 
-type ErrCheckTxAsync struct {
-	Err error
-}
-
-func (e ErrCheckTxAsync) Error() string {
-	return fmt.Sprintf("check tx async: %v", e.Err)
-}
-
-func (e ErrCheckTxAsync) Unwrap() error {
-	return e.Err
-}
-
 type ErrAppConnMempool struct {
 	Err error
 }
```
