Audit Report

## Title
Storage-deposit charge coalescing in `execute_postponed_deposits` silently drops charges/refunds when a Terminated marker sits between two Alive segments for the same contract account - (File: `substrate/frame/revive/src/metering/storage.rs`)

## Summary
`RawMeter::execute_postponed_deposits` coalesces deferred deposit `Charge` entries keyed only by contract `AccountId`, with no notion of contract "generation." [1](#0-0)  When a `Terminated` marker for account `A` sits between two `Alive` charges for the same account (which occurs when a CREATE2 redeploy reuses `A`'s address within the same call stack), the merge arm for `(Alive, Terminated)`/`(Terminated, Alive)` unconditionally subtracts the `Alive` amount from `total_deposit` and converts the merged entry to `Terminated`, so that amount is never passed to `E::charge`. [2](#0-1) 

## Finding Description
Charges are appended in call order: on normal frame pop via `absorb()`, which pushes `Charge{contract, Alive{amount}}` for the net deposit of that sub-call, [3](#0-2)  and on termination via `Root::terminate()`, which pushes `Charge{contract, Terminated}` and adds the refund to `total_deposit`. [4](#0-3) 

`AccountInfoOf`/the contract's storage entry is removed synchronously inside `do_terminate`, described in the code as done "last as we cannot roll this back": [5](#0-4)  This means a subsequent `Instantiate` in the *same* call stack that derives the same address (e.g. via `create2` with the same salt/init-code) passes the duplicate-address guard in `ContractInfo::new`, since that guard only checks `AccountInfoOf::is_contract(address)` at the time of the new instantiate: [6](#0-5)  The address derivation itself (`address::create2`) is called from `FrameArgs::Instantiate` handling in `exec.rs`. [7](#0-6)  The existing "reject re-entrant instantiate at an in-construction address" fix (`prdoc/pr_12645.prdoc`) only blocks re-entrant collisions while a constructor frame for the same address is still on the call stack — it does not address a fully-completed-and-terminated instance being redeployed later in the same transaction, since by then no `Constructor` frame for that address remains on the stack.

Given this, the sequence `write(A)[c1] -> terminate(A) -> redeploy at A -> write(A)[c2]` produces charges `[Alive{c1}, Terminated, Alive{c2}]` for the same account key. `sort_by` is stable and the key is identical for all three entries, so order is preserved into the coalescing loop, which merges all three into one `Terminated` entry, subtracting both `c1` and `c2` from `total_deposit`. [1](#0-0)  The subsequent dispatch loops only invoke `E::charge` for entries still tagged `ContractState::Alive`, so neither `c1` nor `c2` triggers an actual balance/hold movement via this path. [8](#0-7)  The only existing guard is a `debug_assert!` for the `(Terminated, Terminated)` case, which does not fire here and provides no protection against the `Alive`-after-`Terminated` scenario. [9](#0-8) 

## Impact Explanation
The redeployed contract's storage deposit accounting diverges from its actual `ContractInfo` state: `ContractInfo::update_contract` at `absorb()` time has already recorded the new instance's storage usage/deposit fields in persistent storage, but the corresponding balance charge (or refund) for that usage is silently dropped from `total_deposit` and never dispatched through `E::charge`. This is a genuine storage-deposit accounting bypass reachable purely through ordinary contract logic (no privileged origin), matching an in-scope pallet-revive accounting/soundness issue.

## Likelihood Explanation
Exploitation requires an attacker-authored contract that, within a single call stack: instantiates at address `A`, performs a storage-affecting write, terminates `A` (removing `AccountInfoOf` immediately per `do_terminate`), then redeploys a new contract at the same address `A` via CREATE2 with the same salt/init-code, and performs another storage write before the call stack unwinds to the root meter. This is fully attacker-controlled through standard EVM-style CREATE2/"metamorphic contract" semantics that `pallet-revive` supports, and is repeatable via ordinary signed extrinsics — no admin, governance, or node-level privilege is needed. The main residual uncertainty (acknowledged in the original report) is a full end-to-end confirmation via an actual `bare_call` integration test proving the exact charge/frame ordering in a live execution, since order-of-absorption depends on nested frame pop timing which was reasoned about via code inspection rather than directly executed here.

## Recommendation
Tag each `Charge` with a per-instantiation identifier (e.g., derived from the trie ID or a deployment generation counter) so that charges from a redeployed instance are never coalesced with a prior `Terminated` marker for the same address. At minimum, `execute_postponed_deposits` should treat a `Terminated` marker as a hard boundary: any `Alive` charges appearing after a `Terminated` entry for the same account id should be split into a new coalescing group and dispatched independently, rather than merged into the terminated entry.

## Proof of Concept
1. Unit-test `RawMeter::execute_postponed_deposits` directly with a manually constructed `charges` vector `[Charge{A, Alive{Charge(c1)}}, Charge{A, Terminated}, Charge{A, Alive{Charge(c2)}}]` and assert that `E::charge` is invoked with `Charge(c2)` for `A`. Currently the merged entry becomes `Terminated` and `c2` (along with `c1`) is subtracted from `total_deposit` without any corresponding `E::charge` call, in `substrate/frame/revive/src/metering/storage.rs`.
2. Integration-level PoC in `substrate/frame/revive/src/tests.rs`: use `bare_call`/`bare_instantiate` to (a) instantiate contract `X` at address `A` via CREATE2 with salt `S`, (b) write storage in `A`, (c) self-destruct `A`, (d) within the same call, redeploy a contract at `A` using the same salt `S`, (e) write storage in the redeployed `A`, then assert that `balance_on_hold(A) == ContractInfo(A).total_deposit()` — the mismatch demonstrates the dropped charge.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L296-303)
```rust
		self.total_deposit = self
			.total_deposit
			.saturating_add(&absorbed.total_deposit)
			.saturating_add(&own_deposit);
		self.charges.extend_from_slice(&absorbed.charges);

		self.recalulculate_max_charged();

```

**File:** substrate/frame/revive/src/metering/storage.rs (L396-429)
```rust
		// Coalesce charges of the same contract
		self.charges.sort_by(|a, b| a.contract.cmp(&b.contract));
		self.charges = {
			let mut coalesced: Vec<Charge<T>> = Vec::with_capacity(self.charges.len());
			for mut ch in mem::take(&mut self.charges) {
				if let Some(last) = coalesced.last_mut() {
					if last.contract == ch.contract {
						match (&mut last.state, &mut ch.state) {
							(
								ContractState::Alive { amount: last_amount },
								ContractState::Alive { amount: ch_amount },
							) => {
								*last_amount = last_amount.saturating_add(&ch_amount);
							},
							(ContractState::Alive { amount }, ContractState::Terminated) |
							(ContractState::Terminated, ContractState::Alive { amount }) => {
								// undo all deposits made by a terminated contract
								self.total_deposit = self.total_deposit.saturating_sub(&amount);
								last.state = ContractState::Terminated;
							},
							(ContractState::Terminated, ContractState::Terminated) => {
								debug_assert!(
									false,
									"We never emit two terminates for the same contract."
								)
							},
						}
						continue;
					}
				}
				coalesced.push(ch);
			}
			coalesced
		};
```

**File:** substrate/frame/revive/src/metering/storage.rs (L431-441)
```rust
		// refunds first so origin is able to pay for the charges using the refunds
		for charge in self.charges.iter() {
			if let ContractState::Alive { amount: amount @ Deposit::Refund(_) } = &charge.state {
				E::charge(origin, &charge.contract, amount, exec_config)?;
			}
		}
		for charge in self.charges.iter() {
			if let ContractState::Alive { amount: amount @ Deposit::Charge(_) } = &charge.state {
				E::charge(origin, &charge.contract, amount, exec_config)?;
			}
		}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L446-456)
```rust
	/// Flag a `contract` as terminated.
	///
	/// This will signal to the meter to discard all charged and refunds incured by this
	/// contract.
	pub fn terminate(&mut self, contract: T::AccountId, refunded: BalanceOf<T>) {
		self.total_deposit = self.total_deposit.saturating_add(&Deposit::Refund(refunded));
		self.charges.push(Charge { contract, state: ContractState::Terminated });

		// no need to recalculate max_charged here as the total consumed amount will just decrease
		// with this extra refund
	}
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

**File:** substrate/frame/revive/src/exec.rs (L1839-1846)
```rust
			// delete the contracts data last as its infallible
			ContractInfo::<T>::queue_for_deletion(trie_id.clone(), contract_account.clone());
			AccountInfoOf::<T>::remove(contract_address);
			ImmutableDataOf::<T>::remove(contract_address);

			// the meter needs to discard all deposits interacting with the terminated contract
			// we do this last as we cannot roll this back
			transaction_meter.terminate(contract_account.clone(), refund);
```

**File:** substrate/frame/revive/src/storage.rs (L196-212)
```rust
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
```
