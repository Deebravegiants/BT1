# [?] fix(chain): race condition when access read-only methods, caused by non-thread-safe cache

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-03-21
Source: https://github.com/vechain/thor/commit/ee0ed7547d5cdc475d3ef371d8863ceff8a61c47
Type: security-commit

## Details
fix(chain): race condition when access read-only methods, caused by non-thread-safe cache

use arc cache

## Patch
### chain/cache.go
```diff
@@ -0,0 +1,28 @@
+package chain
+
+import lru "github.com/hashicorp/golang-lru"
+
+type cache struct {
+	*lru.ARCCache
+	loader func(key interface{}) (interface{}, error)
+}
+
+func newLRU(maxSize int, loader func(key interface{}) (interface{}, error)) *cache {
+	arc, err := lru.NewARC(maxSize)
+	if err != nil {
+		panic(err)
+	}
+	return &cache{arc, loader}
+}
+
+func (c *cache) GetOrLoad(key interface{}) (interface{}, error) {
+	if value, ok := c.Get(key); ok {
+		return value, nil
+	}
+	value, err := c.loader(key)
+	if err != nil {
+		return nil, err
+	}
+	c.Add(key, value)
+	return value, nil
+}
```

### chain/chain.go
```diff
@@ -32,11 +32,11 @@ type Chain struct {
 }
 
 type caches struct {
-	header       *lru
-	body         *lru
-	txIDs        *lru
-	receipts     *lru
-	trunkBlockID *lru
+	header       *cache
+	body         *cache
+	txIDs        *cache
+	receipts     *cache
+	trunkBlockID *cache
 }
 
 // New create an instance of Chain.
```

### chain/lru.go
```diff
@@ -1,28 +0,0 @@
-package chain
-
-import cache "github.com/hashicorp/golang-lru/simplelru"
-
-type lru struct {
-	*cache.LRU
-	loader func(key interface{}) (interface{}, error)
-}
-
-func newLRU(maxSize int, loader func(key interface{}) (interface{}, error)) *lru {
-	cache, err := cache.NewLRU(maxSize, nil)
-	if err != nil {
-		panic(err)
-	}
-	return &lru{cache, loader}
-}
-
-func (l *lru) GetOrLoad(key interface{}) (interface{}, error) {
-	if value, ok := l.Get(key); ok {
-		return value, nil
-	}
-	value, err := l.loader(key)
-	if err != nil {
-		return nil, err
-	}
-	l.Add(key, value)
-	return value, nil
-}
```
