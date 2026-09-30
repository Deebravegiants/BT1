# [?] internal/ethapi: fix nil deref + fix estimateGas console bindings (#21601)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-09-23
Source: https://github.com/ethereum/go-ethereum/commit/c1544423d655f540b55bb6ec0e7167dad9683c42
Type: security-commit

## Details
internal/ethapi: fix nil deref + fix estimateGas console bindings (#21601)

* tried to fix

* fix for js api

* fix for nil pointer ex

* rev space

* rev space

* input call formatter

## Patch
### internal/ethapi/api.go
```diff
@@ -963,6 +963,9 @@ func DoEstimateGas(ctx context.Context, b Backend, args CallArgs, blockNrOrHash
 		if err != nil {
 			return 0, err
 		}
+		if block == nil {
+			return 0, errors.New("block not found")
+		}
 		hi = block.GasLimit()
 	}
 	// Recap the highest gas limit with account's available balance.
```

### internal/web3ext/web3ext.go
```diff
@@ -500,6 +500,13 @@ web3._extend({
 			params: 1,
 			inputFormatter: [web3._extend.formatters.inputTransactionFormatter]
 		}),
+		new web3._extend.Method({
+			name: 'estimateGas',
+			call: 'eth_estimateGas',
+			params: 2,
+			inputFormatter: [web3._extend.formatters.inputCallFormatter, web3._extend.formatters.inputBlockNumberFormatter],
+			outputFormatter: web3._extend.utils.toDecimal
+		}),
 		new web3._extend.Method({
 			name: 'submitTransaction',
 			call: 'eth_submitTransaction',
```
