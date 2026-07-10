### Title
Proposer's Storage Deposit Permanently Stuck in Contract After `propose_update` Execution — (`crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

---

### Summary

When a participant calls `propose_update`, they must attach a NEAR deposit to cover storage costs for the update entry (including the full contract WASM bytes). When any update reaches threshold and `do_update` is called, it clears **all** pending entries — freeing the storage and returning the storage cost to the contract's balance — but never refunds the original proposers. There is no sweep or withdraw mechanism. All proposers' deposits are permanently stuck in the contract.

---

### Finding Description

In `propose_update`, the caller must attach a deposit calculated by `ProposedUpdates::required_deposit(&update)`: [1](#0-0) 

The required deposit is computed from `bytes_used`, which includes the full contract code length: [2](#0-1) 

Excess above the required deposit is refunded to the proposer: [3](#0-2) 

However, the `UpdateEntry` struct stores only `update` and `bytes_used` — **not** the proposer's account ID or the deposit amount: [4](#0-3) 

When `do_update` is triggered by a successful `vote_update`, it removes the executed entry and then **clears all remaining entries and votes**: [5](#0-4) 

Clearing `entries` frees the on-chain storage, which returns the storage cost to the **contract's** available balance — not to the individual proposers. Because the proposer's account ID and deposit amount are never recorded, there is no way to refund them. No sweep or withdraw function exists anywhere in the contract.

This means:
1. The proposer of the executed update loses their deposit.
2. Every other pending proposer (whose entries are also cleared by `entries.clear()`) also permanently loses their deposit.

---

### Impact Explanation

For a contract upgrade with ~500 KB of WASM, `bytes_used` is approximately 500,000 bytes plus overhead for 128 participant vote slots. At NEAR's storage cost of ~10^19 yoctoNEAR/byte, the required deposit is on the order of **5 NEAR per proposal**. If multiple proposals are pending when an update executes, all of their deposits are simultaneously lost. The contract's balance grows by the sum of all freed storage deposits with no recovery path. This breaks the production accounting invariant that a participant who pays for storage should receive the freed funds when that storage is released.

---

### Likelihood Explanation

Contract upgrades are a routine operational activity for the MPC network. Every upgrade cycle involves at least one `propose_update` call followed by threshold `vote_update` calls. The deposit loss occurs deterministically on every successful upgrade execution. No adversarial action is required — normal protocol operation is sufficient to trigger the loss.

---

### Recommendation

1. Extend `UpdateEntry` to record the proposer's `AccountId` and the exact deposit amount paid.
2. When an entry is removed (either because it was executed or because `entries.clear()` is called), transfer the stored deposit back to the original proposer via `Promise::new(proposer).transfer(deposit)`.
3. Alternatively, implement a participant-callable `reclaim_update_deposit(id: UpdateId)` function that refunds the deposit for a cleared entry.

---

### Proof of Concept

1. Participant A calls `propose_update` with a 500 KB contract binary, attaching ~5 NEAR.
2. Participant B calls `propose_update` with a config update, attaching a smaller deposit.
3. Threshold participants call `vote_update` for A's proposal.
4. `do_update` is triggered: `entries.clear()` removes both A's and B's entries, freeing their storage.
5. The freed ~5+ NEAR is credited to the contract's balance.
6. Neither A nor B has any mechanism to reclaim their deposits.
7. Repeating this over the contract's lifetime causes cumulative, irrecoverable NEAR loss for all participants who ever proposed updates. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1297-1334)
```rust
    /// Propose update to either code or config, but not both of them at the same time.
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
