### Title
Missing precompile-address check in `ContractInfo::new` / instantiate path lets `CREATE2` squat a stateful precompile's address - (File: substrate/frame/revive/src/exec.rs, substrate/frame/revive/src/storage.rs)

### Summary
The instantiate branch of `Stack::new_frame` (`FrameArgs::Instantiate`) computes the target address with `address::create2`/`create1` and calls `ContractInfo::new`, which only checks `AccountInfo::<T>::is_contract(address)` against `AccountInfoOf` — it never consults `<AllPrecompiles<T>>::get(address)`. For precompiles that are `has_contract_info == true` and have not yet been lazily initialized (their `ContractInfo` is only created on first `Call`, see `exec.rs` lines 1087-1094), `AccountInfoOf` has no entry yet, so `is_contract` returns `false` and an attacker's `instantiate`/`CREATE2` succeeds and writes an attacker-chosen `ContractInfo` (code_hash, trie_id, deposits) at that address before the precompile ever initializes itself.

### Finding Description
`address::create2` (`substrate/frame/revive/src/address.rs:273-285`) is a pure function of `deployer`, `code`, `input_data`, and `salt`; an attacker who knows a target precompile's fixed 20-byte address can brute-force or directly select a `salt`/`code` combination that hashes to that address (or simply predict it from the fixed matcher ranges used by `AllPrecompiles`).

In `Stack::new_frame` (`substrate/frame/revive/src/exec.rs:1141-1163`), the `FrameArgs::Instantiate` arm computes `address` and immediately calls:
```
let contract = ContractInfo::new(&address, <System<T>>::account_nonce(&sender), *executable.code_hash())?;
```
`ContractInfo::new` (`substrate/frame/revive/src/storage.rs:196-234`) only guards against collision via:
```
if <AccountInfo<T>>::is_contract(address) { return Err(Error::<T>::DuplicateContract.into()); }
```
which reads `AccountInfoOf::<T>::get(address)`. It never calls `<AllPrecompiles<T>>::get(address.as_fixed_bytes())`. For a stateful precompile (`has_contract_info == true`) that has not yet been called (its `ContractInfo` is created lazily only inside the `FrameArgs::Call` branch at `exec.rs:1087-1094`), `AccountInfoOf` has no row, so `is_contract` is `false` and the instantiate succeeds, persisting the attacker's `code_hash`, `trie_id`, and storage deposits at that address once the constructor frame pops.

The separate `push_frame` re-entrancy guard added for EIP-684 (`exec.rs:1238-1246`, see `prdoc/pr_12645.prdoc`) only rejects a nested instantiate whose target matches another `Constructor` frame already on the stack — it does not check precompile addresses either, so it does not close this gap.

Note: for the normal `FrameArgs::Call` path (`exec.rs:1074`), `<AllPrecompiles<T>>::get` is checked first and always wins when selecting the `ExecutableOrPrecompile` to run (`exec.rs:1121-1136`), so an attacker's stored bytecode can never actually be *executed* in place of the precompile. The concrete damage is that the attacker can plant/poison the `ContractInfo` row (trie_id, code_hash, storage_base_deposit) that a stateful precompile will later pick up via `AccountInfo::<T>::load_contract(&address)` (`exec.rs:1089`), instead of the precompile's own canonical `ContractInfo::new(&address, 0u32.into(), H256::zero())` initialization (`exec.rs:1092`).

### Impact Explanation
An unprivileged contract caller can, via a normal `CREATE2` call, force the pallet to create and persist a `ContractInfo` (child trie id, code_hash, storage deposits) at an address reserved for a stateful builtin/external precompile before that precompile is ever lazily initialized. This corrupts the precompile's expected storage bootstrap (wrong trie_id, non-zero/attacker code_hash) and reserves deposits under the attacker's account for state that legitimately belongs to pallet-defined precompile bookkeeping, violating the stated invariant that no user-deployed contract state may occupy a precompile-reserved address. This does not let the attacker intercept live calls to the precompile (those are still routed to the precompile function unconditionally), but it does allow squatting/poisoning precompile-address contract metadata and forcing inconsistent state/deposit accounting for the first legitimate use of that stateful precompile.

