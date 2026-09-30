# [?] Add test that breaks poseidon due to a security issue

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/go-iden3-crypto
Published: 2019-12-16
Source: https://github.com/iden3/go-iden3-crypto/commit/27ec5b26df8cb53951fc81f9351f200f9d597b18
Type: security-commit

## Details
Add test that breaks poseidon due to a security issue

## Patch
### poseidon/poseidon.go
```diff
@@ -168,15 +168,15 @@ func Hash(arr []*big.Int) (*big.Int, error) {
 
 	r := constants.fqR.Zero()
 	for i := 0; i < len(arr); i = i + 5 {
-		var fiveElems []*big.Int
+		var fiveElems [5]*big.Int
 		for j := 0; j < 5; j++ {
 			if i+j < len(arr) {
-				fiveElems = append(fiveElems, arr[i+j])
+				fiveElems[j] = arr[i+j]
 			} else {
-				fiveElems = append(fiveElems, big.NewInt(int64(0)))
+				fiveElems[j] = _constants.Zero
 			}
 		}
-		ph, err := PoseidonHash(fiveElems)
+		ph, err := PoseidonHash(fiveElems[:])
 		if err != nil {
 			return nil, err
 		}
```

### poseidon/poseidon_test.go
```diff
@@ -66,6 +66,16 @@ func TestPoseidon(t *testing.T) {
 	assert.Equal(t, "10747013384255785702102976082726575658403084163954725275481577373644732938016", hmsg2.String())
 }
 
+func TestPoseidonBroken(t *testing.T) {
+	h1, err := Hash([]*big.Int{big.NewInt(0), big.NewInt(1), big.NewInt(2), big.NewInt(3), big.NewInt(4),
+		big.NewInt(5), big.NewInt(6), big.NewInt(7), big.NewInt(8), big.NewInt(9)})
+	assert.Nil(t, err)
+	h2, err := Hash([]*big.Int{big.NewInt(5), big.NewInt(6), big.NewInt(7), big.NewInt(8), big.NewInt(9),
+		big.NewInt(0), big.NewInt(1), big.NewInt(2), big.NewInt(3), big.NewInt(4)})
+	assert.Nil(t, err)
+	assert.NotEqual(t, h1, h2)
+}
+
 func BenchmarkPoseidon(b *testing.B) {
 	b12 := big.NewInt(int64(12))
 	b45 := big.NewInt(int64(45))
```
