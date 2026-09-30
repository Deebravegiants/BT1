# [?] Include comment about something that looks like a vulnerability, but isn't. (#820)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2020-02-12
Source: https://github.com/algorand/go-algorand/commit/a88dc6c5fe5b9188279690bef85285714995499a
Type: security-commit

## Details
Include comment about something that looks like a vulnerability, but isn't. (#820)

## Patch
### logging/telemetryConfig.go
```diff
@@ -64,6 +64,7 @@ func createTelemetryConfig() TelemetryConfig {
 		URI:                "",
 		MinLogLevel:        logrus.WarnLevel,
 		ReportHistoryLevel: logrus.WarnLevel,
+		// These credentials are here intentionally. Not a bug.
 		UserName:           "telemetry-v9",
 		Password:           "oq%$FA1TOJ!yYeMEcJ7D688eEOE#MGCu",
 	}
```

### logging/telemetryConfig_test.go
```diff
@@ -33,6 +33,7 @@ func Test_loadTelemetryConfig(t *testing.T) {
 		URI:                "elastic.algorand.com",
 		MinLogLevel:        4,
 		ReportHistoryLevel: 4,
+		// These credentials are here intentionally. Not a bug.
 		UserName:           "telemetry-v9",
 		Password:           "oq%$FA1TOJ!yYeMEcJ7D688eEOE#MGCu",
 	}
```
