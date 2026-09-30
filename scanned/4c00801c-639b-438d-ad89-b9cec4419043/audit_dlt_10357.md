# [?] api: fix race condition

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2020-01-21
Source: https://github.com/0xsoniclabs/sonic/commit/cd1774be259984cd0d76a19d20d2631faef25df6
Type: security-commit

## Details
api: fix race condition

## Patch
### gossip/ethapi_backend.go
```diff
@@ -378,12 +378,15 @@ func (b *EthAPIBackend) SubscribeNewTxsNotify(ch chan<- evmcore.NewTxsNotify) no
 func (b *EthAPIBackend) Progress() ethapi.PeerProgress {
 	p2pProgress := b.svc.pm.myProgress()
 	highestP2pProgress := b.svc.pm.highestPeerProgress()
+	b.svc.engineMu.RLock()
+	lastBlock := b.svc.store.GetBlock(p2pProgress.NumOfBlocks)
+	b.svc.engineMu.RUnlock()
 
 	return ethapi.PeerProgress{
 		CurrentEpoch:     p2pProgress.Epoch,
 		CurrentBlock:     p2pProgress.NumOfBlocks,
 		CurrentBlockHash: p2pProgress.LastBlock,
-		CurrentBlockTime: b.svc.store.GetBlock(p2pProgress.NumOfBlocks).Time,
+		CurrentBlockTime: lastBlock.Time,
 		HighestBlock:     highestP2pProgress.NumOfBlocks,
 		HighestEpoch:     highestP2pProgress.Epoch,
 	}
```
