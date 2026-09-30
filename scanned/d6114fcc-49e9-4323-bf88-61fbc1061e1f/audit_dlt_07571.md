# [?] core/types: fix panic on invalid signature length (#33647)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-01-21
Source: https://github.com/ethereum/go-ethereum/commit/8fad02ac63a1c0972f47b7c5b41d5577fa4d2932
Type: security-commit

## Details
core/types: fix panic on invalid signature length (#33647)

Replace panic with error return in decodeSignature to prevent crashes on
invalid inputs, and update callers to propagate the error.

## Patch
### core/types/transaction_signing.go
```diff
@@ -282,7 +282,10 @@ func (s *modernSigner) SignatureValues(tx *Transaction, sig []byte) (R, S, V *bi
 	if tx.inner.chainID().Sign() != 0 && tx.inner.chainID().Cmp(s.chainID) != 0 {
 		return nil, nil, nil, fmt.Errorf("%w: have %d want %d", ErrInvalidChainId, tx.inner.chainID(), s.chainID)
 	}
-	R, S, _ = decodeSignature(sig)
+	R, S, _, err = decodeSignature(sig)
+	if err != nil {
+		return nil, nil, nil, err
+	}
 	V = big.NewInt(int64(sig[64]))
 	return R, S, V, nil
 }
@@ -373,7 +376,10 @@ func (s EIP155Signer) SignatureValues(tx *Transaction, sig []byte) (R, S, V *big
 	if tx.Type() != LegacyTxType {
 		return nil, nil, nil, ErrTxTypeNotSupported
 	}
-	R, S, V = decodeSignature(sig)
+	R, S, V, err = decodeSignature(sig)
+	if err != nil {
+		return nil, nil, nil, err
+	}
 	if s.chainId.Sign() != 0 {
 		V = big.NewInt(int64(sig[64] + 35))
 		V.Add(V, s.chainIdMul)
@@ -442,8 +448,8 @@ func (fs FrontierSigner) SignatureValues(tx *Transaction, sig []byte) (r, s, v *
 	if tx.Type() != LegacyTxType {
 		return nil, nil, nil, ErrTxTypeNotSupported
 	}
-	r, s, v = decodeSignature(sig)
-	return r, s, v, nil
+	r, s, v, err = decodeSignature(sig)
+	return r, s, v, err
 }
 
 // Hash returns the hash to be signed by the sender.
@@ -459,14 +465,14 @@ func (fs FrontierSigner) Hash(tx *Transaction) common.Hash {
 	})
 }
 
-func decodeSignature(sig []byte) (r, s, v *big.Int) {
+func decodeSignature(sig []byte) (r, s, v *big.Int, err error) {
 	if len(sig) != crypto.SignatureLength {
-		panic(fmt.Sprintf("wrong size for signature: got %d, want %d", len(sig), crypto.SignatureLength))
+		return nil, nil, nil, fmt.Errorf("wrong size for signature: got %d, want %d", len(sig), crypto.SignatureLength)
 	}
 	r = new(big.Int).SetBytes(sig[:32])
 	s = new(big.Int).SetBytes(sig[32:64])
 	v = new(big.Int).SetBytes([]byte{sig[64] + 27})
-	return r, s, v
+	return r, s, v, nil
 }
 
 func recoverPlain(sighash common.Hash, R, S, Vb *big.Int, homestead bool) (common.Address, error) {
```

### core/types/transaction_signing_test.go
```diff
@@ -200,3 +200,28 @@ func Benchmark_modernSigner_Equal(b *testing.B) {
 		}
 	}
 }
+
+func TestSignatureValuesError(t *testing.T) {
+	// 1. Setup a valid transaction
+	tx := NewTransaction(0, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil)
+	signer := HomesteadSigner{}
+
+	// 2. Call WithSignature with invalid length sig (not 65 bytes)
+	invalidSig := make([]byte, 64)
+
+	func() {
+		defer func() {
+			if r := recover(); r != nil {
+				t.Fatalf("Panicked for invalid signature length, expected error: %v", r)
+			}
+		}()
+		_, err := tx.WithSignature(signer, invalidSig)
+		if err == nil {
+			t.Fatal("Expected error for invalid signature length, got nil")
+		} else {
+			// This is just a sanity check to ensure we got an error,
+			// the exact error message is verified in unit tests elsewhere if needed.
+			t.Logf("Got expected error: %v", err)
+		}
+	}()
+}
```

### core/types/tx_setcode.go
```diff
@@ -94,7 +94,10 @@ func SignSetCode(prv *ecdsa.PrivateKey, auth SetCodeAuthorization) (SetCodeAutho
 	if err != nil {
 		return SetCodeAuthorization{}, err
 	}
-	r, s, _ := decodeSignature(sig)
+	r, s, _, err := decodeSignature(sig)
+	if err != nil {
+		return SetCodeAuthorization{}, err
+	}
 	return SetCodeAuthorization{
 		ChainID: auth.ChainID,
 		Address: auth.Address,
```
