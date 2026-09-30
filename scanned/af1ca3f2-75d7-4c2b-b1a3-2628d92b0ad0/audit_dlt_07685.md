# [?] Fixed panic in running eth devnet (#13508)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-01-20
Source: https://github.com/erigontech/erigon/commit/e0689a291e40f665acfb2c86863208a6ff583c22
Type: security-commit

## Details
Fixed panic in running eth devnet (#13508)

## Patch
### eth/backend.go
```diff
@@ -1530,7 +1530,7 @@ func (s *Ethereum) Start() error {
 		diagnostics.Send(diagnostics.SyncStageList{StagesList: diagnostics.InitStagesFromList(s.pipelineStagedSync.StagesIdsList())})
 		s.waitForStageLoopStop = nil // TODO: Ethereum.Stop should wait for execution_server shutdown
 		go s.eth1ExecutionServer.Start(s.sentryCtx)
-	} else if s.config.PolygonSync {
+	} else if s.chainConfig.Bor != nil && s.config.PolygonSync {
 		diagnostics.Send(diagnostics.SyncStageList{StagesList: diagnostics.InitStagesFromList(s.stagedSync.StagesIdsList())})
 		s.waitForStageLoopStop = nil // Shutdown is handled by context
 		s.bgComponentsEg.Go(func() error {
```
