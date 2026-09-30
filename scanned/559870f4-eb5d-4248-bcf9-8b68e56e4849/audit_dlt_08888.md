# [?] Fix panic when BlockLatest fails during sync (#765)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-05-12
Source: https://github.com/NethermindEth/juno/commit/8c47b9e8f02a7edb47d71503a9f4cc1e70f4d1e9
Type: security-commit

## Details
Fix panic when BlockLatest fails during sync (#765)

## Patch
### sync/sync.go
```diff
@@ -108,8 +108,9 @@ func (s *Synchronizer) verifierTask(ctx context.Context, block *core.Block, stat
 				highestBlock, err := s.StarknetData.BlockLatest(ctx)
 				if err != nil {
 					s.log.Warnw("Failed fetching latest block", "err", err.Error())
+				} else {
+					s.HighestBlockHeader = highestBlock.Header
 				}
-				s.HighestBlockHeader = highestBlock.Header
 			}
 
 			s.log.Infow("Stored Block", "number", block.Number, "hash",
```
