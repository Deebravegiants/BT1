# [?] Ignored overflow possibility, fixed dimensions in warm/cold access.

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-08-27
Source: https://github.com/OffchainLabs/go-ethereum/commit/f24194ca9a85a96dc2e8301443d5cdd421b6ec2c
Type: security-commit

## Details
Ignored overflow possibility, fixed dimensions in warm/cold access.

## Patch
### core/state/access_events.go
```diff
@@ -17,7 +17,6 @@
 package state
 
 import (
-	"fmt"
 	"maps"
 
 	"github.com/ethereum/go-ethereum/arbitrum/multigas"
@@ -154,51 +153,47 @@ func (ae *AccessEvents) AddTxDestination(addr common.Address, sendsValue bool) {
 }
 
 // SlotGas returns the amount of gas to be charged for a cold storage access.
-func (ae *AccessEvents) SlotGas(addr common.Address, slot common.Hash, isWrite bool) (*multigas.MultiGas, error) {
+func (ae *AccessEvents) SlotGas(addr common.Address, slot common.Hash, isWrite bool) *multigas.MultiGas {
 	treeIndex, subIndex := utils.StorageIndex(slot.Bytes())
 	return ae.touchAddressAndChargeMultigas(addr, *treeIndex, subIndex, isWrite)
 }
 
 // touchAddressAndChargeMultigas adds any missing access event to the access event list, and returns the cold
 // access cost to be charged, if need be.
-func (ae *AccessEvents) touchAddressAndChargeMultigas(addr common.Address, treeIndex uint256.Int, subIndex byte, isWrite bool) (*multigas.MultiGas, error) {
+func (ae *AccessEvents) touchAddressAndChargeMultigas(addr common.Address, treeIndex uint256.Int, subIndex byte, isWrite bool) *multigas.MultiGas {
 	stemRead, selectorRead, stemWrite, selectorWrite, selectorFill := ae.touchAddress(addr, treeIndex, subIndex, isWrite)
 
 	gas := multigas.ZeroGas()
 	// Reading includes witness calculation (computation), and storage access
 	// The computation cost for the witness calculation is negligible compared to the storage access cost
-	if stemRead && gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessBranchReadCost) {
-		return nil, fmt.Errorf("failed to increment gas for branch read due to overflow")
+	if stemRead {
+		gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessBranchReadCost)
 	}
-	if selectorRead && gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessChunkReadCost) {
-		return nil, fmt.Errorf("failed to increment gas for chunk read due to overflow")
+	if selectorRead {
+		gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessChunkReadCost)
 	}
 
 	// Writing includes witness calculation (computation), and the update of a slot value (storage access)
 	// The computation cost for the witness calculation is negligible compared to the storage access cost
 	// Potential new space allocation (growth) is not considered in this step
-	if stemWrite && gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessBranchWriteCost) {
-		return nil, fmt.Errorf("failed to increment gas for branch write due to overflow")
+	if stemWrite {
+		gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessBranchWriteCost)
 	}
-	if selectorWrite && gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessChunkWriteCost) {
-		return nil, fmt.Errorf("failed to increment gas for chunk write due to overflow")
+	if selectorWrite {
+		gas.SafeIncrement(multigas.ResourceKindStorageAccess, params.WitnessChunkWriteCost)
 	}
 
 	// New space allocation for the verkle tree
-	if selectorFill && gas.SafeIncrement(multigas.ResourceKindStorageGrowth, params.WitnessChunkFillCost) {
-		return nil, fmt.Errorf("failed to increment gas for chunk fill due to overflow")
+	if selectorFill {
+		gas.SafeIncrement(multigas.ResourceKindStorageGrowth, params.WitnessChunkFillCost)
 	}
-	return gas, nil
+	return gas
 }
 
 // touchAddressAndChargeGas adds any missing access event to the access event list, and returns the cold
 // access cost to be charged, if need be.
 func (ae *AccessEvents) touchAddressAndChargeGas(addr common.Address, treeIndex uint256.Int, subIndex byte, isWrite bool) uint64 {
-	multiGas, err := ae.touchAddressAndChargeMultigas(addr, treeIndex, subIndex, isWrite)
-	if err != nil {
-		return 0
-	}
-	return multiGas.SingleGas()
+	return ae.touchAddressAndChargeMultigas(addr, treeIndex, subIndex, isWrite).SingleGas()
 }
 
 // touchAddress adds any missing access event to the access event list.
```

