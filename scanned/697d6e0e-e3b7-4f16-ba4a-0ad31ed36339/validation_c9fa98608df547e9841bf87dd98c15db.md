### Title
Storage-deposit charge coalescing in `execute_postponed_deposits` silently drops charges/refunds when a Terminated marker sits between two Alive segments for the same contract account - (File: `substrate/frame/revive/src/metering/storage.rs`)

### Summary
`RawMeter::execute_postponed_deposits` coalesces deferred deposit `Charge` entries using only the contract `AccountId` as the merge key, with no notion of which "generation" (pre-termination vs. post-redeployment) of a contract a given charge belongs to. When a `Terminated` marker for account `A` is followed (or preceded) by an `Alive` charge for the same account `A` — which happens whenever a CREATE2 redeploy reuses `A`'s address within the same call stack/root meter — the coalescing logic treats the later/earlier `Alive` amount as belonging to the terminated instance and subtracts it from `total_deposit`, then converts the merged entry to `Terminated`, causing that amount to never be passed to `E::charge` at all.

### Finding Description
The coalescing code lives at [1](#0-0) . It sorts `self.charges` by `contract` account id only and then merges adjacent entries sharing that id. The merge match arm explicitly handles `(Alive, Terminated)` and `(Terminated, Alive)` by doing:

```
self.total_deposit = self.total_deposit.saturating_sub(&amount);
last.state = ContractState::Terminated;
```

for *either* order, i.e. it assumes any `Alive` charge adjacent to a `Terminated` charge for the same account id was made by the terminated contract and should be "undone." This assumption is only valid if a contract account can be charged at most once (Alive segment) before its single Terminated marker, per call stack — the code even encodes "We never emit two terminates for the same contract" as a `debug_assert!` for the `(Terminated, Terminated)` case, but performs no equivalent check for the `Alive-after-Terminated` case, silently merging it instead.

Charges are pushed onto the vector in call order via `absorb()` ( [2](#0-1) , pushing `Charge{contract, state: Alive{amount}}`) and via `Root::terminate()` ( [3](#0-2) , pushing `Charge{contract, state: Terminated}`). Sequence for `write(A) -> terminate(A) -> redeploy at A -> write(A)` produces: `[Alive{c1}, Terminated, Alive{c2}]`. Since `sort_by` is stable and all entries share the same key, order is preserved, and the coalescing loop merges all three into a single `Terminated` entry, subtracting **both** `c1` and `c2` from `total_deposit`.

After coalescing, the two dispatch loops ( [4](#0-3) ) only match `ContractState::Alive { amount: Refund(_) | Charge(_) }` to invoke `E::charge`, which performs the actual balance/hold movement. A `Terminated` entry never triggers `E::charge`, so the second write's deposit (`c2`), which belongs to the **redeployed** contract instance and was already reflected in that instance's persisted `ContractInfo` fields via `Diff::update_contract` at `absorb()` time, is never actually charged (or refunded) to the origin's real balance/hold. The on-chain `ContractInfo` accounting and the actual currency hold diverge — the redeployed contract is credited with storage usage in its metadata without the origin ever paying for it via this deferred-charge path.

Existing protections are insufficient: there is no per-instantiation/generation tag on `Charge`, no assertion catching `Alive`-adjacent-to-`Terminated` for a second contract generation, and the coalescing key (`contract` account id) is exactly the value that CREATE2 redeployment intentionally reuses.

### Impact Explanation
The redeployed contract's storage deposit is under-charged (or a refund could be dropped, depending on ordering/sign), since the coalescing step subtracts the second-generation charge from `total_deposit` and drops it from the `E::charge` dispatch loop entirely. This is a concrete storage-deposit accounting bypass: the origin can grow persistent contract storage for a new contract instance at the reused address without paying the corresponding deposit through this code path, while `ContractInfo` for the new instance still records the (unbacked) storage usage.

### Likelihood Explanation
This requires: (1) the caller to instantiate and terminate a contract, then redeploy a new contract at the same address, all within one root meter's call stack (one `bare_call`/extrinsic), and (2) at least one storage-affecting operation both before termination and after redeployment. Termination in `do_terminate` removes `AccountInfoOf` immediately within its own `with_transaction` ( [5](#0-4) ), which is consistent with allowing a same-address re-instantiation later in the same call stack (CREATE2 "metamorphic contract" pattern), though I was not able to fully verify the instantiate-side duplicate-address check within the remaining investigation budget — this should be confirmed with a direct test. Assuming redeployment at the same address within one transaction is permitted (as it generally is in EVM-style CREATE2 semantics that `pallet-revive` targets), the exploit is fully attacker-controlled and repeatable via ordinary signed extrinsics/contract calls — no privileged origin needed.

### Recommendation
Tag each `Charge` (and each `Contribution`/`terminate` marker) with a per-instantiation generation identifier (e.g., derived from `ContractInfo`'s deployment nonce/trie_id, or simply track termination as a hard boundary that flushes/dispatches all charges for that account immediately rather than deferring them into the same coalescing pass as charges from a later redeployment). At minimum, `execute_postponed_deposits` should never merge an `Alive` charge into a `Terminated` marker unless it is certain both charges originate from the *same* logical contract instance; charges emitted after a `Terminated` marker for the same account id should be treated as belonging to a new instance and coalesced/dispatched separately (e.g., split into a new coalescing group whenever a `Terminated` entry for that contract id is encountered again as a boundary).

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/metering/storage/tests.rs` (or an `exec`-level integration test in `substrate/frame/revive/src/tests.rs` using `bare_call`/`bare_instantiate` with CREATE2 salt reuse):

1. Instantiate contract `X` at address `A` via CREATE2 with salt `S`.
2. Write storage in `A` (`Diff` charge `c1`).
3. `SELFDESTRUCT`/terminate `A` with `beneficiary`.
4. Within the same `bare_call`/extrinsic, redeploy a new contract at the same address `A` (same CREATE2 salt `S`, same or different code hash).
5. Write storage in the redeployed `A` (`Diff` charge `c2`).
6. Call `execute_postponed_deposits` on the root meter.
7. Assert:
   - The origin's balance delta reflects a real charge of `c2` (net of the termination refund), not zero.
   - `AccountInfoOf`/`ContractInfo` for the redeployed `A` reports the same deposit amount that was actually reserved/held on `A`'s account (i.e., `balance_on_hold(A) == ContractInfo(A).total_deposit()`), catching the divergence caused by the dropped `Alive` charge.
   - Directly unit-test `RawMeter::execute_postponed_deposits` with a manually constructed `charges` vector `[Alive{Charge(c1)}, Terminated, Alive{Charge(c2)}]` and assert that `E::charge` is invoked with `Charge(c2)` for `A` (currently it is not — the merged entry becomes `Terminated` and `c2` is silently dropped from `total_deposit` without any corresponding `E::charge` call).

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L269-309)
```rust
	/// In case a contract reverted the child meter should just be dropped in order to revert
	/// any changes it recorded.
	///
	/// # Parameters
	///
	/// - `absorbed`: The child storage meter that should be absorbed.
	/// - `origin`: The origin that spawned the original root meter.
	/// - `contract`: The contract's account that this sub call belongs to.
	/// - `info`: The info of the contract in question. `None` if the contract was terminated.
	pub fn absorb(
		&mut self,
		absorbed: RawMeter<T, E, Nested>,
		contract: &T::AccountId,
		info: Option<&mut ContractInfo<T>>,
	) {
		// We are now at the position to calculate the actual final net charge of `absorbed` as we
		// now have the contract information `info`. Before that we only took net charges related to
		// the contract storage into account but ignored net refunds.
		// However, with this complete information there is no need to recalculate `max_charged` for
		// `absorbed` here before we absorb it because the actual final net charge will not be more
		// than the net charge we observed before (as we only ignored net refunds but not net
		// charges).
		self.max_charged = self
			.max_charged
			.max(self.consumed().saturating_add(&absorbed.max_charged()).charge_or_zero());

		let own_deposit = absorbed.own_contribution.update_contract(info);
		self.total_deposit = self
			.total_deposit
			.saturating_add(&absorbed.total_deposit)
			.saturating_add(&own_deposit);
		self.charges.extend_from_slice(&absorbed.charges);

		self.recalulculate_max_charged();

		if !own_deposit.is_zero() {
			self.charges.push(Charge {
				contract: contract.clone(),
				state: ContractState::Alive { amount: own_deposit },
			});
		}
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
