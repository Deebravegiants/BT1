# [?] Merge pull request #495 from OffchainLabs/fix-total-multigas-overflow-check

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-07-22
Source: https://github.com/OffchainLabs/go-ethereum/commit/2ac1d7b74a82d5f1f531849ca4e5e4f1865cf62c
Type: security-commit

## Details
Merge pull request #495 from OffchainLabs/fix-total-multigas-overflow-check

Check multigas total value overflow

## Patch
### arbitrum/multigas/resources.go
```diff
@@ -14,89 +14,115 @@ const (
 	NumResourceKind
 )
 
-// MultiGas tracks gas for each resource separately.
+// MultiGas tracks gas usage across multiple resource kinds, while also
+// maintaining a single-dimensional total gas sum and refund amount.
 type MultiGas struct {
 	gas    [NumResourceKind]uint64
+	total  uint64
 	refund uint64
 }
 
+// ZeroGas creates a MultiGas value with all fields set to zero.
 func ZeroGas() *MultiGas {
 	return &MultiGas{}
 }
 
+// NewMultiGas creates a new MultiGas with the given resource kind initialized to `amount`.
+// All other kinds are zero. The total is also set to `amount`.
 func NewMultiGas(kind ResourceKind, amount uint64) *MultiGas {
 	mg := ZeroGas()
 	mg.gas[kind] = amount
+	mg.total = amount
 	return mg
 }
 
+// ComputationGas returns a MultiGas initialized with computation gas.
 func ComputationGas(amount uint64) *MultiGas {
 	return NewMultiGas(ResourceKindComputation, amount)
 }
 
+// HistoryGrowthGas returns a MultiGas initialized with history growth gas.
 func HistoryGrowthGas(amount uint64) *MultiGas {
 	return NewMultiGas(ResourceKindHistoryGrowth, amount)
 }
 
+// StorageAccessGas returns a MultiGas initialized with storage access gas.
 func StorageAccessGas(amount uint64) *MultiGas {
 	return NewMultiGas(ResourceKindStorageAccess, amount)
 }
 
+// StorageGrowthGas returns a MultiGas initialized with storage growth gas.
 func StorageGrowthGas(amount uint64) *MultiGas {
 	return NewMultiGas(ResourceKindStorageGrowth, amount)
 }
 
+// Get returns the gas amount for the specified resource kind.
 func (z *MultiGas) Get(kind ResourceKind) uint64 {
 	return z.gas[kind]
 }
 
-func (z *MultiGas) Set(kind ResourceKind, gas uint64) *MultiGas {
+// Set sets the gas for a given resource kind to `gas`, adjusting the total accordingly.
+// Returns the same MultiGas and a boolean indicating if an overflow occurred when updating the total.
+func (z *MultiGas) Set(kind ResourceKind, gas uint64) (*MultiGas, bool) {
+	newTotal, overflow := math.SafeAdd(z.total-z.gas[kind], gas)
+	if overflow {
+		return z, true
+	}
+
 	z.gas[kind] = gas
-	return z
+	z.total = newTotal
+	return z, false
 }
 
 // GetRefund gets the SSTORE refund computed at the end of the transaction.
 func (z *MultiGas) GetRefund() uint64 {
 	return z.refund
 }
 
-// SetRefund sets the SSTORE refund computed at the end of the transaction.
+// SetRefund sets the SSTORE refund computed at the end of the transaction and returns the modified MultiGas.
 func (z *MultiGas) SetRefund(amount uint64) *MultiGas {
 	z.refund = amount
 	return z
 }
 
-// SafeAdd sets z to the sum x+y and returns z and checks for overflow.
+// SafeAdd sets z to the sum of x and y, per resource kind and total.
+// Returns the modified MultiGas and a boolean indicating if an overflow occurred in either the kind-specific or total value.
 func (z *MultiGas) SafeAdd(x *MultiGas, y *MultiGas) (*MultiGas, bool) {
-	for i := ResourceKindUnknown; i < NumResourceKind; i++ {
-		var overflow bool
-		z.gas[i], overflow = math.SafeAdd(x.gas[i], y.gas[i])
+	for i := range z.gas {
+		newValue, overflow := math.SafeAdd(x.gas[i], y.gas[i])
 		if overflow {
-			return z, overflow
+			return z, true
 		}
+		z.gas[i] = newValue
+	}
+
+	newTotal, overflow := math.SafeAdd(x.total, y.total)
+	if overflow {
+		return z, true
 	}
+	z.total = newTotal
 	return z, false
 }
 
-// SafeIncrement increments the given resource kind by the amount of gas and checks for overflow.
+// SafeIncrement increments the given resource kind by the amount of gas and to the total.
+// Returns true if an overflow occurred in either the kind-specific or total value.
 func (z *MultiGas) SafeIncrement(kind ResourceKind, gas uint64) bool {
-	result, overflow := math.SafeAdd(z.gas[kind], gas)
+	newValue, overflow := math.SafeAdd(z.gas[kind], gas)
 	if overflow {
-		return overflow
+		return true
 	}
-	z.gas[kind] = result
+
+	newTotal, overflow := math.SafeAdd(z.total, gas)
+	if overflow {
+		return true
+	}
+
+	z.gas[kind] = newValue
+	z.total = newTotal
 	return false
 }
 
-// SingleGas converts the multi-gas to single-dimensional gas checking for overflow.
-func (z *MultiGas) SingleGas() (uint64, bool) {
-	var sum uint64
-	for _, value := range z.gas {
-		var overflow bool
-		sum, overflow = math.SafeAdd(sum, value)
-		if overflow {
-			return 0, overflow
-		}
-	}
-	return sum, false
+// SingleGas returns single-dimensional gas sum.
+func (z *MultiGas) SingleGas() uint64 {
+	return z.total
 }
```

