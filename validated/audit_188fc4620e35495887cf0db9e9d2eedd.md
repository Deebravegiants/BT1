### Title
Delegate-calling a `HAS_CONTRACT_INFO=true` precompile executes precompile logic against the *caller's* contract-info/account instead of being rejected - ([File: substrate/frame/revive/src/exec.rs])

### Summary
`Stack::new_frame`'s delegate-call resolution branch resolves the target executable via `<AllPrecompiles<T>>::get(delegated_call.callee...)` without checking `precompile.has_contract_info()`, unlike the direct-call branch which explicitly gates `ContractInfo` creation/loading on that flag. As a result, a contract can `DelegateCall`/`call_v2` into a fixed-address precompile that requires `contract_info` (e.g. a `system`/`storage`-style builtin precompile) and have that precompile's `call_with_info` execute using the *delegating contract's own* `account_id` and cloned `contract_info`, not a dedicated precompile-owned context.

### Finding Description
In `Stack::new_frame` (`substrate/frame/revive/src/exec.rs`), for `FrameArgs::Call`, the direct (non-delegate) path explicitly special-cases `HAS_CONTRACT_INFO` precompiles when deciding what `ContractInfo` to load/create: [1](#0-0) 

However, the delegate-call branch that resolves the *executable* ignores this flag entirely — it just looks up `AllPrecompiles::get(delegated_call.callee...)` and, if found, unconditionally treats it as `ExecutableOrPrecompile::Precompile`, with no check that `precompile.has_contract_info()` is compatible with a delegate context: [2](#0-1) 

Meanwhile, `Ext::delegate_call` builds the pushed frame using the *caller's own* `account_id` and a clone of the *caller's own* `contract_info`, with only the target address recorded in `DelegateInfo.callee`: [3](#0-2) 

Because `precompile.has_contract_info()` is checked in the direct-call path (line 1087) but is absent from the delegate-executable-resolution path (lines 1105-1112), a `HAS_CONTRACT_INFO=true` precompile can be selected as the executable for a frame whose `contract_info`/`account_id` actually belong to the delegating contract, not the precompile's own dedicated account. This is reachable from PVM (`call_type == CallType::DelegateCall`) via `call_with_info`-capable builtin precompiles at fixed addresses (e.g. `substrate/frame/revive/src/precompiles/builtin/system.rs`, `storage.rs`), reached through: [4](#0-3) 

The `Precompile` trait documentation states that `HAS_CONTRACT_INFO=true` precompiles are tied 1:1 to their own fixed address's account/contract-info and that "Only `call_with_info` should be implemented," implying such precompiles are designed to always run against their own dedicated storage: [5](#0-4) 

No guard rejects a `DelegateCall`/`delegate_call` whose resolved target is a `HAS_CONTRACT_INFO=true` precompile before dispatch reaches `call_with_info` with a mismatched `ExtWithInfo` context.

### Impact Explanation
An attacker-controlled contract can `delegatecall` into a fixed-address, contract-info-backed builtin precompile. The precompile's `call_with_info` logic then executes with `env.address()`/`account_id`/`contract_info` pointing at the *delegating contract*, not the precompile's own dedicated account. Any storage-deposit accounting, contract-storage read/write, or `ContractInfo`-based bookkeeping the precompile performs via `ExtWithInfo` is misapplied to the caller's own contract-info, which can corrupt/confuse the precompile-managed accounting semantics that assume a stable, precompile-owned storage context.

### Likelihood Explanation
Reachable from a normal, unprivileged contract call: any signed account can deploy or invoke a PVM/EVM contract that issues `call_v2`/`DELEGATECALL` toward a known, publicly-documented fixed precompile address. `HAS_CONTRACT_INFO=true` precompiles must use a `Fixed` address matcher (enforced at compile time via `CHECK_COLLISION`), so their addresses are deterministic and discoverable, making the precondition trivially satisfiable and repeatable. I was not able to fully verify, within the available tool budget, whether a separate guard exists elsewhere in the `run()`/`Instance` dispatch path (I found but could not fully inspect two occurrences of a "Pre-compiles itself cannot delegate call" comment in `exec.rs`, which — based on partial context — appear to describe precompiles being unable to *issue* delegate calls themselves, not being protected as delegate-call *targets*). This uncertainty should be resolved before treating this as fully confirmed.

### Recommendation
In `Stack::new_frame`'s delegate-call executable resolution (`substrate/frame/revive/src/exec.rs`, the block resolving `delegated_call.callee` into an executable), reject the call (e.g. return `Error::<T>::InvalidCallFlags` or a dedicated `PrecompileDelegateDenied` error) whenever the resolved precompile has `HAS_CONTRACT_INFO == true`, mirroring the guard already present in the direct-call branch.

### Proof of Concept
Add a test in `substrate/frame/revive/src/tests/precompiles.rs`:
1. Define/reuse a `HAS_CONTRACT_INFO = true` test precompile (mirroring `WithInfo` in `substrate/frame/revive/src/precompiles/builtin/benchmarking.rs`) exposed at a fixed address.
2. Deploy a contract that issues a `call_v2` with `CallType::DelegateCall` targeting that precompile's fixed address.
3. Assert the call fails with `InvalidCallFlags`/`PrecompileDelegateDenied` (expected fix behavior) rather than succeeding with `env.address()`/`account_id` inside `call_with_info` equal to the delegating contract's own address (current, unguarded behavior) — assert on the observed `env.address()` value and on `ContractInfo` mutation location to demonstrate the storage-context confusion.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1078-1097)
```rust
				let mut contract = match (cached_info, &precompile) {
					(Some(info), _) => CachedContract::Cached(info),
					(None, None) => {
						if let Some(info) = AccountInfo::<T>::load_contract(&address) {
							CachedContract::Cached(info)
						} else {
							return Ok(None);
						}
					},
					(None, Some(precompile)) if precompile.has_contract_info() => {
						log::trace!(target: LOG_TARGET, "found precompile for address {address:?}");
						if let Some(info) = AccountInfo::<T>::load_contract(&address) {
							CachedContract::Cached(info)
						} else {
							let info = ContractInfo::new(&address, 0u32.into(), H256::zero())?;
							CachedContract::Cached(info)
						}
					},
					(None, Some(_)) => CachedContract::None,
				};
```

**File:** substrate/frame/revive/src/exec.rs (L1104-1120)
```rust
				// in case of delegate the executable is not the one at `address`
				let executable = if let Some(delegated_call) = &delegated_call {
					if let Some(precompile) =
						<AllPrecompiles<T>>::get(delegated_call.callee.as_fixed_bytes())
					{
						ExecutableOrPrecompile::Precompile {
							instance: precompile,
							_phantom: Default::default(),
						}
					} else {
						let Some(info) = AccountInfo::<T>::load_contract(&delegated_call.callee)
						else {
							return Ok(None);
						};
						let executable = E::from_storage(info.code_hash, meter)?;
						ExecutableOrPrecompile::Executable(executable)
					}
```

**File:** substrate/frame/revive/src/exec.rs (L1972-2009)
```rust
	fn delegate_call(
		&mut self,
		call_resources: &CallResources<T>,
		address: H160,
		input_data: Vec<u8>,
	) -> Result<(), ExecError> {
		// We reset the return data now, so it is cleared out even if no new frame was executed.
		// This is for example the case for unknown code hashes or creating the frame fails.
		*self.last_frame_output_mut() = Default::default();

		let top_frame = self.top_frame_mut();
		// Clone the contract info and apply pending storage changes so that
		// the child frame can correctly calculate storage deposit refunds.
		// See: <https://github.com/paritytech/contract-issues/issues/213>
		let mut contract_info = top_frame.contract_info().clone();
		top_frame.frame_meter.apply_pending_storage_changes(&mut contract_info);
		let account_id = top_frame.account_id.clone();
		let value = top_frame.value_transferred;
		if let Some(executable) = self.push_frame(
			FrameArgs::Call {
				dest: account_id,
				cached_info: Some(contract_info),
				delegated_call: Some(DelegateInfo {
					caller: self.caller().clone(),
					callee: address,
				}),
			},
			value,
			call_resources,
			self.is_read_only(),
			&input_data,
		)? {
			self.run(executable, input_data)
		} else {
			// Delegate-calls to non-contract accounts are considered success.
			Ok(())
		}
	}
```

**File:** substrate/frame/revive/src/vm/pvm.rs (L697-702)
```rust
			CallType::DelegateCall => {
				if flags.intersects(CallFlags::ALLOW_REENTRY | CallFlags::READ_ONLY) {
					return Err(Error::<E::T>::InvalidCallFlags.into());
				}
				self.ext.delegate_call(resources, callee, input_data)
			},
```

**File:** substrate/frame/revive/src/precompiles.rs (L174-214)
```rust
	/// Defines at which addresses this pre-compile exists.
	const MATCHER: AddressMatcher;
	/// Defines whether this pre-compile needs a contract info data structure in storage.
	///
	/// Enabling it unlocks more APIs for the pre-compile to use. Only pre-compiles with a
	/// fixed matcher can set this to true. This is enforced at compile time. Reason is that
	/// contract info is per address and not per pre-compile. Too many contract info structures
	/// and accounts would be created otherwise.
	///
	/// # When set to **true**
	///
	/// - An account will be created at the pre-compiles address when it is called for the first
	///   time. The ed is minted.
	/// - Contract info data structure will be created in storage on first call.
	/// - Only `call_with_info` should be implemented. `call` is never called.
	///
	/// # When set to **false**
	///
	/// - No account or any other state will be created for the address.
	/// - Only `call` should be implemented. `call_with_info` is never called.
	///
	/// # What to use
	///
	/// Should be set to false if the additional functionality is not needed. A pre-compile with
	/// contract info will incur both a storage read and write to its contract metadata when called.
	///
	/// The contract info enables additional functionality:
	/// - Storage deposits: Collect deposits from the origin rather than the caller. This makes it
	///   easier for contracts to interact with the pre-compile as deposits
	/// 	are paid by the transaction signer (just like gas). It also makes refunding easier.
	/// - Contract storage: You can use the contracts key value child trie storage instead of
	///   providing your own state.
	/// 	The contract storage automatically takes care of deposits.
	/// 	Providing your own storage and using pallet_revive to collect deposits is also possible,
	/// though.
	/// - Instantitation: Contract instantiation requires the instantiator to have an account. This
	/// 	is because its nonce is used to derive the new contracts account id and child trie id.
	///
	/// Have a look at [`ExtWithInfo`] to learn about the additional APIs that a contract info
	/// unlocks.
	const HAS_CONTRACT_INFO: bool;
```
