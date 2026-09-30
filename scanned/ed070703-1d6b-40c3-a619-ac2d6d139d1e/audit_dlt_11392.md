# [?] fix: fixed panic

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2024-09-18
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/ec436b4c2b525f8bc5b1138147bbce59026a8148
Type: security-commit

## Details
fix: fixed panic

## Patch
### ecc/bls12-377/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bls12-378/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bls12-381/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bls24-315/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bls24-317/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bn254/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bw6-633/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bw6-756/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### ecc/bw6-761/shplonk/shplonk_test.go
```diff
@@ -34,7 +34,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err != nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```

### internal/generator/shplonk/template/shplonk.test.go.tmpl
```diff
@@ -16,7 +16,11 @@ var bAlpha *big.Int
 func init() {
 	const srsSize = 230
 	bAlpha = new(big.Int).SetInt64(42) // randomise ?
-	testSrs, _ = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	var err error
+	testSrs, err = kzg.NewSRS(ecc.NextPowerOfTwo(srsSize), bAlpha)
+	if err!=nil {
+		panic(err)
+	}
 }
 
 func TestOpening(t *testing.T) {
```
