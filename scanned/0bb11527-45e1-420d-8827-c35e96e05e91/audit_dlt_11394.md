# [?] fix: race condition with supportAdx relique in internal/fptower

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2022-07-27
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/4372d4b2f19886b12895e1b4b4e84577a2412288
Type: security-commit

## Details
fix: race condition with supportAdx relique in internal/fptower

## Patch
### ecc/bls12-377/internal/fptower/e2_test.go
```diff
@@ -189,12 +189,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -404,12 +398,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### ecc/bls12-378/internal/fptower/e2_test.go
```diff
@@ -189,12 +189,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -404,12 +398,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### ecc/bls12-381/internal/fptower/e2_test.go
```diff
@@ -189,12 +189,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -415,12 +409,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### ecc/bls24-315/internal/fptower/e2_test.go
```diff
@@ -177,12 +177,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -386,12 +380,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### ecc/bls24-317/internal/fptower/e2_test.go
```diff
@@ -189,12 +189,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -389,12 +383,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### ecc/bn254/internal/fptower/e2_test.go
```diff
@@ -189,12 +189,6 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -413,12 +407,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```

### internal/generator/tower/template/fq12over6over2/tests/fq2.go.tmpl
```diff
@@ -173,12 +173,7 @@ func TestE2ReceiverIsOperand(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
+
 }
 
 func TestE2MulMaxed(t *testing.T) {
@@ -401,12 +396,6 @@ func TestE2Ops(t *testing.T) {
 
 	properties.TestingRun(t, gopter.ConsoleReporter(false))
 
-	if supportAdx {
-		t.Log("disabling ADX")
-		supportAdx = false
-		properties.TestingRun(t, gopter.ConsoleReporter(false))
-		supportAdx = true
-	}
 }
 
 // ------------------------------------------------------------
```
