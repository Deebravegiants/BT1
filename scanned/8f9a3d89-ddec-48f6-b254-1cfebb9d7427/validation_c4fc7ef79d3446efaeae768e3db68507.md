### Title
Missing fuel reassignment in `EngineMeter::charge_ref_time` breaks wasmi fuel/ref_time reconciliation - ([File: substrate/frame/contracts/src/gas.rs])

### Summary
`EngineMeter::<T>::charge_ref_time` computes `self.fuel.checked_sub(amount)` but never assigns the result back to `self.fuel`; the computed, decremented value is discarded. Because `self.fuel` is left unchanged by this function, the `Syncable` value handed back to the caller (and ultimately written into the wasmi engine's fuel counter) never reflects the ref_time cost of the host call that just ran.

### Finding Description
`EngineMeter::<T>::charge_ref_time` is:
```rust
fn charge_ref_time(&mut self, ref_time: u64) -> Result<Syncable, DispatchError> {
    let amount = ref_time
        .checked_div(T::Schedule::get().ref_time_by_fuel())
        .ok_or(Error::<T>::InvalidSchedule)?;

    self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
    Ok(Syncable(self.fuel))
}
``` [1](#0-0) 

The line `self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;` only performs the `checked_sub` for the purpose of detecting underflow (returning `OutOfGas` if it *would* underflow); the `Option<u64>` result is dropped, and `self.fuel` is never updated to the reduced value. The function then returns `Ok(Syncable(self.fuel))` — the pre-existing, unreduced fuel value.

This function is invoked from `GasMeter::sync_to_executor`, which is called when leaving a host function to compute how much ref_time the host call itself consumed (`ref_time_consumed`) and convert it into engine fuel units to push back into the wasmi executor:
```rust
pub fn sync_to_executor(&mut self, before: RefTimeLeft) -> Result<Syncable, DispatchError> {
    let ref_time_consumed = before.0.saturating_sub(self.gas_left().ref_time());
    self.engine_meter.charge_ref_time(ref_time_consumed)
}
``` [2](#0-1) 

Because `charge_ref_time` never actually decrements `self.fuel`, the `Syncable` returned to the caller (and subsequently written back into the wasmi engine's internal fuel counter for the next slice of wasm bytecode execution) always reflects the *pre-host-call* fuel level rather than the correctly reduced level. Each time a contract calls any host function, the wasmi engine's execution-fuel budget effectively gets "topped back up" to the stale `self.fuel` value instead of being debited for the host call's ref_time cost. This is a real, independent accounting bug in the fuel reconciliation path (distinct from, and more severe than, the rounding-based mechanism hypothesized in the question) — it means the engine-side fuel counter used to bound raw wasm-bytecode execution between host calls never accounts for host-call costs at all, regardless of any division rounding in `ref_time_by_fuel()`.

Note that primary ref_time accounting for host function costs still goes through `GasMeter::charge` directly reducing `gas_left` [3](#0-2) , so the overall weight budget (`gas_left`) is not directly bypassed by this bug. However, the wasmi engine's own instruction-fuel counter — which is the mechanism that actually bounds unmetered wasm bytecode execution between host calls — is not being kept in sync with the true remaining budget, since `charge_ref_time`'s effect on `self.fuel` is silently discarded.

### Impact Explanation
A contract that repeatedly invokes cheap host functions inside a tight loop can cause the wasmi engine's internal fuel counter to be repeatedly reset to a stale, higher value on every host-call return (via the unmodified `self.fuel` returned as `Syncable`), rather than being properly debited for each host call's ref_time cost. This allows the wasm interpreter to execute more raw bytecode instructions between reconciliation points than the ref_time budget should permit, which matches the scoped impact of gas-metering underflow / unmetered computation enabling weight-budget overrun.

### Likelihood Explanation
The bug triggers unconditionally on every call to `charge_ref_time` (i.e., on every host function return during contract execution), requiring no special schedule configuration or division-rounding edge case — any contract exercising host calls in a loop is a sufficient precondition, making this both easily reachable and repeatable.

### Recommendation
Fix `charge_ref_time` to actually assign the decremented value back to `self.fuel`:
```rust
self.fuel = self.fuel.checked_sub(amount).ok_or_else(|| Error::<T>::OutOfGas)?;
```
so that the `Syncable` returned to the caller (and pushed into the wasmi engine's fuel counter) reflects the true post-host-call fuel level.

### Proof of Concept
Rust unit test in `substrate/frame/contracts/src/gas.rs`'s test module:
1. Construct a `GasMeter::<Test>` with a known `gas_limit` and a `Schedule` with a fixed `ref_time_by_fuel()`.
2. Simulate a host-call boundary: call `sync_from_executor(initial_fuel)`, then perform a `charge()` for a token representing host-call cost, then call `sync_to_executor(before)`.
3. Assert that the returned `Syncable`'s inner `u64` value equals `initial_fuel - (token_weight.ref_time() / ref_time_by_fuel())`, not the unchanged `initial_fuel`.
4. Repeat across multiple host-call boundaries and assert the engine fuel value monotonically decreases in lockstep with `gas_consumed()`, i.e., `gas_limit - gas_consumed() == engine fuel * ref_time_by_fuel()` within one unit of rounding tolerance — this assertion fails against current code because `self.fuel` never decreases via `charge_ref_time`.

### Citations

**File:** substrate/frame/contracts/src/gas.rs (L69-76)
```rust
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

**File:** substrate/frame/contracts/src/gas.rs (L255-258)
```rust
	pub fn sync_to_executor(&mut self, before: RefTimeLeft) -> Result<Syncable, DispatchError> {
		let ref_time_consumed = before.0.saturating_sub(self.gas_left().ref_time());
		self.engine_meter.charge_ref_time(ref_time_consumed)
	}
```
