# [?] Fix Slasher Backup DB panic on call. (#8099)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2020-12-14
Source: https://github.com/OffchainLabs/prysm/commit/630d57377abaa1ef0ca24f24bbdd676d4534077e
Type: security-commit

## Details
Fix Slasher Backup DB panic on call. (#8099)

## Patch
### slasher/node/node.go
```diff
@@ -89,16 +89,16 @@ func NewSlasherNode(cliCtx *cli.Context) (*SlasherNode, error) {
 		stop:                  make(chan struct{}),
 	}
 
+	if err := slasher.startDB(); err != nil {
+		return nil, err
+	}
+
 	if !cliCtx.Bool(cmd.DisableMonitoringFlag.Name) {
 		if err := slasher.registerPrometheusService(cliCtx); err != nil {
 			return nil, err
 		}
 	}
 
-	if err := slasher.startDB(); err != nil {
-		return nil, err
-	}
-
 	if err := slasher.registerBeaconClientService(); err != nil {
 		return nil, err
 	}
```
