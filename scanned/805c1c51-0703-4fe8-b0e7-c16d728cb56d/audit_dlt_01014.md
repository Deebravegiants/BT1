# [H] Cosmos EVM Allows Partial Precompile State Writes

## Summary
Severity: High
Chain: github.com/cosmos/evm
Component: github.com/cosmos/evm
CWE: Improper Control of Generation of Code ('Code Injection')
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-mjfq-3qr2-6g84
Type: github-advisory

## Details
### Impact
Setting lower EVM call gas allows users to partially execute precompiles and error at specific points in the precompile code without reverting the partially written state. 

If executed on the distribution precompile when claiming funds, it could cause funds to be transferred to a user without resetting the claimable rewards to 0. The vulnerability could also be used to cause indeterministic execution by failing at other points in the code, halting validators.

Any evmOS or Cosmos EVM chain using precompiles is affected.

### Patches
The vulnerability was patched by wrapping each precompile execution into an atomic function that reverts any partially committed state on error.

- [evmos/os](https://github.com/evmos/os) patch file: https://drive.google.com/file/d/1LfC0WSrQOqwTOW3qfaE6t8Jqf1PLVtS_/

For chains using a different file structure, you must manually apply the diff:

### **In `x/evm/statedb.go`:**

Add the following function:
```go
func (s *StateDB) RevertMultiStore(cms storetypes.CacheMultiStore, events sdk.Events) {
	s.cacheCtx = s.cacheCtx.WithMultiStore(cms)
	s.writeCache = func() {
		// rollback the events to the ones
		// on the snapshot
		s.ctx.EventManager().EmitEvents(events)
		cms.Write()
	}
}
```

### **In `x/evm/statedb/journal.go`:**

Replace the `Revert` function with the following:
```go
func (pc precompileCallChange) Revert(s *StateDB) {
	// rollback multi store from cache ctx to the previous
	// state stored in the snapshot
	s.RevertMultiStore(pc.multiStore, pc.events)
}
```

### **In `precompiles/common/precompile.go`:**

Change the function signature in `HandleGasError` to:
```go
func HandleGasError(ctx sdk.Context, contract *vm.Contract, initialGas storetypes.Gas, err *error, stateDB *statedb.StateDB, snapshot snapshot) func() {
...
}
```

In the `HandleGasError` function, add the following line in the switch statement in the `case storetypes.ErrorOutOfGas:` case:
```go
stateDB.RevertMultiStore(snapshot.MultiStore, snapshot.Events)
```

Add the following function:
```go
// RunAtomic is used within the Run function of each Precompile implementation.
// It handles rolling back to the provided snapshot if an error is returned from the core precompile logic.
// Note: This is only required for stateful precompiles.
func (p Precompile) RunAtomic(s snapshot, stateDB *statedb.StateDB, fn func() ([]byte, error)) ([]byte, error) {
	bz, err := fn()
	if err != nil {
		// revert to snapshot on error
		stateDB.RevertMultiStore(s.MultiStore, s.Events)
	}
	return bz, err
}
```

### **All Precompiles:**
Finally, in each precompile, locate the `Run` function, and wrap each switch statement and return values into `p.RunAtomic`. For example:
```go
// Run executes the precompiled contract IBC transfer methods defined in the ABI.
func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz []byte, err error) {
	ctx, stateDB, snapshot, method, initialGas, args, err := p.RunSetup(evm, contract, readOnly, p.IsTransaction)
	if err != nil {
		return nil, err
	}

	// This handles any out of gas errors that may occur during the execution of a precompile tx or query.
	// It avoids panics and returns the out of gas error so the EVM can continue gracefully.
	defer cmn.HandleGasError(ctx, contract, initialGas, &err, stateDB, snapshot)()

        // === WRAP HERE ===
	return p.RunAtomic(snapshot, stateDB, func() ([]byte, error) {
		switch method.Name {
		// TODO Approval transactions => need cosmos-sdk v0.46 & ibc-go v6.2.0
		// Authorization Methods:
		case exampleCase:
			bz, err = p.example(ctx, evm.Origin, stateDB, method, args)
		default:
			return nil, fmt.Errorf(cmn.ErrUnknownMethod, method.Name)
		}

		if err != nil {
			return nil, err
		}

		cost := ctx.GasMeter().GasConsumed() - initialGas

		if !contract.UseGas(cost) {
			return nil, vm.ErrOutOfGas
		}

		if err := p.AddJournalEntries(stateDB, snapshot); err != nil {
			return nil, err
		}

		return bz, nil
	})
}
```


### Workarounds
There are no workarounds for chains that make use of precompiles. A coordinated upgrade is necessary to patch the issue.

### Testing
A test was introduced in the distribution precompile to ensure that partial state writes no longer occur when a lower gas amount is set.
