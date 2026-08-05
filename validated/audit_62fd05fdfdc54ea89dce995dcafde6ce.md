Audit Report

## Title
Reentrant `instantiate` during contract construction can collide with the in-construction address in `pallet-contracts` (unlike `pallet-revive`, which was patched for this exact bug) - (File: `substrate/frame/contracts/src/exec.rs`)

## Summary
`pallet-contracts` derives new contract addresses deterministically from `(sender, code_hash, input_data, salt)` with no dependence on the call-stack nonce [1](#0-0) , and only persists a contract's `ContractInfo` to `<ContractInfoOf<T>>` when a **`Call`** frame pops — never for a `Constructor` frame [2](#0-1) . Because `ContractInfo::new`'s only collision guard checks `<ContractInfoOf<T>>::contains_key(account)` [3](#0-2) , it cannot see an address whose constructor is still running higher up the call stack, and `push_frame` performs no additional cross-frame check against other in-progress `Constructor` frames [4](#0-3) .

## Finding Description
The exploit path is: contract `B` is instantiated by factory `A` (address `X` derived from `(A, code_hash, input_data, salt)`, `Constructor` frame pushed for `X`, `ContractInfo` only cached in-memory). `B`'s constructor calls back into `A` (a `Call` frame, not a self-call, so the "no calling into a contract from its own constructor" restriction referenced in the `push_frame` comment does not block this, since that restriction concerns re-entering the same account, not re-entering a different upstream caller) [5](#0-4) . `A` then calls `Ext::instantiate` again with the *same* `code_hash`, `input_data`, and `salt`, producing the same deterministic address `X` [6](#0-5) [7](#0-6) . Since `X`'s `ContractInfo` was never written to `ContractInfoOf` (only a `Constructor` frame is on the stack for it), `ContractInfo::new`'s `contains_key` check passes, and a second `Constructor` frame for the identical account `X` is pushed onto the stack alongside the first, unguarded by any cross-frame check in `push_frame` [8](#0-7) .

This is confirmed to be the exact bug class that was identified and fixed for the sibling `pallet-revive` pallet: the `prdoc/pr_12645.prdoc` changelog explicitly describes "A contract's `ContractInfo` is not written to `AccountInfoOf` until its constructor frame pops... A re-entrant `CREATE2` with the same salt and code... therefore resolved to the same address and ran a second constructor frame for one account, permanently leaking its consumer reference and code refcount and orphaning the second child trie's storage deposit," and states the fix adds a `push_frame` check against existing `Constructor` frames on the stack [9](#0-8) . A corresponding regression test `reentrant_instantiate_at_same_address_is_rejected` exists for `pallet-revive` verifying the fixed behavior [10](#0-9) . No equivalent guard or test exists in `pallet-contracts`'s `push_frame`.

## Impact Explanation
A malicious, fully permissionless contract deployer can trigger two `Constructor` frames to run concurrently for a single account `X` in `pallet-contracts`, mirroring the confirmed `pallet-revive` bug: this corrupts per-account bookkeeping (double consumer-reference/refcount increments, duplicated or orphaned storage-deposit accounting, and inconsistent child-trie storage state for one account). This is a genuine state-corruption class issue reachable via ordinary, permissionless contract-to-contract calls, with no privileged origin required.

## Likelihood Explanation
Likelihood is realistic: any account can call the standard `instantiate`/`instantiate_with_code` extrinsics and deploy arbitrary attacker-controlled contract code implementing the constructor/factory re-entrancy pattern described above, entirely on-chain, with no relayer/bridge/node privileges needed. The fact that Parity independently identified, documented (`prdoc/pr_12645.prdoc`), and fixed (with a dedicated regression test) the structurally identical vulnerability in `pallet-revive` strongly corroborates that the analogous unguarded code path in `pallet-contracts` is exploitable rather than theoretical.

## Recommendation
Add the same cross-frame check used in `pallet-revive`'s `push_frame` to `pallet-contracts`'s `push_frame`: before pushing a new `Constructor` frame, iterate existing frames and reject with `Error::<T>::DuplicateContract` if any existing frame is also a `Constructor` frame for the same `account_id`, matching the EIP-684-style guard already applied in `pallet-revive`.

## Proof of Concept
Port `pallet-revive`'s `reentrant_instantiate_at_same_address_is_rejected` test to `substrate/frame/contracts/src/tests.rs`: deploy factory contract `A`, have `A` instantiate constructor contract `B` with a fixed `salt`/`code_hash`/`input_data`; `B`'s constructor calls back into `A`, which calls `Ext::instantiate` a second time with identical `code_hash`/`input_data`/`salt`. In `pallet-contracts` this second call is expected to succeed (creating a colliding second `Constructor` frame for the same account) rather than returning `Error::<T>::DuplicateContract`, confirming the missing guard relative to the fixed `pallet-revive` behavior.

### Citations

**File:** substrate/frame/contracts/src/address.rs (L55-67)
```rust
impl<T: Config> AddressGenerator<T> for DefaultAddressGenerator {
	/// Formula: `hash("contract_addr_v1" ++ deploying_address ++ code_hash ++ input_data ++ salt)`
	fn contract_address(
		deploying_address: &T::AccountId,
		code_hash: &CodeHash<T>,
		input_data: &[u8],
		salt: &[u8],
	) -> T::AccountId {
		let entropy = (b"contract_addr_v1", deploying_address, code_hash, input_data, salt)
			.using_encoded(T::Hashing::hash);
		Decode::decode(&mut TrailingZeroInput::new(entropy.as_ref()))
			.expect("infinite length input; no invalid inputs for type; qed")
	}
```

**File:** substrate/frame/contracts/src/exec.rs (L866-882)
```rust
				FrameArgs::Instantiate { sender, nonce, executable, salt, input_data } => {
					let account_id = Contracts::<T>::contract_address(
						&sender,
						&executable.code_hash(),
						input_data,
						salt,
					);
					let contract = ContractInfo::new(&account_id, nonce, *executable.code_hash())?;
					(
						account_id,
						contract,
						executable,
						None,
						ExportedFunction::Constructor,
						Some(nonce),
					)
				},
```

**File:** substrate/frame/contracts/src/exec.rs (L909-948)
```rust
	/// Create a subsequent nested frame.
	fn push_frame(
		&mut self,
		frame_args: FrameArgs<T, E>,
		value_transferred: BalanceOf<T>,
		gas_limit: Weight,
		deposit_limit: BalanceOf<T>,
		read_only: bool,
	) -> Result<E, ExecError> {
		if self.frames.len() == T::CallStack::size() {
			return Err(Error::<T>::MaxCallDepthReached.into());
		}

		// We need to make sure that changes made to the contract info are not discarded.
		// See the `in_memory_changes_not_discarded` test for more information.
		// We do not store on instantiate because we do not allow to call into a contract
		// from its own constructor.
		let frame = self.top_frame();
		if let (CachedContract::Cached(contract), ExportedFunction::Call) =
			(&frame.contract_info, frame.entry_point)
		{
			<ContractInfoOf<T>>::insert(frame.account_id.clone(), contract.clone());
		}

		let frame = top_frame_mut!(self);
		let nested_gas = &mut frame.nested_gas;
		let nested_storage = &mut frame.nested_storage;
		let (frame, executable, _) = Self::new_frame(
			frame_args,
			value_transferred,
			nested_gas,
			gas_limit,
			nested_storage,
			deposit_limit,
			self.determinism,
			read_only,
		)?;
		self.frames.push(frame);
		Ok(executable)
	}
```

**File:** substrate/frame/contracts/src/exec.rs (L1335-1361)
```rust
	fn instantiate(
		&mut self,
		gas_limit: Weight,
		deposit_limit: BalanceOf<Self::T>,
		code_hash: CodeHash<T>,
		value: BalanceOf<T>,
		input_data: Vec<u8>,
		salt: &[u8],
	) -> Result<(AccountIdOf<T>, ExecReturnValue), ExecError> {
		let executable = E::from_storage(code_hash, self.gas_meter_mut())?;
		let nonce = self.next_nonce();
		let executable = self.push_frame(
			FrameArgs::Instantiate {
				sender: self.top_frame().account_id.clone(),
				nonce,
				executable,
				salt,
				input_data: input_data.as_ref(),
			},
			value,
			gas_limit,
			deposit_limit,
			self.is_read_only(),
		)?;
		let account_id = self.top_frame().account_id.clone();
		self.run(executable, input_data).map(|ret| (account_id, ret))
	}
```

**File:** substrate/frame/contracts/src/storage.rs (L81-88)
```rust
	pub fn new(
		account: &AccountIdOf<T>,
		nonce: u64,
		code_hash: CodeHash<T>,
	) -> Result<Self, DispatchError> {
		if <ContractInfoOf<T>>::contains_key(account) {
			return Err(Error::<T>::DuplicateContract.into());
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

**File:** substrate/frame/revive/src/exec/tests.rs (L1270-1273)
```rust
#[test]
fn reentrant_instantiate_at_same_address_is_rejected() {
	// EIP-684: while `B1` constructs at address `X`, its constructor re-enters the deployer to
	// instantiate the same code+salt. That resolves to `X` again and must be rejected rather
```
