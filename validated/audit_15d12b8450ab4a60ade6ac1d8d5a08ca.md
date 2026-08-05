Confirmed: the code exactly matches the claim. Line 74 computes `self.fuel.checked_sub(amount)` only for its `None`-check (via `.ok_or_else`) and discards the `Some` value — `self.fuel` is never reassigned, unlike `set_fuel` at line 63 which does `self.fuel = fuel;`. This means `sync_to_executor` (line 255-258) returns the *unchanged* pre-host-call fuel value, which gets written back into wasmi's `Store` via `set_fuel`, silently un-charging wasmi's own instruction budget for every host-function call while `gas_left` (the weight/fee-based limit) is still correctly decremented. This is a genuine, reachable double-bookkeeping bug: the two gas-tracking mechanisms (wasmi fuel vs. `gas_left` weight) diverge, letting a contract execute more raw Wasm instructions than its `gas_limit` should allow before `OutOfGas` is eventually raised — a real, unprivileged, deterministic accounting bug in `pallet_contracts`.

Audit Report

## Title
`EngineMeter::charge_ref_time` never persists the fuel decrement, letting host-function costs be silently "refunded" to the wasmi engine's fuel counter - (File: substrate/frame/contracts/src/gas.rs)

## Summary
`EngineMeter::charge_ref_time` computes `self.fuel.checked_sub(amount)` only to check for underflow but never assigns the result back to `self.fuel`, unlike `set_fuel` which correctly persists its computed value. Consequently `sync_to_executor` returns the unchanged pre-host-call fuel to be written back into wasmi's `Store`, meaning every chargeable host-function call's weight cost is deducted from `gas_left` but never subtracted from wasmi's own fuel counter, letting contracts execute more raw bytecode than their `gas_limit` should permit.

## Finding Description
`EngineMeter::charge_ref_time` at `substrate/frame/contracts/src/gas.rs:69-76` is:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;

    self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```
The `checked_sub` result (`Some(new_value)`) is discarded; `self.fuel` retains its pre-call value. Contrast with `set_fuel` (lines 58-65) which explicitly does `self.fuel = fuel;` after computing the delta — confirming the omission in `charge_ref_time` is an inconsistency/defect rather than intended behavior.

This function is called from `GasMeter::sync_to_executor` (lines 255-258), invoked when leaving a host function via the `sync_gas_after` code generated in `substrate/frame/contracts/proc-macro/src/lib.rs`. The returned `Syncable` value is written back into wasmi's `Store` via `__caller__.set_fuel(fuel.into())`. Since `self.fuel` was never decremented, this write-back restores wasmi's fuel to the value it had before the host call started — effectively un-charging the host function's cost from wasmi's own budget, even though the same cost is correctly subtracted from `gas_left` via `GasMeter::charge`. The two gas-tracking mechanisms (`gas_left` weight-based limit and wasmi's raw fuel) thus diverge on every chargeable host call, and the divergence is only caught later when `gas_left` finally underflows (in a subsequent `sync_from_executor` or at `process_result`) — by which time wasmi has already executed the extra, over-credited instructions.

## Impact Explanation
Any unprivileged account calling or instantiating a contract via the standard `pallet_contracts::Call::call`/`instantiate` extrinsics can author Wasm that repeatedly invokes any chargeable host function (e.g. `seal_set_storage`) to accumulate uncharged wasmi fuel, allowing the contract to execute more raw bytecode instructions than its declared `gas_limit` should permit before `OutOfGas` is eventually raised. This is a resource-accounting bug that lets real CPU/wall-clock work occur beyond what was paid for, without affecting balances directly — a weight/DoS-adjacent issue rather than fund loss.

## Likelihood Explanation
The bug is deterministic and triggers on every host-function call; no privileged origin, race condition, or special setup is required — any signed account can deploy a contract that loops calling a chargeable host function. This is trivially reachable and repeatable, scaling linearly with the number of host calls made.

## Recommendation
Fix `EngineMeter::charge_ref_time` to persist the decremented value:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;
    self.fuel = self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```

## Proof of Concept
1. Unit test in `substrate/frame/contracts/src/gas.rs`: construct `GasMeter::<Test>::new(gas_limit)`, call `sync_from_executor(engine_fuel)`, then `charge(token)` for a host-function-equivalent cost, then `sync_to_executor(before)`.
2. Assert the returned fuel value equals `engine_fuel - (host_cost / ref_time_by_fuel)`. Currently the assertion fails because the returned fuel equals `engine_fuel` unchanged.
3. Integration test: deploy a fixture contract looping `seal_set_storage` calls interleaved with busy-loops under a fixed `gas_limit`, and confirm actual wasmi fuel/instructions consumed exceeds the theoretical bound `gas_limit / ref_time_by_fuel`. [1](#0-0) [2](#0-1)

### Citations

**File:** substrate/frame/contracts/src/gas.rs (L56-76)
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
