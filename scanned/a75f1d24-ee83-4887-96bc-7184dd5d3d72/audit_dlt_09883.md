# [?] [evm] fix invalid contract address causing SimulateExecution panic (#4333)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2024-07-17
Source: https://github.com/iotexproject/iotex-core/commit/4fb35e34db7132b0f7e68143d6b75d0b3b4af28a
Type: security-commit

## Details
[evm] fix invalid contract address causing SimulateExecution panic (#4333)

## Patch
### action/protocol/execution/evm/evm.go
```diff
@@ -638,6 +638,9 @@ func SimulateExecution(
 ) ([]byte, *action.Receipt, error) {
 	ctx, span := tracer.NewSpan(ctx, "evm.SimulateExecution")
 	defer span.End()
+	if err := ex.SanityCheck(); err != nil {
+		return nil, nil, err
+	}
 	bcCtx := protocol.MustGetBlockchainCtx(ctx)
 	g := genesis.MustExtractGenesisContext(ctx)
 	ctx = protocol.WithActionCtx(
```
