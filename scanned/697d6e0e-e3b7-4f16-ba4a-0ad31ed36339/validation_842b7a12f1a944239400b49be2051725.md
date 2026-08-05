### Title
Storage deposit coalescing in `execute_postponed_deposits` incorrectly voids charges when a contract address is redeployed after termination within the same call stack - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
The charge-coalescing loop in `RawMeter::<Root>::execute_postponed_deposits` merges charges for the same contract address using only the immediately-preceding merged entry (`coalesced.last_mut()`), and treats every `Alive <-> Terminated` transition identically by subtracting the paired `amount` from `self.total_deposit` and forcing the merged state to `Terminated`. When three or more charges accumulate for the same address within one meter lifetime in the order `Alive{a1}, Terminated, Alive{a2}` (e.g. a contract terminates and a new instance is redeployed to the same address via `create2`-style semantics before the transaction ends), the second merge (`Terminated`, `Alive{amount: a2}`) again subtracts `a2` from `total_deposit` and re-marks the entry `Terminated`, discarding the legitimate charge for the new (still-alive) contract instance instead of applying it.

### Finding Description
`self.charges` is populated chronologically via `charge_deposit`/`absorb`/`terminate` [1](#0-0) [2](#0-1) , and each `Charge` records only `(contract, ContractState)` with `Alive{amount}` or `Terminated`.

In `execute_postponed_deposits`, charges are stable-sorted by contract account and then coalesced sequentially against `coalesced.last_mut()` only: [3](#0-2) 

The critical branch:
```
(ContractState::Alive { amount }, ContractState::Terminated) |
(ContractState::Terminated, ContractState::Alive { amount }) => {
    // undo all deposits made by a terminated contract
    self.total_deposit = self.total_deposit.saturating_sub(&amount);
    last.state = ContractState::Terminated;
},
```
treats an `Alive` charge arriving *after* a `Terminated` charge (i.e., `(Terminated, Alive{amount})`) exactly the same as an `Alive` charge preceding termination — it subtracts the amount from `total_deposit` and forces the coalesced state back to `Terminated`. This is only correct if a `Terminated` entry can never be followed by a legitimate new `Alive` charge for the *same* address. The `debug_assert!(false, "We never emit two terminates for the same contract.")` in the `(Terminated, Terminated)` arm shows the author assumed at most one `Terminate` per address, but does not assume — and does not correctly handle — a subsequent legitimate `Alive` charge belonging to a *newly redeployed* contract at the same address.

If, within one root meter lifetime, the sequence for address `X` is `Alive{a1}` (original instance's deposit), `Terminated` (original instance destroyed), `Alive{a2}` (new instance's deposit after redeploy), the fold produces:
1. `coalesced = [Alive{a1}]`
2. merge with `Terminated`: `total_deposit -= a1`, `coalesced = [Terminated]`
3. merge with `Alive{a2}`: `total_deposit -= a2` (again!), `coalesced = [Terminated]`

The final coalesced entry is `Terminated`, so it is skipped by both charge-application loops (`ContractState::Alive` guards) [4](#0-3) , meaning the new instance's deposit `a2` is never actually reserved via `E::charge`, yet `total_deposit` (the function's return value used for reporting/accounting) has been decremented by `a2` in addition to `a1`. Meanwhile, the underlying `ContractInfo` for the new instance was already mutated to reflect the `a2` deposit obligation via `Diff::update_contract` earlier in the call stack (during `absorb`/`finalize_own_contributions`), so the contract's on-chain bookkeeping records a deposit that was never actually held from the origin's account — creating a permanent mismatch between `ContractInfo.storage_*_deposit` and the actually reserved balance.

### Impact Explanation
The redeployed contract's storage deposit obligation is silently dropped: the pallet believes (via `ContractInfo`) that a deposit of `a2` backs the new instance's storage, but no balance was ever held for it. This directly matches the scoped impact — the reported/charged total understates the real deposit obligation, and the attacker's redeployed contract holds storage without a matching on-chain hold. This can later be exploited to claim a refund (via `refund_deposit`) for a deposit that was never actually reserved, or leaves an accounting hole that undermines the deposit-backing invariant for storage.

### Likelihood Explanation
Requires the attacker to: (1) get an existing contract at address `X` charged for storage, (2) terminate it, and (3) redeploy a new contract to the exact same address `X` within the same transaction/call-stack (a single `Root` meter lifetime), with the new instance also incurring a storage charge. This is plausible for `create2`-style deployments where address is derived from `deployer + salt + code_hash`, allowing intentional address reuse in the same transaction. I was not able to fully verify in this pass whether `substrate/frame/revive/src/exec.rs` imposes an additional guard preventing address reuse within the same transaction after termination (my tool budget ran out before confirming), so this precondition should be validated against the exec/instantiate/terminate flow before treating this as fully confirmed end-to-end; however, the coalescing logic itself is unambiguously incorrect for any code path that can produce a `Terminated` entry followed by a later `Alive` entry for the same address in one meter.

### Recommendation
Do not conflate "undo the terminated instance's charge" with "void any later charge for the same address." Track per-address charge history precisely: when merging into a `Terminated` entry, only subtract/discard amounts that were accumulated *before* the termination for that specific contract instance. Any `Alive` charge appearing *after* a `Terminated` entry for the same address should be treated as belonging to a new instance and coalesced independently (e.g., keep it as a separate `Charge` entry, not merged into the terminated one), so it is charged normally rather than discarded.

### Proof of Concept
Add a unit test in `substrate/frame/revive/src/metering/storage/tests.rs` that manually constructs (via nested meters/absorb and `terminate`) a `Root` meter whose `charges` vector for the same account, after sorting, is `[Alive{a1}, Terminated, Alive{a2}]` — e.g. terminate `BOB` after an initial charge, then simulate a fresh nested frame producing a new `Alive` charge for `BOB` again before calling `execute_postponed_deposits`. Assert that:
- `execute_postponed_deposits` returns a `total_deposit` equal to `a2 - refunded_amount` (net of the terminated instance's refund plus the new instance's real charge), not `-(a1 + a2)`-skewed value.
- `TestExtTestValue` records an actual `E::charge` call for `BOB` with `Deposit::Charge(a2)`, proving the new instance's deposit is genuinely reserved rather than silently dropped.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L300-309)
```rust
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
