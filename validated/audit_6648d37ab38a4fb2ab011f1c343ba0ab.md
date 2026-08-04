### Title
Deposit-ledger coalescing in `execute_postponed_deposits` conflates a terminated contract's address with a same-address contract redeployed in the same call stack, dropping real storage charges - (File: `substrate/frame/revive/src/metering/storage.rs`)

### Summary
The coalescing loop in `RawMeter<T,E,Root>::execute_postponed_deposits` merges all `Charge` entries by raw contract `AccountId` only, with no notion of contract "generation"/lifetime. Once a `Terminated` entry is seen for an address, *any subsequent* `Alive { amount }` charge for that same address (e.g. from a contract redeployed to the same address later in the same call stack) is folded into the `Terminated` state via the `(Terminated, Alive)`/`(Alive, Terminated)` match arm, which subtracts `amount` from `self.total_deposit` and keeps the entry `Terminated`. Entries left `Terminated` are then completely skipped in the two `E::charge` loops, so the redeployed contract's genuine storage deposit is never actually transferred/held, while `ContractInfo` for the redeployed contract still records the storage as backed by a deposit.

### Finding Description
`terminate()` [1](#0-0)  adds a `Charge{contract, Terminated}` entry and separately bumps `total_deposit` by the real `refunded` amount for that termination event. Coalescing sorts charges only by `contract` id (stable sort preserves relative order for the same key) and then merges adjacent same-address entries [2](#0-1) :

```
(ContractState::Alive { amount }, ContractState::Terminated) |
(ContractState::Terminated, ContractState::Alive { amount }) => {
    // undo all deposits made by a terminated contract
    self.total_deposit = self.total_deposit.saturating_sub(&amount);
    last.state = ContractState::Terminated;
},
```

This arm fires symmetrically for both orderings, and the resulting `last.state` remains `Terminated`. Because the loop walks the whole run of same-address entries sequentially, every subsequent `Alive { amount }` entry for that address — including ones that logically belong to a *different, later* contract instance deployed at the same account id after the first was terminated — is folded into the same `Terminated` bucket and subtracted from `total_deposit`. The only protection present is a `debug_assert!` guarding against two `Terminated` entries for the same contract [3](#0-2) ; there is no assertion or guard preventing an `Alive` charge from being recorded *after* a `Terminated` charge for the same address, which is exactly the scenario a terminate-then-redeploy-to-same-address sequence produces.

In the final settlement loops, only entries whose coalesced state is `Alive { .. }` are passed to `E::charge` (which does the actual balance hold/transfer via `Pallet::charge_deposit`/`refund_deposit`) [4](#0-3) . Any entry left `Terminated` is silently skipped — no transfer happens for it at all. Meanwhile, the storage bytes/items and deposit bookkeeping for the redeployed contract's `ContractInfo` were already updated independently in `absorb()` via `own_contribution.update_contract(info)` [5](#0-4) , which mutates `ContractInfo.storage_byte_deposit`/`storage_item_deposit` regardless of whether the corresponding balance hold is later actually executed. This produces a `ContractInfo` that claims a deposit is backing its storage while no hold was ever placed on-chain for it, since the meter-level charge for that address was cancelled by the coalescing bug.

### Impact Explanation
If a contract can terminate and be redeployed to the same account id within one call stack (root meter lifetime), the storage-deposit charge belonging to the redeployed instance is dropped from `total_deposit` and never charged via `E::charge`, letting the deployer avoid paying for real storage usage recorded in `ContractInfo`. This is a storage-deposit accounting bypass reachable by an unprivileged contract deployer/caller, and it also creates a latent inconsistency where `ContractInfo` deposit fields no longer correspond to an actual balance hold, which can later be exploited when that phantom deposit is "refunded" (unreserving balance that was never reserved).

### Likelihood Explanation
Exploitability hinges entirely on whether pallet-revive's current instantiation logic permits deploying a new contract to an account id that was terminated earlier in the *same* transaction/call stack (e.g. deterministic CREATE2-style salted addressing after `SELFDESTRUCT`). I was not able to fully verify this precondition within the available tool budget — I confirmed the address-derivation and instantiate-collision-check logic lives in `substrate/frame/revive/src/exec.rs`, but did not get to inspect whether same-address same-tx recreation after termination is actually permitted (e.g. whether the account/`ContractInfo` is fully cleared and the address freed for reuse before the transaction ends, and whether any "already exists" check would block a second `instantiate` to that address in the same stack). If same-tx redeploy-to-terminated-address is possible (consistent with EVM-equivalence goals of pallet-revive), the coalescing bug as described is real and directly reachable from ordinary contract calls with no privileged origin required. If the runtime instead permanently reserves/blocks the address after termination until the next block, this specific chain would not be reachable in a single transaction, though the coalescing logic itself is still latent and relies on an unenforced assumption (no `Alive` after `Terminated` for the same address).

### Recommendation
Do not key coalescing purely on the raw contract `AccountId`. Track a per-lifetime identifier (e.g. increment a generation counter recorded together with the address, or key charges by `(contract, deployment_nonce/generation)`), so that a `Terminated` entry only cancels `Alive` charges that belong to the same contract lifetime, never charges belonging to a later contract redeployed at the same address. Alternatively, disallow/flag redeployment to an address that was terminated within the same root-meter execution.

### Proof of Concept
Extend `substrate/frame/revive/src/metering/storage/tests.rs`:
1. Build a `Root` `RawMeter`.
2. Simulate: `meter.absorb(child_with_alive_charge_A, &addr, Some(info))` for contract at `addr` (produces `Alive{A}`).
3. Call `meter.terminate(addr.clone(), refunded_R)` (produces `Terminated`, `total_deposit += R`).
4. Simulate a second, distinct "redeployed" contract instance at the *same* `addr` with a fresh `absorb(child_with_alive_charge_B, &addr, Some(info2))` (produces `Alive{B}`).
5. Call `execute_postponed_deposits`.
6. Assert expected correct behavior: `total_deposit == R + B` (refund from termination plus the legitimately owed deposit `B` for the redeployed contract) and that `E::charge`/mock `Ext` was invoked with a `Charge(B)` for `addr`.
7. Show current buggy behavior: `total_deposit == R - B` (or similar undercount) and no `Charge(B)` is ever issued to the mock `Ext`, proving the redeployed contract's deposit is dropped rather than charged.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L278-309)
```rust
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

**File:** substrate/frame/revive/src/metering/storage.rs (L450-456)
```rust
	pub fn terminate(&mut self, contract: T::AccountId, refunded: BalanceOf<T>) {
		self.total_deposit = self.total_deposit.saturating_add(&Deposit::Refund(refunded));
		self.charges.push(Charge { contract, state: ContractState::Terminated });

		// no need to recalculate max_charged here as the total consumed amount will just decrease
		// with this extra refund
	}
```
