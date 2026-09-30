# [?] eth: fix accidental nil panic on nil errors

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2016-03-31
Source: https://github.com/axieinfinity/ronin-archive/commit/4326061e35a76ebf1bd02379bfc2f1d05dddc529
Type: security-commit

## Details
eth: fix accidental nil panic on nil errors

## Patch
### eth/api.go
```diff
@@ -1531,7 +1531,7 @@ func (api *PrivateDebugAPI) TraceBlock(blockRlp []byte, config vm.Config) BlockT
 	return BlockTraceResult{
 		Validated:  validated,
 		StructLogs: formatLogs(logs),
-		Error:      err.Error(),
+		Error:      formatError(err),
 	}
 }
 
@@ -1557,7 +1557,7 @@ func (api *PrivateDebugAPI) TraceBlockByNumber(number uint64, config vm.Config)
 	return BlockTraceResult{
 		Validated:  validated,
 		StructLogs: formatLogs(logs),
-		Error:      err.Error(),
+		Error:      formatError(err),
 	}
 }
 
@@ -1573,7 +1573,7 @@ func (api *PrivateDebugAPI) TraceBlockByHash(hash common.Hash, config vm.Config)
 	return BlockTraceResult{
 		Validated:  validated,
 		StructLogs: formatLogs(logs),
-		Error:      err.Error(),
+		Error:      formatError(err),
 	}
 }
 
@@ -1666,7 +1666,7 @@ func formatLogs(structLogs []vm.StructLog) []structLogRes {
 			Gas:     trace.Gas,
 			GasCost: trace.GasCost,
 			Depth:   trace.Depth,
-			Error:   trace.Err.Error(),
+			Error:   formatError(trace.Err),
 			Stack:   make([]string, len(trace.Stack)),
 			Storage: make(map[string]string),
 		}
@@ -1686,6 +1686,15 @@ func formatLogs(structLogs []vm.StructLog) []structLogRes {
 	return formattedStructLogs
 }
 
+// formatError formats a Go error into either an empty string or the data content
+// of the error itself.
+func formatError(err error) string {
+	if err == nil {
+		return ""
+	}
+	return err.Error()
+}
+
 // TraceTransaction returns the structured logs created during the execution of EVM
 // and returns them as a JSON object.
 func (s *PrivateDebugAPI) TraceTransaction(txHash common.Hash, logger vm.LogConfig) (*ExecutionResult, error) {
```
