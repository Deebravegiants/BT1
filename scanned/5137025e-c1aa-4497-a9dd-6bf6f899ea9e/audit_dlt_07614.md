# [?] les: fix serverHandler crash after setHead (#24200)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-01-05
Source: https://github.com/ethereum/go-ethereum/commit/335914a63afae019a2b901d88f13b28eb0d6ca58
Type: security-commit

## Details
les: fix serverHandler crash after setHead (#24200)

## Patch
### les/server_handler.go
```diff
@@ -421,7 +421,10 @@ func (h *serverHandler) broadcastLoop() {
 			}
 			var reorg uint64
 			if lastHead != nil {
-				reorg = lastHead.Number.Uint64() - rawdb.FindCommonAncestor(h.chainDb, header, lastHead).Number.Uint64()
+				// If a setHead has been performed, the common ancestor can be nil.
+				if ancestor := rawdb.FindCommonAncestor(h.chainDb, header, lastHead); ancestor != nil {
+					reorg = lastHead.Number.Uint64() - ancestor.Number.Uint64()
+				}
 			}
 			lastHead, lastTd = header, td
 			log.Debug("Announcing block to peers", "number", number, "hash", hash, "td", td, "reorg", reorg)
```
