# [?] accounts/abi/bind: fix data race in TestWaitDeployedCornerCases (#32740)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-09-25
Source: https://github.com/ethereum/go-ethereum/commit/7611f351c18de983c49544f09aa042bd0403243b
Type: security-commit

## Details
accounts/abi/bind: fix data race in TestWaitDeployedCornerCases (#32740)

Fixes race in WaitDeploy test where the backend is closed before goroutine using it wraps up.

---------

Co-authored-by: lightclient <lightclient@protonmail.com>

## Patch
### accounts/abi/bind/v2/util_test.go
```diff
@@ -100,22 +100,29 @@ func TestWaitDeployed(t *testing.T) {
 }
 
 func TestWaitDeployedCornerCases(t *testing.T) {
-	backend := simulated.NewBackend(
-		types.GenesisAlloc{
-			crypto.PubkeyToAddress(testKey.PublicKey): {Balance: big.NewInt(10000000000000000)},
-		},
+	var (
+		backend = simulated.NewBackend(
+			types.GenesisAlloc{
+				crypto.PubkeyToAddress(testKey.PublicKey): {Balance: big.NewInt(10000000000000000)},
+			},
+		)
+		head, _     = backend.Client().HeaderByNumber(t.Context(), nil) // Should be child's, good enough
+		gasPrice    = new(big.Int).Add(head.BaseFee, big.NewInt(1))
+		signer      = types.LatestSigner(params.AllDevChainProtocolChanges)
+		code        = common.FromHex("6060604052600a8060106000396000f360606040526008565b00")
+		ctx, cancel = context.WithCancel(t.Context())
 	)
 	defer backend.Close()
 
-	head, _ := backend.Client().HeaderByNumber(context.Background(), nil) // Should be child's, good enough
-	gasPrice := new(big.Int).Add(head.BaseFee, big.NewInt(1))
-
-	// Create a transaction to an account.
-	code := "6060604052600a8060106000396000f360606040526008565b00"
-	tx := types.NewTransaction(0, common.HexToAddress("0x01"), big.NewInt(0), 3000000, gasPrice, common.FromHex(code))
-	tx, _ = types.SignTx(tx, types.LatestSigner(params.AllDevChainProtocolChanges), testKey)
-	ctx, cancel := context.WithCancel(context.Background())
-	defer cancel()
+	// 1. WaitDeploy on a transaction that does not deploy a contract, verify it
+	// returns an error.
+	tx := types.MustSignNewTx(testKey, signer, &types.LegacyTx{
+		Nonce:    0,
+		To:       &common.Address{0x01},
+		Gas:      300000,
+		GasPrice: gasPrice,
+		Data:     code,
+	})
 	if err := backend.Client().SendTransaction(ctx, tx); err != nil {
 		t.Errorf("failed to send transaction: %q", err)
 	}
@@ -124,19 +131,35 @@ func TestWaitDeployedCornerCases(t *testing.T) {
 		t.Errorf("error mismatch: want %q, got %q, ", bind.ErrNoAddressInReceipt, err)
 	}
 
-	// Create a transaction that is not mined.
-	tx = types.NewContractCreation(1, big.NewInt(0), 3000000, gasPrice, common.FromHex(code))
-	tx, _ = types.SignTx(tx, types.LatestSigner(params.AllDevChainProtocolChanges), testKey)
-
+	// 2. Create a contract, but cancel the WaitDeploy before it is mined.
+	tx = types.MustSignNewTx(testKey, signer, &types.LegacyTx{
+		Nonce:    1,
+		Gas:      300000,
+		GasPrice: gasPrice,
+		Data:     code,
+	})
+
+	// Wait in another thread so that we can quickly cancel it after submitting
+	// the transaction.
+	done := make(chan struct{})
 	go func() {
-		contextCanceled := errors.New("context canceled")
-		if _, err := bind.WaitDeployed(ctx, backend.Client(), tx.Hash()); err.Error() != contextCanceled.Error() {
-			t.Errorf("error mismatch: want %q, got %q, ", contextCanceled, err)
+		defer close(done)
+		want := errors.New("context canceled")
+		_, err := bind.WaitDeployed(ctx, backend.Client(), tx.Hash())
+		if err == nil || errors.Is(want, err) {
+			t.Errorf("error mismatch: want %v, got %v", want, err)
 		}
 	}()
 
 	if err := backend.Client().SendTransaction(ctx, tx); err != nil {
 		t.Errorf("failed to send transaction: %q", err)
 	}
 	cancel()
+
+	// Wait for goroutine to exit or for a timeout.
+	select {
+	case <-done:
+	case <-time.After(time.Second * 2):
+		t.Fatalf("failed to cancel wait deploy")
+	}
 }
```
