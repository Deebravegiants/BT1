### Title
Sequential (non-reentrant) same-contract calls let a stale storage-deposit `Charge` be applied after `terminate()`, permanently locking origin funds in a dead account - (File: substrate/frame/contracts/src/storage/meter.rs)

### Summary
`RawMeter::try_into_deposit` in `substrate/frame/contracts/src/storage/meter.rs` processes the `charges: Vec<Charge<T>>` list by simply filtering into "refunds first, then charges", with no coalescing per contract account, even though the accompanying comment on the `charges` field assumes "only one charge per contract." If the same contract account is called twice, non-overlapping, within a single call stack (call #1 accrues an `Alive` `Charge`, call #2 terminates the contract producing a `Terminated` `Refund`), both entries survive independently in the vector and are executed separately by `ReservingExt::charge`.

### Finding Description
`RawMeter::absorb` (`storage/meter.rs:325-344`) unconditionally pushes a new `Charge{contract, amount, state}` entry every time a nested frame is absorbed, keyed only by contract account, with no lookup/merge against a prior entry for the same contract. `RawMeter::terminate` (`meter.rs:470-476`) sets `own_contribution = Contribution::Terminated{deposit: Refund(info.total_deposit()), beneficiary}` for the *current* frame only; it has no visibility into other, already-absorbed charges recorded earlier for the same contract in the same call stack.

`Ext::terminate` in `exec.rs` guards against concurrent reentrancy via `if self.is_recursive() { return Err(TerminatedWhileReentrant) }`, but this only checks whether the account is *currently* on the frame stack. It does not prevent a contract from being called, returning, and then being called again (sequentially, not concurrently) later in the same top-level call stack orchestrated by a caller/router contract — a completely ordinary, non-malicious usage pattern (e.g. a contract calling a token contract twice in one transaction).

Concretely:
1. EOA calls contract `A`.
2. `A` calls `B` (frame 1): `B` writes storage, accruing e.g. `Deposit::Charge(5)`. Frame pops normally (not reverted); `A`'s meter absorbs it, pushing `Charge{contract: B, amount: Charge(5), state: Alive}` into the root meter's `charges` vec (via chained `absorb` calls up to root).
3. Frame 1 has already returned, so `is_recursive()` is `false` for `B`'s account.
4. `A` calls `B` again (frame 2): `B` calls `terminate(beneficiary)`. `Ext::terminate` succeeds (not reentrant), sets frame's `nested_storage` to `Terminated{deposit: Refund(total_deposit), beneficiary}`, deletes `ContractInfoOf::<T>` for `B`, decrements refcount/consumers, schedules trie deletion.
5. Frame 2 absorbs into `A`'s meter, pushing a second, independent `Charge{contract: B, amount: Refund(total_deposit), state: Terminated{beneficiary}}`.
6. At top level, `try_into_deposit` (`meter.rs:395-408`) iterates `self.charges` filtering `Refund` entries first, calling `E::charge` for the `Terminated` refund: this calls `transfer_on_hold(..., Precision::BestEffort)` from `B` to origin, then (because `state` is `Terminated`) sweeps `B`'s remaining `reducible_balance` to `beneficiary` and `dec_consumers`.
7. Then the second loop processes `Charge` (non-refund) entries, including the stale entry from step 2: `E::charge(origin, B, Charge(5), Alive)` executes `transfer_and_hold(HoldReason::StorageDepositReserve, origin, B, 5, Precision::Exact, Preserve, Polite)`, transferring 5 units from `origin` into `B`'s now-dead account and placing a hold there.

Because `B`'s `ContractInfoOf` entry has already been removed and its consumer already decremented, this account is no longer a callable contract; there is no permissionless way to invoke `terminate()` again on it to release the newly-created hold (`HoldReason::StorageDepositReserve`). The `origin`'s deposit balance becomes stranded/unclaimable — a permanent partial fund freeze, in direct violation of the "assets must ... not be permanently frozen" invariant. This is a real accounting/ordering bug: `try_into_deposit`/`ReservingExt::charge` never checks whether the target `contract` account referenced by a `Charge::Charge` entry is still a live contract before transferring-and-holding into it.

Note: the sibling `pallet-revive` implementation (`substrate/frame/revive/src/metering/storage.rs::execute_postponed_deposits`, lines ~396-429) explicitly guards against exactly this class of issue by sorting and coalescing charges per contract, with special-case logic: `(Alive, Terminated) => { undo all deposits made by a terminated contract; ... }`, and an explicit debug-assert "We never emit two terminates for the same contract." This coalescing logic does not exist in `substrate/frame/contracts/src/storage/meter.rs`'s `try_into_deposit`, confirming that pallet-revive's authors identified and fixed this exact ordering hazard while the older `pallet_contracts` meter was left without the safeguard.

### Impact Explanation
A user's storage-deposit balance can be permanently locked in a dead/deleted contract account with no code and no remaining `ContractInfo`, making the held balance practically unrecoverable through the normal contract-termination path. This is a fund-freeze bug matching the "User-controlled assets must remain fully backed and cannot be ... permanently frozen" invariant. It is a self-inflicted loss for the calling account in the straightforward reproduction (caller controls both `A` and `B`), but it demonstrates a real accounting-order flaw reachable purely through normal `pallet_contracts::call` extrinsics with attacker-authored contracts — no privileged access required. The invariant "(refund to origin) + (residual sweep to beneficiary) + (remaining on-hold)" does not sum correctly: an extra `Charge` transfer is executed against an account that no longer has any owner/contract to reclaim it.

### Likelihood Explanation
Preconditions are simple and fully attacker-controlled: deploy two contracts `A` (orchestrator) and `B` (callee); have `A` call `B` twice sequentially in one transaction, with `B` writing storage on the first call and calling `terminate()` on the second. No governance, no race condition with other users, and no privileged origin is needed — a single signed extrinsic (`pallet_contracts::call`) triggers the whole sequence deterministically. This is trivially reproducible on every run.

### Recommendation
In `substrate/frame/contracts/src/storage/meter.rs::RawMeter<T,E,Root>::try_into_deposit`, coalesce `self.charges` by `contract` account before executing them (mirroring `pallet-revive`'s `execute_postponed_deposits`), so that any `Alive` `Charge`/`Refund` entries for a contract that has also been `Terminated` in the same call stack are discarded/merged into the `Terminated` refund rather than executed independently. Alternatively/additionally, `ReservingExt::charge` should verify the destination `contract` account is still a live contract (`ContractInfoOf::<T>::contains_key`) before performing a `Deposit::Charge` transfer-and-hold, and reroute/refund to `origin` instead if not.

### Proof of Concept
Rust integration test (in `substrate/frame/contracts/src/tests.rs` style, using two fixture contracts):
1. Deploy contract `B` with a `call()` entry point that: on first invocation writes N bytes of storage (accrues deposit); on second invocation calls `terminate_v1(beneficiary)`.
2. Deploy contract `A` with a `call()` entry point that performs two sequential `call_v2` calls into `B` (first non-terminating, second terminating), using `ALLOW_REENTRY` only for other frames, not needed here since calls are sequential.
3. Fund `ALICE` and dispatch `Contracts::call(ALICE, A, ...)`.
4. Assertions:
   - `ContractInfoOf::<Test>::contains_key(&B)` is `false` after the call (terminated).
   - `pallet_balances::Holds::<Test>::get(&B)` (or `Currency::balance_on_hold(HoldReason::StorageDepositReserve, &B)`) is nonzero after the call, proving a stale hold was placed on a dead contract account.
   - `ALICE`'s free/reducible balance does not equal `pre-call balance - (net legitimate deposit)`, i.e. it's short by the stale `Charge` amount, demonstrating funds are stuck at `B`'s address with no reachable recovery path.
   - (Fuzz/invariant variant) For randomized sequences of `charge`/`terminate`/second-call-to-same-contract on `RawMeter<Test, ReservingExt, Nested>`, assert `sum(refund to origin) + sum(sweep to beneficiary) + sum(remaining on-hold at contract) == pre-termination on-hold balance`; the assertion fails whenever a post-termination `Charge` entry for the same contract is present in `self.charges`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** substrate/frame/contracts/src/storage/meter.rs (L325-344)
```rust
	pub fn absorb(
		&mut self,
		absorbed: RawMeter<T, E, Nested>,
		contract: &T::AccountId,
		info: Option<&mut ContractInfo<T>>,
	) {
		let own_deposit = absorbed.own_contribution.update_contract(info);
		self.total_deposit = self
			.total_deposit
			.saturating_add(&absorbed.total_deposit)
			.saturating_add(&own_deposit);
		self.charges.extend_from_slice(&absorbed.charges);
		if !own_deposit.is_zero() {
			self.charges.push(Charge {
				contract: contract.clone(),
				amount: own_deposit,
				state: absorbed.contract_state(),
			});
		}
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L395-409)
```rust
	pub fn try_into_deposit(self, origin: &Origin<T>) -> Result<DepositOf<T>, DispatchError> {
		// Only refund or charge deposit if the origin is not root.
		let origin = match origin {
			Origin::Root => return Ok(Deposit::Charge(Zero::zero())),
			Origin::Signed(o) => o,
		};
		for charge in self.charges.iter().filter(|c| matches!(c.amount, Deposit::Refund(_))) {
			E::charge(origin, &charge.contract, &charge.amount, &charge.state)?;
		}
		for charge in self.charges.iter().filter(|c| matches!(c.amount, Deposit::Charge(_))) {
			E::charge(origin, &charge.contract, &charge.amount, &charge.state)?;
		}
		Ok(self.total_deposit)
	}
}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L465-476)
```rust
	/// Call to tell the meter that the currently executing contract was terminated.
	///
	/// This will manipulate the meter so that all storage deposit accumulated in
	/// `contract_info` will be refunded to the `origin` of the meter. And the free
	/// (`reducible_balance`) will be sent to the `beneficiary`.
	pub fn terminate(&mut self, info: &ContractInfo<T>, beneficiary: T::AccountId) {
		debug_assert!(matches!(self.contract_state(), ContractState::Alive));
		self.own_contribution = Contribution::Terminated {
			deposit: Deposit::Refund(info.total_deposit()),
			beneficiary,
		};
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L540-607)
```rust
	fn charge(
		origin: &T::AccountId,
		contract: &T::AccountId,
		amount: &DepositOf<T>,
		state: &ContractState<T>,
	) -> Result<(), DispatchError> {
		match amount {
			Deposit::Charge(amount) | Deposit::Refund(amount) if amount.is_zero() => return Ok(()),
			Deposit::Charge(amount) => {
				// This could fail if the `origin` does not have enough liquidity. Ideally, though,
				// this should have been checked before with `check_limit`.
				T::Currency::transfer_and_hold(
					&HoldReason::StorageDepositReserve.into(),
					origin,
					contract,
					*amount,
					Precision::Exact,
					Preservation::Preserve,
					Fortitude::Polite,
				)?;

				Pallet::<T>::deposit_event(Event::StorageDepositTransferredAndHeld {
					from: origin.clone(),
					to: contract.clone(),
					amount: *amount,
				});
			},
			Deposit::Refund(amount) => {
				let transferred = T::Currency::transfer_on_hold(
					&HoldReason::StorageDepositReserve.into(),
					contract,
					origin,
					*amount,
					Precision::BestEffort,
					Restriction::Free,
					Fortitude::Polite,
				)?;

				Pallet::<T>::deposit_event(Event::StorageDepositTransferredAndReleased {
					from: contract.clone(),
					to: origin.clone(),
					amount: transferred,
				});

				if transferred < *amount {
					// This should never happen, if it does it means that there is a bug in the
					// runtime logic. In the rare case this happens we try to refund as much as we
					// can, thus the `Precision::BestEffort`.
					log::error!(
						target: LOG_TARGET,
						"Failed to repatriate full storage deposit {:?} from contract {:?} to origin {:?}. Transferred {:?}.",
						amount, contract, origin, transferred,
					);
				}
			},
		}
		if let ContractState::<T>::Terminated { beneficiary } = state {
			System::<T>::dec_consumers(&contract);
			// Whatever is left in the contract is sent to the termination beneficiary.
			T::Currency::transfer(
				&contract,
				&beneficiary,
				T::Currency::reducible_balance(&contract, Preservation::Expendable, Polite),
				Preservation::Expendable,
			)?;
		}
		Ok(())
	}