### arbitrum/multigas/resources_test.go
```diff
@@ -6,6 +6,56 @@ import (
 )
 
 func TestMultiGas(t *testing.T) {
+	t.Run("Test constructor", func(t *testing.T) {
+		// Test ZeroGas
+		zero := ZeroGas()
+		if zero.SingleGas() != 0 {
+			t.Errorf("ZeroGas total should be 0, got %d", zero.SingleGas())
+		}
+
+		// Test specific constructors
+		comp := ComputationGas(100)
+		if comp.Get(ResourceKindComputation) != 100 {
+			t.Errorf("ComputationGas: expected Get(ResourceKindComputation) == 100, got %d", comp.Get(ResourceKindComputation))
+		}
+		if comp.SingleGas() != 100 {
+			t.Errorf("ComputationGas: expected SingleGas() == 100, got %d", comp.SingleGas())
+		}
+
+		storage := StorageAccessGas(200)
+		if storage.Get(ResourceKindStorageAccess) != 200 {
+			t.Errorf("StorageAccessGas: expected Get(ResourceKindStorageAccess) == 200, got %d", storage.Get(ResourceKindStorageAccess))
+		}
+		if storage.SingleGas() != 200 {
+			t.Errorf("StorageAccessGas: expected SingleGas() == 200, got %d", storage.SingleGas())
+		}
+	})
+
+	t.Run("Test constructors", func(t *testing.T) {
+		// Test ZeroGas
+		zero := ZeroGas()
+		if zero.SingleGas() != 0 {
+			t.Errorf("ZeroGas(): SingleGas(), got %d, want 0", zero.SingleGas())
+		}
+
+		// Test specific constructors
+		comp := ComputationGas(100)
+		if got := comp.Get(ResourceKindComputation); got != 100 {
+			t.Errorf("ComputationGas(100): Get(ResourceKindComputation), got %d, want 100", got)
+		}
+		if got := comp.SingleGas(); got != 100 {
+			t.Errorf("ComputationGas(100): SingleGas(), got %d, want 100", got)
+		}
+
+		storage := StorageAccessGas(200)
+		if got := storage.Get(ResourceKindStorageAccess); got != 200 {
+			t.Errorf("StorageAccessGas(200): Get(ResourceKindStorageAccess), got %d, want 200", got)
+		}
+		if got := storage.SingleGas(); got != 200 {
+			t.Errorf("StorageAccessGas(200): SingleGas(), got %d, want 200", got)
+		}
+	})
+
 	// Test SafeAdd
 	gas, overflow := new(MultiGas).SafeAdd(ComputationGas(10), HistoryGrowthGas(20))
 	if overflow {
@@ -23,11 +73,20 @@ func TestMultiGas(t *testing.T) {
 	if got, want := gas.Get(ResourceKindStorageGrowth), uint64(0); got != want {
 		t.Errorf("unexpected storage growth gas: got %v, want %v", got, want)
 	}
+	if got, want := gas.SingleGas(), uint64(30); got != want {
+		t.Errorf("unexpected single gas: got %v, want %v", got, want)
+	}
 
-	// Test SafeAdd checks for overflow
+	// Test SafeAdd checks for one dimensional overflow
 	_, overflow = new(MultiGas).SafeAdd(ComputationGas(math.MaxUint64), ComputationGas(1))
 	if !overflow {
-		t.Errorf("unexpected overflow: got %v, want %v", overflow, true)
+		t.Errorf("expected overflow: got %v, want %v", overflow, true)
+	}
+
+	// Test SafeAdd checks for total overflow
+	_, overflow = new(MultiGas).SafeAdd(ComputationGas(math.MaxUint64), HistoryGrowthGas(1))
+	if !overflow {
+		t.Errorf("expected overflow: got %v, want %v", overflow, true)
 	}
 
 	// Test SafeIncrement
@@ -42,22 +101,12 @@ func TestMultiGas(t *testing.T) {
 	// Test SafeIncrement checks for overflow
 	overflow = gas.SafeIncrement(ResourceKindComputation, math.MaxUint64)
 	if !overflow {
-		t.Errorf("unexpected overflow: got %v, want %v", overflow, true)
+		t.Errorf("expected overflow: got %v, want %v", overflow, true)
 	}
 
 	// Test SingleGas
-	singleGas, overflow := gas.SingleGas()
-	if overflow {
-		t.Errorf("unexpected overflow: got %v, want %v", overflow, false)
-	}
+	singleGas := gas.SingleGas()
 	if want := uint64(41); singleGas != want {
 		t.Errorf("unexpected storage growth gas: got %v, want %v", singleGas, want)
 	}
-
-	// Test SingleGas checks for overflow
-	gas.Set(ResourceKindComputation, math.MaxUint64)
-	_, overflow = gas.SingleGas()
-	if !overflow {
-		t.Errorf("unexpected overflow: got %v, want %v", overflow, true)
-	}
 }
```

