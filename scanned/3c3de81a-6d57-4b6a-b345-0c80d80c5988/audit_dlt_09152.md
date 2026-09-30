# [?] fix: deadlock in balance shutdown (#14125)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-08-15
Source: https://github.com/smartcontractkit/chainlink/commit/8fa8c3a07512bb8358abdabc3fdcc8ae310c6c1c
Type: security-commit

## Details
fix: deadlock in balance shutdown (#14125)

* fix: deadlock in balance shutdown

* bump dependency

## Patch
### .changeset/tasty-windows-own.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+#bugfix balance shutdown deadlock
```

### core/chains/evm/monitor/balance.go
```diff
@@ -82,17 +82,13 @@ func (bm *balanceMonitor) close() error {
 
 // OnNewLongestChain checks the balance for each key
 func (bm *balanceMonitor) OnNewLongestChain(_ context.Context, _ *evmtypes.Head) {
-	ok := bm.sleeperTask.IfStarted(bm.checkBalances)
+	bm.eng.Debugw("BalanceMonitor: signalling balance worker")
+	ok := bm.sleeperTask.WakeUpIfStarted()
 	if !ok {
 		bm.eng.Debugw("BalanceMonitor: ignoring OnNewLongestChain call, balance monitor is not started", "state", bm.sleeperTask.State())
 	}
 }
 
-func (bm *balanceMonitor) checkBalances() {
-	bm.eng.Debugw("BalanceMonitor: signalling balance worker")
-	bm.sleeperTask.WakeUp()
-}
-
 func (bm *balanceMonitor) updateBalance(ethBal assets.Eth, address gethCommon.Address) {
 	bm.promUpdateEthBalance(&ethBal, address)
 
```

### core/scripts/go.mod
```diff
@@ -22,7 +22,7 @@ require (
 	github.com/prometheus/client_golang v1.17.0
 	github.com/shopspring/decimal v1.4.0
 	github.com/smartcontractkit/chainlink-automation v1.0.4
-	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad
+	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4
 	github.com/smartcontractkit/chainlink/v2 v2.0.0-00010101000000-000000000000
 	github.com/smartcontractkit/libocr v0.0.0-20240717100443-f6226e09bee7
 	github.com/spf13/cobra v1.8.0
```

### core/scripts/go.sum
```diff
@@ -1186,8 +1186,8 @@ github.com/smartcontractkit/chainlink-automation v1.0.4 h1:iyW181JjKHLNMnDleI8um
 github.com/smartcontractkit/chainlink-automation v1.0.4/go.mod h1:u4NbPZKJ5XiayfKHD/v3z3iflQWqvtdhj13jVZXj/cM=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95 h1:LAgJTg9Yr/uCo2g7Krp88Dco2U45Y6sbJVl8uKoLkys=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95/go.mod h1:/ZWraCBaDDgaIN1prixYcbVvIk/6HeED9+8zbWQ+TMo=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad h1:QmXA8j7f1gNK52dRuW78ZAbzTRlv62fRZQdp0aYFJmc=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4 h1:5x4kknDjui1m1E5Ad6oXc/sFi6nPN2cQqUfSIdwr5iQ=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45 h1:NBQLtqk8zsyY4qTJs+NElI3aDFTcAo83JHvqD04EvB0=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45/go.mod h1:LV0h7QBQUpoC2UUi6TcUvcIFm1xjP/DtEcqV8+qeLUs=
 github.com/smartcontractkit/chainlink-data-streams v0.0.0-20240801131703-fd75761c982f h1:I9fTBJpHkeldFplXUy71eLIn6A6GxuR4xrABoUeD+CM=
```

### go.mod
```diff
@@ -75,7 +75,7 @@ require (
 	github.com/smartcontractkit/chain-selectors v1.0.10
 	github.com/smartcontractkit/chainlink-automation v1.0.4
 	github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95
-	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad
+	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4
 	github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45
 	github.com/smartcontractkit/chainlink-data-streams v0.0.0-20240801131703-fd75761c982f
 	github.com/smartcontractkit/chainlink-feeds v0.0.0-20240710170203-5b41615da827
```

### go.sum
```diff
@@ -1141,8 +1141,8 @@ github.com/smartcontractkit/chainlink-automation v1.0.4 h1:iyW181JjKHLNMnDleI8um
 github.com/smartcontractkit/chainlink-automation v1.0.4/go.mod h1:u4NbPZKJ5XiayfKHD/v3z3iflQWqvtdhj13jVZXj/cM=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95 h1:LAgJTg9Yr/uCo2g7Krp88Dco2U45Y6sbJVl8uKoLkys=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95/go.mod h1:/ZWraCBaDDgaIN1prixYcbVvIk/6HeED9+8zbWQ+TMo=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad h1:QmXA8j7f1gNK52dRuW78ZAbzTRlv62fRZQdp0aYFJmc=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4 h1:5x4kknDjui1m1E5Ad6oXc/sFi6nPN2cQqUfSIdwr5iQ=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45 h1:NBQLtqk8zsyY4qTJs+NElI3aDFTcAo83JHvqD04EvB0=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45/go.mod h1:LV0h7QBQUpoC2UUi6TcUvcIFm1xjP/DtEcqV8+qeLUs=
 github.com/smartcontractkit/chainlink-data-streams v0.0.0-20240801131703-fd75761c982f h1:I9fTBJpHkeldFplXUy71eLIn6A6GxuR4xrABoUeD+CM=
```

### integration-tests/go.mod
```diff
@@ -33,7 +33,7 @@ require (
 	github.com/slack-go/slack v0.12.2
 	github.com/smartcontractkit/chain-selectors v1.0.21
 	github.com/smartcontractkit/chainlink-automation v1.0.4
-	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad
+	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4
 	github.com/smartcontractkit/chainlink-testing-framework v1.34.2
 	github.com/smartcontractkit/chainlink-testing-framework/grafana v0.0.0-20240405215812-5a72bc9af239
 	github.com/smartcontractkit/chainlink/v2 v2.0.0-00010101000000-000000000000
```

### integration-tests/go.sum
```diff
@@ -1490,8 +1490,8 @@ github.com/smartcontractkit/chainlink-automation v1.0.4 h1:iyW181JjKHLNMnDleI8um
 github.com/smartcontractkit/chainlink-automation v1.0.4/go.mod h1:u4NbPZKJ5XiayfKHD/v3z3iflQWqvtdhj13jVZXj/cM=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95 h1:LAgJTg9Yr/uCo2g7Krp88Dco2U45Y6sbJVl8uKoLkys=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95/go.mod h1:/ZWraCBaDDgaIN1prixYcbVvIk/6HeED9+8zbWQ+TMo=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad h1:QmXA8j7f1gNK52dRuW78ZAbzTRlv62fRZQdp0aYFJmc=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4 h1:5x4kknDjui1m1E5Ad6oXc/sFi6nPN2cQqUfSIdwr5iQ=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45 h1:NBQLtqk8zsyY4qTJs+NElI3aDFTcAo83JHvqD04EvB0=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45/go.mod h1:LV0h7QBQUpoC2UUi6TcUvcIFm1xjP/DtEcqV8+qeLUs=
 github.com/smartcontractkit/chainlink-data-streams v0.0.0-20240801131703-fd75761c982f h1:I9fTBJpHkeldFplXUy71eLIn6A6GxuR4xrABoUeD+CM=
```

### integration-tests/load/go.mod
```diff
@@ -16,7 +16,7 @@ require (
 	github.com/rs/zerolog v1.31.0
 	github.com/slack-go/slack v0.12.2
 	github.com/smartcontractkit/chainlink-automation v1.0.4
-	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad
+	github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4
 	github.com/smartcontractkit/chainlink-testing-framework v1.34.2
 	github.com/smartcontractkit/chainlink/integration-tests v0.0.0-20240214231432-4ad5eb95178c
 	github.com/smartcontractkit/chainlink/v2 v2.9.0-beta0.0.20240216210048-da02459ddad8
```

### integration-tests/load/go.sum
```diff
@@ -1472,8 +1472,8 @@ github.com/smartcontractkit/chainlink-automation v1.0.4 h1:iyW181JjKHLNMnDleI8um
 github.com/smartcontractkit/chainlink-automation v1.0.4/go.mod h1:u4NbPZKJ5XiayfKHD/v3z3iflQWqvtdhj13jVZXj/cM=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95 h1:LAgJTg9Yr/uCo2g7Krp88Dco2U45Y6sbJVl8uKoLkys=
 github.com/smartcontractkit/chainlink-ccip v0.0.0-20240806144315-04ac101e9c95/go.mod h1:/ZWraCBaDDgaIN1prixYcbVvIk/6HeED9+8zbWQ+TMo=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad h1:QmXA8j7f1gNK52dRuW78ZAbzTRlv62fRZQdp0aYFJmc=
-github.com/smartcontractkit/chainlink-common v0.2.2-0.20240814082155-8b06c222c7ad/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4 h1:5x4kknDjui1m1E5Ad6oXc/sFi6nPN2cQqUfSIdwr5iQ=
+github.com/smartcontractkit/chainlink-common v0.2.2-0.20240815090511-4586e672b8e4/go.mod h1:Jg1sCTsbxg76YByI8ifpFby3FvVqISStHT8ypy9ocmY=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45 h1:NBQLtqk8zsyY4qTJs+NElI3aDFTcAo83JHvqD04EvB0=
 github.com/smartcontractkit/chainlink-cosmos v0.4.1-0.20240710121324-3ed288aa9b45/go.mod h1:LV0h7QBQUpoC2UUi6TcUvcIFm1xjP/DtEcqV8+qeLUs=
 github.com/smartcontractkit/chainlink-data-streams v0.0.0-20240801131703-fd75761c982f h1:I9fTBJpHkeldFplXUy71eLIn6A6GxuR4xrABoUeD+CM=
```
