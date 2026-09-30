# [?] fix deadlock (#2659)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2021-05-09
Source: https://github.com/iotexproject/iotex-core/commit/30520703cb75bf32e88e92fb723f6b6f26b66e58
Type: security-commit

## Details
fix deadlock (#2659)

## Patch
### blocksync/buffer.go
```diff
@@ -58,11 +58,13 @@ func (b *blockBuffer) cleanup(height uint64) {
 	size := len(b.blocks)
 	if size > int(b.bufferSize)*2 {
 		log.L().Warn("blockBuffer is leaking memory.", zap.Int("bufferSize", size))
+		newBlocks := map[uint64]*block.Block{}
 		for h := range b.blocks {
-			if h <= height {
-				b.delete(h)
+			if h > height {
+				newBlocks[h] = b.blocks[h]
 			}
 		}
+		b.blocks = newBlocks
 	}
 }
 
```
