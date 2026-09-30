# [?] fix crash in integration commands (#17061)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-08
Source: https://github.com/erigontech/erigon/commit/77caf29d0888ac83f4579297f36ae6e3e3154836
Type: security-commit

## Details
fix crash in integration commands (#17061)

## Patch
### cmd/integration/commands/stages.go
```diff
@@ -1368,7 +1368,9 @@ func newSync(ctx context.Context, db kv.TemporalRwDB, miningConfig *buildercfg.M
 		panic(err)
 	}
 	cfg.Snapshot = allSn.Cfg()
-	borSn.DownloadComplete() // mark as ready
+	if borSn != nil {
+		borSn.DownloadComplete() // mark as ready
+	}
 	engine := initConsensusEngine(ctx, chainConfig, cfg.Dirs.DataDir, db, blockReader, bridgeStore, heimdallStore, logger)
 
 	statusDataProvider := sentry.NewStatusDataProvider(
```
