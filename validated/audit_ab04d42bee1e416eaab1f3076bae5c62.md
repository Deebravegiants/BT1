### Title
`EngineMeter::charge_ref_time` never mutates `fuel`, letting a malicious contract leak fuel and overrun the gas limit before it is caught - ([File: substrate/frame/contracts/src/gas.rs])

### Summary
`EngineMeter::charge_ref_time` computes whether subtracting the fuel-equivalent of a host-function's ref_time charge would underflow, but it discards the result of `checked_sub` instead of assigning it back to `self.fuel`. The function then returns the *unchanged* (pre-charge) fuel value, which is fed straight back into the wasmi engine via `store.set_fuel(...)`. As a result, every host-function call effectively "refunds" fuel that should have been permanently deducted, letting a contract accumulate unmetered execution capacity that is only caught (as `OutOfGas`) after the excess Wasm instructions have already executed.

### Finding Description
`EngineMeter::charge_ref_time` in `substrate/frame/contracts/src/gas.rs`: [1](#0-0) 

```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;

    self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```

`self.fuel.checked_sub(amount)` is only used to check for an `OutOfGas` underflow; its `Some` value (the correctly decremented fuel) is never assigned back to `self.fuel`. The function then returns `Syncable(self.fuel)` — the *stale, pre-charge* fuel value.

This value flows directly into the wasmi engine. The macro-generated host-function wrapper does: [2](#0-1) 

```rust
let fuel = __caller__.data_mut().ext().gas_meter_mut().sync_to_executor(__gas_left_before__)...?;
__caller__.set_fuel(fuel.into()).expect("Fuel metering is enabled; qed");
```

and `sync_to_executor` calls `charge_ref_time`: [3](#0-2) 

So each time a host function is invoked and exited, the wasmi engine's fuel counter is reset to the value it had **before entering the host function**, instead of that value minus the fuel-equivalent of the host-function's own ref_time charge. The `GasMeter.gas_left` (the outer, authoritative accounting field) is still correctly decremented for both the wasm-fuel-tracked consumption (via `sync_from_executor` → `EngineMeter::set_fuel`, which *does* correctly assign `self.fuel = fuel`) and the direct host-function charge (via `charge()`), so the bug is invisible to `gas_left` bookkeeping in isolation. The real effect is that the wasmi engine's own internal fuel pool becomes inflated relative to the true remaining `gas_left`/`R` budget by the accumulated per-call amounts that should have been deducted.

Because wasmi enforces its own trap only when *its* internal fuel counter reaches zero, a contract that repeatedly calls cheap host functions (any host function with a nonzero `RuntimeCosts` charge) accumulates a growing "fuel reserve" that was never actually removed from the engine. It can then spend that leaked reserve on a single long, real-Wasm-only compute burst between two sync points. The over-limit consumption is only detected afterward, when `sync_from_executor`'s `gas_left.checked_reduce(weight_consumed)` finally underflows and returns `Error::<T>::OutOfGas` — but by then the CPU time for that burst has already been spent. [4](#0-3) 

### Impact Explanation
This allows an unprivileged contract, invoked via the ordinary `pallet_contracts::Pallet::call`/`instantiate` extrinsics with an attacker-supplied Wasm blob, to execute real CPU-bound Wasm instructions beyond the amount its declared `gas_limit`/weight should permit, before the runtime's `OutOfGas` check can stop it. Aggregated across many contract calls in a block, this is a weight-accounting bypass that can push actual execution time above the block's declared weight, i.e. a block-overweight / gas-metering-bypass DoS vector, matching the scoped impact.

### Likelihood Explanation
- No special privileges are required: any signed account can deploy and call a contract (`Contracts::instantiate_with_code` / `Contracts::call`).
- The trigger is purely code-controlled: repeatedly invoke any host function with nonzero `RuntimeCosts` weight (e.g. simple getters) in a loop to accumulate leaked fuel, then run a tight compute loop to consume the leaked reserve as unmetered CPU time.
- The bug is deterministic (not a race or timing issue) and reproducible on every call that mixes host-function invocations with a following compute-heavy stretch.
- The magnitude of leakage per call is bounded by the host function's own ref_time charge divided by `ref_time_by_fuel`, but it accumulates linearly with the number of host calls, so a contract can amplify it arbitrarily within its own gas budget.

### Recommendation
Fix `EngineMeter::charge_ref_time` to actually persist the decremented fuel value, e.g.:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;
    self.fuel = self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```
Add a regression test asserting that fuel set on the wasmi store strictly decreases (by the correct amount) across repeated host-function calls, matching `ref_time` charged by `GasMeter::charge`.

### Proof of Concept
Rust unit test plan in `substrate/frame/contracts/src/gas.rs` tests module:
1. Construct a `GasMeter::<Test>::new(limit)` with a known `ref_time_by_fuel`.
2. Simulate the host-call cycle: call `sync_from_executor(engine_fuel)` with a starting fuel value, then call `gas_meter.charge(some_token_with_nonzero_weight)` (simulating a host-function's internal cost charge), then call `sync_to_executor(before)`.
3. Assert that the fuel value returned by `sync_to_executor` (the `Syncable`, which is what gets written back via `set_fuel` to the executor) equals `initial_fuel - (token.weight().ref_time() / ref_time_by_fuel())`, i.e., strictly less than the pre-call fuel.
4. Repeat the entry/charge/exit cycle N times without ever hitting `OutOfGas`, and assert cumulative reported fuel decreases monotonically; with the current buggy code this assertion fails because `self.fuel` never changes across calls to `charge_ref_time`.
5. As an integration-level PoC, deploy a contract whose Wasm calls a cheap host function (e.g. a getter) M times in a loop, then runs a large busy-loop; assert via benchmarking/instrumentation that actual wasmi fuel consumed for the busy-loop portion exceeds `gas_limit.ref_time()/ref_time_by_fuel() - (fuel already spent on the M host calls)`, demonstrating the leaked reserve is spendable.

### Citations

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

**File:** substrate/frame/contracts/src/gas.rs (L239-245)
```rust
	pub fn sync_from_executor(&mut self, engine_fuel: u64) -> Result<RefTimeLeft, DispatchError> {
		let weight_consumed = self.engine_meter.set_fuel(engine_fuel);
		self.gas_left
			.checked_reduce(weight_consumed)
			.ok_or_else(|| Error::<T>::OutOfGas)?;
		Ok(RefTimeLeft(self.gas_left.ref_time()))
	}
```

**File:** substrate/frame/contracts/src/gas.rs (L247-258)
```rust
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

**File:** substrate/frame/contracts/proc-macro/src/lib.rs (L733-748)
```rust
		// Write gas from pallet-contracts into wasmi after leaving the host function.
		let sync_gas_after = if expand_blocks {
			quote! {
				let fuel = __caller__
					.data_mut()
					.ext()
					.gas_meter_mut()
					.sync_to_executor(__gas_left_before__)
					.map_err(|err| {
						let err = TrapReason::from(err);
						wasmi::Error::host(err)
					})?;
				 __caller__
					 .set_fuel(fuel.into())
					 .expect("Fuel metering is enabled; qed");
			}
```
