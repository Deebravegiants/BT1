# [?] Fix panic when fetching block in case of reorg (#1259)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-06-06
Source: https://github.com/0xPolygon/bor/commit/c0d1fbb86a99668cff01d7ff5d482792d8c4fc36
Type: security-commit

## Details
Fix panic when fetching block in case of reorg (#1259)

## Patch
### ethstats/ethstats.go
```diff
@@ -735,6 +735,12 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 			}
 		}
 
+		// It's weird, but it's possible that the block is nil here.
+		// even though the check for error is done above.
+		if block == nil {
+			return nil
+		}
+
 		header = block.Header()
 		td = fullBackend.GetTd(context.Background(), header.Hash())
 
```
