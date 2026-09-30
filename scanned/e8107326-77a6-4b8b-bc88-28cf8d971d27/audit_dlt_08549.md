# [?] fix: bug in new signer - overflow in roundToIndex, fixed by explicit writing the formula

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-08-01
Source: https://github.com/algorand/go-algorand/commit/ac77b5723d619f2d578163bac0a30f8586cd4246
Type: security-commit

## Details
fix: bug in new signer - overflow in roundToIndex, fixed by explicit writing the formula

## Patch
### crypto/merklekeystore/keystore.go
```diff
@@ -116,11 +116,12 @@ func New(firstValid, lastValid, interval uint64, sigAlgoType crypto.AlgorithmTyp
 		return nil, errDivisorIsZero
 	}
 	if firstValid == 0 {
-		firstValid++
+		firstValid = 1
 	}
 
 	// calculates the number of indices from first valid round and up to lastValid.
-	numberOfKeys := roundToIndex(firstValid, lastValid, interval) + 1
+	// writing this explicit calculation to avoid overflow.
+	numberOfKeys := lastValid/interval - ((firstValid - 1) / interval)
 	keys := make([]crypto.SignatureAlgorithm, numberOfKeys)
 	for i := range keys {
 		keys[i] = *crypto.NewSigner(sigAlgoType)
```

### crypto/merklekeystore/keystore_test.go
```diff
@@ -42,13 +42,17 @@ func TestSignerCreation(t *testing.T) {
 
 	signer, err := New(2, 2, 2, crypto.PlaceHolderType)
 	a.NoError(err)
+	a.Equal(1, len(signer.SignatureAlgorithms))
+
 	sig, err := signer.Sign(genHashableForTest(), 2)
 	a.NoError(err)
 	a.NoError(signer.GetVerifier().Verify(2, 2, 2, genHashableForTest(), sig))
-	a.Equal(1, len(signer.SignatureAlgorithms))
+
 
 	signer, err = New(2, 2, 3, crypto.PlaceHolderType)
 	a.NoError(err)
+	a.Equal(0, len(signer.SignatureAlgorithms))
+
 	_, err = signer.Sign(genHashableForTest(), 2)
 	a.Error(err)
 
```
