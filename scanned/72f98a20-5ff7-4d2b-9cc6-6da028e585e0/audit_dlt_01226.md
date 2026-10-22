# [?] execution/vm: fix gas tracing underflow with EIP-8037 state gas (#20128)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-26
Source: https://github.com/erigontech/erigon/commit/b206fff09c1248eb07d252606431e4472f9d6136
Type: security-commit

## Details
execution/vm: fix gas tracing underflow with EIP-8037 state gas (#20128)

## Summary

Fixes #20086.

The tracing variable `cost` in the interpreter loop accumulated both
`dynamicCost.Regular` and `dynamicCost.State`, but `gasCopy` only
captured regular gas from `callContext.gas`. When `OnGasChange(gasCopy,
gasCopy-cost, ...)` was called for opcodes that charge state gas (e.g.
SSTORE creating a new slot, CREATE, CREATE2), the uint64 subtraction
underflowed — producing garbage values visible in
`debug_traceTransaction` and similar RPC methods.

**Fix:** Remove `cost += dynamicCost.State`. State gas is already
charged separately via `useMdGas()`, and `cost` is only used for
tracing, so it should only reflect regular gas to match `gasCopy`.

**Note:** State gas consumption events are intentionally suppressed via
`GasChangeIgnored`, pending a spec for multi-dimensional gas tracing.
The `useMdGas()` infrastructure already accepts tracer/reason
parameters, so adding state gas tracing events in the future is
straightforward.

### Changes
- `execution/vm/interpreter.go`: Remove `cost += dynamicCost.State` (1
line), add clarifying comment
- `execution/vm/runtime/runtime_test.go`: Add
`TestGasTracingNoUnderflowOnStateGas` — executes SSTORE under Amsterdam
rules and verifies `OnGasChange` never produces underflowing values

## Test plan
- [x] `go test -short ./execution/vm/...` passes
- [x] `TestGasTracingNoUnderflowOnStateGas` verifies the fix
- [ ] CI lint + full test suite

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: Andrew Ashikhmin <34320705+yperbasis@users.noreply.github.com>
Co-authored-by: yperbasis <andrey.ashikhmin@gmail.com>

### execution/vm/interpreter.go
```diff
@@ -458,7 +458,11 @@ func (evm *EVM) Run(contract Contract, gas mdgas.MdGas, input []byte, readOnly b
 				evm.regularGasConsumed += dynamicCost.Regular - evm.CallGasTemp()
 			}
 			if dynamicCost.State > 0 {
-				cost += dynamicCost.State
+				// Note: do NOT add dynamicCost.State to `cost` here.
+				// `cost` is only used for tracing and is compared against `gasCopy`
+				// which captures only regular gas. Adding state gas would cause
+				// uint64 underflow in the OnGasChange(gasCopy, gasCopy-cost, ...) call below.
+				// State gas is charged separately via useMdGas.
 				ok := callContext.useMdGas(evm, dynamicCost.State, mdgas.StateGas, nil, tracing.GasChangeIgnored)
 				if !ok {
 					return nil, callContext.Gas(), ErrOutOfGas
```

### execution/vm/runtime/runtime_test.go
```diff
@@ -830,3 +830,63 @@ func TestCreateCollisionWithEIP7702Delegation(t *testing.T) {
 	require.NoError(t, err)
 	require.True(t, val.IsZero(), "CREATE should have returned 0 (collision), but got %x", val)
 }
+
+// TestGasTracingNoUnderflowOnStateGas verifies that the OnGasChange tracer
+// callback receives correct (non-underflowing) gas values when an opcode
+// charges state gas under EIP-8037 multi-dimensional gas (Amsterdam rules).
+//
+// The bug: the interpreter accumulated both regular and state dynamic gas into
+// a single `cost` variable, then computed `gasCopy - cost` for the tracer
+// callback. Because `gasCopy` only captured regular gas, the subtraction
+// underflowed when state gas was non-zero (e.g. SSTORE creating a new slot).
+func TestGasTracingNoUnderflowOnStateGas(t *testing.T) {
+	t.Parallel()
+
+	// Track all OnGasChange calls and check for underflow.
+	type gasChange struct {
+		oldGas uint64
+		newGas uint64
+		reason tracing.GasChangeReason
+	}
+	var gasChanges []gasChange
+
+	hooks := &tracing.Hooks{
+		OnGasChange: func(old, newGas uint64, reason tracing.GasChangeReason) {
+			gasChanges = append(gasChanges, gasChange{old, newGas, reason})
+			// The key invariant: new gas must never exceed old gas for a
+			// consumption event (GasChangeCallOpCode). A uint64 underflow
+			// would produce a very large value.
+			if reason == tracing.GasChangeCallOpCode && newGas > old {
+				t.Errorf("OnGasChange underflow: old=%d new=%d reason=%s", old, newGas, reason)
+			}
+		},
+	}
+
+	// Build bytecode: SSTORE(slot=0, value=1) then STOP.
+	// Under Amsterdam with an empty slot this triggers state gas.
+	code := []byte{
+		byte(vm.PUSH1), 1, // value = 1
+		byte(vm.PUSH1), 0, // slot = 0
+		byte(vm.SSTORE), // creates new slot -> charges state gas
+		byte(vm.STOP),
+	}
+
+	cfg := &Config{
+		EVMConfig: vm.Config{Tracer: hooks},
+		GasLimit:  10_000_000,
+	}
+
+	_, _, err := Execute(code, nil, cfg, t.TempDir())
+	require.NoError(t, err)
+
+	// Verify we actually observed at least one GasChangeCallOpCode event
+	// (the SSTORE should have triggered it).
+	found := false
+	for _, gc := range gasChanges {
+		if gc.reason == tracing.GasChangeCallOpCode {
+			found = true
+			break
+		}
+	}
+	require.True(t, found, "expected at least one GasChangeCallOpCode event from SSTORE")
+}
```
