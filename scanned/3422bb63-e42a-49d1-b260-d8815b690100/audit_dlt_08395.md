# [?] fix(mempool): data race in mempool prepare proposal handler (backport #21413) (#21541)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-09-05
Source: https://github.com/cosmos/cosmos-sdk/commit/e89009eac56461abf8150001f41927c40b1a53a8
Type: security-commit

## Details
fix(mempool): data race in mempool prepare proposal handler (backport #21413) (#21541)

Co-authored-by: yihuang <huang@crypto.com>
Co-authored-by: Julien Robert <julien@rbrt.fr>

## Patch
### CHANGELOG.md
```diff
@@ -53,6 +53,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (x/consensus) [#21493](https://github.com/cosmos/cosmos-sdk/pull/21493) Fix regression that prevented to upgrade to > v0.50.7 without consensus version params.
 * (baseapp) [#21256](https://github.com/cosmos/cosmos-sdk/pull/21256) Halt height will not commit the block indicated, meaning that if halt-height is set to 10, only blocks until 9 (included) will be committed. This is to go back to the original behavior before a change was introduced in v0.50.0.
 * (baseapp) [#21444](https://github.com/cosmos/cosmos-sdk/pull/21444) Follow-up, Return PreBlocker events in FinalizeBlockResponse.
+* (baseapp) [#21413](https://github.com/cosmos/cosmos-sdk/pull/21413) Fix data race in sdk mempool.
 
 ## [v0.50.9](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.9) - 2024-08-07
 
```

### baseapp/abci_utils.go
```diff
@@ -279,14 +279,18 @@ func (h *DefaultProposalHandler) PrepareProposalHandler() sdk.PrepareProposalHan
 			return &abci.ResponsePrepareProposal{Txs: h.txSelector.SelectedTxs(ctx)}, nil
 		}
 
-		iterator := h.mempool.Select(ctx, req.Txs)
 		selectedTxsSignersSeqs := make(map[string]uint64)
-		var selectedTxsNums int
-		for iterator != nil {
-			memTx := iterator.Tx()
+		var (
+			resError        error
+			selectedTxsNums int
+			invalidTxs      []sdk.Tx // invalid txs to be removed out of the loop to avoid dead lock
+		)
+		mempool.SelectBy(ctx, h.mempool, req.Txs, func(memTx sdk.Tx) bool {
 			signerData, err := h.signerExtAdapter.GetSigners(memTx)
 			if err != nil {
-				return nil, err
+				// propagate the error to the caller
+				resError = err
+				return false
 			}
 
 			// If the signers aren't in selectedTxsSignersSeqs then we haven't seen them before
@@ -310,8 +314,7 @@ func (h *DefaultProposalHandler) PrepareProposalHandler() sdk.PrepareProposalHan
 				txSignersSeqs[signer.Signer.String()] = signer.Sequence
 			}
 			if !shouldAdd {
-				iterator = iterator.Next()
-				continue
+				return true
 			}
 
 			// NOTE: Since transaction verification was already executed in CheckTx,
@@ -320,14 +323,11 @@ func (h *DefaultProposalHandler) PrepareProposalHandler() sdk.PrepareProposalHan
 			// check again.
 			txBz, err := h.txVerifier.PrepareProposalVerifyTx(memTx)
 			if err != nil {
-				err := h.mempool.Remove(memTx)
-				if err != nil && !errors.Is(err, mempool.ErrTxNotFound) {
-					return nil, err
-				}
+				invalidTxs = append(invalidTxs, memTx)
 			} else {
 				stop := h.txSelector.SelectTxForProposal(ctx, uint64(req.MaxTxBytes), maxBlockGas, memTx, txBz)
 				if stop {
-					break
+					return false
 				}
 
 				txsLen := len(h.txSelector.SelectedTxs(ctx))
@@ -348,7 +348,18 @@ func (h *DefaultProposalHandler) PrepareProposalHandler() sdk.PrepareProposalHan
 				selectedTxsNums = txsLen
 			}
 
-			iterator = iterator.Next()
+			return true
+		})
+
+		if resError != nil {
+			return nil, resError
+		}
+
+		for _, tx := range invalidTxs {
+			err := h.mempool.Remove(tx)
+			if err != nil && !errors.Is(err, mempool.ErrTxNotFound) {
+				return nil, err
+			}
 		}
 
 		return &abci.ResponsePrepareProposal{Txs: h.txSelector.SelectedTxs(ctx)}, nil
```

### types/mempool/mempool.go
```diff
@@ -13,8 +13,7 @@ type Mempool interface {
 	Insert(context.Context, sdk.Tx) error
 
 	// Select returns an Iterator over the app-side mempool. If txs are specified,
-	// then they shall be incorporated into the Iterator. The Iterator must
-	// closed by the caller.
+	// then they shall be incorporated into the Iterator. The Iterator is not thread-safe to use.
 	Select(context.Context, [][]byte) Iterator
 
 	// CountTx returns the number of transactions currently in the mempool.
@@ -25,6 +24,16 @@ type Mempool interface {
 	Remove(sdk.Tx) error
 }
 
+// ExtMempool is a extension of Mempool interface introduced in v0.50
+// for not be breaking in a patch release.
+// In v0.52+, this interface will be merged into Mempool interface.
+type ExtMempool interface {
+	Mempool
+
+	// SelectBy use callback to iterate over the mempool, it's thread-safe to use.
+	SelectBy(context.Context, [][]byte, func(sdk.Tx) bool)
+}
+
 // Iterator defines an app-side mempool iterator interface that is as minimal as
 // possible. The order of iteration is determined by the app-side mempool
 // implementation.
@@ -41,3 +50,18 @@ var (
 	ErrTxNotFound           = errors.New("tx not found in mempool")
 	ErrMempoolTxMaxCapacity = errors.New("pool reached max tx capacity")
 )
+
+// SelectBy is compatible with old interface to avoid breaking api.
+// In v0.52+, this function is removed and SelectBy is merged into Mempool interface.
+func SelectBy(ctx context.Context, mempool Mempool, txs [][]byte, callback func(sdk.Tx) bool) {
+	if ext, ok := mempool.(ExtMempool); ok {
+		ext.SelectBy(ctx, txs, callback)
+		return
+	}
+
+	// fallback to old behavior, without holding the lock while iteration.
+	iter := mempool.Select(ctx, txs)
+	for iter != nil && callback(iter.Tx()) {
+		iter = iter.Next()
+	}
+}
```

### types/mempool/noop.go
```diff
@@ -6,7 +6,7 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
-var _ Mempool = (*NoOpMempool)(nil)
+var _ ExtMempool = (*NoOpMempool)(nil)
 
 // NoOpMempool defines a no-op mempool. Transactions are completely discarded and
 // ignored when BaseApp interacts with the mempool.
@@ -16,7 +16,8 @@ var _ Mempool = (*NoOpMempool)(nil)
 // is FIFO-ordered by default.
 type NoOpMempool struct{}
 
-func (NoOpMempool) Insert(context.Context, sdk.Tx) error      { return nil }
-func (NoOpMempool) Select(context.Context, [][]byte) Iterator { return nil }
-func (NoOpMempool) CountTx() int                              { return 0 }
-func (NoOpMempool) Remove(sdk.Tx) error                       { return nil }
+func (NoOpMempool) Insert(context.Context, sdk.Tx) error                  { return nil }
+func (NoOpMempool) Select(context.Context, [][]byte) Iterator             { return nil }
+func (NoOpMempool) SelectBy(context.Context, [][]byte, func(sdk.Tx) bool) {}
+func (NoOpMempool) CountTx() int                                          { return 0 }
+func (NoOpMempool) Remove(sdk.Tx) error                                   { return nil }
```

### types/mempool/priority_nonce.go
```diff
@@ -12,8 +12,8 @@ import (
 )
 
 var (
-	_ Mempool  = (*PriorityNonceMempool[int64])(nil)
-	_ Iterator = (*PriorityNonceIterator[int64])(nil)
+	_ ExtMempool = (*PriorityNonceMempool[int64])(nil)
+	_ Iterator   = (*PriorityNonceIterator[int64])(nil)
 )
 
 type (
@@ -350,9 +350,13 @@ func (i *PriorityNonceIterator[C]) Tx() sdk.Tx {
 //
 // NOTE: It is not safe to use this iterator while removing transactions from
 // the underlying mempool.
-func (mp *PriorityNonceMempool[C]) Select(_ context.Context, _ [][]byte) Iterator {
+func (mp *PriorityNonceMempool[C]) Select(ctx context.Context, txs [][]byte) Iterator {
 	mp.mtx.Lock()
 	defer mp.mtx.Unlock()
+	return mp.doSelect(ctx, txs)
+}
+
+func (mp *PriorityNonceMempool[C]) doSelect(_ context.Context, _ [][]byte) Iterator {
 	if mp.priorityIndex.Len() == 0 {
 		return nil
 	}
@@ -367,6 +371,17 @@ func (mp *PriorityNonceMempool[C]) Select(_ context.Context, _ [][]byte) Iterato
 	return iterator.iteratePriority()
 }
 
+// SelectBy will hold the mutex during the iteration, callback returns if continue.
+func (mp *PriorityNonceMempool[C]) SelectBy(ctx context.Context, txs [][]byte, callback func(sdk.Tx) bool) {
+	mp.mtx.Lock()
+	defer mp.mtx.Unlock()
+
+	iter := mp.doSelect(ctx, txs)
+	for iter != nil && callback(iter.Tx()) {
+		iter = iter.Next()
+	}
+}
+
 type reorderKey[C comparable] struct {
 	deleteKey txMeta[C]
 	insertKey txMeta[C]
```

### types/mempool/priority_nonce_test.go
```diff
@@ -1,9 +1,11 @@
 package mempool_test
 
 import (
+	"context"
 	"fmt"
 	"math"
 	"math/rand"
+	"sync"
 	"testing"
 	"time"
 
@@ -396,6 +398,89 @@ func (s *MempoolTestSuite) TestIterator() {
 	}
 }
 
+func (s *MempoolTestSuite) TestIteratorConcurrency() {
+	t := s.T()
+	ctx := sdk.NewContext(nil, cmtproto.Header{}, false, log.NewNopLogger())
+	accounts := simtypes.RandomAccounts(rand.New(rand.NewSource(0)), 2)
+	sa := accounts[0].Address
+	sb := accounts[1].Address
+
+	tests := []struct {
+		txs  []txSpec
+		fail bool
+	}{
+		{
+			txs: []txSpec{
+				{p: 20, n: 1, a: sa},
+				{p: 15, n: 1, a: sb},
+				{p: 6, n: 2, a: sa},
+				{p: 21, n: 4, a: sa},
+				{p: 8, n: 2, a: sb},
+			},
+		},
+		{
+			txs: []txSpec{
+				{p: 20, n: 1, a: sa},
+				{p: 15, n: 1, a: sb},
+				{p: 6, n: 2, a: sa},
+				{p: 21, n: 4, a: sa},
+				{p: math.MinInt64, n: 2, a: sb},
+			},
+		},
+	}
+
+	for i, tt := range tests {
+		t.Run(fmt.Sprintf("case %d", i), func(t *testing.T) {
+			pool := mempool.DefaultPriorityMempool()
+
+			// create test txs and insert into mempool
+			for i, ts := range tt.txs {
+				tx := testTx{id: i, priority: int64(ts.p), nonce: uint64(ts.n), address: ts.a}
+				c := ctx.WithPriority(tx.priority)
+				err := pool.Insert(c, tx)
+				require.NoError(t, err)
+			}
+
+			// iterate through txs
+			stdCtx, cancel := context.WithCancel(context.Background())
+			var wg sync.WaitGroup
+			wg.Add(1)
+			go func() {
+				defer wg.Done()
+
+				id := len(tt.txs)
+				for {
+					select {
+					case <-stdCtx.Done():
+						return
+					default:
+						id++
+						tx := testTx{id: id, priority: int64(rand.Intn(100)), nonce: uint64(id), address: sa}
+						c := ctx.WithPriority(tx.priority)
+						err := pool.Insert(c, tx)
+						require.NoError(t, err)
+					}
+				}
+			}()
+
+			var i int
+			pool.SelectBy(ctx, nil, func(memTx sdk.Tx) bool {
+				tx := memTx.(testTx)
+				if tx.id < len(tt.txs) {
+					require.Equal(t, tt.txs[tx.id].p, int(tx.priority))
+					require.Equal(t, tt.txs[tx.id].n, int(tx.nonce))
+					require.Equal(t, tt.txs[tx.id].a, tx.address)
+					i++
+				}
+				return i < len(tt.txs)
+			})
+			require.Equal(t, i, len(tt.txs))
+			cancel()
+			wg.Wait()
+		})
+	}
+}
+
 func (s *MempoolTestSuite) TestPriorityTies() {
 	ctx := sdk.NewContext(nil, cmtproto.Header{}, false, log.NewNopLogger())
 	accounts := simtypes.RandomAccounts(rand.New(rand.NewSource(0)), 3)
```

### types/mempool/sender_nonce.go
```diff
@@ -15,8 +15,8 @@ import (
 )
 
 var (
-	_ Mempool  = (*SenderNonceMempool)(nil)
-	_ Iterator = (*senderNonceMempoolIterator)(nil)
+	_ ExtMempool = (*SenderNonceMempool)(nil)
+	_ Iterator   = (*senderNonceMempoolIterator)(nil)
 )
 
 var DefaultMaxTx = -1
@@ -158,9 +158,13 @@ func (snm *SenderNonceMempool) Insert(_ context.Context, tx sdk.Tx) error {
 //
 // NOTE: It is not safe to use this iterator while removing transactions from
 // the underlying mempool.
-func (snm *SenderNonceMempool) Select(_ context.Context, _ [][]byte) Iterator {
+func (snm *SenderNonceMempool) Select(ctx context.Context, txs [][]byte) Iterator {
 	snm.mtx.Lock()
 	defer snm.mtx.Unlock()
+	return snm.doSelect(ctx, txs)
+}
+
+func (snm *SenderNonceMempool) doSelect(_ context.Context, _ [][]byte) Iterator {
 	var senders []string
 
 	senderCursors := make(map[string]*skiplist.Element)
@@ -188,6 +192,17 @@ func (snm *SenderNonceMempool) Select(_ context.Context, _ [][]byte) Iterator {
 	return iter.Next()
 }
 
+// SelectBy will hold the mutex during the iteration, callback returns if continue.
+func (snm *SenderNonceMempool) SelectBy(ctx context.Context, txs [][]byte, callback func(sdk.Tx) bool) {
+	snm.mtx.Lock()
+	defer snm.mtx.Unlock()
+
+	iter := snm.doSelect(ctx, txs)
+	for iter != nil && callback(iter.Tx()) {
+		iter = iter.Next()
+	}
+}
+
 // CountTx returns the total count of txs in the mempool.
 func (snm *SenderNonceMempool) CountTx() int {
 	snm.mtx.Lock()
```
