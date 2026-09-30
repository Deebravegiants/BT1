# [?] go/oasis-node: Fix possible nil dereference in newNode

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-06-05
Source: https://github.com/oasisprotocol/oasis-core/commit/d0551abb74b878bf62b44115fd917a9786c9357b
Type: security-commit

## Details
go/oasis-node: Fix possible nil dereference in newNode

## Patch
### go/oasis-node/cmd/node/node.go
```diff
@@ -540,10 +540,10 @@ func NewTestNode() (*Node, error) {
 	return newNode(true)
 }
 
-func newNode(testNode bool) (node *Node, err error) { // nolint: gocyclo
+func newNode(testNode bool) (n *Node, err error) { // nolint: gocyclo
 	logger := cmdCommon.Logger()
 
-	node = &Node{
+	node := &Node{
 		svcMgr:  background.NewServiceManager(logger),
 		readyCh: make(chan struct{}),
 	}
```
