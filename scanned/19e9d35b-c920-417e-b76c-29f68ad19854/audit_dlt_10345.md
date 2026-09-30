# [?] avoid underflow of cap limit

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-05-03
Source: https://github.com/0xsoniclabs/sonic/commit/8b9a63317a3d1b3bce2ccef1a2e0906c0bd74a73
Type: security-commit

## Details
avoid underflow of cap limit

## Patch
### gossip/evmstore/store.go
```diff
@@ -239,9 +239,9 @@ func (s *Store) Cap() {
 		nodes, imgs = triedb.Size()
 		limit       = common.StorageSize(s.cfg.Cache.TrieDirtyLimit)
 	)
-	if nodes > limit || imgs > 4*1024*1024 {
-		log.Warn("(Cap) If we exceeded our memory allowance, flush matured singleton nodes to disk")
-		triedb.Cap(limit - ethdb.IdealBatchSize)
+	if nodes > limit+ethdb.IdealBatchSize || imgs > 4*1024*1024 {
+		log.Warn("If we exceeded our memory allowance, flush matured singleton nodes to disk")
+		triedb.Cap(limit)
 	}
 }
 
```
