# [?] go/worker/client: Fix nil dereference on early Query

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-10-13
Source: https://github.com/oasisprotocol/oasis-core/commit/95284bbff4214e9e678a7f2f9fac2d014374c666
Type: security-commit

## Details
go/worker/client: Fix nil dereference on early Query

## Patch
### .changelog/5403.bugfix.md
```diff
@@ -0,0 +1 @@
+go/worker/client: Fix nil dereference on early Query
```

### go/worker/client/committee/node.go
```diff
@@ -149,13 +149,14 @@ func (n *Node) Query(ctx context.Context, round uint64, method string, args []by
 	// Fetch the active descriptor so we can get the current message limits.
 	n.commonNode.CrossNode.Lock()
 	dsc := n.commonNode.CurrentDescriptor
-	latestRound := n.commonNode.CurrentBlock.Header.Round
+	blk := n.commonNode.CurrentBlock
 	n.commonNode.CrossNode.Unlock()
 
-	if dsc == nil {
+	if dsc == nil || blk == nil {
 		return nil, api.ErrNoHostedRuntime
 	}
 	maxMessages := dsc.Executor.MaxMessages
+	latestRound := n.commonNode.CurrentBlock.Header.Round
 
 	rtInfo, err := hrt.GetInfo(ctx)
 	if err != nil {
```
