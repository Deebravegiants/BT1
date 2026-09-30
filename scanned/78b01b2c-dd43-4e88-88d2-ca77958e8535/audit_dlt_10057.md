# [?] guard another possible panic

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-04-25
Source: https://github.com/multiversx/mx-chain-go/commit/d052f5c380532425dade9fb2ef6bea0d21b03269
Type: security-commit

## Details
guard another possible panic

## Patch
### process/block/baseProcess.go
```diff
@@ -2352,10 +2352,19 @@ func (bp *baseProcessor) requestProofIfNeeded(currentHeaderHash []byte, epoch ui
 		return false
 	}
 	if bp.proofsPool.HasProof(shardID, currentHeaderHash) {
-		bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)].hasProof = true
+		_, ok := bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)]
+		if ok {
+			bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)].hasProof = true
+		}
+
 		return true
 	}
 
+	_, ok := bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)]
+	if !ok {
+		bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)] = &hdrInfo{}
+	}
+
 	bp.hdrsForCurrBlock.hdrHashAndInfo[string(currentHeaderHash)].hasProofRequested = true
 	bp.hdrsForCurrBlock.missingProofs++
 	go bp.requestHandler.RequestEquivalentProofByHash(shardID, currentHeaderHash)
```
