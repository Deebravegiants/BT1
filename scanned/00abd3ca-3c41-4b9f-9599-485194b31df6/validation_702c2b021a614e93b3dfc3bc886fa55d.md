### Title
`EngineMeter::charge_ref_time` never actually deducts fuel for host-call costs, letting the wasmi engine execute extra instructions beyond `gas_limit` - (File: substrate/frame/contracts/src/gas.rs)

### Summary
`EngineMeter::charge_ref_time` computes the fuel equivalent of a host-function's ref_time cost but never applies the resulting subtraction to `self.fuel`; it only uses the result of `checked_sub` for a bounds check and discards it. This means every host call's ref_time cost is deducted from `gas_left` (the pallet's bookkeeping counter) but is never removed from the real wasmi engine fuel budget, so the interpreter is left with more executable fuel than the declared `gas_limit` should permit.

### Finding Description
`EngineMeter::charge_ref_time` is invoked from `GasMeter::sync_to_executor`, which is called at the end of every host function to convert the ref_time cost charged during that host call (via `GasMeter::charge`) into an equivalent number of wasmi fuel units that must be subtracted from the engine's remaining fuel before it resumes interpreting the contract's WASM bytecode: [1](#0-0) 

The critical line is:
```rust
self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
Ok(Syncable(self.fuel))
```
`checked_sub` returns a new value, but that value is discarded — `self.fuel` is never reassigned. Only the overflow/underflow check is performed; the actual subtraction never happens. Compare this with the symmetrical `set_fuel` function, which correctly assigns `self.fuel = fuel` after computing the consumed amount: [2](#0-1) 

Because `charge_ref_time` returns `Syncable(self.fuel)` (the *unchanged* pre-host-call fuel value) instead of the reduced value, every call that eventually writes this `Syncable` back into the real wasmi engine (via `store.set_fuel(...)`) resets the engine's fuel counter to the value it had before the host call, silently reverting the intended deduction for the host call's own ref_time cost.

The pallet's authoritative accounting counter, `gas_left`, is still correctly decremented by `GasMeter::charge` for the host-call cost, and by `sync_from_executor` for genuine WASM-instruction fuel consumption observed from the engine (an exact multiplication, no precision loss): [3](#0-2) 

However, because the wasmi engine's own local fuel budget is never reduced by the host-call cost, the interpreter is left able to execute additional real WASM instructions between host-call boundaries that were never "paid for" out of that budget. Any subsequent overspend is only caught lazily, the next time `sync_from_executor` calls `gas_left.checked_reduce(...)`, by which point the extra WASM instructions have already been executed by the node (real CPU/time cost incurred) even though the eventual `OutOfGas` error means the reported `actual_weight` (via `gas_consumed()`) does not reflect this extra execution, since `gas_left` is not mutated on a failed `checked_reduce`.

The comment on `charge_ref_time` ("Returns the amount of fuel left") confirms the intent was for `self.fuel` to actually be reduced and returned — the missing assignment is a genuine logic error, not intended behavior.

### Impact Explanation
A contract that repeatedly invokes host functions (each with a nonzero ref_time cost from the `Schedule`) accumulates a persistent gap between the wasmi engine's actual fuel budget and what `gas_limit` intends to allow, since every host call's cost is dropped from the engine-fuel side of the accounting. This lets the contract's WASM code execute more raw instructions than its `gas_limit` should permit before the discrepancy surfaces (if it surfaces at all before the call naturally completes), resulting in real CPU time consumed by the node beyond what is reflected in `actual_weight`/`gas_consumed()`. This is a weight-limit/gas-metering escape (DoS-relevant: extra unaccounted computation performed per dispatched extrinsic), matching the scoped impact.

### Likelihood Explanation
This is trivially and deterministically reachable by any unprivileged account: upload and instantiate any WASM contract that makes multiple host calls (e.g., calls to `seal_caller`, `seal_block_number`, storage reads, etc., which all have nonzero benchmarked ref_time costs) inside a loop with a `gas_limit` set close to the true resource limit. No special `Schedule` values or division-boundary tuning is required — the bug fires on the very first host call that has a nonzero ref_time cost, since `self.fuel` is unconditionally never decremented in `charge_ref_time`. This makes the flaw fully repeatable and independent of `ref_time_by_fuel()` quantization, though the truncating division in the `amount` computation (`ref_time.checked_div(ref_time_by_fuel())`) compounds the loss slightly further.

### Recommendation
Fix `charge_ref_time` to actually apply the subtraction:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;
    self.fuel = self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```
Additionally consider rounding the `ref_time / ref_time_by_fuel()` division up (ceiling) rather than truncating down, so host-call costs are never under-charged against the engine's fuel budget.

### Proof of Concept
Rust unit test targeting `gas.rs` directly (fast, deterministic, no full contract needed):
```rust
#[test]
fn charge_ref_time_actually_deducts_engine_fuel() {
    // Construct EngineMeter with a known fuel value and ref_time_by_fuel from the test Schedule.
    let mut meter = EngineMeter::<Test>::new(Weight::from_parts(100_000, 0));
    let fuel_before = meter.fuel;
    let host_call_ref_time_cost = 1_000; // matches an integer multiple of ref_time_by_fuel()
    let syncable = meter.charge_ref_time(host_call_ref_time_cost).unwrap();
    let fuel_after: u64 = syncable.into();
    // BUG: fuel_after currently equals fuel_before (no deduction occurred).
    assert_ne!(fuel_after, fuel_before, "engine fuel must be reduced by host-call cost");
    assert_eq!(fuel_after, fuel_before - host_call_ref_time_cost / T::Schedule::get().ref_time_by_fuel());
}
```
Integration-level PoC: instantiate a contract that loops N times calling a cheap host function (e.g., `seal_block_number`) followed by a tight WASM compute loop; assert via `into_dispatch_result`/`actual_weight` that reported `gas_consumed()` after execution does not account for all instructions actually interpreted by wasmi (observable indirectly by setting `gas_limit` just above `N * host_call_cost` and confirming the contract can still perform significantly more computation than the remaining budget after host costs are subtracted, before `OutOfGas` is eventually triggered, if at all).

### Citations

**File:** substrate/frame/contracts/src/gas.rs (L56-65)
```rust
	/// Set the fuel left to the given value.
	/// Returns the amount of Weight consumed since the last update.
	fn set_fuel(&mut self, fuel: u64) -> Weight {
		let consumed = self
			.fuel
			.saturating_sub(fuel)
			.saturating_mul(T::Schedule::get().ref_time_by_fuel());
		self.fuel = fuel;
		Weight::from_parts(consumed, 0)
	}
```

**File:** substrate/frame/contracts/src/gas.rs (L67-76)
```rust
	/// Charge the given amount of gas.
	/// Returns the amount of fuel left.
	fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
		let amount = ref_time
			.checked_div(T::Schedule::get().ref_time_by_fuel())
			.ok_or(Error::<T>::InvalidSchedule)?;

		self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
		Ok(Syncable(self.fuel))
	}
```

**File:** substrate/frame/contracts/src/gas.rs (L239-258)
```rust
	pub fn sync_from_executor(&mut self, engine_fuel: u64) -> Result<RefTimeLeft, DispatchError> {
		let weight_consumed = self.engine_meter.set_fuel(engine_fuel);
		self.gas_left
			.checked_reduce(weight_consumed)
			.ok_or_else(|| Error::<T>::OutOfGas)?;
		Ok(RefTimeLeft(self.gas_left.ref_time()))
	}

	/// Hand over the gas metering responsibility from this meter to the executor.
	///
	/// Needs to be called when leaving a host function in order to calculate how much
	/// gas needs to be charged from the **executor**. It updates the last seen executor
	/// total value so that it is correct when `sync_from_executor` is called the next time.
	///
	/// It is important that this does **not** actually sync with the executor. That has
	/// to be done by the caller.
	pub fn sync_to_executor(&mut self, before: RefTimeLeft) -> Result<Syncable, DispatchError> {
		let ref_time_consumed = before.0.saturating_sub(self.gas_left().ref_time());
		self.engine_meter.charge_ref_time(ref_time_consumed)
	}
```
