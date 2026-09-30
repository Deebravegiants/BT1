# [?] fix possible deadlock when stoping updateFilterMapsHeads goroutine

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2026-02-23
Source: https://github.com/OffchainLabs/go-ethereum/commit/ed73b4fe6b5a76620b330d55717e22833a80504e
Type: security-commit

## Details
fix possible deadlock when stoping updateFilterMapsHeads goroutine

## Patch
### arbitrum/backend.go
```diff
@@ -129,6 +129,7 @@ func (b *Backend) Start() error {
 }
 
 func (b *Backend) updateFilterMapsHeads() {
+	defer close(b.closeFilterMaps)
 	headEventCh := make(chan core.ChainEvent, 10)
 	blockProcCh := make(chan bool, 10)
 	sub := b.arb.BlockChain().SubscribeChainEvent(headEventCh)
@@ -198,8 +199,12 @@ func (b *Backend) Stop() error {
 
 	// stop updateFilterMapsHeads goroutine and wait for it to finish
 	ch := make(chan struct{})
-	b.closeFilterMaps <- ch
-	<-ch
+	select {
+	case <-b.closeFilterMaps:
+		// updateFilterMapsHeads exited earlier and closed closeFilterMaps channel
+	case b.closeFilterMaps <- ch:
+		<-ch
+	}
 
 	b.filterMaps.Stop()
 	b.shutdownTracker.Stop()
```
