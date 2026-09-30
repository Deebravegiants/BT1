# [?] eth/syncer: fix nil deref when the target block is missing (#35442)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-08-04
Source: https://github.com/ethereum/go-ethereum/commit/b483fe9e71ff2197976c30d046643edf6934e261
Type: security-commit

## Details
eth/syncer: fix nil deref when the target block is missing (#35442)

i didn't try to trigger the nil deref, but fixing it shouldn't be
controversial

## Patch
### eth/syncer/syncer.go
```diff
@@ -180,9 +180,10 @@ func (s *Syncer) run() {
 				var synced bool
 				var block *types.Header
 				if target != nil {
-					tb := s.backend.BlockChain().GetBlockByHash(target.Hash())
-					synced = tb != nil
-					block = tb.Header()
+					if tb := s.backend.BlockChain().GetBlockByHash(target.Hash()); tb != nil {
+						synced = true
+						block = tb.Header()
+					}
 				} else {
 					timestamp := time.Unix(int64(ev.Latest.Time), 0)
 					synced = time.Since(timestamp) < 10*time.Minute
```
