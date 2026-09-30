# [?] mempool: fix nil pointer dereference (#5412)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-09-29
Source: https://github.com/cometbft/cometbft/commit/e0f686ccaca27cfef86ead0e24a0375a5d3de0b7
Type: security-commit

## Details
mempool: fix nil pointer dereference (#5412)

previously, the second next could return nil, which would be the reason
for panic on line 275:

memTx := next.Value.(*mempoolTx)

Closes #5408

## Patch
### mempool/reactor.go
```diff
@@ -288,10 +288,11 @@ func (memR *Reactor) txs(next *clist.CElement, peerID uint16, peerHeight int64)
 			batch = append(batch, memTx.tx)
 		}
 
-		if next.Next() == nil {
+		n := next.Next()
+		if n == nil {
 			return batch
 		}
-		next = next.Next()
+		next = n
 	}
 }
 
```

### mempool/reactor_test.go
```diff
@@ -14,6 +14,7 @@ import (
 	"github.com/stretchr/testify/require"
 
 	"github.com/tendermint/tendermint/abci/example/kvstore"
+	abci "github.com/tendermint/tendermint/abci/types"
 	cfg "github.com/tendermint/tendermint/config"
 	"github.com/tendermint/tendermint/libs/log"
 	tmrand "github.com/tendermint/tendermint/libs/rand"
@@ -64,6 +65,66 @@ func TestReactorBroadcastTxsMessage(t *testing.T) {
 	waitForTxsOnReactors(t, txs, reactors)
 }
 
+// regression test for https://github.com/tendermint/tendermint/issues/5408
+func TestReactorConcurrency(t *testing.T) {
+	config := cfg.TestConfig()
+	const N = 2
+	reactors := makeAndConnectReactors(config, N)
+	defer func() {
+		for _, r := range reactors {
+			if err := r.Stop(); err != nil {
+				assert.NoError(t, err)
+			}
+		}
+	}()
+	for _, r := range reactors {
+		for _, peer := range r.Switch.Peers().List() {
+			peer.Set(types.PeerStateKey, peerState{1})
+		}
+	}
+	var wg sync.WaitGroup
+
+	const numTxs = 5
+
+	for i := 0; i < 1000; i++ {
+		wg.Add(2)
+
+		// 1. submit a bunch of txs
+		// 2. update the whole mempool
+		txs := checkTxs(t, reactors[0].mempool, numTxs, UnknownPeerID)
+		go func() {
+			defer wg.Done()
+
+			reactors[0].mempool.Lock()
+			defer reactors[0].mempool.Unlock()
+
+			deliverTxResponses := make([]*abci.ResponseDeliverTx, len(txs))
+			for i := range txs {
+				deliverTxResponses[i] = &abci.ResponseDeliverTx{Code: 0}
+			}
+			err := reactors[0].mempool.Update(1, txs, deliverTxResponses, nil, nil)
+			assert.NoError(t, err)
+		}()
+
+		// 1. submit a bunch of txs
+		// 2. update none
+		_ = checkTxs(t, reactors[1].mempool, numTxs, UnknownPeerID)
+		go func() {
+			defer wg.Done()
+
+			reactors[1].mempool.Lock()
+			defer reactors[1].mempool.Unlock()
+			err := reactors[1].mempool.Update(1, []types.Tx{}, make([]*abci.ResponseDeliverTx, 0), nil, nil)
+			assert.NoError(t, err)
+		}()
+
+		// 1. flush the mempool
+		reactors[1].mempool.Flush()
+	}
+
+	wg.Wait()
+}
+
 // Send a bunch of txs to the first reactor's mempool, claiming it came from peer
 // ensure peer gets no txs.
 func TestReactorNoBroadcastToSender(t *testing.T) {
```
