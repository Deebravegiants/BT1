# [?] fix: Changed v2 upgrade handler to not panic when client status is not found. (#449)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2023-12-11
Source: https://github.com/dymensionxyz/dymension/commit/8e297d31f1d659350cbf1aa87be4325d4117c368
Type: security-commit

## Details
fix: Changed v2 upgrade handler to not panic when client status is not found. (#449)

## Patch
### app/upgrades/v2/upgrade.go
```diff
@@ -143,10 +143,10 @@ func verifyClientStatus(ctx sdk.Context, clientKeeper clientkeeper.Keeper, clien
 				msg := fmt.Sprintf("client status has changed after upgrade. Expected: %s, got: %s", clientStatuses[clientID], status)
 				panic(msg)
 			}
-			return false
 		} else {
-			panic(fmt.Sprintf("client status not found for clientID: %s", clientID))
+			fmt.Printf("client status not found for clientID: %s", clientID)
 		}
+		return false
 	})
 
 	logger.Info("Client status verification passed successfully")
```
