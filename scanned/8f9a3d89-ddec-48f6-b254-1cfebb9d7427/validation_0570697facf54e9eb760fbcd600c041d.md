### Title
Storage deposit charges are silently erased when a contract terminates and a new contract is redeployed at the same address within the same transaction - (File: `substrate/frame/revive/src/metering/storage.rs`)

### Summary
`RawMeter::execute_postponed_deposits` coalesces per-contract `Charge` entries by account address before charging the origin, but the coalescing logic in [1](#0-0)  assumes that once a `Terminated` marker is seen for an address, every other charge recorded against that same address in the transaction belongs to the terminated incarnation and can be subtracted out of `total_deposit`. This assumption breaks when a contract self-destructs and a *new* contract is legitimately re-instantiated at the same address later in the same transaction (e.g. via `CREATE2` with the same salt/code), because the new incarnation's real storage charge gets netted against the old incarnation's termination and is never charged.

### Finding Description
`Stack::do_terminate` removes `AccountInfoOf` for the contract synchronously (`AccountInfoOf::<T>::remove(contract_address)` at [2](#0-1) ) and calls `transaction_meter.terminate(contract_account.clone(), refund)` at [3](#0-2) , which pushes a `Charge { contract, state: ContractState::Terminated }` directly onto the root meter's `charges` vector via [4](#0-3) . Because `AccountInfoOf` is cleared immediately (not deferred), the address is free for reuse within the same transaction, e.g. by a subsequent `CREATE2` instantiation with the same salt and code hash (nonce-independent per the collision behaviour documented in `prdoc/pr_12645.prdoc`). The existing reentrancy guard added for `DuplicateContract` only rejects collisions with an address that is *still under construction* on the call stack (see [5](#0-4) ); it does not prevent a *sequential* redeploy at a freed address after full termination.

When the redeployed contract subsequently accrues its own storage charge, `RawMeter::absorb` appends a new `Charge { contract, state: Alive { amount } }` entry for the same address at [6](#0-5) . The resulting `charges` vector for that address, in chronological order, is `[Alive{C1}, Terminated, Alive{C2}]`. `execute_postponed_deposits` sorts by contract with a stable sort (preserving this relative order) and then coalesces consecutive entries for the same address: `(Alive, Terminated)` and `(Terminated, Alive)` are both handled by the same branch which unconditionally does `total_deposit = total_deposit.saturating_sub(&amount); last.state = Terminated;` ( [7](#0-6) ). Applying this branch twice in sequence subtracts **both** `C1` and `C2` from `total_deposit`, and the final coalesced state for the address remains `Terminated`, so the charge/refund loops at [8](#0-7)  never charge anything for that address. The genuine storage charge `C2` incurred by the redeployed contract is thus erased and never collected from the origin — `total_deposit` (the value returned and used for accounting) is underestimated.

The design comment `debug_assert!(false, "We never emit two terminates for the same contract.")` at [9](#0-8)  shows the code only anticipated a single `Alive -> Terminated` transition per address per transaction, not `Alive -> Terminated -> Alive` from a distinct, later, redeployed incarnation sharing the same address.

### Impact Explanation
An unprivileged, signed caller can cause the runtime to under-charge the storage deposit for legitimate storage usage of a redeployed contract, effectively obtaining "free" storage rent that is never collected from the origin's balance. This corrupts the storage-deposit economic invariant (deposit collected must equal net cost of all storage changes in the transaction) without requiring any privileged access — only a normal contract-calling extrinsic.

### Likelihood Explanation
Requires: (1) a contract that charges storage, (2) the same address terminated later in the same transaction (via `SELFDESTRUCT`/system precompile `terminate`, which frees `AccountInfoOf` synchronously), and (3) a subsequent instantiation at the identical address within the same transaction (feasible via `CREATE2` with the same salt/code hash, which is nonce-independent and therefore deterministic) that itself performs storage writes. All of this is achievable by ordinary contract code the attacker deploys and calls; no admin, governance, or node privileges are needed. The main uncertainty is whether any additional check (e.g., code-hash refcount, nonce increment, or child-trie id collision protection) blocks the redeploy step in practice — this could not be fully confirmed from the available code and would need to be validated with an integration test.

### Recommendation
In `execute_postponed_deposits`, do not merge charges across a `Terminated` boundary for the same address as if they were the same lifetime. Track charges per-(address, incarnation) rather than per-address only, or reset/flush pending charges for an address immediately at the point of `terminate()` instead of deferring coalescing to the end of the transaction, so any `Alive` charge that logically follows a `Terminated` entry for the same address is recognized as belonging to a new incarnation and charged independently rather than netted out.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` style, using the existing `TestExt`/`TestMeter` harness:
1. Build a `TestMeter` (`Root` state).
2. Simulate: absorb a nested meter for contract `X` with an `Alive` charge of amount `C1` (via `charge_deposit`/`absorb`).
3. Call `meter.terminate(X.clone(), refunded)` to push the `Terminated` marker.
4. Absorb another nested meter for the *same* address `X` with an `Alive` charge of amount `C2`.
5. Call `execute_postponed_deposits` and assert:
   - The returned `total_deposit` equals a naive independent sum `refunded - C1 + C2` (net of the true refund and both real charges), not `total_deposit` with both `C1` and `C2` erroneously subtracted.
   - `TestExtTestValue`'s recorded charges include a charge of `C2` to `X`, which the current code fails to produce because the coalesced state collapses to `Terminated`.

Differential fuzz/invariant test idea: generate randomized sequences of `charge`/`terminate`/`charge` events at a fixed address and compare `execute_postponed_deposits()`'s `total_deposit` against a naive re-simulation that tracks each incarnation separately, asserting they are always equal.

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

**File:** substrate/frame/revive/src/metering/storage.rs (L432-441)
```rust
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

**File:** substrate/frame/revive/src/exec.rs (L1841-1841)
```rust
			AccountInfoOf::<T>::remove(contract_address);
```

**File:** substrate/frame/revive/src/exec.rs (L1846-1846)
```rust
			transaction_meter.terminate(contract_account.clone(), refund);
```

**File:** substrate/frame/revive/src/exec/tests.rs (L1270-1290)
```rust
#[test]
fn reentrant_instantiate_at_same_address_is_rejected() {
	// EIP-684: while `B1` constructs at address `X`, its constructor re-enters the deployer to
	// instantiate the same code+salt. That resolves to `X` again and must be rejected rather
	// than run a second constructor for one account.
	let salt = [42u8; 32];

	let constructor_ch = MockLoader::insert(Constructor, |ctx, _| {
		// Re-enter the deployer (BOB) while we are still being constructed.
		ctx.ext
			.call(
				&CallResources::NoLimits,
				&BOB_ADDR,
				U256::zero(),
				vec![],
				ReentrancyProtection::AllowReentry,
				false,
			)
			.unwrap();
		exec_success()
	});
```
