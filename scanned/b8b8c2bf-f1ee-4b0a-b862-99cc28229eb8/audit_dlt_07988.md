# [?] fix nil pointer dereference on DoCall

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2025-03-27
Source: https://github.com/0xPolygon/bor/commit/7d005ab547fb5e26745d0e241bd59a3df4f7bf2f
Type: security-commit

## Details
fix nil pointer dereference on DoCall

## Patch
### internal/ethapi/api.go
```diff
@@ -1399,7 +1399,10 @@ func applyMessageWithEVM(ctx context.Context, evm *vm.EVM, msg *core.Message, st
 	}
 
 	if err != nil {
-		return result, fmt.Errorf("err: %w (supplied gas %d)", err, msg.GasLimit)
+		return nil, fmt.Errorf("err: %w (supplied gas %d)", err, msg.GasLimit)
+	}
+	if result == nil {
+		return nil, errors.New("EVM ApplyMessage returned nil result without error")
 	}
 
 	return result, nil
@@ -1463,6 +1466,9 @@ func (api *BlockChainAPI) CallWithState(ctx context.Context, args TransactionArg
 	if err != nil {
 		return nil, err
 	}
+	if result == nil {
+		return nil, fmt.Errorf("DoCall returned nil result with no error (block=%v)", blockNrOrHash)
+	}
 
 	if int(api.b.RPCRpcReturnDataLimit()) > 0 && len(result.ReturnData) > int(api.b.RPCRpcReturnDataLimit()) {
 		return nil, fmt.Errorf("call returned result of length %d exceeding limit %d", len(result.ReturnData), int(api.b.RPCRpcReturnDataLimit()))
```
