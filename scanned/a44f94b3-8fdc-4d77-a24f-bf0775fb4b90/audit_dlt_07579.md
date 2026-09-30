# [?] core/txpool/legacypool: fix data race of pricedList access (#31758)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-05-04
Source: https://github.com/ethereum/go-ethereum/commit/2d86a54000be027286145f7aec36dd78fadcf070
Type: security-commit

## Details
core/txpool/legacypool: fix data race of pricedList access (#31758)

## Patch
### core/txpool/legacypool/legacypool.go
```diff
@@ -1934,7 +1934,7 @@ func (pool *LegacyPool) Clear() {
 		pool.reserver.Release(addr)
 	}
 	pool.all.Clear()
-	pool.priced = newPricedList(pool.all)
+	pool.priced.Reheap()
 	pool.pending = make(map[common.Address]*list)
 	pool.queue = make(map[common.Address]*list)
 	pool.pendingNonces = newNoncer(pool.currentState)
```
