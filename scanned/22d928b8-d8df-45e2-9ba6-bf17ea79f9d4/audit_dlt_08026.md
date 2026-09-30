# [?] Fix race condition in p2p/enode (#1609)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-06-23
Source: https://github.com/celo-org/celo-blockchain/commit/ba4eb763975752787cc2b099b81616f036d00cb4
Type: security-commit

## Details
Fix race condition in p2p/enode (#1609)

## Patch
### p2p/enode/iter_test.go
```diff
@@ -268,7 +268,7 @@ func (s *genIter) Node() *Node {
 }
 
 func (s *genIter) Close() {
-	s.index = ^uint32(0)
+	atomic.StoreUint32(&s.index, ^uint32(0))
 }
 
 func testNode(id, seq uint64) *Node {
```
