# [?] fix eth trace panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-07-12
Source: https://github.com/filecoin-project/lotus/commit/8723d19e62dc83288b0a001b8bea585ce0ffbb0d
Type: security-commit

## Details
fix eth trace panic

## Patch
### node/impl/full/eth_trace.go
```diff
@@ -446,7 +446,7 @@ func decodeCreateViaEAM(et *types.ExecutionTrace) (initcode []byte, addr *ethtyp
 	}
 	ret, err := decodeReturn[eam12.CreateReturn](&et.MsgRct)
 	if err != nil {
-		return nil, (*ethtypes.EthAddress)(&ret.EthAddress), err
+		return nil, nil, err
 	}
 	return initcode, (*ethtypes.EthAddress)(&ret.EthAddress), nil
 }
```
