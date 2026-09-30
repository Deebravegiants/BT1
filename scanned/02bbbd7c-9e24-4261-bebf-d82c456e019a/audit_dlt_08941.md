# [?] fix(axelarnet): panic in CLI command (#1089)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-12-14
Source: https://github.com/axelarnetwork/axelar-core/commit/7708f47177e3b86a4c985c75555bfe14d03acf48
Type: security-commit

## Details
fix(axelarnet): panic in CLI command (#1089)

## Patch
### x/axelarnet/client/cli/tx.go
```diff
@@ -193,7 +193,7 @@ func GetCmdRegisterAsset() *cobra.Command {
 			chain := args[0]
 			denom := args[1]
 
-			minAmount, ok := sdk.NewIntFromString(args[3])
+			minAmount, ok := sdk.NewIntFromString(args[2])
 			if !ok {
 				return fmt.Errorf("could not convert string to integer")
 			}
```
