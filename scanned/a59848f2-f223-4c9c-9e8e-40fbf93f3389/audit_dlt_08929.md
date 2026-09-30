# [?] bridge/e2e: fix panic in testSolanaToTerraLockup

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-01-25
Source: https://github.com/wormhole-foundation/wormhole/commit/7201b64a77c23f06f1f0ebfba7074422d5532f81
Type: security-commit

## Details
bridge/e2e: fix panic in testSolanaToTerraLockup

## Patch
### bridge/e2e/solana.go
```diff
@@ -131,6 +131,7 @@ func testSolanaToTerraLockup(t *testing.T, ctx context.Context, tc *TerraClient,
 	// Get balance if deployed
 	beforeCw20, err := getTerraBalance(ctx, terraToken)
 	if err != nil {
+		beforeCw20 = new(big.Int)
 		t.Log(err) // account may not yet exist, defaults to 0
 	}
 	t.Logf("CW20 balance: %v", beforeCw20)
```
