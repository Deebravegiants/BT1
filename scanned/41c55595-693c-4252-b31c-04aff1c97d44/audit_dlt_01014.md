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

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-mjfq-3qr2-6g84_
