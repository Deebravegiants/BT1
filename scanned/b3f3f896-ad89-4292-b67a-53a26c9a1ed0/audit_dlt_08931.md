# [?] Fix crash when testSolanaLockup is executed for the first time

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-01-19
Source: https://github.com/wormhole-foundation/wormhole/commit/d0d00f4972cc9aa16947aa396961eba7863ac866
Type: security-commit

## Details
Fix crash when testSolanaLockup is executed for the first time

We forgot to initialize the big.Int.

## Patch
### bridge/e2e/solana.go
```diff
@@ -79,6 +79,7 @@ func testSolanaLockup(t *testing.T, ctx context.Context, ec *ethclient.Client, c
 	// Store balance of wrapped destination token
 	beforeErc20, err := token.BalanceOf(nil, devnet.GanacheClientDefaultAccountAddress)
 	if err != nil {
+		beforeErc20 = new(big.Int)
 		t.Log(err) // account may not yet exist, defaults to 0
 	}
 	t.Logf("ERC20 balance: %v", beforeErc20)
```