### core/vm/gas_table.go
```diff
@@ -117,16 +117,16 @@ func gasSStore(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi
 		switch {
 		case current == (common.Hash{}) && y.Sign() != 0: // 0 => non 0
 			multiGas := multigas.StorageGrowthGas(params.SstoreSetGas)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil
 		case current != (common.Hash{}) && y.Sign() == 0: // non 0 => 0
 			evm.StateDB.AddRefund(params.SstoreRefundGas)
 			multiGas := multigas.StorageAccessGas(params.SstoreClearGas)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil
 		default: // non 0 => non 0 (or 0 => 0)
 			multiGas := multigas.StorageAccessGas(params.SstoreResetGas)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil
 		}
 	}
@@ -148,22 +148,22 @@ func gasSStore(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi
 	value := common.Hash(y.Bytes32())
 	if current == value { // noop (1)
 		multiGas := multigas.StorageAccessGas(params.NetSstoreNoopGas)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 	original := evm.StateDB.GetCommittedState(contract.Address(), x.Bytes32())
 	if original == current {
 		if original == (common.Hash{}) { // create slot (2.1.1)
 			multiGas := multigas.StorageGrowthGas(params.NetSstoreInitGas)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil
 		}
 
 		if value == (common.Hash{}) { // delete slot (2.1.2b)
 			evm.StateDB.AddRefund(params.NetSstoreClearRefund)
 		}
 		multiGas := multigas.StorageAccessGas(params.NetSstoreCleanGas)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil // write existing slot (2.1.2)
 	}
 	if original != (common.Hash{}) {
@@ -181,7 +181,7 @@ func gasSStore(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi
 		}
 	}
 	multiGas := multigas.StorageAccessGas(params.NetSstoreDirtyGas)
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -214,22 +214,22 @@ func gasSStoreEIP2200(evm *EVM, contract *Contract, stack *Stack, mem *Memory, m
 
 	if current == value { // noop (1)
 		multiGas := multigas.StorageAccessGas(params.SloadGasEIP2200)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 	original := evm.StateDB.GetCommittedState(contract.Address(), x.Bytes32())
 	if original == current {
 		if original == (common.Hash{}) { // create slot (2.1.1)
 			multiGas := multigas.StorageGrowthGas(params.SstoreSetGasEIP2200)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil
 		}
 		if value == (common.Hash{}) { // delete slot (2.1.2b)
 			evm.StateDB.AddRefund(params.SstoreClearsScheduleRefundEIP2200)
 		}
 
 		multiGas := multigas.StorageAccessGas(params.SstoreResetGasEIP2200)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 	if original != (common.Hash{}) {
@@ -247,7 +247,7 @@ func gasSStoreEIP2200(evm *EVM, contract *Contract, stack *Stack, mem *Memory, m
 		}
 	}
 	multiGas := multigas.StorageAccessGas(params.SloadGasEIP2200)
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil // dirty update (2.2)
 }
 
@@ -284,7 +284,7 @@ func makeGasLog(n uint64) gasFunc {
 		if overflow = multiGas.SafeIncrement(multigas.ResourceKindHistoryGrowth, memorySizeGas); overflow {
 			return multigas.ZeroGas(), 0, ErrGasUintOverflow
 		}
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 }
@@ -341,7 +341,7 @@ func gasCreate2(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memoryS
 	if overflow = multiGas.SafeIncrement(multigas.ResourceKindComputation, wordGas); overflow {
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -365,7 +365,7 @@ func gasCreateEip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, m
 	if overflow = multiGas.SafeIncrement(multigas.ResourceKindComputation, moreGas); overflow {
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 func gasCreate2Eip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize uint64) (*multigas.MultiGas, uint64, error) {
@@ -388,7 +388,7 @@ func gasCreate2Eip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory,
 	if overflow = multiGas.SafeIncrement(multigas.ResourceKindComputation, moreGas); overflow {
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -462,7 +462,7 @@ func gasCall(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize
 		}
 	}
 
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	evm.callGasTemp, err = callGas(evm.chainRules.IsEIP150, contract.Gas, singleGas, stack.Back(0))
 	if err != nil {
 		return multigas.ZeroGas(), 0, err
@@ -473,7 +473,7 @@ func gasCall(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
 
-	singleGas, _ = multiGas.SingleGas()
+	singleGas = multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -508,7 +508,7 @@ func gasCallCode(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memory
 		}
 	}
 
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	evm.callGasTemp, err = callGas(evm.chainRules.IsEIP150, contract.Gas, singleGas, stack.Back(0))
 	if err != nil {
 		return multigas.ZeroGas(), 0, err
@@ -519,7 +519,7 @@ func gasCallCode(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memory
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
 
-	singleGas, _ = multiGas.SingleGas()
+	singleGas = multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -538,7 +538,7 @@ func gasDelegateCall(evm *EVM, contract *Contract, stack *Stack, mem *Memory, me
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
 
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -557,7 +557,7 @@ func gasStaticCall(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memo
 		return multigas.ZeroGas(), 0, ErrGasUintOverflow
 	}
 
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -585,7 +585,7 @@ func gasSelfdestruct(evm *EVM, contract *Contract, stack *Stack, mem *Memory, me
 	if !evm.StateDB.HasSelfDestructed(contract.Address()) {
 		evm.StateDB.AddRefund(params.SelfdestructRefundGas)
 	}
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
```

