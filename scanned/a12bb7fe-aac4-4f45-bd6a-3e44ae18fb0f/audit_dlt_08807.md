# [?] fix panic etherman (#3133)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2024-01-24
Source: https://github.com/0xPolygon/zkevm-node/commit/c3dddf79b228c8f190c8cad71807a56599d6ef18
Type: security-commit

## Details
fix panic etherman (#3133)

## Patch
### etherman/etherman.go
```diff
@@ -215,6 +215,10 @@ func NewClient(cfg Config, l1Config L1Config) (*Client, error) {
 	if err != nil {
 		return nil, err
 	}
+	oldGlobalExitRoot, err := oldpolygonzkevmglobalexitroot.NewOldpolygonzkevmglobalexitroot(l1Config.GlobalExitRootManagerAddr, ethClient)
+	if err != nil {
+		return nil, err
+	}
 	pol, err := pol.NewPol(l1Config.PolAddr, ethClient)
 	if err != nil {
 		return nil, err
@@ -241,14 +245,15 @@ func NewClient(cfg Config, l1Config L1Config) (*Client, error) {
 	log.Debug("rollupID: ", rollupID)
 
 	return &Client{
-		EthClient:             ethClient,
-		ZkEVM:                 zkevm,
-		OldZkEVM:              oldZkevm,
-		RollupManager:         rollupManager,
-		Pol:                   pol,
-		GlobalExitRootManager: globalExitRoot,
-		SCAddresses:           scAddresses,
-		RollupID:              rollupID,
+		EthClient:                ethClient,
+		ZkEVM:                    zkevm,
+		OldZkEVM:                 oldZkevm,
+		RollupManager:            rollupManager,
+		Pol:                      pol,
+		GlobalExitRootManager:    globalExitRoot,
+		OldGlobalExitRootManager: oldGlobalExitRoot,
+		SCAddresses:              scAddresses,
+		RollupID:                 rollupID,
 		GasProviders: externalGasProviders{
 			MultiGasProvider: cfg.MultiGasProvider,
 			Providers:        gProviders,
```
