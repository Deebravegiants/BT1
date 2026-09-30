# [?] fix(load): totalSupply overflow (#4244)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-09-04
Source: https://github.com/ava-labs/avalanchego/commit/41b296eb9112236369d188a539d10ac6e60bf6b7
Type: security-commit

## Details
fix(load): totalSupply overflow (#4244)

## Patch
### tests/load/main/main.go
```diff
@@ -168,10 +168,10 @@ func newTokenContract(
 	}
 
 	var (
-		totalRecipients = int64(len(recipients) + 1)
+		totalRecipients = big.NewInt(int64(len(recipients)) + 1)
 		// assumes that token has 18 decimals
 		recipientAmount = big.NewInt(1e18)
-		totalSupply     = big.NewInt(totalRecipients * 1e18)
+		totalSupply     = new(big.Int).Mul(totalRecipients, recipientAmount)
 	)
 
 	_, tx, contract, err := contracts.DeployERC20(txOpts, client, totalSupply)
```
