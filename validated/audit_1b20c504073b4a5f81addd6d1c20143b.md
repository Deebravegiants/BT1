### Title
Coalescing logic in `execute_postponed_deposits` conflates a terminated contract with a same-address redeployed instance, skipping the real deposit charge while still crediting `total_deposit` as reclaimed - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
The charge-coalescing loop in `RawMeter::execute_postponed_deposits` groups all `Charge` entries purely by `contract: T::AccountId`, with no notion of contract *instance*/generation. Once a `Terminated` entry for an address is folded in, any later `Alive` charge for the *same address* is unconditionally treated as belonging to the dead instance and is "undone" (subtracted from `total_deposit`), even if it actually originates from a brand-new contract redeployed at that same address later in the same transaction.

### Finding Description
`execute_postponed_deposits` sorts `self.charges` by `contract` and merges consecutive entries for the same address [1](#0-0) . The merge arm

```
(ContractState::Alive { amount }, ContractState::Terminated) |
(ContractState::Terminated, ContractState::Alive { amount }) => {
    // undo all deposits made by a terminated contract
    self.total_deposit = self.total_deposit.saturating_sub(&amount);
    last.state = ContractState::Terminated;
}
``` [2](#0-1) 

is designed for the case where a single contract instance accumulates storage charges and then self-terminates within the same call (its accumulated `own_deposit` charge must be cancelled because `terminate()` already folds the full refund into `total_deposit` separately: `self.total_deposit = self.total_deposit.saturating_add(&Deposit::Refund(refunded))` [3](#0-2) ).

The `Charge` struct only carries `contract: T::AccountId` and a `ContractState` [4](#0-3)  — there is no per-instance discriminator (e.g. a nonce/generation tag). Consequently, once the coalesced entry for an address becomes `Terminated`, the loop's `last.contract == ch.contract` check has no way to distinguish "another charge from the *same dead* contract" from "a charge from a *newly redeployed* contract at the same address." Any subsequent `Alive` charge merged after that point hits the `(Terminated, Alive)` arm again and is likewise subtracted from `total_deposit` and turned into `Terminated`.

Critically, after coalescing, only `ContractState::Alive` entries are ever passed to `E::charge` in the refund and charge loops that follow [5](#0-4) ; a `Terminated` entry is never charged or refunded through `E::charge` at all. Meanwhile, the redeployed contract's `ContractInfo.storage_byte_deposit`/`storage_item_deposit` fields were already updated eagerly at frame-`absorb` time via `Contribution::update_contract` [6](#0-5) , independent of this later coalescing/charging step. This produces a desync: the new contract's on-chain `ContractInfo` bookkeeping records real deposit-backed storage, but the corresponding `E::charge` (the actual `hold`/reserve call against `origin`'s balance) for that new instance's charge is skipped because its `Charge` entry got merged into a `Terminated` state and is filtered out of both charge loops.

I was not able to fully verify within the available tool budget whether pallet-revive's `instantiate` path permits genuinely redeploying a *new* contract instance at the exact same address within the same transaction after a `terminate` (this requires deterministic/salt-based address derivation reused after destruction, analogous to CREATE2+SELFDESTRUCT patterns). This is the key reachability precondition for the exploit chain and remains unconfirmed from the code I was able to inspect (`substrate/frame/revive/src/exec.rs` address/redeploy logic was not fully reviewed before the tool budget was exhausted).

### Impact Explanation
If the redeploy-at-same-address-in-same-tx precondition holds, the net effect is an accounting desync (a missed charge against `origin`, not an inflated refund as literally worded in the question) — the new contract's storage is backed by `ContractInfo` deposit fields without the corresponding balance actually being held from `origin`. This would still constitute a storage-deposit accounting break (uncollateralized storage), but the specific mechanism described in the question — a refund paid out for storage never reclaimed — is not what the traced code produces; rather it produces a skipped charge for storage that was in fact created. The debug_assert at the `(Terminated, Terminated)` arm [7](#0-6)  shows the authors did anticipate multiple entries per address post-termination were not expected to recur in this particular shape, but the `(Terminated, Alive)` arm is not guarded the same way.

### Likelihood Explanation
Unconfirmed. The bug in the coalescing code itself is real and verifiable directly from `storage.rs`, but I could not confirm the precondition (attacker being able to redeploy a contract at the identical address within the same transaction after `terminate`) from the code available to me in this session.

### Recommendation
Not applicable pending confirmation of the redeploy precondition; if confirmed, the `Charge` struct should carry a per-instance identifier (e.g. incrementing generation/nonce per address within a transaction) so the coalescing loop in `execute_postponed_deposits` never merges charges belonging to different contract instances that happen to share an address.

### Proof of Concept
Not constructed — the exact reachable `instantiate`/address-derivation path in `substrate/frame/revive/src/exec.rs` needed to confirm same-address redeploy-in-same-tx was not verified before the tool budget was exhausted.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L203-207)
```rust
#[derive(DebugNoBound, Clone)]
struct Charge<T: Config> {
	contract: T::AccountId,
	state: ContractState<T>,
}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L295-309)
```rust
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

**File:** substrate/frame/revive/src/metering/storage.rs (L450-452)
```rust
	pub fn terminate(&mut self, contract: T::AccountId, refunded: BalanceOf<T>) {
		self.total_deposit = self.total_deposit.saturating_add(&Deposit::Refund(refunded));
		self.charges.push(Charge { contract, state: ContractState::Terminated });
```
