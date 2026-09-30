# [?] fix: no panic

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2022-06-16
Source: https://github.com/neutron-org/neutron/commit/76138350311c5a400641e079db1fe9c311f2fd24
Type: security-commit

## Details
fix: no panic

## Patch
### x/interchaintxs/client/cli/tx.go
```diff
@@ -97,13 +97,13 @@ func SubmitTxCmd() *cobra.Command {
 				}
 
 				if err := json.Unmarshal(contents, &rawTxMsgs); err != nil {
-					panic(err)
+					return fmt.Errorf("cannot unmarshal msgs array: %w", err)
 				}
 
 				for _, txMsg := range rawTxMsgs.Msgs {
 					var sdkMsg sdk.Msg
 					if err := cdc.UnmarshalInterfaceJSON(txMsg, &sdkMsg); err != nil {
-						panic(err)
+						return fmt.Errorf("cannot unmarshal submessage: %w", err)
 					}
 					txMsgs = append(txMsgs, sdkMsg)
 				}
```
