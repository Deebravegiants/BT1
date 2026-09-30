# [?] fix nil pointer dereference on DoCall

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2025-03-27
Source: https://github.com/0xPolygon/bor/commit/1eecdf40166db928aef2c455151284af097d9108
Type: security-commit

## Details
fix nil pointer dereference on DoCall

## Patch
### internal/ethapi/api.go
```diff
@@ -1324,7 +1324,10 @@ func doCallWithState(ctx context.Context, b Backend, args TransactionArgs, heade
 	}
 
 	if err != nil {
-		return result, fmt.Errorf("err: %w (supplied gas %d)", err, msg.GasLimit)
+		return nil, fmt.Errorf("err: %w (supplied gas %d)", err, msg.GasLimit)
+	}
+	if result == nil {
+		return nil, errors.New("EVM ApplyMessage returned nil result without error")
 	}
 
 	return result, nil
@@ -1388,6 +1391,9 @@ func (api *BlockChainAPI) CallWithState(ctx context.Context, args TransactionArg
 	if err != nil {
 		return nil, err
 	}
+	if result == nil {
+		return nil, fmt.Errorf("DoCall returned nil result with no error (block=%v)", blockNrOrHash)
+	}
 
 	if int(api.b.RPCRpcReturnDataLimit()) > 0 && len(result.ReturnData) > int(api.b.RPCRpcReturnDataLimit()) {
 		return nil, fmt.Errorf("call returned result of length %d exceeding limit %d", len(result.ReturnData), int(api.b.RPCRpcReturnDataLimit()))
```
