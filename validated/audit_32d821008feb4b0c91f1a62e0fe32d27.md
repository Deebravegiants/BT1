### Title
Coalescing logic in `execute_postponed_deposits` misattributes deposits when a contract address is terminated and reused, corrupting `total_deposit` and dropping legitimate charges - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
The charge-coalescing loop in `RawMeter::execute_postponed_deposits` (`substrate/frame/revive/src/metering/storage.rs:396-429`) assumes each contract address produces at most one `Terminated` marker and treats every subsequent `Alive` charge for the same address, after a `Terminated` entry has been seen, as belonging to the terminated instance. If a contract address is reused within the same transaction (terminate then redeploy via `CREATE2` at the same address), the new instance's legitimate deposit charge is silently folded into the terminated bucket: it is subtracted from `self.total_deposit` and its `Charge`/`Refund` record is destroyed (state forced to `Terminated`, discarding the `amount`). This causes the per-account `E::charge` loop to never execute a hold/refund for that legitimate deposit, and `total_deposit` to be under/over-stated relative to the sum of legitimate deltas.

### Finding Description
`self.charges` accumulates one `Charge{contract, state}` entry per absorbed sub-call or termination event, pushed via `absorb` (`storage.rs:304-309`), `charge_deposit` (`storage.rs:481-485`), and `terminate` (`storage.rs:450-456`). Nothing prevents multiple entries for the *same address* spanning an `Alive` charge, a `Terminated` marker, and a further `Alive` charge, which is exactly what happens if a contract self-destructs and a new contract is deployed at the same address (CREATE2 address collision after the account was reaped) within one call stack/transaction.

In the coalescing step:
```rust
(ContractState::Alive { amount }, ContractState::Terminated) |
(ContractState::Terminated, ContractState::Alive { amount }) => {
    // undo all deposits made by a terminated contract
    self.total_deposit = self.total_deposit.saturating_sub(&amount);
    last.state = ContractState::Terminated;
},
```
this arm is order-symmetric: it does not distinguish "old Alive charge that predates termination and must be undone" from "new Alive charge belonging to a freshly redeployed contract that must be preserved". Whichever `Alive` amount appears adjacent to the `Terminated` marker after sorting gets subtracted from `total_deposit`, and the coalesced entry's `state` is forced back to `Terminated`, losing the amount entirely. A third occurrence for the same address (a further `Alive` charge, e.g. from the second contract's own storage writes) folds against this now-`Terminated` `last` entry via the same arm, subtracting it as well, and the address permanently reads as `Terminated` in `self.charges`.

Consequences:
- In the subsequent per-charge loops (`storage.rs:432-441`), only `ContractState::Alive` entries trigger `E::charge`; the coalesced-to-`Terminated` entry is skipped, so no hold/refund transfer happens for the new contract's legitimate deposit even though its `ContractInfo` (`storage_byte_deposit`/`storage_item_deposit`) was already updated during `Diff::update_contract` in `absorb`.
- `self.total_deposit`, which is returned to the caller as "the total amount of deposit that should change hands", is decremented by both the original (correctly voided) charge and the new contract's legitimate charge, so it no longer equals the sum of legitimate deposit deltas.
- The `debug_assert!(false, "We never emit two terminates for the same contract.")` only guards `Terminated, Terminated`; it does nothing to guard the `Terminated` followed by a further legitimate `Alive` charge for a redeployed contract, confirming the code's implicit (and here violated) assumption that an address is touched at most once after termination.

### Impact Explanation
The bug corrupts deposit accounting for a reused contract address: legitimate storage-deposit charges for the newly redeployed contract are dropped from the actual charge/refund execution (`E::charge` never runs for that address) while simultaneously being subtracted from the aggregate `total_deposit` returned by the meter. This desynchronizes on-chain `ContractInfo` bookkeeping (which reflects an increased deposit) from the actual `HoldReason::StorageDepositReserve` holds/transfers performed against the origin, and from the reported `total_deposit`. Depending on transfer direction and downstream consumers of the returned `total_deposit` (fee/deposit accounting reported to the extrinsic caller), this can result in the origin being charged less than the storage it actually consumes, or in a computed total that does not match the sum of legitimate deposit deltas — an accounting/backing violation of storage deposits, matching the scoped "miscomputed total_deposit via coalescing" impact, though its manifestation is an under/mis-charge combined with dropped enforcement rather than a directly inflated refund payout in the `E::charge` loop itself (since the folded entry is completely skipped, not converted into a larger `Refund`).

### Likelihood Explanation
Requires: (1) a contract self-destructing within a call stack, (2) the same address being reused by a fresh contract instantiation via `CREATE2` within the same transaction, and (3) the redeployed contract performing storage writes so a legitimate `Alive` charge is recorded for that address again — all achievable by an unprivileged contract deployer/caller crafting a single transaction that does terminate + redeploy + write, without needing any privileged access. The remaining uncertainty is whether `pallet_revive`'s account-reaping/`CREATE2` address-derivation path actually permits redeploying to an address freed by `terminate` within the *same* transaction (this depends on `exec.rs` termination/instantiation ordering that could not be fully re-verified here); if allowed, the bug is deterministically reachable and repeatable every time the sequence occurs.

### Recommendation
Do not coalesce `Alive` charges that occur *after* a `Terminated` marker for the same address as if they belonged to the terminated instance. Track termination coalescing per logical contract "incarnation" rather than per raw address — e.g., insert an explicit boundary/generation marker when a contract is terminated so that charges recorded for a subsequently redeployed contract at the same address are coalesced independently, never merged with or subtracted against the terminated incarnation's charges.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs`:
1. Build a `RawMeter<Root>`; simulate: `charge_deposit(X, Deposit::Charge(100))` (first instance), `terminate(X, refunded=100)`, then a second incarnation: `charge_deposit(X, Deposit::Charge(50))` (redeployed contract's legitimate charge).
2. Call `execute_postponed_deposits(&Origin::Signed(origin), ..)`.
3. Assert that the returned `total_deposit` equals the expected net legitimate delta (refund of the first 100 plus a genuine charge of 50 for the redeployed instance), and separately assert (via a mock `Ext::charge` recorder) that `E::charge` was invoked for address `X` with `Deposit::Charge(50)` for the redeployed instance — the current implementation fails both assertions because the 50 charge is dropped and `total_deposit` is under-reported by the folded amount.