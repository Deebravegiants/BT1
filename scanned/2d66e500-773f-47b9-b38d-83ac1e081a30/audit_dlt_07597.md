# [?] core/txpool/legacypool: fix data race of txlookup access (#31641)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-04-17
Source: https://github.com/ethereum/go-ethereum/commit/87974974a7b3fcce873851205b889f7d839d7fb7
Type: security-commit

## Details
core/txpool/legacypool: fix data race of txlookup access (#31641)

## Patch
### core/txpool/legacypool/legacypool.go
```diff
@@ -1827,6 +1827,16 @@ func (t *lookup) Remove(hash common.Hash) {
 	delete(t.txs, hash)
 }
 
+// Clear resets the lookup structure, removing all stored entries.
+func (t *lookup) Clear() {
+	t.lock.Lock()
+	defer t.lock.Unlock()
+
+	t.slots = 0
+	t.txs = make(map[common.Hash]*types.Transaction)
+	t.auths = make(map[common.Address][]common.Hash)
+}
+
 // TxsBelowTip finds all remote transactions below the given tip threshold.
 func (t *lookup) TxsBelowTip(threshold *big.Int) types.Transactions {
 	found := make(types.Transactions, 0, 128)
@@ -1923,7 +1933,7 @@ func (pool *LegacyPool) Clear() {
 	for addr := range pool.queue {
 		pool.reserver.Release(addr)
 	}
-	pool.all = newLookup()
+	pool.all.Clear()
 	pool.priced = newPricedList(pool.all)
 	pool.pending = make(map[common.Address]*list)
 	pool.queue = make(map[common.Address]*list)
```
