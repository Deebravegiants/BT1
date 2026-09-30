# [?] Fix SaturatingDecrement underflow bug

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-11-24
Source: https://github.com/OffchainLabs/go-ethereum/commit/6a75e60f00676fc1574eefca700145844c27f5c5
Type: security-commit

## Details
Fix SaturatingDecrement underflow bug

## Patch
### arbitrum/multigas/resources.go
```diff
@@ -327,16 +327,20 @@ func (z MultiGas) SaturatingIncrement(kind ResourceKind, gas uint64) MultiGas {
 func (z MultiGas) SaturatingDecrement(kind ResourceKind, gas uint64) MultiGas {
 	res := z
 
-	if v, c := bits.Sub64(res.gas[kind], gas, 0); c != 0 {
-		res.gas[kind] = 0 // clamp
+	current := res.gas[kind]
+	var reduced uint64
+	if current < gas {
+		reduced = current
+		res.gas[kind] = 0
 	} else {
-		res.gas[kind] = v
+		reduced = gas
+		res.gas[kind] = current - gas
 	}
 
-	if t, c := bits.Sub64(res.total, gas, 0); c != 0 {
-		res.total = 0 // clamp
+	if res.total < reduced {
+		res.total = 0
 	} else {
-		res.total = t
+		res.total -= reduced
 	}
 
 	return res
```

### arbitrum/multigas/resources_test.go
```diff
@@ -400,13 +400,25 @@ func TestSaturatingDecrement(t *testing.T) {
 	}
 
 	// saturating decrement on kind
-	gas = ComputationGas(0)
-	newGas = gas.SaturatingDecrement(ResourceKindComputation, 1)
+	gas = MultiGasFromPairs(
+		Pair{ResourceKindComputation, 10},
+		Pair{ResourceKindStorageAccess, 10},
+	)
+
+	newGas = gas.SaturatingDecrement(ResourceKindComputation, 20)
 	if got, want := newGas.Get(ResourceKindComputation), uint64(0); got != want {
-		t.Errorf("expected computation gas to clamp to zero: got %v, want %v", got, want)
+		t.Errorf("unexpected comp gas: got %v, want %v", got, want)
 	}
-	if got, want := newGas.SingleGas(), uint64(0); got != want {
-		t.Errorf("expected total to clamp to zero: got %v, want %v", got, want)
+	if got, want := newGas.Get(ResourceKindStorageAccess), uint64(10); got != want {
+		t.Errorf("unexpected storage access gas: got %v, want %v", got, want)
+	}
+	if got, want := newGas.SingleGas(), uint64(10); got != want {
+		t.Errorf("unexpected total (should drop by 10 only): got %v, want %v", got, want)
+	}
+
+	if got, want := newGas.SingleGas(),
+		newGas.Get(ResourceKindComputation)+newGas.Get(ResourceKindStorageAccess); got != want {
+		t.Errorf("total/sum mismatch: total=%v sum=%v", got, want)
 	}
 
 	// total-only decrement case
```
