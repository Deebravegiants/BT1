# [?] Fix potential nil panic in LegacyTraceTransaction

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-12-01
Source: https://github.com/NethermindEth/juno/commit/c1e9e58d0dd2a3bf898045ca1789543e3ed29611
Type: security-commit

## Details
Fix potential nil panic in LegacyTraceTransaction

## Patch
### rpc/handlers.go
```diff
@@ -1354,7 +1354,7 @@ func (h *Handler) TraceTransaction(ctx context.Context, hash felt.Felt) (json.Ra
 // https://github.com/starkware-libs/starknet-specs/blob/1ae810e0137cc5d175ace4554892a4f43052be56/api/starknet_trace_api_openrpc.json#L11
 func (h *Handler) LegacyTraceTransaction(ctx context.Context, hash felt.Felt) (json.RawMessage, *jsonrpc.Error) {
 	trace, err := h.traceTransaction(ctx, &hash, true)
-	if err.Code == ErrTxnHashNotFound.Code {
+	if err != nil && err.Code == ErrTxnHashNotFound.Code {
 		err = ErrInvalidTxHash
 	}
 	return trace, err
```