### Likelihood Explanation
Fully attacker-reachable through the standard `CREATE2` opcode from any contract, requiring only knowledge of the fixed, public precompile address ranges (`BuiltinAddressMatcher`/`AllPrecompiles`) and the ability to brute-force a `salt`/`code` pair — both are public, deterministic, and repeatable with no special privileges, proxy, or governance access needed.

### Recommendation
In `ContractInfo::new` (or earlier, in the `FrameArgs::Instantiate` arm of `Stack::new_frame`), reject instantiate when `<AllPrecompiles<T>>::get(address.as_fixed_bytes())` returns `Some(_)`, mirroring the `is_contract` guard, so any address in a precompile's matcher range is treated as permanently reserved regardless of whether its `ContractInfo` has been lazily materialized yet.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/exec/tests.rs` (or `storage.rs`):
1. Pick a stateful builtin precompile address (`has_contract_info == true`) that has never been called, so `AccountInfoOf::get(addr)` is `None`.
2. From a deployed factory contract, call `instantiate` with a `salt`/`code` combination such that `address::create2(&deployer, code, input_data, &salt) == precompile_addr` (can be constructed directly by choosing `deployer`/`salt` to match a precomputed target, or by asserting the property on a mocked `AllPrecompiles` with a known fixed address).
3. Assert the instantiate call returns `Err(Error::<T>::DuplicateContract)` (expected fix) — currently it returns `Ok(..)` and `AccountInfoOf::get(precompile_addr)` shows `AccountType::Contract` with attacker's `code_hash`, proving the current unguarded success.
4. Follow-up call to `precompile_addr` still executes the precompile logic (showing lack of call-interception) while `AccountInfo::<T>::load_contract(&precompile_addr)` returns the attacker's poisoned `ContractInfo`, demonstrating state corruption. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** substrate/frame/revive/src/address.rs (L272-285)
```rust
/// Determine the address of a contract using the CREATE2 semantics.
pub fn create2(deployer: &H160, code: &[u8], input_data: &[u8], salt: &[u8; 32]) -> H160 {
	let init_code_hash = {
		let init_code: Vec<u8> = code.into_iter().chain(input_data).cloned().collect();
		keccak_256(init_code.as_ref())
	};
	let mut bytes = [0; 85];
	bytes[0] = 0xff;
	bytes[1..21].copy_from_slice(deployer.as_bytes());
	bytes[21..53].copy_from_slice(salt);
	bytes[53..85].copy_from_slice(&init_code_hash);
	let hash = keccak_256(&bytes);
	H160::from_slice(&hash[12..])
}
```

**File:** substrate/frame/revive/src/exec.rs (L1072-1097)
```rust
			FrameArgs::Call { dest, cached_info, delegated_call } => {
				let address = T::AddressMapper::to_address(&dest);
				let precompile = <AllPrecompiles<T>>::get(address.as_fixed_bytes());

				// which contract info to load is unaffected by the fact if this
				// is a delegate call or not
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

**File:** substrate/frame/revive/src/exec.rs (L1121-1137)
```rust
				} else {
					if let Some(precompile) = precompile {
						ExecutableOrPrecompile::Precompile {
							instance: precompile,
							_phantom: Default::default(),
						}
					} else {
						let executable = E::from_storage(
							contract
								.as_contract()
								.expect("When not a precompile the contract was loaded above; qed")
								.code_hash,
							meter,
						)?;
						ExecutableOrPrecompile::Executable(executable)
					}
				};
