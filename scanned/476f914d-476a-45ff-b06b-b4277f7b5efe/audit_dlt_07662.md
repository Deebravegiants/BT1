# [?] execution/types: fix panic on invalid signature length (#18734)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-01-23
Source: https://github.com/erigontech/erigon/commit/8f95619a60c97d7dac23e49ba63ef7f34e1ffad5
Type: security-commit

## Details
execution/types: fix panic on invalid signature length (#18734)

Make `decodeSignature` fail gracefully by returning an error on invalid
input, and adjust callers to handle the error accordingly.

## Patch
### execution/types/transaction_signing.go
```diff
@@ -328,7 +328,10 @@ func (sg Signer) SenderWithContext(context *secp256k1.Context, txn Transaction)
 func (sg Signer) SignatureValues(txn Transaction, sig []byte) (R, S, V *uint256.Int, err error) {
 	switch t := txn.(type) {
 	case *LegacyTx:
-		R, S, V = decodeSignature(sig)
+		R, S, V, err = decodeSignature(sig)
+		if err != nil {
+			return nil, nil, nil, err
+		}
 		if sg.chainID.IsZero() {
 			V.Add(V, &u256.Num27)
 		} else {
@@ -342,7 +345,10 @@ func (sg Signer) SignatureValues(txn Transaction, sig []byte) (R, S, V *uint256.
 		if chainId != nil && !chainId.IsZero() && !chainId.Eq(&sg.chainID) {
 			return nil, nil, nil, ErrInvalidChainId
 		}
-		R, S, V = decodeSignature(sig)
+		R, S, V, err = decodeSignature(sig)
+		if err != nil {
+			return nil, nil, nil, err
+		}
 	default:
 		return nil, nil, nil, ErrTxTypeNotSupported
 	}
@@ -365,14 +371,14 @@ func (sg Signer) Equal(other Signer) bool {
 		sg.setCode == other.setCode
 }
 
-func decodeSignature(sig []byte) (r, s, v *uint256.Int) {
+func decodeSignature(sig []byte) (r, s, v *uint256.Int, err error) {
 	if len(sig) != crypto.SignatureLength {
-		panic(fmt.Sprintf("wrong size for signature: got %d, want %d", len(sig), crypto.SignatureLength))
+		return nil, nil, nil, fmt.Errorf("wrong size for signature: got %d, want %d", len(sig), crypto.SignatureLength)
 	}
 	r = new(uint256.Int).SetBytes(sig[:32])
 	s = new(uint256.Int).SetBytes(sig[32:64])
 	v = new(uint256.Int).SetBytes(sig[64:65])
-	return r, s, v
+	return r, s, v, nil
 }
 
 func recoverPlain(context *secp256k1.Context, sighash common.Hash, R, S, Vb *uint256.Int, homestead bool) (accounts.Address, error) {
```

### execution/types/transaction_signing_test.go
```diff
@@ -165,3 +165,28 @@ func TestChainId(t *testing.T) {
 		t.Error("expected no error")
 	}
 }
+
+func TestSignatureValuesError(t *testing.T) {
+	// 1. Setup a valid transaction
+	tx := NewTransaction(0, common.Address{}, new(uint256.Int), 0, new(uint256.Int), nil)
+	signer := LatestSignerForChainID(big.NewInt(18))
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
+		_, err := tx.WithSignature(*signer, invalidSig)
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
