# [?] fix: element.SetString(_) returns error if invalid input instead of panic

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2022-07-27
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/0692859967bce9cc6bfeee0844cc8f4f0955f2db
Type: security-commit

## Details
fix: element.SetString(_) returns error if invalid input instead of panic

## Patch
### ecc/bls12-377/bls12-377.go
```diff
@@ -91,7 +91,7 @@ func init() {
 
 	g1Gen.X.SetString("81937999373150964239938255573465948239988671502647976594219695644855304257327692006745978603320413799295628339695")
 	g1Gen.Y.SetString("241266749859715473739788878240585681733927191168601896383759122102112907357779751001206799952863815012735208165030")
-	g1Gen.Z.SetString("1")
+	g1Gen.Z.SetOne()
 
 	g2Gen.X.SetString("233578398248691099356572568220835526895379068987715365179118596935057653620464273615301663571204657964920925606294",
 		"140913150380207355837477652521042157274541796891053068589147167627541651775299824604154852141315666357241556069118")
```

### ecc/bls12-377/fp/element.go
```diff
@@ -181,7 +181,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fp.Element with <nil>")
@@ -1086,20 +1086,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-377/fr/element.go
```diff
@@ -175,7 +175,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fr.Element with <nil>")
@@ -944,20 +944,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-377/multiexp_test.go
```diff
@@ -148,7 +148,7 @@ func TestMultiExpG1(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G1Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g1GenAff, &finalBigScalarBi)
 
@@ -378,7 +378,7 @@ func TestMultiExpG2(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G2Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g2GenAff, &finalBigScalarBi)
 
```

### ecc/bls12-378/bls12-378.go
```diff
@@ -87,7 +87,7 @@ func init() {
 	// E(3,y) * cofactor
 	g1Gen.X.SetString("302027100877540500544138164010696035562809807233645104772290911818386302983750063098216015456036850656714568735197")
 	g1Gen.Y.SetString("232851047397483214541821965369374725182070455016459237170823497053622811786333462699984177726412751508198874482530")
-	g1Gen.Z.SetString("1")
+	g1Gen.Z.SetOne()
 
 	// E_t(1,y) * cofactor'
 	g2Gen.X.SetString("470810816643554779222760025249941413452299198622737082648784137654933833261310635469274149014014206108405592809732",
```

### ecc/bls12-378/fp/element.go
```diff
@@ -181,7 +181,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fp.Element with <nil>")
@@ -1086,20 +1086,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-378/fr/element.go
```diff
@@ -175,7 +175,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fr.Element with <nil>")
@@ -944,20 +944,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-378/multiexp_test.go
```diff
@@ -148,7 +148,7 @@ func TestMultiExpG1(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G1Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g1GenAff, &finalBigScalarBi)
 
@@ -378,7 +378,7 @@ func TestMultiExpG2(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G2Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g2GenAff, &finalBigScalarBi)
 
```

### ecc/bls12-381/bls12-381.go
```diff
@@ -81,7 +81,7 @@ func init() {
 
 	g1Gen.X.SetString("3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507")
 	g1Gen.Y.SetString("1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569")
-	g1Gen.Z.SetString("1")
+	g1Gen.Z.SetOne()
 
 	g2Gen.X.SetString("352701069587466618187139116011060144890029952792775240219908644239793785735715026873347600343865175952761926303160",
 		"3059144344244213709971259814753781636986470325476647558659373206291635324768958432433509563104347017837885763365758")
```

### ecc/bls12-381/fp/element.go
```diff
@@ -181,7 +181,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fp.Element with <nil>")
@@ -1086,20 +1086,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-381/fr/element.go
```diff
@@ -175,7 +175,7 @@ func (z *Element) SetInterface(i1 interface{}) (*Element, error) {
 	case int:
 		return z.SetInt64(int64(c1)), nil
 	case string:
-		return z.SetString(c1), nil
+		return z.SetString(c1)
 	case *big.Int:
 		if c1 == nil {
 			return nil, errors.New("can't set fr.Element with <nil>")
@@ -944,20 +944,21 @@ func (z *Element) setBigInt(v *big.Int) *Element {
 // Incorrect placement of underscores is reported as a panic if there
 // are no other errors.
 //
-func (z *Element) SetString(number string) *Element {
+// If the number is invalid this method leaves z unchanged and returns nil, error.
+func (z *Element) SetString(number string) (*Element, error) {
 	// get temporary big int from the pool
 	vv := bigIntPool.Get().(*big.Int)
 
 	if _, ok := vv.SetString(number, 0); !ok {
-		panic("Element.SetString failed -> can't parse number into a big.Int " + number)
+		return nil, errors.New("Element.SetString failed -> can't parse number into a big.Int " + number)
 	}
 
 	z.SetBigInt(vv)
 
 	// release object into pool
 	bigIntPool.Put(vv)
 
-	return z
+	return z, nil
 }
 
 // MarshalJSON returns json encoding of z (z.Text(10))
```

### ecc/bls12-381/multiexp_test.go
```diff
@@ -148,7 +148,7 @@ func TestMultiExpG1(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G1Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g1GenAff, &finalBigScalarBi)
 
@@ -378,7 +378,7 @@ func TestMultiExpG2(t *testing.T) {
 			var finalBigScalar fr.Element
 			var finalBigScalarBi big.Int
 			var op1ScalarMul G2Affine
-			finalBigScalar.SetString("9455").Mul(&finalBigScalar, &mixer)
+			finalBigScalar.SetUint64(9455).Mul(&finalBigScalar, &mixer)
 			finalBigScalar.ToBigIntRegular(&finalBigScalarBi)
 			op1ScalarMul.ScalarMultiplication(&g2GenAff, &finalBigScalarBi)
 
```