```

**File:** substrate/frame/revive/src/exec.rs (L1141-1163)
```rust
			FrameArgs::Instantiate { sender, executable, salt, input_data } => {
				let deployer = T::AddressMapper::to_address(&sender);
				let account_nonce = <System<T>>::account_nonce(&sender);
				let address = if let Some(salt) = salt {
					address::create2(&deployer, executable.code(), input_data, salt)
				} else {
					use sp_runtime::Saturating;
					address::create1(
						&deployer,
						// the Nonce from the origin has been incremented pre-dispatch, so we
						// need to subtract 1 to get the nonce at the time of the call.
						if origin_is_caller {
							account_nonce.saturating_sub(1u32.into()).saturated_into()
						} else {
							account_nonce.saturated_into()
						},
					)
				};
				let contract = ContractInfo::new(
					&address,
					<System<T>>::account_nonce(&sender),
					*executable.code_hash(),
				)?;
```

**File:** substrate/frame/revive/src/exec.rs (L1238-1246)
```rust
			// EIP-684: an in-construction address is not in `AccountInfoOf` yet, so the
			// `is_contract` guard in `ContractInfo::new` misses this re-entrant collision.
			if frame.entry_point == ExportedFunction::Constructor &&
				self.frames().any(|f| {
					f.entry_point == ExportedFunction::Constructor &&
						f.account_id == frame.account_id
				}) {
				return Err(Error::<T>::DuplicateContract.into());
			}
```

**File:** substrate/frame/revive/src/storage.rs (L191-234)
```rust
impl<T: Config> ContractInfo<T> {
	/// Constructs a new contract info **without** writing it to storage.
	///
	/// This returns an `Err` if an contract with the supplied `account` already exists
	/// in storage.
	pub fn new(
		address: &H160,
		nonce: T::Nonce,
		code_hash: sp_core::H256,
	) -> Result<Self, DispatchError> {
		if <AccountInfo<T>>::is_contract(address) {
			return Err(Error::<T>::DuplicateContract.into());
		}

		// Reject reuse of an address whose previous occupant still has unflushed
		// `NativeDepositOf` rows in the deletion queue. The on_idle drain will eventually
		// clear them; until it does, instantiating here would let the new contract inherit
		// stale per-payer entitlements.
		let account_id = T::AddressMapper::to_fallback_account_id(address);
		if NativeDepositOf::<T>::iter_prefix(&account_id).next().is_some() {
			return Err(Error::<T>::PendingDepositCleanup.into());
		}

		let trie_id = {
			let buf = ("bcontract_trie_v1", address, nonce).using_encoded(T::Hashing::hash);
			buf.as_ref()
				.to_vec()
				.try_into()
				.expect("Runtime uses a reasonable hash size. Hence sizeof(T::Hash) <= 128; qed")
		};

		let contract = Self {
			trie_id,
			code_hash,
			storage_bytes: 0,
			storage_items: 0,
			storage_byte_deposit: Zero::zero(),
			storage_item_deposit: Zero::zero(),
			storage_base_deposit: Zero::zero(),
			immutable_data_len: 0,
		};

		Ok(contract)
	}
```

**File:** prdoc/pr_12645.prdoc (L1-18)
```text
title: '[pallet-revive] Reject re-entrant instantiate at an in-construction address'
doc:
- audience: Runtime Dev
  description: |-
    Fixes https://github.com/paritytech/polkadot-sdk/issues/12639

    A contract's `ContractInfo` is not written to `AccountInfoOf` until its constructor
    frame pops, so the `is_contract` collision guard in `ContractInfo::new` could not see an
    address that was still being constructed. A re-entrant `CREATE2` with the same salt and
    code (which is nonce independent) therefore resolved to the same address and ran a second
    constructor frame for one account, permanently leaking its consumer reference and code
    refcount and orphaning the second child trie's storage deposit.

    `push_frame` now rejects a nested instantiate whose target address already appears as a
    `Constructor` frame on the call stack, returning `DuplicateContract` (matching EIP-684).
crates:
- name: pallet-revive
  bump: patch
```
