# [?] fix panic

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-03-06
Source: https://github.com/onflow/flow-go/commit/125041ef2e4d28e93f07e2c03de7414d5e86c14d
Type: security-commit

## Details
fix panic

## Patch
### engine/execution/computation/computer/result_collector.go
```diff
@@ -309,7 +309,13 @@ func (collector *resultCollector) logInspectionResults(
 	// logLevel := zerolog.TraceLevel
 	// leo: debugging with info level log
 	logLevel := zerolog.InfoLevel
-	for _, inspectionResult := range results {
+	for i, inspectionResult := range results {
+		if inspectionResult == nil {
+			log.Warn().
+				Int("index", i).
+				Msg("inspection result is nil, likely due to a panic or error during inspection")
+			continue
+		}
 		lvl, evt := inspectionResult.AsLogEvent()
 		if lvl > logLevel {
 			logLevel = lvl
```

### fvm/inspection/token_changes.go
```diff
@@ -307,6 +307,11 @@ func walkLoaded(
 				f(value)
 				return true
 			})
+		case interpreter.PathLinkValue, interpreter.AccountLinkValue:
+			// Link values are deprecated legacy types that don't contain tokens.
+			// PathLinkValue.Walk and AccountLinkValue.Walk panic with "unreachable",
+			// so we skip them.
+			return
 		default:
 			// This assumes all other types cannot be partially loaded.
 			v.Walk(c, f)
```
