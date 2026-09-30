# [?] [p2p] fix the panic at cooldown cache

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2022-02-13
Source: https://github.com/harmony-one/harmony/commit/8f24ee77b2c8d824fe6aac34eafe0b7340821958
Type: security-commit

## Details
[p2p] fix the panic at cooldown cache

## Patch
### p2p/stream/common/streammanager/cooldown.go
```diff
@@ -27,11 +27,13 @@ func newCoolDownCache() *coolDownCache {
 // Has check and add the peer ID to the cache
 func (cache *coolDownCache) Has(id peer.ID) bool {
 	has := cache.timeCache.Has(string(id))
-	cache.timeCache.Add(string(id))
+	if !has {
+		cache.timeCache.Add(string(id))
+	}
 	return has
 }
 
-// Reset reset the cooldown cache
+// Reset the cool down cache
 func (cache *coolDownCache) Reset() {
 	cache.timeCache.Q = list.New()
 	cache.timeCache.M = make(map[string]time.Time)
```
