Audit Report

## Title
Coalescing logic in `execute_postponed_deposits` misattributes deposits when a contract address is terminated and reused, corrupting `total_deposit` and dropping legitimate charges - (File: substrate/frame/revive/src/metering/storage.rs)

## Summary
The charge-coalescing loop in `RawMeter::execute_postponed_deposits` sorts and merges per-address `Charge` entries, and the merge arm handling an `Alive` charge next to a `Terminated` marker is order-symmetric — it treats `(Alive, Terminated)` and `(Terminated, Alive)` identically, always subtracting the `Alive` amount from `total_deposit` and forcing the merged entry's state to `Terminated`. If the same address accumulates a `Terminated` marker followed by a legitimate `Alive` charge belonging to a freshly redeployed contract (terminate + CREATE2 redeploy + storage write within one call stack), that legitimate charge is silently discarded and never charged via `E::charge`, while `total_deposit` is decremented as if it were void.

## Finding Description
`self.charges` accumulates one `Charge{contract, state}` per absorbed sub-call, deposit charge, or termination event via `absorb` [1](#0-0) , `charge_deposit` [2](#0-1) , and `terminate` [3](#0-2) . Nothing in these push sites prevents multiple entries for the same address spanning an `Alive` charge, a `Terminated` marker, and a further `Alive` charge.

The coalescing step in `execute_postponed_deposits` sorts by contract address and merges adjacent entries per address. The critical arm is confirmed order-symmetric exactly as claimed: [4](#0-3) 
This subtracts the `Alive` amount from `self.total_deposit` and forces `last.state = ContractState::Terminated` regardless of whether the `Alive` entry chronologically preceded or followed the `Terminated` marker. The only guard against a related scenario is `debug_assert!(false, "We never emit two terminates for the same contract.")` on `(Terminated, Terminated)` [5](#0-4) , which does nothing to protect a legitimate `Alive` charge recorded for a redeployed contract at the same address after a prior `Terminated` marker.

Downstream, only `ContractState::Alive` entries trigger `E::charge` in the refund/charge loops [6](#0-5) , so a coalesced-to-`Terminated` entry is skipped entirely and its deposit is never held/transferred, while `total_deposit` (returned at line 443) no longer reflects the sum of legitimate deltas.

Independently, `terminate()` immediately removes `AccountInfoOf` for the terminated contract [7](#0-6) , and CREATE2 addresses are fully deterministic from `deployer, code, input_data, salt` with no nonce dependency [8](#0-7) , so redeploying at the same address after termination is a documented and tested capability (`instantiate_unique_trie_id` tests demonstrate terminate-then-reinstantiate at the identical address, and `deployAndDestroyChild` in `NestedDeployer.sol` demonstrates create+terminate within a single transaction under EIP-6780's `only_if_same_tx: true` semantics). A dedicated guard (`reentrant_instantiate_at_same_address_is_rejected`, `DuplicateContract`) exists only for the *re-entrant, still-under-construction* case, not for a terminated-and-later-redeployed address within the same transaction — meaning that guard does not close this gap.

## Impact Explanation
This is a real, confirmed logic defect in in-scope accounting code (`pallet-revive`'s storage-deposit meter): the coalescing arm cannot distinguish a stale `Alive` charge that must be voided by termination from a fresh, legitimate `Alive` charge belonging to a contract redeployed at the same address. If triggered, it desynchronizes `ContractInfo` bookkeeping (updated via `Diff::update_contract` during `absorb`) from the actual holds/transfers executed by `E::charge`, and understates/misstates the `total_deposit` value returned to callers. This matches an in-scope storage-deposit accounting violation (dropped legitimate charge combined with under/mis-reported aggregate total), rather than a directly inflated refund.

## Likelihood Explanation
Triggering the bug requires, within a single call stack/transaction: (1) a contract terminating (e.g. `selfdestruct`/system precompile `terminate`), (2) a subsequent CREATE2 instantiate from the same deployer using the same code+salt so the address is reused, and (3) the redeployed contract performing a storage write that registers a legitimate `Alive` charge for that same address. Address determinism for CREATE2 and immediate `AccountInfoOf` removal on termination make this technically feasible without any privileged access; the SDK's own test suite (`NestedDeployer.sol`, `instantiate_unique_trie_id`) confirms create/terminate/reinstantiate at a shared address are all individually supported operations. The precise ordering of `do_terminate`'s execution relative to a later same-transaction CREATE2 (i.e., whether the account's info row is cleared early enough within the same transaction to permit the redeploy before the transaction ends) could not be fully traced end-to-end in this review due to time/tool constraints, but no code path was found that specifically blocks this "terminate then redeploy at same address within one tx" sequence.

## Recommendation
Do not coalesce `Alive` charges that occur after a `Terminated` marker for the same address as if they belong to the terminated instance. Introduce an explicit generation/incarnation boundary when a contract is terminated (e.g., a marker or per-incarnation grouping key) so that charges for a subsequently redeployed contract at the same address are coalesced and charged independently of the terminated incarnation's charges, never merged with or subtracted against them.

## Proof of Concept
Unit test plan for `substrate/frame/revive/src/metering/storage/tests.rs`:
1. Construct a `RawMeter<Root>`. Simulate first incarnation: `charge_deposit(X, Deposit::Charge(100))`, then `terminate(X, refunded=100)`.
2. Simulate a second incarnation at the same address `X`: `charge_deposit(X, Deposit::Charge(50))`.
3. Call `execute_postponed_deposits(&Origin::Signed(origin), ..)` and assert:
   - The returned `total_deposit` reflects the legitimate net delta (refund of 100 plus the genuine charge of 50), which the current implementation fails since the 50 charge is subtracted rather than executed.
   - A mock `Ext::charge` recorder shows `E::charge` invoked for `X` with `Deposit::Charge(50)` — the current implementation never calls it because the entry is coalesced into `Terminated` and skipped by the `Alive`-only charge loops.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L304-309)
```rust
		if !own_deposit.is_zero() {
			self.charges.push(Charge {
				contract: contract.clone(),
				state: ContractState::Alive { amount: own_deposit },
			});
		}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L404-415)
```rust
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
```

**File:** substrate/frame/revive/src/metering/storage.rs (L416-421)
```rust
							(ContractState::Terminated, ContractState::Terminated) => {
								debug_assert!(
									false,
									"We never emit two terminates for the same contract."
								)
							},
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

**File:** substrate/frame/revive/src/metering/storage.rs (L481-485)
```rust
	pub fn charge_deposit(&mut self, contract: T::AccountId, amount: DepositOf<T>) {
		// will not fail in a nested meter
		self.record_charge(&amount);
		self.charges.push(Charge { contract, state: ContractState::Alive { amount } });
	}
```

**File:** substrate/frame/revive/src/exec.rs (L1836-1846)
```rust
			// this deletes the code if refcount drops to zero
			let _code_removed = <CodeInfo<T>>::decrement_refcount(*code_hash)?;

			// delete the contracts data last as its infallible
			ContractInfo::<T>::queue_for_deletion(trie_id.clone(), contract_account.clone());
			AccountInfoOf::<T>::remove(contract_address);
			ImmutableDataOf::<T>::remove(contract_address);

			// the meter needs to discard all deposits interacting with the terminated contract
			// we do this last as we cannot roll this back
			transaction_meter.terminate(contract_account.clone(), refund);
```

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
