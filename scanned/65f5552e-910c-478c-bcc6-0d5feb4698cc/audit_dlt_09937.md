# [?] Merge branch 'debug-api' of github.com:klaytn/klaytn-ghsa-4vx6-m7jv-g2ch into debug-api

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-11-21
Source: https://github.com/kaiachain/kaia/commit/3e47806fb18d0fac57e0c5dadf5bb08b02fec8af
Type: security-commit

## Details
Merge branch 'debug-api' of github.com:klaytn/klaytn-ghsa-4vx6-m7jv-g2ch into debug-api

## Patch
### node/cn/tracers/api.go
```diff
@@ -500,7 +500,7 @@ func (api *API) TraceBlock(ctx context.Context, blob hexutil.Bytes, config *Trac
 // TraceBlockFromFile returns the structured logs created during the execution of
 // EVM and returns them as a JSON object.
 func (api *API) TraceBlockFromFile(ctx context.Context, file string, config *TraceConfig) ([]*txTraceResult, error) {
-	if api.unsafeTrace {
+	if !api.unsafeTrace {
 		return nil, errors.New("TraceBlockFromFile is not supported in 'debug' namespace, use 'unsafedebug' namespace instead")
 	}
 	blob, err := ioutil.ReadFile(file)
@@ -804,7 +804,7 @@ func (api *API) traceTx(ctx context.Context, message blockchain.Message, vmctx v
 		if *config.Tracer == fastCallTracer {
 			tracer = vm.NewInternalTxTracer()
 		} else {
-			// Constuct the JavaScript tracer to execute with
+			// Construct the JavaScript tracer to execute with
 			if tracer, err = New(*config.Tracer, api.unsafeTrace); err != nil {
 				return nil, err
 			}
```
