# [?] p2p/dnsdisc: fix crash when iterator closed before first call to Next (#22906)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-05-20
Source: https://github.com/ethereum/go-ethereum/commit/16bc57438bd3d28e947d12f6f295da62e4ca9e26
Type: security-commit

## Details
p2p/dnsdisc: fix crash when iterator closed before first call to Next (#22906)

## Patch
### p2p/dnsdisc/client.go
```diff
@@ -298,6 +298,12 @@ func (it *randomIterator) pickTree() *clientTree {
 	it.mu.Lock()
 	defer it.mu.Unlock()
 
+	// First check if iterator was closed.
+	// Need to do this here to avoid nil map access in rebuildTrees.
+	if it.trees == nil {
+		return nil
+	}
+
 	// Rebuild the trees map if any links have changed.
 	if it.lc.changed {
 		it.rebuildTrees()
```

### p2p/dnsdisc/client_test.go
```diff
@@ -115,6 +115,21 @@ func TestIterator(t *testing.T) {
 	checkIterator(t, it, nodes)
 }
 
+func TestIteratorCloseWithoutNext(t *testing.T) {
+	tree1, url1 := makeTestTree("t1", nil, nil)
+	c := NewClient(Config{Resolver: newMapResolver(tree1.ToTXT("t1"))})
+	it, err := c.NewIterator(url1)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	it.Close()
+	ok := it.Next()
+	if ok {
+		t.Fatal("Next returned true after Close")
+	}
+}
+
 // This test checks if closing randomIterator races.
 func TestIteratorClose(t *testing.T) {
 	nodes := testNodes(nodesSeed1, 500)
```
