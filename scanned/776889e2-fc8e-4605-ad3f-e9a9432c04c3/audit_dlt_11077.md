# [?] op-e2e: Fix race condition with removing included tx from the pool

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-10-27
Source: https://github.com/kroma-network/kroma/commit/40858b5a39819cce8bf9e7962fd510cd76a6d678
Type: security-commit

## Details
op-e2e: Fix race condition with removing included tx from the pool

The tx pool updates async, so the list of pending transactions may contain transactions included in a block if the tx pool update hasn't completed.
Filter any transactions with nonces that are too low to avoid this race condition.

## Patch
### op-e2e/actions/l1_miner.go
```diff
@@ -1,11 +1,8 @@
 package actions
 
 import (
-	"context"
 	"math/big"
-	"time"
 
-	"github.com/ethereum-optimism/optimism/op-e2e/e2eutils/wait"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/consensus/misc/eip1559"
 	"github.com/ethereum/go-ethereum/core"
@@ -98,22 +95,12 @@ func (s *L1Miner) ActL1IncludeTx(from common.Address) Action {
 			t.InvalidAction("no tx inclusion when not building l1 block")
 			return
 		}
-		var i uint64
-		var txs []*types.Transaction
-		var q []*types.Transaction
-		// Wait for the tx to be in the pending tx queue
-		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
-		defer cancel()
-		err := wait.For(ctx, time.Second, func() (bool, error) {
-			i = s.pendingIndices[from]
-			txs, q = s.eth.TxPool().ContentFrom(from)
-			return uint64(len(txs)) > i, nil
-		})
-		require.NoError(t, err,
-			"no pending txs from %s, and have %d unprocessable queued txs from this account: %w", from, len(q), err)
-		tx := txs[i]
+		getPendingIndex := func(from common.Address) uint64 {
+			return s.pendingIndices[from]
+		}
+		tx := firstValidTx(t, from, getPendingIndex, s.eth.TxPool().ContentFrom, s.EthClient().NonceAt)
 		s.IncludeTx(t, tx)
-		s.pendingIndices[from] = i + 1 // won't retry the tx
+		s.pendingIndices[from] = s.pendingIndices[from] + 1 // won't retry the tx
 	}
 }
 
```

### op-e2e/actions/l2_engine.go
```diff
@@ -1,12 +1,9 @@
 package actions
 
 import (
-	"context"
 	"errors"
-	"time"
 
 	"github.com/ethereum-optimism/optimism/op-e2e/e2eutils"
-	"github.com/ethereum-optimism/optimism/op-e2e/e2eutils/wait"
 	"github.com/ethereum-optimism/optimism/op-program/client/l2/engineapi"
 	"github.com/stretchr/testify/require"
 
@@ -179,22 +176,8 @@ func (e *L2Engine) ActL2IncludeTx(from common.Address) Action {
 			return
 		}
 
-		var i uint64
-		var txs []*types.Transaction
-		var q []*types.Transaction
-		// Wait for the tx to be in the pending tx queue
-		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
-		defer cancel()
-		err := wait.For(ctx, time.Second, func() (bool, error) {
-			i = e.engineApi.PendingIndices(from)
-			txs, q = e.eth.TxPool().ContentFrom(from)
-			return uint64(len(txs)) > i, nil
-		})
-		require.NoError(t, err,
-			"no pending txs from %s, and have %d unprocessable queued txs from this account: %w", from, len(q), err)
-
-		tx := txs[i]
-		err = e.engineApi.IncludeTx(tx, from)
+		tx := firstValidTx(t, from, e.engineApi.PendingIndices, e.eth.TxPool().ContentFrom, e.EthClient().NonceAt)
+		err := e.engineApi.IncludeTx(tx, from)
 		if errors.Is(err, engineapi.ErrNotBuildingBlock) {
 			t.InvalidAction(err.Error())
 		} else if errors.Is(err, engineapi.ErrUsesTooMuchGas) {
```

### op-e2e/actions/tx_helper.go
```diff
@@ -0,0 +1,49 @@
+package actions
+
+import (
+	"context"
+	"math/big"
+	"time"
+
+	"github.com/ethereum-optimism/optimism/op-e2e/e2eutils/wait"
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/stretchr/testify/require"
+)
+
+// firstValidTx finds the first transaction that is valid for inclusion from the specified address.
+// It uses a waiter and filtering of already included transactions to avoid race conditions with the async
+// updates to the transaction pool.
+func firstValidTx(
+	t Testing,
+	from common.Address,
+	pendingIndices func(common.Address) uint64,
+	contentFrom func(common.Address) ([]*types.Transaction, []*types.Transaction),
+	nonceAt func(context.Context, common.Address, *big.Int) (uint64, error),
+) *types.Transaction {
+	var i uint64
+	var txs []*types.Transaction
+	var q []*types.Transaction
+	// Wait for the tx to be in the pending tx queue
+	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
+	defer cancel()
+	err := wait.For(ctx, time.Second, func() (bool, error) {
+		i = pendingIndices(from)
+		txs, q = contentFrom(from)
+		// Remove any transactions that have already been included in the head block
+		// The tx pool only prunes included transactions async so they may still be in the list
+		nonce, err := nonceAt(ctx, from, nil)
+		if err != nil {
+			return false, err
+		}
+		for len(txs) > 0 && txs[0].Nonce() < nonce {
+			t.Logf("Removing already included transaction from list of length %v", len(txs))
+			txs = txs[1:]
+		}
+		return uint64(len(txs)) > i, nil
+	})
+	require.NoError(t, err,
+		"no pending txs from %s, and have %d unprocessable queued txs from this account: %w", from, len(q), err)
+
+	return txs[i]
+}
```
