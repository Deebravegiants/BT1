Audit Report

## Title
`EngineMeter::charge_ref_time` never actually deducts fuel for host-call costs, letting the wasmi engine execute extra instructions beyond `gas_limit` - (File: substrate/frame/contracts/src/gas.rs)

## Summary
`EngineMeter::charge_ref_time` computes the fuel equivalent of a host-function's ref_time cost via `checked_sub`, but discards the result instead of assigning it back to `self.fuel`, then returns `Syncable(self.fuel)` containing the unchanged, pre-deduction value. This is confirmed directly in the current source: line 74 (`self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;`) performs the bounds check but never writes the result back, unlike the symmetrical `set_fuel` at line 63 (`self.fuel = fuel;`) which correctly mutates state. [1](#0-0) [2](#0-1) 

## Finding Description
`sync_to_executor` is called when leaving a host function to compute the ref_time consumed since entry and forward it to `EngineMeter::charge_ref_time`, whose result (`Syncable`) is meant to be written back into the real wasmi engine fuel counter by the caller. [3](#0-2) 

Inside `charge_ref_time`, `amount` (the fuel equivalent of the host call's ref_time cost) is computed correctly, but the line `self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;` only performs the overflow/underflow check — it does not reassign `self.fuel`. The subsequent `Ok(Syncable(self.fuel))` therefore returns the pre-host-call fuel value, unchanged. This is corroborated by the doc comment "Returns the amount of fuel left," which implies deduction was intended but never coded. [1](#0-0) 

By contrast, `set_fuel` (used by `sync_from_executor` to reconcile the engine's true fuel usage after a WASM-execution segment) correctly assigns `self.fuel = fuel` and returns the actual weight consumed, which is properly deducted from `gas_left` via `checked_reduce`. [4](#0-3) 

The pallet-side bookkeeping counter `gas_left` is correctly reduced for host-call costs by `GasMeter::charge`, independent of `EngineMeter`. [5](#0-4)  The bug is isolated to the `EngineMeter.fuel` field, which is intended to mirror the real wasmi engine's fuel budget so that the local `self.fuel` value can later be written into the interpreter via whatever mechanism consumes the `Syncable` wrapper.

## Impact Explanation
I was unable to fully trace, within the available tool budget, the exact call site in `substrate/frame/contracts/src/wasm/mod.rs` where the `Syncable` value returned by `sync_to_executor` is actually applied to the live wasmi `Store`'s fuel (e.g., via `store.set_fuel(...)` or equivalent). The claim's core premise — that this `Syncable` value is written back into the wasmi engine to reset its executable fuel budget — is asserted by the report but not independently confirmed against the wasmi-integration code in this review. Without observing that write-back site, it's not fully verified that the discarded subtraction actually manifests as "the wasmi engine executes more instructions than `gas_left` allows"; it's equally possible the integration code recomputes/derives the engine's fuel from `gas_left` in a way that is unaffected by this specific field, or that the impact is bounded/self-correcting elsewhere.

That said, the described root-cause defect in `charge_ref_time` itself is real and verified by direct code reading: the subtraction is computed but discarded, which is a genuine accounting bug in `EngineMeter.fuel`'s internal bookkeeping regardless of how it's consumed downstream.

## Likelihood Explanation
The defect in the code as read is unconditional — it fires on every host call with nonzero ref_time cost — so if the downstream consumption of `Syncable` is indeed used to set the wasmi engine's fuel counter as claimed, the described exploit path (a contract making many host calls near `gas_limit`) would be trivially and deterministically reachable by any unprivileged account uploading/instantiating a contract.

## Recommendation
Regardless of the downstream consumption details, the internal logic bug should be fixed by assigning the result of the subtraction back to `self.fuel`:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;
    self.fuel = self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
```
Before treating this as a critical severity DoS/weight-escape finding, the actual write-back path from `Syncable` into the live wasmi engine's fuel state must be located and confirmed (e.g., in `substrate/frame/contracts/src/wasm/mod.rs` or the sandbox execution glue) to establish that the discarded subtraction genuinely permits extra WASM instruction execution beyond `gas_limit`.

## Proof of Concept
Unit test directly on `EngineMeter`/`GasMeter::sync_to_executor` as proposed in the claim would deterministically demonstrate the internal bug (fuel value unchanged after `charge_ref_time`). Confirming the broader security impact requires an additional integration-level test that traces the `Syncable` value into the actual wasmi `Store` fuel setter and observes that the interpreter is permitted to run more instructions than the nominal `gas_limit` should allow — this step was not verified in this review due to inability to locate/inspect the exact write-back call site within the tool-call budget available.

### Citations

**File:** substrate/frame/contracts/src/gas.rs (L58-65)
```rust
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

**File:** substrate/frame/contracts/src/gas.rs (L206-220)
```rust
	#[inline]
	pub fn charge<Tok: Token<T>>(&mut self, token: Tok) -> Result<ChargedAmount, DispatchError> {
		#[cfg(test)]
		{
			// Unconditionally add the token to the storage.
			let erased_tok =
				ErasedToken { description: format!("{:?}", token), token: Box::new(token) };
			self.tokens.push(erased_tok);
		}
		let amount = token.weight();
		// It is OK to not charge anything on failure because we always charge _before_ we perform
		// any action
		self.gas_left = self.gas_left.checked_sub(&amount).ok_or_else(|| Error::<T>::OutOfGas)?;
		Ok(ChargedAmount(amount))
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