### core/vm/operations_acl.go
```diff
@@ -58,7 +58,7 @@ func makeGasSStoreFunc(clearingRefund uint64) gasFunc {
 			// Warm slot access considered as storage access.
 			// See rationale in: https://github.com/OffchainLabs/nitro/blob/master/docs/decisions/0002-multi-dimensional-gas-metering.md
 			multiGas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WarmStorageReadCostEIP2929)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil // SLOAD_GAS
 		}
 		original := evm.StateDB.GetCommittedState(contract.Address(), x.Bytes32())
@@ -67,7 +67,7 @@ func makeGasSStoreFunc(clearingRefund uint64) gasFunc {
 				// Creating a new slot considered as storage growth.
 				// See rationale in: https://github.com/OffchainLabs/nitro/blob/master/docs/decisions/0002-multi-dimensional-gas-metering.md
 				multiGas.SafeIncrement(multigas.ResourceKindStorageGrowth, params.SstoreSetGasEIP2200)
-				singleGas, _ := multiGas.SingleGas()
+				singleGas := multiGas.SingleGas()
 				return multiGas, singleGas, nil
 			}
 			if value == (common.Hash{}) { // delete slot (2.1.2b)
@@ -79,7 +79,7 @@ func makeGasSStoreFunc(clearingRefund uint64) gasFunc {
 			//  Storage slot writes (nonzero → zero) considered as storage access.
 			//  See rationale in: https://github.com/OffchainLabs/nitro/blob/master/docs/decisions/0002-multi-dimensional-gas-metering.md
 			multiGas.SafeIncrement(multigas.ResourceKindStorageAccess, params.SstoreResetGasEIP2200-params.ColdSloadCostEIP2929)
-			singleGas, _ := multiGas.SingleGas()
+			singleGas := multiGas.SingleGas()
 			return multiGas, singleGas, nil // write existing slot (2.1.2)
 		}
 		if original != (common.Hash{}) {
@@ -109,7 +109,7 @@ func makeGasSStoreFunc(clearingRefund uint64) gasFunc {
 		// Warm slot access considered as storage access.
 		// See rationale in: https://github.com/OffchainLabs/nitro/blob/master/docs/decisions/0002-multi-dimensional-gas-metering.md
 		multiGas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WarmStorageReadCostEIP2929)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil // dirty update (2.2)
 	}
 }
@@ -214,7 +214,7 @@ func makeCallVariantGasCallEIP2929(oldCalculator gasFunc, addressPosition int) g
 			return multigas.ZeroGas(), 0, ErrGasUintOverflow
 		}
 
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 }
@@ -270,7 +270,7 @@ func makeSelfdestructGasFn(refundsEnabled bool) gasFunc {
 		if refundsEnabled && !evm.StateDB.HasSelfDestructed(contract.Address()) {
 			evm.StateDB.AddRefund(params.SelfdestructRefundGas)
 		}
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 	return gasFunc
@@ -345,7 +345,7 @@ func makeCallVariantGasCallEIP7702(oldCalculator gasFunc) gasFunc {
 			return multigas.ZeroGas(), 0, ErrGasUintOverflow
 		}
 
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 }
```

