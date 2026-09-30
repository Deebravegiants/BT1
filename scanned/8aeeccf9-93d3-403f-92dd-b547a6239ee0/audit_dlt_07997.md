# [?] eth/tracers: avoid data race when tracing block with bor tx (#1214)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-05-03
Source: https://github.com/0xPolygon/bor/commit/3a719a86d136761c415d926f93758cf9a328e4af
Type: security-commit

## Details
eth/tracers: avoid data race when tracing block with bor tx (#1214)

## Patch
### eth/tracers/api.go
```diff
@@ -835,8 +835,10 @@ func (api *API) traceBlock(ctx context.Context, block *types.Block, config *Trac
 
 				if stateSyncPresent && task.index == len(txs)-1 {
 					if *config.BorTraceEnabled {
-						config.BorTx = newBoolPtr(true)
-						res, err = api.traceTx(ctx, msg, txctx, blockCtx, task.statedb, config)
+						// avoid data race
+						newConfig := *config
+						newConfig.BorTx = newBoolPtr(true)
+						res, err = api.traceTx(ctx, msg, txctx, blockCtx, task.statedb, &newConfig)
 					} else {
 						break
 					}
```
