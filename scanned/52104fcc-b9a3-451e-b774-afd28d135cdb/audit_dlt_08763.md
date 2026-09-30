# [?] node: fixes deadlock on Wait()

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-04-25
Source: https://github.com/scroll-tech/go-ethereum/commit/5f7eb78918fe88a9e4f64e47044c29fcb934d924
Type: security-commit

## Details
node: fixes deadlock on Wait()

## Patch
### node/node.go
```diff
@@ -536,6 +536,7 @@ func (n *Node) Stop() error {
 func (n *Node) Wait() {
 	n.lock.RLock()
 	if n.server == nil {
+		n.lock.RUnlock()
 		return
 	}
 	stop := n.stop
```
