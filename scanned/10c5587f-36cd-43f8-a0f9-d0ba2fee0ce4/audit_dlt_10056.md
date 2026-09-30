# [?] fix race condition

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-05-29
Source: https://github.com/multiversx/mx-chain-go/commit/c5ccca7892034fd99797d2560db4c33dee39e957
Type: security-commit

## Details
fix race condition

## Patch
### update/sync/syncEpochStartShardHeaders.go
```diff
@@ -132,7 +132,9 @@ func (p *pendingEpochStartShardHeader) syncEpochStartShardHeader(shardId uint32,
 			p.mutPending.Unlock()
 			return nil
 		case <-p.chNew:
+			p.mutPending.RLock()
 			nonce = p.latestReceivedHeader.GetNonce()
+			p.mutPending.RUnlock()
 			continue
 		case <-ctx.Done():
 			p.mutPending.Lock()
@@ -198,8 +200,10 @@ func (p *pendingEpochStartShardHeader) receivedProof(proof data.HeaderProofHandl
 		return
 	}
 	p.latestReceivedProof = proof
+	lastReceivedHeader := p.latestReceivedHeader
+	lastReceivedHash := p.latestReceivedHash
 	p.mutPending.Unlock()
-	p.updateReceivedHeaderAndProof(p.latestReceivedHeader, p.latestReceivedHash)
+	p.updateReceivedHeaderAndProof(lastReceivedHeader, lastReceivedHash)
 }
 
 // GetEpochStartHeader returns the synced epoch start header
```
