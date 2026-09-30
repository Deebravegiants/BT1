# [?] fix: recreate-missing-state-from panic

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-08-10
Source: https://github.com/OffchainLabs/nitro/commit/d4175348a5cdd33c2e4c34907fa6fde378ba5cf9
Type: security-commit

## Details
fix: recreate-missing-state-from panic

recreate-missing-state-from panics when attempting to execute stylus code
as the stylus target cache is uninitialized

## Patch
### cmd/nitro/init.go
```diff
@@ -644,6 +644,10 @@ func openInitializeChainDb(ctx context.Context, stack *node.Node, config *NodeCo
 					return chainDb, l2BlockChain, err
 				}
 				if config.Init.RecreateMissingStateFrom > 0 {
+					err = gethexec.PopulateStylusTargetCache(&config.Execution.StylusTarget)
+					if err != nil {
+						return chainDb, l2BlockChain, err
+					}
 					err = staterecovery.RecreateMissingStates(chainDb, l2BlockChain, cacheConfig, config.Init.RecreateMissingStateFrom)
 					if err != nil {
 						return chainDb, l2BlockChain, fmt.Errorf("failed to recreate missing states: %w", err)
```
