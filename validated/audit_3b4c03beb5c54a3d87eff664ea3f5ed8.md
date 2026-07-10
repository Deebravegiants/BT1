### Title
Deposits for Non-Winning `propose_update` Proposals Are Permanently Lost When `do_update` Clears All Entries - (File: `crates/contract/src/update.rs`)

---

### Summary

When `ProposedUpdates::do_update` executes a winning contract-upgrade or config-update proposal, it unconditionally clears **all** pending proposals and votes. Because `UpdateEntry` does not record the proposer's account ID or the deposit amount, and no refund path exists in `do_update`, every NEAR deposit paid by proposers of non-winning proposals is permanently locked in the contract with no mechanism to recover it.

---

### Finding Description

`propose_update` in `lib.rs` requires a storage-proportional deposit from each proposer:

```rust
// crates/contract/src/lib.rs:1308-1331
let attached = env::attached_deposit();
let required = ProposedUpdates::required_deposit(&update);
if attached < required { ... }
let id = self.proposed_updates.propose(update);
// Refund only the *excess* over required — the required amount stays in the contract
if let Some(diff) = attached.checked_sub(required) && diff > NearToken::from_yoctonear(0) {
    Promise::new(proposer).transfer(diff).detach();
}
```

The deposit is consumed by the contract. However, `UpdateEntry` — the struct stored per proposal — contains only the update payload and `bytes_used`; it does **not** record the proposer's `AccountId` or the deposit amount:

```rust
// crates/contract/src/update.rs:132-135
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
```

When a proposal reaches threshold votes, `vote_update` calls `do_update`, which removes the winning entry and then **clears all remaining entries and votes without any refund**:

```rust
// crates/contract/src/update.rs:195-200
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    // Clear all entries as they might be no longer valid
    self.entries.clear();
    self.vote_by_participant.clear();
    ...
}
```

There is no code path anywhere in the contract that refunds deposits for cleared non-winning proposals. The `UpdateEntry` struct carries no proposer identity, so even a future fix would have no data to refund against.

The deposit size is non-trivial: for a contract binary of ~1 MB, `bytes_used` includes the code length plus overhead for 128 assumed participant votes, yielding a required deposit on the order of **10+ NEAR** per proposal.

---

### Impact Explanation

Every participant who calls `propose_update` for a proposal that is not ultimately executed loses their full required deposit permanently. The funds are locked in the contract balance with no recovery mechanism. This directly breaks the balance/accounting invariant: deposits are collected but the contract provides no path to reclaim them when the associated state is cleared.

This matches the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

The scenario is a normal governance flow: multiple participants independently propose different upgrades (e.g., different contract binaries or config values). When one proposal reaches threshold and `do_update` fires, all competing proposals are wiped. This is explicitly tested and documented behavior. No adversarial action is required — the loss occurs automatically during routine governance. Any participant who proposes an update that does not win the vote loses their deposit.

---

### Recommendation

1. Add `proposer: AccountId` and `deposit: NearToken` fields to `UpdateEntry` so the refund target and amount are recoverable.
2. In `do_update`, iterate over all remaining entries before calling `self.entries.clear()` and schedule a `Promise::new(entry.proposer).transfer(entry.deposit)` for each.
3. Alternatively, track deposits in a separate `LookupMap<UpdateId, (AccountId, NearToken)>` and drain it in `do_update`.

---

### Proof of Concept

1. Participant A calls `propose_update` with a 500 KB contract binary. Required deposit ≈ 5 NEAR. Deposit is consumed.
2. Participant B calls `propose_update` with a different 500 KB binary. Required deposit ≈ 5 NEAR. Deposit is consumed.
3. Threshold participants vote for proposal A via `vote_update`.
4. `vote_update` calls `self.proposed_updates.do_update(&id_A, gas)`.
5. Inside `do_update`: proposal A's entry is removed and executed; `self.entries.clear()` wipes proposal B's entry; `self.vote_by_participant.clear()` wipes all votes.
6. Participant B's ≈ 5 NEAR deposit remains in the contract balance forever — `UpdateEntry` for B carried no `proposer` field, so no refund was issued and no refund can ever be issued. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/contract/src/update.rs (L132-135)
```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
```

**File:** crates/contract/src/update.rs (L195-200)
```rust
    pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
        let entry = self.entries.remove(id)?;

        // Clear all entries as they might be no longer valid
        self.entries.clear();
        self.vote_by_participant.clear();
```

**File:** crates/contract/src/update.rs (L278-299)
```rust
fn bytes_used(update: &Update) -> u128 {
    let mut bytes_used = std::mem::size_of::<UpdateEntry>() as u128;

    // Assume a high max of 128 participant votes per update entry.
    bytes_used += 128 * std::mem::size_of::<AccountId>() as u128;

    match update {
        Update::Contract(code) => {
            bytes_used += code.len() as u128;
        }
        Update::Config(config) => {
            let bytes = serde_json::to_vec(&config).unwrap();
            bytes_used += bytes.len() as u128;
        }
    }

    bytes_used
}

fn required_deposit(bytes_used: u128) -> NearToken {
    env::storage_byte_cost().saturating_mul(bytes_used)
}
```

**File:** crates/contract/src/lib.rs (L1308-1331)
```rust
        let attached = env::attached_deposit();
        let required = ProposedUpdates::required_deposit(&update);
        if attached < required {
            return Err(InvalidParameters::InsufficientDeposit {
                attached: attached.as_yoctonear(),
                required: required.as_yoctonear(),
            }
            .into());
        }

        let id = self.proposed_updates.propose(update);

        log!(
            "propose_update: signer={}, id={:?}",
            env::signer_account_id(),
            id,
        );

        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```
