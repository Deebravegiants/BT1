### Title
Weight/fuel desynchronization between host-call charges and PolkaVM engine fuel allows execution beyond `effective_weight_limit` before `OutOfGas` is raised - (File: substrate/frame/revive/src/metering/weight.rs)

### Summary
`WeightMeter::sync_to_executor` is invoked exactly once, before the PolkaVM instance starts running (`substrate/frame/revive/src/vm/pvm/env.rs` `prepare_call`), and `WeightMeter::sync_from_executor` is invoked exactly once, only after the entire `instance.run()` loop has fully terminated (`substrate/frame/revive/src/vm/pvm.rs` `PreparedCall::call`). During the whole run loop, host-function (`Ecalli`) costs are charged directly against `weight_consumed` via `charge_weight_token`/`WeightMeter::charge`, which never accounts for the fuel the PolkaVM engine is concurrently burning for interpreted instructions. This lets the sum of host-call charges and the engine's own fuel consumption each independently approach `effective_weight_limit`, so the *combined* real resource consumption can exceed the limit before the single, end-of-call `sync_from_executor` call detects and reports `OutOfGas`.

### Finding Description
In `substrate/frame/revive/src/vm/pvm/env.rs` (`prepare_call`, line 85), `sync_to_executor()` computes the PolkaVM fuel budget from `weight_left()` *once*, before the instance starts executing:
```
let gas_limit_polkavm: polkavm::Gas = runtime.ext().frame_meter_mut().sync_to_executor();
...
instance.set_gas(gas_limit_polkavm);
```
This uses `EngineMeter::sync_remaining_ref_time` [1](#0-0) , converting the entire current `weight_left()` into a fuel budget for the whole call.

The interpreter loop in `substrate/frame/revive/src/vm/pvm.rs` (`PreparedCall::call`, lines 841-858) only calls `sync_from_executor` once, after `handle_interrupt` finally returns `Some(exec_result)` (i.e., `Finished`, `Trap`, `NotEnoughGas`, `Return`, `Termination`, error). For every `Ecalli` (host-function call) encountered along the way, `handle_interrupt` dispatches to `handle_ecall` and returns `None`, continuing the loop *without* ever syncing fuel back to the `WeightMeter` [2](#0-1) .

Host functions charge weight directly via `charge_gas`/`charge_weight_token`, which calls `WeightMeter::charge` [3](#0-2) . That check compares `self.weight_consumed` (which, mid-execution, reflects only previously-charged host-call costs, since instruction fuel has not been synced yet) against `effective_weight_limit`. Because `self.weight_consumed` lags behind the engine's real, in-flight fuel usage for the entire duration of a call (potentially containing thousands of interleaved host calls and instruction bursts), the enforcement performed by each individual `charge()` call is blind to the concurrently-accumulating engine fuel debt.

Concretely: at call start, `effective_weight_limit = L`, `weight_consumed = 0`. The engine is given a fuel budget worth up to `L` (`sync_to_executor`). The contract can run instructions that consume close to the full `L` of fuel internally (not yet synced), then invoke a host call; the host call's `charge()` only sees `weight_consumed = 0` plus the new charge, so it is allowed even though real (unsynced) fuel consumption is already near `L`. This can repeat for many host calls (each individually cheap and within `effective_weight_limit` as measured against the stale `weight_consumed`), accumulating host-cost charges that are themselves bounded by `L`. Only when the run loop finally exits does `sync_from_executor` add the engine's actual fuel-derived weight on top of the already-charged host costs, and only then is the overflow detected and `OutOfGas` returned [4](#0-3) . By that point, both the host-call work and the instruction execution the fuel represents have already been performed on-chain — the check is a post-hoc, not preventive, enforcement for the interleaved portion of a single call/frame's execution.

### Impact Explanation
Within a single contract call/frame, the maximum enforceable weight is effectively the sum of two independently-bounded budgets — (a) host-call charges bounded by `effective_weight_limit`, and (b) engine-fuel consumption bounded by the fuel budget derived from `weight_left()` at call start — rather than a single, correctly synchronized bound. This allows a crafted contract (host-call-heavy loop interleaved with fuel-heavy instruction bursts) to cause real, already-executed computation to exceed `effective_weight_limit` before `OutOfGas` is raised, i.e., a weight/gas metering bypass enabling execution beyond the intended budget for that call. The final result is still eventually rejected as `OutOfGas`, but the excess computation has already consumed real block-execution time/resources by the time the error is surfaced.

### Likelihood Explanation
This is fully reachable by any unprivileged account able to deploy and invoke a PolkaVM contract (`instantiate`/`call` extrinsics or EVM-compatible `eth_transact`), no privileged origin required. The attacker only needs ordinary PVM bytecode crafted to interleave many cheap host calls (e.g., `caller`, `now`, `block_number`, or other low-cost syscalls) with heavy instruction loops, both of which are freely composable in contract bytecode. No signature/origin/proxy checks are relevant; this is a pure weight-metering desynchronization bug in the execution engine sync protocol.

### Recommendation
Synchronize the `WeightMeter` with the PolkaVM engine on every host-function boundary, not just once per call: call `sync_from_executor` immediately upon entering a host call (to account for fuel consumed by instructions since the last sync) before charging the host-call cost, and call `sync_to_executor` again immediately before returning control to the engine (to give it an updated, correctly-reduced fuel budget). This ensures `weight_consumed` always reflects true cumulative consumption at the moment each `charge()` decision is made, preserving the invariant `weight_consumed <= effective_weight_limit` at every check.

### Proof of Concept
Rust unit/fuzz test in `substrate/frame/revive/src/metering/weight.rs`'s test module:
1. Construct a `WeightMeter` with `effective_weight_limit = L`.
2. Call `sync_to_executor()` to obtain the initial fuel budget `F0` (simulating engine start).
3. Simulate the engine consuming fuel down to near-zero (`engine_fuel ≈ 0`) *without* calling `sync_from_executor` (simulating instructions executed before any host call).
4. While `sync_from_executor` has not yet been called, invoke `charge(token)` for a token whose weight cost `C` is `< L` (simulating a host call charged while engine fuel is still un-synced) — assert it succeeds (`Ok`).
5. Repeat step 4 multiple times such that cumulative host charges approach `L`.
6. Finally call `sync_from_executor(engine_fuel ≈ 0)` and observe that `weight_consumed` jumps to `(sum of host charges) + (fuel consumed ≈ F0 converted to weight)`, which exceeds `L`.
7. Assert: at every point *before* the final `sync_from_executor` call, `weight_consumed <= effective_weight_limit` holds only because it excludes the unsynced engine fuel — i.e., the invariant "`weight_consumed` reflects true total consumption" is violated during the interleaved sequence, and the total real work performed (fuel spent + host costs) exceeds `L` before `OutOfGas` is returned.

### Citations

**File:** substrate/frame/revive/src/metering/weight.rs (L59-64)
```rust
	/// Charge the given amount of ref time.
	/// Returns the amount of fuel left.
	fn sync_remaining_ref_time(&mut self, remaining_ref_time: u64) -> polkavm::Gas {
		self.fuel = remaining_ref_time.saturating_div(Self::ref_time_per_fuel());
		self.fuel.try_into().unwrap_or(polkavm::Gas::MAX)
	}
```

**File:** substrate/frame/revive/src/metering/weight.rs (L187-207)
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
		let new_consumed = self.weight_consumed.saturating_add(amount);
		if new_consumed.any_gt(self.effective_weight_limit) {
			return Err(<Error<T>>::OutOfGas.into());
		}

		self.weight_consumed = new_consumed;
		Ok(ChargedAmount(amount))
	}
```

**File:** substrate/frame/revive/src/metering/weight.rs (L236-248)
```rust
	pub fn sync_from_executor(&mut self, engine_fuel: polkavm::Gas) -> Result<(), DispatchError> {
		let weight_consumed = self
			.engine_meter
			.set_fuel(engine_fuel.try_into().map_err(|_| Error::<T>::OutOfGas)?);

		self.weight_consumed.saturating_accrue(weight_consumed);
		if self.weight_consumed.any_gt(self.effective_weight_limit) {
			self.weight_consumed = self.effective_weight_limit;
			return Err(<Error<T>>::OutOfGas.into());
		}

		Ok(())
	}
```

**File:** substrate/frame/revive/src/vm/pvm/env.rs (L152-184)
```rust
			Ok(Step) => None,
			Ok(Ecalli(idx)) => {
				// This is a special hard coded syscall index which is used by benchmarks
				// to abort contract execution. It is used to terminate the execution without
				// breaking up a basic block. The fixed index is used so that the benchmarks
				// don't have to deal with import tables.
				if cfg!(feature = "runtime-benchmarks") && idx == SENTINEL {
					return Some(Ok(ExecReturnValue {
						flags: ReturnFlags::empty(),
						data: Vec::new(),
					}));
				}
				let Some(syscall_symbol) = module.imports().get(idx) else {
					return Some(Err(<Error<E::T>>::InvalidSyscall.into()));
				};
				match self.handle_ecall(instance, syscall_symbol.as_bytes()) {
					Ok(None) => None,
					Ok(Some(return_value)) => {
						instance.write_output(return_value);
						None
					},
					Err(TrapReason::Return(ReturnData { flags, data })) => {
						match ReturnFlags::from_bits(flags) {
							None => Some(Err(Error::<E::T>::InvalidCallFlags.into())),
							Some(flags) => Some(Ok(ExecReturnValue { flags, data })),
						}
					},
					Err(TrapReason::Termination) => Some(Ok(Default::default())),
					Err(TrapReason::SupervisorError(error)) => Some(Err(error.into())),
				}
			},
		}
	}
```
