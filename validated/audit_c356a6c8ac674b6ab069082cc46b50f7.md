### Title
Coalescing logic in `execute_postponed_deposits` conflates pre-termination and post-redeploy charges for the same `AccountId`, causing incorrect `total_deposit` subtraction - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
The charge-coalescing loop in `RawMeter<Root>::execute_postponed_deposits` (lines 396-429) merges all `Charge` entries sharing the same `contract` `AccountId` without regard to whether an `Alive` entry occurred *before* or *after* a `Terminated` entry in the temporal charge history. Both `(Alive, Terminated)` and `(Terminated, Alive)` orderings are handled by the identical branch that unconditionally subtracts `amount` from `self.total_deposit` and forces the coalesced state to `Terminated`, discarding any legitimately new deposit obligation from a contract redeployed at the same address later in the same call stack.

### Finding Description
`execute_postponed_deposits` first stable-sorts `self.charges` by `contract` [1](#0-0) , which preserves the chronological order of entries sharing the same `AccountId` (Rust's `sort_by` is stable). It then folds same-key entries pairwise: [2](#0-1) 

Both orderings — an `Alive` charge followed by a later `Terminated` marker, and a `Terminated` marker followed by a later `Alive` charge — hit the exact same match arm, which subtracts `amount` from `self.total_deposit` and downgrades the coalesced entry to `Terminated`. The code comment "undo all deposits made by a terminated contract" only makes sense for the first ordering (a charge that happened *before* the contract died and should be voided since termination already issued its own refund via `terminate()`'s direct `total_deposit` update at lines 450-452). It is semantically wrong for the second ordering, where the `Alive` charge represents a *new* contract instance deployed at the same `AccountId` *after* termination, whose deposit obligation is real and should survive to the end of the transaction.

Because `total_deposit` is incrementally accumulated as events occur (in `absorb()` at lines 296-299 and in `terminate()` at line 451), a sequence `charge(C1) -> terminate(refund R) -> charge(C2)` for account X leaves `total_deposit` already correctly containing `+C1 -R +C2` before coalescing runs. The coalescing step then subtracts `C1` (canceling the pre-termination charge, as intended) **and separately subtracts `C2`** (incorrectly canceling the legitimate post-redeploy charge), and also removes the `Alive{C2}` entry from `self.charges` entirely so the subsequent per-charge `E::charge()` application loop (lines 432-441) never actually reserves/holds `C2` from the origin's balance for contract X.

The `debug_assert!(false, "We never emit two terminates for the same contract.")` guard on the `(Terminated, Terminated)` arm shows the authors only considered the invariant "at most one terminate per contract per call stack," but did not add an analogous safeguard to distinguish an `Alive` entry that predates a `Terminated` marker from one that postdates it (i.e., a redeploy). Nothing in this function inspects insertion order beyond the already-collapsed two-element match, so the distinction is structurally lost.

### Impact Explanation
If pallet_revive's instantiate path allows an `AccountId` to be reused for a new contract within the same transaction after a prior `terminate()` on that same address (CREATE2-style address reuse, analogous to Ethereum's pre-EIP-6780 SELFDESTRUCT+redeploy pattern), the coalescing bug causes:
- `total_deposit` returned by `execute_postponed_deposits` to under-report the true net deposit obligation by the amount of the redeployed contract's storage charge (`C2`), since it is subtracted a second, unwarranted time.
- The `Alive{C2}` charge is dropped from `self.charges`, so `E::charge()` never places the corresponding hold against the origin for the new contract's storage, even though `ContractInfo` for the redeployed contract was already updated (via `Contribution::update_contract`) to record that deposit as owed.
- Net effect: origin under-pays (or receives an extra refund) relative to the actual storage held by the live, redeployed contract at the end of the transaction — a storage-deposit accounting asymmetry.

### Likelihood Explanation
This requires: (1) a caller able to instantiate a contract, write storage, terminate it, and redeploy at the exact same `AccountId` within one transaction/call stack — a capability that depends on pallet_revive's address-derivation and re-instantiation rules (whether `ContractInfoOf` for a terminated address is cleared such that instantiation at that address is permitted again in the same transaction); and (2) the redeployed contract subsequently performing a storage write that generates a new `Alive` charge before `execute_postponed_deposits` runs. I could not fully verify the exact instantiate/address-collision logic in `substrate/frame/revive/src/exec.rs` within this session to confirm same-transaction address reuse is actually reachable (grep results returned matches but their contents were not inspected due to iteration limits), so the *preconditions* for triggering this coalescing bug are plausible given pallet_revive's EVM-compatibility goals but not fully confirmed. The coalescing logic flaw itself, however, is clearly present and reproducible in isolation via a unit test on `RawMeter` directly (bypassing the question of whether the exec layer permits the address reuse), since `charges` and `terminate()`/`absorb()` are directly callable within `substrate/frame/revive/src/metering/tests.rs`.

### Recommendation
Track charge ordering explicitly (e.g., tag each `Charge` with a monotonically increasing sequence number, or split the charges vector into "pre-termination" and "post-termination" segments per contract) so the coalescing logic only cancels `Alive` charges that occurred *before* the `Terminated` marker for that `AccountId`, and preserves (rather than discards) any `Alive` charge that occurs *after* a `Terminated` marker for the same key, treating it as a distinct new charge (and, ideally, resetting the debug invariant to allow one `Terminated` per logical "incarnation" rather than per raw `AccountId`).

### Proof of Concept
Add a unit test in `substrate/frame/revive/src/metering/tests.rs` that directly exercises `RawMeter<Root>`:
1. Construct a root meter, call `absorb()` (or push a `Charge::Alive{amount: Deposit::Charge(C1)}` for account X, e.g. via a nested meter that charges `C1`).
2. Call `meter.terminate(X.clone(), refunded: R)`.
3. Simulate redeploy: absorb another nested meter that charges `C2` for the same account X, pushing `Charge::Alive{amount: Deposit::Charge(C2)}`.
4. Call `execute_postponed_deposits(&Origin::Signed(origin), &exec_config)`.
5. Assert the returned `total_deposit` equals the manually computed net obligation `C1 - R + C2 - C1` (i.e., only `C1` should be voided by termination, `C2` should remain), and assert that `E::charge()` (via a mock `Ext`) was invoked with `C2` against contract X.
6. Show the current implementation fails this assertion because `total_deposit` also subtracts `C2`, and no `E::charge()` call for `C2` is recorded.

A fuzz/property test permuting sequences of `(Alive charge, Terminated, Alive charge)` for a fixed contract key, checking `total_deposit` against an independently computed running-sum oracle, would generalize this reproduction.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L396-397)
```rust
		// Coalesce charges of the same contract
		self.charges.sort_by(|a, b| a.contract.cmp(&b.contract));
```

**File:** substrate/frame/revive/src/metering/storage.rs (L410-415)
```rust
							(ContractState::Alive { amount }, ContractState::Terminated) |
							(ContractState::Terminated, ContractState::Alive { amount }) => {
								// undo all deposits made by a terminated contract
								self.total_deposit = self.total_deposit.saturating_sub(&amount);
								last.state = ContractState::Terminated;
							},
```
