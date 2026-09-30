# [?] op-deployer: Fix invalid intent panic in SR command (#13006)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-11-21
Source: https://github.com/bobanetwork/boba/commit/042433b89ce38ccc15456e9673829f6783bb97ac
Type: security-commit

## Details
op-deployer: Fix invalid intent panic in SR command (#13006)

## Patch
### op-deployer/pkg/deployer/inspect/superchain_registry.go
```diff
@@ -28,6 +28,10 @@ func SuperchainRegistryCLI(cliCtx *cli.Context) error {
 		return fmt.Errorf("failed to read intent: %w", err)
 	}
 
+	if err := globalIntent.Check(); err != nil {
+		return fmt.Errorf("intent check failed: %w", err)
+	}
+
 	envVars := map[string]string{}
 	envVars["SCR_CHAIN_NAME"] = ""
 	envVars["SCR_CHAIN_SHORT_NAME"] = ""
```

### op-deployer/pkg/deployer/state/intent.go
```diff
@@ -1,6 +1,7 @@
 package state
 
 import (
+	"errors"
 	"fmt"
 	"math/big"
 
@@ -67,11 +68,11 @@ func (c *Intent) Check() error {
 	}
 
 	if c.L1ContractsLocator == nil {
-		c.L1ContractsLocator = artifacts.DefaultL1ContractsLocator
+		return errors.New("l1ContractsLocator must be set")
 	}
 
 	if c.L2ContractsLocator == nil {
-		c.L2ContractsLocator = artifacts.DefaultL2ContractsLocator
+		return errors.New("l2ContractsLocator must be set")
 	}
 
 	var err error
```
