### Title
Proposer's Storage Deposit Permanently Lost on Update Execution — (File: `crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

---

### Summary

`propose_update` charges the proposer a storage-staking deposit sized to the contract code or config payload. When the update is later executed via `vote_update` → `do_update`, all stored entries are cleared and the storage is freed, but the deposit is **never returned to the proposer**. The `UpdateEntry` struct does not record the proposer's account ID, so there is no recipient to refund. The deposit is permanently absorbed into the contract's balance — the exact "funds returned to the wrong party" pattern from the reference report, applied to the update-proposal lifecycle.

---

### Finding Description

`propose_update` in `crates/contract/src/lib.rs` computes a required deposit:

```rust
let required = ProposedUpdates::required_deposit(&update);
``` [1](#0-0) 

Only the **excess** above `required` is refunded immediately to the proposer:

```rust
if let Some(diff) = attached.checked_sub(required)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(proposer).transfer(diff).detach();
}
``` [2](#0-1) 

The `required` portion stays in the contract. `required_deposit` is calculated as `env::storage_byte_cost() × bytes_used`, where `bytes_used` includes the full contract code length plus overhead for up to 128 participant votes:

```rust
fn bytes_used(update: &Update) -> u128 {
    let mut bytes_used = std::mem::size_of::<UpdateEntry>() as u128;
    bytes_used += 128 * std::mem::size_of::<AccountId>() as u128;
    match update {
        Update::Contract(code) => { bytes_used += code.len() as u128; }
        ...
    }
    bytes_used
}
``` [3](#0-2) 

When `vote_update` reaches threshold and calls `do_update`, all entries and votes are cleared — freeing the storage — but no deposit is returned:

```rust
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    self.entries.clear();
    self.vote_by_participant.clear();
    // ... deploy or config update, no refund
    Some(promise)
}
``` [4](#0-3) 

The `UpdateEntry` struct stores only the update payload and `bytes_used`; the proposer's `AccountId` is never persisted:

```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
``` [5](#0-4) 

There is therefore no path by which the deposit can ever be returned to the proposer.

---

### Impact Explanation

**Medium.** This breaks the production accounting invariant that storage-staking deposits are returned when the storage they cover is freed. For a typical contract upgrade (e.g., a 500 KB WASM binary), `bytes_used` ≈ 508 KB, and at NEAR's mainnet `storage_byte_cost` (~10 yoctoNEAR/byte) the required deposit is approximately **5 NEAR**. That amount is permanently transferred to the contract's general balance on every successful upgrade, with no mechanism for recovery. The proposer — a legitimate participant performing an expected governance action — suffers a direct, irreversible balance loss each time an update they proposed is executed.

---

### Likelihood Explanation

**High.** The only prerequisite is being a participant and calling `propose_update`, which is the normal, documented path for contract upgrades. Contract upgrades occur regularly in production (bug fixes, feature additions). Every such upgrade silently destroys the proposer's deposit.

---

### Recommendation

1. Add a `proposer: AccountId` field to `UpdateEntry` so the deposit recipient is recorded at proposal time.
2. In `do_update`, before clearing entries, iterate over all entries and transfer each entry's storage deposit back to its recorded proposer.
3. Alternatively, store `(proposer, deposit)` in a separate map keyed by `UpdateId` and drain it inside `do_update`.

---

### Proof of Concept

1. Participant Alice calls `propose_update` with a 500 KB contract binary, attaching exactly `required_deposit` (~5 NEAR).
2. The excess refund branch is skipped (diff = 0). The 5 NEAR stays in the contract.
3. Enough participants call `vote_update` to reach threshold.
4. `do_update` is called: `entries.clear()` and `vote_by_participant.clear()` free all storage. No `Promise::transfer` to Alice is scheduled.
5. Alice's 5 NEAR is permanently absorbed into the contract balance. Alice has no recourse. [6](#0-5) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L1298-1334)
```rust
    #[payable]
    #[handle_result]
    pub fn propose_update(
        &mut self,
        #[serializer(borsh)] args: ProposeUpdateArgs,
    ) -> Result<UpdateId, Error> {
        // Only voters can propose updates:
        let proposer = self.voter_or_panic();
        let update: Update = args.try_into()?;

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

        Ok(id)
    }
```

**File:** crates/contract/src/update.rs (L132-135)
```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
```

**File:** crates/contract/src/update.rs (L195-227)
```rust
    pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
        let entry = self.entries.remove(id)?;

        // Clear all entries as they might be no longer valid
        self.entries.clear();
        self.vote_by_participant.clear();

        let mut promise = Promise::new(env::current_account_id());
        match entry.update {
            Update::Contract(code) => {
                // deploy contract then do a `migrate` call to migrate state.
                promise = promise.deploy_contract(code).function_call(
                    method_names::MIGRATE,
                    Vec::new(),
                    NearToken::from_near(0),
                    gas,
                );
            }
            Update::Config(config) => {
                // If we vote for a new config, we should use
                // the value `contract_upgrade_deposit_tera_gas` from the config
                // as the new gas value
                let new_config_gas_value = Gas::from_tgas(config.contract_upgrade_deposit_tera_gas);
                promise = promise.function_call(
                    method_names::UPDATE_CONFIG,
                    serde_json::to_vec(&(&config,)).unwrap(),
                    NearToken::from_near(0),
                    new_config_gas_value,
                );
            }
        }
        Some(promise)
    }
```

**File:** crates/contract/src/update.rs (L278-295)
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
```
