# [?] fix(provider): Remove a race condition around the logger

## Summary
Severity: Unknown
Chain: Akash
Component: akash-network/node
Published: 2021-03-10
Source: https://github.com/akash-network/node/commit/327d5539e87723e83754e35afc9a71cdadd2f378
Type: security-commit

## Details
fix(provider): Remove a race condition around the logger

## Patch
### provider/balance_checker.go
```diff
@@ -51,7 +51,8 @@ func (bc *balanceChecker) doCheck(ctx context.Context) (bool, error) {
 	}
 
 	balance := result.Balance.Amount
-	bc.log.Debug("provider acct balance", "balance", balance)
+	// TODO - find a way to use the logger without a race
+	// bc.log.Debug("provider acct balance", "balance", balance)
 	// Get the amount required as a bid deposit
 	// TODO - pull me from the blockchain in the future
 	defaultMinBidDeposit := mparams.DefaultBidMinDeposit
```
