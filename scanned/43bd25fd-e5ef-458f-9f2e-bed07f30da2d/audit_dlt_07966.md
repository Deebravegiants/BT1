# [?] Fix panic on concurrent map read/write in P-chain wallet (#1355)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2022-04-14
Source: https://github.com/ava-labs/avalanchego/commit/d8b338bf6ac3b564a5c1a5484450340eb6fc0fdf
Type: security-commit

## Details
Fix panic on concurrent map read/write in P-chain wallet (#1355)

## Patch
### wallet/chain/p/backend.go
```diff
@@ -5,6 +5,7 @@ package p
 
 import (
 	"fmt"
+	"sync"
 
 	stdcontext "context"
 
@@ -38,6 +39,7 @@ type backend struct {
 	Context
 	ChainUTXOs
 
+	txsLock sync.RWMutex
 	// txID -> tx
 	txs map[ids.ID]*platformvm.Tx
 }
@@ -108,6 +110,9 @@ func (b *backend) AcceptTx(ctx stdcontext.Context, tx *platformvm.Tx) error {
 		return err
 	}
 
+	b.txsLock.Lock()
+	defer b.txsLock.Unlock()
+
 	b.txs[txID] = tx
 	return nil
 }
@@ -131,6 +136,9 @@ func (b *backend) removeUTXOs(ctx stdcontext.Context, sourceChain ids.ID, utxoID
 }
 
 func (b *backend) GetTx(_ stdcontext.Context, txID ids.ID) (*platformvm.Tx, error) {
+	b.txsLock.RLock()
+	defer b.txsLock.RUnlock()
+
 	tx, exists := b.txs[txID]
 	if !exists {
 		return nil, database.ErrNotFound
```
