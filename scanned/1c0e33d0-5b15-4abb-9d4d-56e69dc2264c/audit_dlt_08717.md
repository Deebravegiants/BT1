# [?] fix eth_syncing crash, move SyncMonitor.Initialize after SeqCoordinator is started

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-26
Source: https://github.com/OffchainLabs/nitro/commit/7ce8c71b1e380e70869643b497ff4a9391837f4c
Type: security-commit

## Details
fix eth_syncing crash, move SyncMonitor.Initialize after SeqCoordinator is started

## Patch
### arbnode/node.go
```diff
@@ -1301,7 +1301,6 @@ func (n *Node) Start(ctx context.Context) error {
 			return fmt.Errorf("error initializing exec client: %w", err)
 		}
 	}
-	n.SyncMonitor.Initialize(n.InboxReader, n.TxStreamer, n.SeqCoordinator)
 	err := n.Stack.Start()
 	if err != nil {
 		return fmt.Errorf("error starting geth stack: %w", err)
@@ -1424,6 +1423,7 @@ func (n *Node) Start(ctx context.Context) error {
 	if n.configFetcher != nil {
 		n.configFetcher.Start(ctx)
 	}
+	n.SyncMonitor.Initialize(n.InboxReader, n.TxStreamer, n.SeqCoordinator)
 	n.SyncMonitor.Start(ctx)
 	if n.ConsensusExecutionSyncer != nil {
 		n.ConsensusExecutionSyncer.Start(ctx)
```
