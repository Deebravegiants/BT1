# [?] R4R: fix panic in traceCall (#1305)

## Summary
Severity: Unknown
Chain: Mantle
Component: mantlenetworkio/mantle
Published: 2023-07-20
Source: https://github.com/mantlenetworkio/mantle/commit/f5e32445f8b127cf6dfad788d530a2f9b24305ce
Type: security-commit

## Details
R4R: fix panic in traceCall (#1305)

# Goals of PR

Core changes:

- add nil pointer checker in traceCall

Notes:

- Write notes here

Related Issues:

- close https://github.com/mantlenetworkio/mantle/issues/1304

## Patch
### l2geth/eth/api_tracer.go
```diff
@@ -554,7 +554,7 @@ func (api *PrivateDebugAPI) TraceCall(ctx context.Context, args ethapi.CallArgs,
 	}
 
 	// Override the fields of specified contracts before execution.
-	if config != nil {
+	if config != nil && config.StateOverrides != nil {
 		for addr, account := range *config.StateOverrides {
 			// Override account nonce.
 			if account.Nonce != nil {
```
