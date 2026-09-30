# [?] Fix nil pointer dereference when version alerter skips and reset test state

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-18
Source: https://github.com/OffchainLabs/nitro/commit/f63dc07b19d4ffef16171e05a34d40b37244a254
Type: security-commit

## Details
Fix nil pointer dereference when version alerter skips and reset test state

Guard against nil alerter in cmd/nitro when NewClient returns (nil, nil)
for invalid semver versions. Also explicitly reset UpgradeGracePeriod
before the ERROR test phase to avoid implicit state carry-over from the
WARN phase.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### cmd/nitro/nitro.go
```diff
@@ -696,8 +696,10 @@ func mainImpl() int {
 		if err != nil {
 			fatalErrChan <- fmt.Errorf("error initializing nitro node version alerter: %w", err)
 		}
-		alerter.Start(ctx)
-		defer alerter.StopAndWait()
+		if alerter != nil {
+			alerter.Start(ctx)
+			defer alerter.StopAndWait()
+		}
 	}
 
 	sigint := make(chan os.Signal, 1)
```

### system_tests/version_alerter_test.go
```diff
@@ -95,6 +95,7 @@ func TestNitroNodeVersionAlerter(t *testing.T) {
 	logHandler.Clear()
 	// Same case as above where node version is still below required minimum.
 	// Set upgrade deadline to the past so now exceeds it, should see an ERROR log.
+	alerter.Cfg.UpgradeGracePeriod = 0
 	builder.nodeConfig.VersionAlerterServer.UpgradeDeadline = time.Now().Add(-time.Minute).Format(time.RFC3339)
 	builder.L2.ConsensusConfigFetcher.Set(builder.nodeConfig)
 	alerter.LogUpgradeMsgIfNecessary(ctx)
```