### core/state/access_events_test.go
```diff
@@ -83,11 +83,7 @@ func TestAccountHeaderGas(t *testing.T) {
 
 	// Check that reading a slot from the account header only charges the
 	// chunk read cost.
-	multiGas, err := ae.SlotGas(testAddr, common.Hash{}, false)
-	if err != nil {
-		t.Fatalf("gas computation failed: %v", err)
-	}
-	gas = multiGas.SingleGas()
+	gas = ae.SlotGas(testAddr, common.Hash{}, false).SingleGas()
 	if gas != params.WitnessChunkReadCost {
 		t.Fatalf("incorrect gas computed, got %d, want %d", gas, params.WitnessChunkReadCost)
 	}
```

### core/vm/operations_acl.go
```diff
@@ -123,10 +123,13 @@ func gasSLoadEIP2929(evm *EVM, contract *Contract, stack *Stack, mem *Memory, me
 		// If he does afford it, we can skip checking the same thing later on, during execution
 		evm.StateDB.AddSlotToAccessList(contract.Address(), slot)
 		// Cold slot access considered as storage access.
-		return multigas.StorageAccessGas(params.ColdSloadCostEIP2929), nil
+		return multigas.MultiGasFromMap(map[multigas.ResourceKind]uint64{
+			multigas.ResourceKindStorageAccess: params.ColdSloadCostEIP2929 - params.WarmStorageReadCostEIP2929,
+			multigas.ResourceKindComputation:   params.WarmStorageReadCostEIP2929,
+		}), nil
 	}
 	// Warm slot access considered as storage access.
-	return multigas.StorageAccessGas(params.WarmStorageReadCostEIP2929), nil
+	return multigas.ComputationGas(params.WarmStorageReadCostEIP2929), nil
 }
 
 // gasExtCodeCopyEIP2929 implements extcodecopy according to EIP-2929
```

### core/vm/operations_gas_test.go
```diff
@@ -442,12 +442,15 @@ func TestGasSSLoad2929(t *testing.T) {
 	testGasSLoad(t, gasSLoadEIP2929,
 		// Load new entry
 		func(_ *Contract, _ StateDB) (common.Hash, *multigas.MultiGas) {
-			return common.HexToHash("0xdeadbeef"), multigas.StorageAccessGas(params.ColdSloadCostEIP2929)
+			return common.HexToHash("0xdeadbeef"), multigas.MultiGasFromMap(map[multigas.ResourceKind]uint64{
+				multigas.ResourceKindStorageAccess: params.ColdSloadCostEIP2929 - params.WarmStorageReadCostEIP2929,
+				multigas.ResourceKindComputation:   params.WarmStorageReadCostEIP2929,
+			})
 		},
 		// Load entry from access list
 		func(contract *Contract, stateDB StateDB) (common.Hash, *multigas.MultiGas) {
 			stateDB.AddSlotToAccessList(contract.Address(), common.HexToHash("0xdeadbeef"))
-			return common.HexToHash("0xdeadbeef"), multigas.StorageAccessGas(params.WarmStorageReadCostEIP2929)
+			return common.HexToHash("0xdeadbeef"), multigas.ComputationGas(params.WarmStorageReadCostEIP2929)
 		},
 	)
 }
```

### core/vm/operations_verkle.go
```diff
@@ -25,21 +25,15 @@ import (
 )
 
 func gasSStore4762(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize uint64) (*multigas.MultiGas, error) {
-	gas, err := evm.AccessEvents.SlotGas(contract.Address(), stack.peek().Bytes32(), true)
-	if err != nil {
-		return nil, err
-	}
+	gas := evm.AccessEvents.SlotGas(contract.Address(), stack.peek().Bytes32(), true)
 	if gas.SingleGas() == 0 {
 		gas = multigas.StorageAccessGas(params.WarmStorageReadCostEIP2929)
 	}
 	return gas, nil
 }
 
 func gasSLoad4762(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize uint64) (*multigas.MultiGas, error) {
-	gas, err := evm.AccessEvents.SlotGas(contract.Address(), stack.peek().Bytes32(), false)
-	if err != nil {
-		return nil, err
-	}
+	gas := evm.AccessEvents.SlotGas(contract.Address(), stack.peek().Bytes32(), false)
 	if gas.SingleGas() == 0 {
 		gas = multigas.StorageAccessGas(params.WarmStorageReadCostEIP2929)
 	}
```
