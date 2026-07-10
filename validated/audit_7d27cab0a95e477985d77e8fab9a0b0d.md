### Title
Proposer's Storage Deposit Permanently Locked When `do_update` Clears All Pending Proposals — (File: `crates/contract/src/update.rs`)

---

### Summary

`propose_update` requires participants to attach a substantial storage deposit (proportional to the update payload size, up to ~15 NEAR for a full contract binary). When any update reaches threshold and `do_update` executes, it clears **all** pending proposals and votes — but the `UpdateEntry` struct stores neither the proposer's `AccountId` nor the deposit amount, making refunds structurally impossible. Every non-executed proposal's deposit is permanently locked in the contract with no recovery path.

---

### Finding Description

In `crates/contract/src/lib.rs`, `propose_update` computes a required deposit and retains exactly that amount:

```rust
let attached = env::attached_deposit();
let required = ProposedUpdates::required_deposit(&update);
// Only excess is refunded; the required portion is kept
if let Some(diff) = attached.checked_sub(required) && diff > NearToken::from_yoctonear(0) {
    Promise::new(proposer).transfer(diff).detach();
}
```

The required deposit is calculated in `crates/contract/src/update.rs` as:

```rust
fn bytes_used(update: &Update) -> u128 {
    let mut bytes_used = std::mem::size_of::<UpdateEntry>() as u128;
    bytes_used += 128 * std::mem::size_of::<AccountId>() as u128; // overestimates: assumes 128 votes
    match update {
        Update::Contract(code) => { bytes_used += code.len() as u128; }
        ...
    }
    bytes_used
}
fn required_deposit(bytes_used: u128) -> NearToken {
    env::storage_byte_cost().saturating_mul(bytes_used)
}
```

For a ~1.5 MB contract binary this yields ~15 NEAR; the devnet default is 8 NEAR (`deposit_near: u128 = 8`).

When threshold votes are reached and `do_update` fires:

```rust
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    // Clear all entries as they might be no longer valid
    self.entries.clear();
    self.vote_by_participant.clear();
    // ← no refund to any proposer, executed or not
    ...
}
```

The `UpdateEntry` struct contains no proposer identity or deposit record:

```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
    // ← no proposer: AccountId, no deposit: NearToken
}
```

Once `entries.clear()` runs, the storage is freed and the NEAR goes to the contract's balance — but there is no on-chain record of who paid what, so no refund can ever be issued. The contract has no `withdraw` method.

---

### Impact Explanation

**Medium.** This breaks the production accounting invariant that storage deposits must be returned when the storage they cover is freed. Every participant who proposes an update that is superseded by another loses their full deposit permanently. With the 8 NEAR devnet default and the overestimated `bytes_used` formula, a single governance cycle where N participants each propose a different update results in (N−1) × 8+ NEAR permanently locked in the contract. The contract's balance grows unboundedly with governance activity, and no participant can recover their funds.

---

### Likelihood Explanation

**Medium.** This occurs in every normal governance cycle where more than one participant proposes an update. The README explicitly documents that "all pending update proposals and votes are cleared" on execution. In a network with 7+ participants, it is routine for multiple proposals to coexist. No adversarial intent is required — the loss is a structural consequence of normal threshold-voting operation.

---

### Recommendation

1. Add `proposer: AccountId` and `deposit: NearToken` fields to `UpdateEntry`.
2. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue `Promise::new(entry.proposer).transfer(entry.deposit)` for each.
3. Also refund the executed proposal's deposit (the proposer receives the update execution as value, but the storage deposit should still be returned once the entry is removed).
4. Alternatively, store a `BTreeMap<UpdateId, (AccountId, NearToken)>` alongside `entries` so refund data survives the `entries.clear()` call.

---

### Proof of Concept

1. Participant A calls `propose_update` with a 1.5 MB contract binary, attaching ~15 NEAR.
   - `UpdateEntry { update: Contract([...]), bytes_used: ~1_500_000 }` is inserted; A's 15 NEAR stays in the contract.
2. Participant B calls `propose_update` with a config update, attaching ~0.1 NEAR.
3. Threshold participants call `vote_update` for B's proposal.
4. `do_update` executes B's update, then calls `self.entries.clear()`.
5. A's entry is erased. A's 15 NEAR is now in the contract's balance with no record of ownership.
6. A has no method to recover the deposit. The contract has no `withdraw` endpoint.
7. Repeat across governance cycles: each superseded proposal permanently inflates the contract's balance at the expense of honest participants. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/contract/src/update.rs (L132-135)
```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
```

**File:** crates/contract/src/update.rs (L195-201)
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
