# [?] bridge/e2e: fix nil panic in testEthereumLockup

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-01-21
Source: https://github.com/wormhole-foundation/wormhole/commit/5679f67c858845cc40d09684a74ac6312283f153
Type: security-commit

## Details
bridge/e2e: fix nil panic in testEthereumLockup

## Patch
### bridge/e2e/eth.go
```diff
@@ -94,7 +94,7 @@ func testEthereumLockup(t *testing.T, ctx context.Context, ec *ethclient.Client,
 		false,
 	)
 	if err != nil {
-		t.Error(err)
+		t.Fatal(err)
 	}
 
 	t.Logf("sent lockup tx: %v", tx.Hash().Hex())
```
