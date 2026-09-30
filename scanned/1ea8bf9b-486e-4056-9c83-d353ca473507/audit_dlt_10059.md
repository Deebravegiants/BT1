# [?] fix possible panic in tests

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-04-16
Source: https://github.com/multiversx/mx-chain-go/commit/70a80e30b925bdd2750afaf574de7049695bcf9d
Type: security-commit

## Details
fix possible panic in tests

## Patch
### epochStart/bootstrap/epochStartMetaBlockProcessor.go
```diff
@@ -231,7 +231,9 @@ func (e *epochStartMetaBlockProcessor) waitForMetaBlock(ctx context.Context) (da
 			return e.metaBlock, e.metaBlockHash, nil
 		case <-ctx.Done():
 			metaBlock, hash, errGet := e.getMostReceivedMetaBlock()
-			e.requestHandler.SetEpoch(e.metaBlock.GetEpoch())
+			if !check.IfNil(e.metaBlock) {
+				e.requestHandler.SetEpoch(e.metaBlock.GetEpoch())
+			}
 			return metaBlock, hash, errGet
 		case <-chanRequests:
 			err = e.requestMetaBlock()
```
