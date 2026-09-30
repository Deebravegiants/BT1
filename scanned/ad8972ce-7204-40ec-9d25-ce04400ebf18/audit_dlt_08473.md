# [?] fix deadlock

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-03-08
Source: https://github.com/sei-protocol/sei-chain/commit/d12b2d4f5e62edd507cb12cb5b85ab60aa113a2d
Type: security-commit

## Details
fix deadlock

## Patch
### sei-iavl/node.go
```diff
@@ -398,7 +398,7 @@ func (node *Node) _hash() ([]byte, error) {
 	defer node.mtx.Unlock()
 	node.hash = h.Sum(nil)
 
-	return node.GetHash(), nil
+	return node.hash, nil
 }
 
 // Hash the node and its descendants recursively. This usually mutates all
@@ -427,7 +427,7 @@ func (node *Node) hashWithCount() ([]byte, int64, error) {
 	defer node.mtx.Unlock()
 	node.hash = h.Sum(nil)
 
-	return node.GetHash(), hashCount + 1, nil
+	return node.hash, hashCount + 1, nil
 }
 
 // validate validates the node contents
```