```

**File:** substrate/frame/contracts/src/exec.rs (L1363-1387)
```rust
	fn terminate(&mut self, beneficiary: &AccountIdOf<Self::T>) -> DispatchResult {
		if self.is_recursive() {
			return Err(Error::<T>::TerminatedWhileReentrant.into());
		}
		let frame = self.top_frame_mut();
		let info = frame.terminate();
		frame.nested_storage.terminate(&info, beneficiary.clone());

		info.queue_trie_for_deletion();
		ContractInfoOf::<T>::remove(&frame.account_id);
		Self::decrement_refcount(info.code_hash);

		for (code_hash, deposit) in info.delegate_dependencies() {
			Self::decrement_refcount(*code_hash);
			frame
				.nested_storage
				.charge_deposit(frame.account_id.clone(), StorageDeposit::Refund(*deposit));
		}

		Contracts::<T>::deposit_event(Event::Terminated {
			contract: frame.account_id.clone(),
			beneficiary: beneficiary.clone(),
		});
		Ok(())
	}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L385-429)
```rust
	pub fn execute_postponed_deposits(
		&mut self,
		origin: &Origin<T>,
		exec_config: &ExecConfig<T>,
	) -> Result<DepositOf<T>, DispatchError> {
		// Only refund or charge deposit if the origin is not root.
		let origin = match origin {
			Origin::Root => return Ok(Deposit::Charge(Zero::zero())),
			Origin::Signed(o) => o,
		};

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