### core/vm/operations_gas_test.go
```diff
@@ -77,13 +77,9 @@ func testGasSStoreFuncFuncWithCases(t *testing.T, config *params.ChainConfig, ga
 					tc.expectedMultiGas, multiGas, tc.name)
 			}
 
-			expectedSingleGas, overflow := tc.expectedMultiGas.SingleGas()
-			if overflow {
-				t.Fatalf("Expected single gas overflow for test case %s", tc.name)
-			}
-
+			expectedSingleGas := tc.expectedMultiGas.SingleGas()
 			if singleGas != expectedSingleGas {
-				t.Errorf("Expected signle gas %d, got %d for test case: %s",
+				t.Errorf("Expected single gas %d, got %d for test case: %s",
 					expectedSingleGas, singleGas, tc.name)
 			}
 
@@ -1184,8 +1180,11 @@ func TestGasSelfdestruct(t *testing.T) {
 			beneficiaryExists: false,
 			isEIP150:          true,
 			isEIP158:          true,
-			expectedMultiGas:  multigas.StorageAccessGas(params.SelfdestructGasEIP150).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas),
-			expectedRefund:    params.SelfdestructRefundGas,
+			expectedMultiGas: func() *multigas.MultiGas {
+				mg, _ := multigas.StorageAccessGas(params.SelfdestructGasEIP150).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas)
+				return mg
+			}(),
+			expectedRefund: params.SelfdestructRefundGas,
 		},
 	}
 
@@ -1196,18 +1195,24 @@ func TestGasSelfdestruct(t *testing.T) {
 func TestMakeSelfdestructGasFn(t *testing.T) {
 	testCases := []GasSelfdestructFuncTestCase{
 		{
-			name:             "selfdestruct - no access list - with refund",
-			expectedMultiGas: multigas.StorageAccessGas(params.ColdAccountAccessCostEIP2929).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas),
-			expectedRefund:   params.SelfdestructRefundGas,
+			name: "selfdestruct - no access list - with refund",
+			expectedMultiGas: func() *multigas.MultiGas {
+				mg, _ := multigas.StorageAccessGas(params.ColdAccountAccessCostEIP2929).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas)
+				return mg
+			}(),
+			expectedRefund: params.SelfdestructRefundGas,
 		},
 		{
 			name:              "has been destructed - no access list - no refund",
 			expectedMultiGas:  multigas.StorageAccessGas(params.ColdAccountAccessCostEIP2929),
 			hasBeenDestructed: true,
 		},
 		{
-			name:             "selfdestruct - in access list - with refund",
-			expectedMultiGas: multigas.StorageAccessGas(params.ColdAccountAccessCostEIP2929).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas),
+			name: "selfdestruct - in access list - with refund",
+			expectedMultiGas: func() *multigas.MultiGas {
+				mg, _ := multigas.StorageAccessGas(params.ColdAccountAccessCostEIP2929).Set(multigas.ResourceKindStorageGrowth, params.CreateBySelfdestructGas)
+				return mg
+			}(),
 			expectedRefund:   params.SelfdestructRefundGas,
 			slotInAccessList: true,
 		},
@@ -1292,7 +1297,7 @@ func TestMakeGasLog(t *testing.T) {
 		expectedComputation := memorySingleGas + params.LogGas + n*params.LogTopicGas
 		expectedHistory := requestedSize * params.LogDataGas
 
-		expectedMultiGas := multigas.ComputationGas(expectedComputation).Set(multigas.ResourceKindHistoryGrowth, expectedHistory)
+		expectedMultiGas, _ := multigas.ComputationGas(expectedComputation).Set(multigas.ResourceKindHistoryGrowth, expectedHistory)
 
 		multiGas, _, err := makeGasLog(n)(evm, contract, stack, mem, memorySize)
 		if err != nil {
```

### core/vm/operations_verkle.go
```diff
@@ -32,7 +32,7 @@ func gasSStore4762(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memo
 	}
 	multiGas := multigas.StorageAccessGas(gas)
 
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
@@ -105,7 +105,7 @@ func makeCallVariantGasEIP4762(oldCalculator gasFunc) gasFunc {
 		//  Witness gas considered as storage access.
 		// See rationale in: https://github.com/OffchainLabs/nitro/blob/master/docs/decisions/0002-multi-dimensional-gas-metering.md
 		multiGas.SafeIncrement(multigas.ResourceKindStorageAccess, witnessGas)
-		singleGas, _ := multiGas.SingleGas()
+		singleGas := multiGas.SingleGas()
 		return multiGas, singleGas, nil
 	}
 }
@@ -138,7 +138,7 @@ func gasSelfdestructEIP4762(evm *EVM, contract *Contract, stack *Stack, mem *Mem
 		}
 	}
 	multiGas := multigas.StorageAccessGas(statelessGas)
-	singleGas, _ := multiGas.SingleGas()
+	singleGas := multiGas.SingleGas()
 	return multiGas, singleGas, nil
 }
 
```
