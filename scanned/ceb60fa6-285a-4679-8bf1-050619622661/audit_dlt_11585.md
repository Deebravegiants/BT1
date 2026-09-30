# [?] fix(ci): fix gosec reported vulnerabilities (#897)

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2022-09-14
Source: https://github.com/evmos/evmos/commit/4ce0a3453efe538b5e1369572b909fb2154c51e0
Type: security-commit

## Details
fix(ci): fix gosec reported vulnerabilities (#897)

* Add #nosec to offending lines

* Update permissions to fix upload SARIF permission issue

* Fix gosec caught vulnerabilities

* Update gosec action from informalsystems/gosec to cosmos/gosec

* Comment out upload sarif step in security.yaml pending fix

## Patch
### .github/workflows/security.yml
```diff
@@ -7,6 +7,9 @@ on:
 
 jobs:
   Gosec:
+    permissions:
+      security-events: write
+
     runs-on: ubuntu-latest
     env:
       GO111MODULE: on
@@ -21,14 +24,15 @@ jobs:
             go.mod
             go.sum
       - name: Run Gosec Security Scanner
-        uses: informalsystems/gosec@master
+        uses: cosmos/gosec@master
         with:
           # we let the report trigger content trigger a failure using the GitHub Security features.
-          args: '-no-fail -fmt sarif -out results.sarif ./...'
-        if: "env.GIT_DIFF_FILTERED != ''"
-      - name: Upload SARIF file
-        uses: github/codeql-action/upload-sarif@v2
-        with:
-          # Path to SARIF file relative to the root of the repository
-          sarif_file: results.sarif
+          args: "-no-fail -fmt sarif -out results.sarif ./..."
         if: "env.GIT_DIFF_FILTERED != ''"
+      # TODO uncomment below when https://github.com/cosmos/gosec/issues/38 is resolved
+      # - name: Upload SARIF file
+      #   uses: github/codeql-action/upload-sarif@v2
+      #   with:
+      #     # Path to SARIF file relative to the root of the repository
+      #     sarif_file: results.sarif
+      #   if: "env.GIT_DIFF_FILTERED != ''"
```

### app/app.go
```diff
@@ -8,6 +8,7 @@ import (
 	"net/http"
 	"os"
 	"path/filepath"
+	"sort"
 
 	"github.com/gorilla/mux"
 	"github.com/rakyll/statik/fs"
@@ -855,7 +856,14 @@ func (app *Evmos) LoadHeight(height int64) error {
 // ModuleAccountAddrs returns all the app's module account addresses.
 func (app *Evmos) ModuleAccountAddrs() map[string]bool {
 	modAccAddrs := make(map[string]bool)
-	for acc := range maccPerms {
+
+	accs := make([]string, 0, len(maccPerms))
+	for k := range maccPerms {
+		accs = append(accs, k)
+	}
+	sort.Strings(accs)
+
+	for _, acc := range accs {
 		modAccAddrs[authtypes.NewModuleAddress(acc).String()] = true
 	}
 
@@ -866,7 +874,14 @@ func (app *Evmos) ModuleAccountAddrs() map[string]bool {
 // allowed to receive external tokens.
 func (app *Evmos) BlockedAddrs() map[string]bool {
 	blockedAddrs := make(map[string]bool)
-	for acc := range maccPerms {
+
+	accs := make([]string, 0, len(maccPerms))
+	for k := range maccPerms {
+		accs = append(accs, k)
+	}
+	sort.Strings(accs)
+
+	for _, acc := range accs {
 		blockedAddrs[authtypes.NewModuleAddress(acc).String()] = !allowedReceivingModAcc[acc]
 	}
 
```

### x/incentives/genesis.go
```diff
@@ -1,6 +1,8 @@
 package incentives
 
 import (
+	"sort"
+
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	authkeeper "github.com/cosmos/cosmos-sdk/x/auth/keeper"
 
@@ -35,10 +37,16 @@ func InitGenesis(
 	}
 
 	// Set allocation meters
-	for denom, amount := range allocationMeters {
+	denoms := make([]string, 0, len(allocationMeters))
+	for k := range allocationMeters {
+		denoms = append(denoms, k)
+	}
+	sort.Strings(denoms)
+
+	for _, denom := range denoms {
 		am := sdk.DecCoin{
 			Denom:  denom,
-			Amount: amount,
+			Amount: allocationMeters[denom],
 		}
 		k.SetAllocationMeter(ctx, am)
 	}
```
