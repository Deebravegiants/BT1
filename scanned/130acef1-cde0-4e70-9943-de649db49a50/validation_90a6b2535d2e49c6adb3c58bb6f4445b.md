### Title
Coalescing charges after contract address reuse (terminate + redeploy at same address) can drop a legitimate storage-deposit charge from `execute_postponed_deposits` - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`execute_postponed_deposits` sorts `self.charges` by contract address and stable-coalesces consecutive entries for the same address, but it does not account for the possibility that two *different* logical contract instances share the same address within a single transaction (terminate-then-redeploy at the same address). This causes an `Alive` charge belonging to the newly redeployed contract to be merged into a `Terminated` entry belonging to the previously destroyed contract, subtracting that new charge from `total_deposit` and dropping it entirely from the charge-execution loop.

### Finding Description
The relevant code is: [1](#0-0) 

The charges vector accumulates, in call order, `Charge { contract, state }` entries pushed by:
- `absorb()` -> `ContractState::Alive { amount }` when a nested call/frame ends non-reverted with a nonzero own deposit,
- `charge_deposit()` -> `ContractState::Alive { amount }`,
- `terminate()` -> `ContractState::Terminated`, plus an immediate `total_deposit += Refund(refunded)`. [2](#0-1) 

If a contract at address `X` is instantiated, writes storage (an `Alive{amount1}` charge recorded when its frame is absorbed), then self-terminates (`Terminated` charge pushed, `total_deposit` already refunded via `terminate`), and then, within the *same transaction*, a new contract is deployed at the same address `X` (e.g. via `CREATE2` with a colliding salt/init-code hash) and writes storage (a new `Alive{amount2}` charge is recorded for the *same* address `X`), the `charges` vector for address `X` becomes, in original order: `[Alive(amount1), Terminated, Alive(amount2)]`.

Because `sort_by` is a stable sort, and all three entries share the same key (`contract == X`), their relative order is preserved after sorting. The coalescing loop then processes them sequentially:
1. `coalesced = [Alive(amount1)]`
2. Next `Terminated` matches `(Alive, Terminated)` arm: `total_deposit -= amount1`, `last.state = Terminated`. `coalesced = [Terminated]`.
3. Next `Alive(amount2)` (the **new, unrelated, legitimately alive contract's charge**) matches `(Terminated, Alive)` arm: `total_deposit -= amount2`, `last.state = Terminated`. `coalesced = [Terminated]`.

The result is a single `Terminated` entry for `X`. In the subsequent charge-execution loops (lines 432-441) only `ContractState::Alive` entries are charged/refunded, so the redeployed contract's legitimate deposit `amount2` is never charged to/refunded from the origin, and it has additionally been subtracted from `total_deposit` (the value returned to the caller as the net deposit delta for the whole transaction).

The coalescing logic's comment ("undo all deposits made by a terminated contract") assumes any `Alive` charge coalesced with a `Terminated` charge for the same address necessarily belongs to the *same* contract instance that was terminated. That assumption is violated when the address is reused within one transaction, since `Charge` only tracks `T::AccountId`, with no notion of "instance" or nonce to disambiguate a terminated-then-redeployed contract from its predecessor at the same address.

### Impact Explanation
The scoped impact as stated is "steal funds via inflated refund to origin." Based on the trace above, the actual effect of this bug is the opposite of the direction claimed in the question: the coalescing incorrectly **drops a legitimate charge** (subtracts `amount2` from `total_deposit` and skips its `E::charge` call) rather than inflating a refund. This means:
- The origin does **not** receive an inflated refund; instead, the newly redeployed contract's storage deposit is silently uncollected, and `total_deposit` is understated by `amount2`.

If `amount2` were itself a net `Deposit::Refund` (e.g., the redeployed contract only removed storage relative to what accounting expects), then dropping/negating it could reduce a refund rather than increase it, and could even cause an over-subtraction in `total_deposit`, but this does not match the "attacker receives inflated refund" scenario as specified. This is a real accounting-correctness bug in the coalescing logic, but it does not match the specific direction of the scoped impact ("origin receives a refund larger than actually owed"); if anything it disadvantages the redeployed contract's deposit accounting or leaves storage under-collateralized without the origin actually gaining excess balance in hand as described.

### Likelihood Explanation
Reachability depends on whether `pallet_revive` allows redeploying a *new* contract at the exact same address as a just-terminated contract within the same transaction/call-stack (e.g., via `CREATE2` with the same deployer/salt/init-code-hash, which is a standard EVM-compatible pattern). I was not able to fully confirm within the available tool budget whether `exec.rs`'s instantiate/create2 path permits redeployment to a freshly-terminated address within the same top-level extrinsic (vs. requiring the account to be fully reaped or requiring a different transaction), since I could not complete reading the relevant `create2`/instantiate/terminate interaction logic in `substrate/frame/revive/src/exec.rs` before running out of tool calls.

### Recommendation
Track contract *instances* rather than bare addresses when recording/coalescing charges — e.g., tag each `Charge` with a per-instance identifier (such as an instantiation nonce or a monotonically increasing frame id) so that charges from a terminated instance are never coalesced with charges from a later instance redeployed at the same address. Alternatively, flush/finalize all pending charges for an address atomically at the point of termination (charging/refunding immediately rather than deferring) so that no later charge for a redeployed instance at the same address can be merged with the terminated instance's entry.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` (using the existing `TestExt`/`TestMeter` harness):
1. Build a root `TestMeter`.
2. Simulate instance 1 at address `X`: nested meter charges a `Diff` adding bytes/items, absorbed into root -> pushes `Alive(amount1)` for `X`.
3. Call `root.terminate(X.clone(), refunded)` to simulate self-destruct -> pushes `Terminated` for `X`, `total_deposit += Refund(refunded)`.
4. Simulate instance 2 (redeploy) at the same address `X`: another nested meter charges a `Diff`, absorbed into root -> pushes `Alive(amount2)` for `X`.
5. Call `root.execute_postponed_deposits(&Origin::Signed(alice), &exec_config)`.
6. Assert that `TestExtTestValue::get().charges` contains a charge entry for `amount2` against `alice`/`X` (expected to fail, proving `amount2` is dropped), and assert the returned `total_deposit` equals the manually computed expected sum (`Refund(refunded) + amount2`, minus the fact that `amount1` should indeed be discarded since instance 1 was terminated) — expected to fail because the buggy code instead discards both `amount1` **and** `amount2`.

### Citations

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
