# [?] Fix RPCClient Deadlock on Unsubscribe and NewHead (#14236) (#1426)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-09-11
Source: https://github.com/smartcontractkit/ccip/commit/fc50683640bcfd73f0074d791fbaf7cdb6b29c71
Type: security-commit

## Details
Fix RPCClient Deadlock on Unsubscribe and NewHead (#14236) (#1426)

Cherry-pick of https://github.com/smartcontractkit/chainlink/pull/14236

---------

Co-authored-by: Dmytro Haidashenko <34754799+dhaidashenko@users.noreply.github.com>

## Patch
### .changeset/curly-birds-guess.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+Fixed deadlock in RPCClient causing CL Node to stop performing RPC requests for the affected chain #bugfix
```

### core/chains/evm/client/rpc_client.go
```diff
@@ -141,6 +141,7 @@ type rpcClient struct {
 	// stateMu since it can happen on state transitions as well as rpcClient Close.
 	chStopInFlight chan struct{}
 
+	chainInfoLock sync.RWMutex
 	// intercepted values seen by callers of the rpcClient excluding health check calls. Need to ensure MultiNode provides repeatable read guarantee
 	highestUserObservations commonclient.ChainInfo
 	// most recent chain info observed during current lifecycle (reseted on DisconnectAll)
@@ -336,7 +337,9 @@ func (r *rpcClient) DisconnectAll() {
 	}
 	r.cancelInflightRequests()
 	r.unsubscribeAll()
+	r.chainInfoLock.Lock()
 	r.latestChainInfo = commonclient.ChainInfo{}
+	r.chainInfoLock.Unlock()
 }
 
 // unsubscribeAll unsubscribes all subscriptions
@@ -1379,8 +1382,8 @@ func (r *rpcClient) onNewHead(ctx context.Context, requestCh <-chan struct{}, he
 		return
 	}
 
-	r.stateMu.Lock()
-	defer r.stateMu.Unlock()
+	r.chainInfoLock.Lock()
+	defer r.chainInfoLock.Unlock()
 	if !commonclient.CtxIsHeathCheckRequest(ctx) {
 		r.highestUserObservations.BlockNumber = max(r.highestUserObservations.BlockNumber, head.Number)
 		r.highestUserObservations.TotalDifficulty = commonclient.MaxTotalDifficulty(r.highestUserObservations.TotalDifficulty, head.TotalDifficulty)
@@ -1398,8 +1401,8 @@ func (r *rpcClient) onNewFinalizedHead(ctx context.Context, requestCh <-chan str
 	if head == nil {
 		return
 	}
-	r.stateMu.Lock()
-	defer r.stateMu.Unlock()
+	r.chainInfoLock.Lock()
+	defer r.chainInfoLock.Unlock()
 	if !commonclient.CtxIsHeathCheckRequest(ctx) {
 		r.highestUserObservations.FinalizedBlockNumber = max(r.highestUserObservations.FinalizedBlockNumber, head.Number)
 	}
@@ -1412,8 +1415,8 @@ func (r *rpcClient) onNewFinalizedHead(ctx context.Context, requestCh <-chan str
 }
 
 func (r *rpcClient) GetInterceptedChainInfo() (latest, highestUserObservations commonclient.ChainInfo) {
-	r.stateMu.RLock()
-	defer r.stateMu.RUnlock()
+	r.chainInfoLock.RLock()
+	defer r.chainInfoLock.RUnlock()
 	return r.latestChainInfo, r.highestUserObservations
 }
 
```

### core/chains/evm/client/rpc_client_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	"fmt"
 	"math/big"
 	"net/url"
+	"sync"
 	"testing"
 	"time"
 
@@ -130,6 +131,32 @@ func TestRPCClient_SubscribeNewHead(t *testing.T) {
 		assert.Equal(t, int64(0), highestUserObservations.FinalizedBlockNumber)
 		assert.Equal(t, (*big.Int)(nil), highestUserObservations.TotalDifficulty)
 	})
+	t.Run("Concurrent Unsubscribe and onNewHead calls do not lead to a deadlock", func(t *testing.T) {
+		const numberOfAttempts = 1000 // need a large number to increase the odds of reproducing the issue
+		server := testutils.NewWSServer(t, chainId, serverCallBack)
+		wsURL := server.WSURL()
+
+		rpc := client.NewRPCClient(lggr, *wsURL, nil, "rpc", 1, chainId, commonclient.Primary, 0, commonclient.QueryTimeout, commonclient.QueryTimeout, "")
+		defer rpc.Close()
+		require.NoError(t, rpc.Dial(ctx))
+		var wg sync.WaitGroup
+		for i := 0; i < numberOfAttempts; i++ {
+			ch := make(chan *evmtypes.Head)
+			sub, err := rpc.SubscribeNewHead(tests.Context(t), ch)
+			require.NoError(t, err)
+			wg.Add(2)
+			go func() {
+				server.MustWriteBinaryMessageSync(t, makeNewHeadWSMessage(&evmtypes.Head{Number: 256, TotalDifficulty: big.NewInt(1000)}))
+				wg.Done()
+			}()
+			go func() {
+				rpc.UnsubscribeAllExceptAliveLoop()
+				sub.Unsubscribe()
+				wg.Done()
+			}()
+			wg.Wait()
+		}
+	})
 	t.Run("Block's chain ID matched configured", func(t *testing.T) {
 		server := testutils.NewWSServer(t, chainId, serverCallBack)
 		wsURL := server.WSURL()
```
