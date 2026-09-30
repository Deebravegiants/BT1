# [?] Merge pull request #14379 from farazdagi/fix/deadlock-in-node-wait

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-04-25
Source: https://github.com/scroll-tech/go-ethereum/commit/8dce4c283dda3a8e10aa30dadab05a8c0dd9e19d
Type: security-commit

## Details
Merge pull request #14379 from farazdagi/fix/deadlock-in-node-wait

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
