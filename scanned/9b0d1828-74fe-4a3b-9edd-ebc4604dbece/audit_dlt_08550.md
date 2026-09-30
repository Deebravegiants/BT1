# [?] fix code panic on 0 divisor

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-07-28
Source: https://github.com/algorand/go-algorand/commit/5d753c0c8146b8e31c16de01e66699408eb88b49
Type: security-commit

## Details
fix code panic on 0 divisor

## Patch
### crypto/merklekeystore/keystore.go
```diff
@@ -127,7 +127,8 @@ func New(firstValid, lastValid, divisor uint64, sigAlgoType crypto.AlgorithmType
 	firstRound := indexToRound(firstValid, divisor, 0)
 
 	if numberOfKeys == 0 {
-		return &Signer{}, nil
+		// always outputs a valid signer that doesn't crash.
+		return &Signer{EphemeralKeys: EphemeralKeys{Divisor: divisor}}, nil
 	}
 
 	keys := make([]crypto.SignatureAlgorithm, numberOfKeys)
```

### crypto/merklekeystore/keystore_test.go
```diff
@@ -30,7 +30,7 @@ func TestSignerCreation(t *testing.T) {
 	a := require.New(t)
 
 	h := genHashableForTest()
-	for i := uint64(0); i < 20; i++ {
+	for i := uint64(1); i < 20; i++ {
 		signer, err := New(i, i+1, 1, crypto.PlaceHolderType)
 		a.NoError(err)
 		_, err = signer.Sign(h, i)
@@ -47,7 +47,9 @@ func TestSignerCreation(t *testing.T) {
 	a.NoError(signer.GetVerifier().Verify(2, 2, genHashableForTest(), sig))
 	a.Equal(1, len(signer.EphemeralKeys.SignatureAlgorithms))
 
-	_, err = New(2, 2, 3, crypto.PlaceHolderType)
+	signer, err = New(2, 2, 3, crypto.PlaceHolderType)
+	a.NoError(err)
+	_, err = signer.Sign(genHashableForTest(), 2)
 	a.Error(err)
 
 	s, err := New(8, 21, 10, crypto.PlaceHolderType)
@@ -66,7 +68,10 @@ func TestSignerCreation(t *testing.T) {
 	a.NoError(err)
 	a.Equal(len(s.EphemeralKeys.SignatureAlgorithms), 1)
 
-	_, err = New(11, 19, 10, crypto.PlaceHolderType)
+	s, err = New(11, 19, 10, crypto.PlaceHolderType)
+	a.NoError(err)
+	a.Equal(0, len(s.EphemeralKeys.SignatureAlgorithms))
+	_, err = signer.Sign(genHashableForTest(), 2)
 	a.Error(err)
 }
 
@@ -75,10 +80,10 @@ func TestDisposableKeyPositions(t *testing.T) {
 	signer, err := New(0, 100, 1, crypto.PlaceHolderType)
 	a.NoError(err)
 
-	for i := uint64(0); i < 100; i++ {
+	for i := uint64(1); i < 100; i++ {
 		pos, err := signer.getKeyPosition(i)
 		a.NoError(err, i)
-		a.Equal(i, pos)
+		a.Equal(i-1, pos)
 	}
 
 	_, err = signer.getKeyPosition(101)
```
