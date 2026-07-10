### Title
Deposits for Non-Winning `propose_update` Proposals Are Permanently Locked in the Contract - (File: crates/contract/src/update.rs)

### Summary

When `propose_update` is called, the proposer must attach a NEAR deposit to cover storage costs. When any update reaches threshold and `do_update` executes, it clears **all** pending proposals without refunding the deposits of the non-winning proposers. Those deposits are permanently locked in the MPC contract with no recovery path.

### Finding Description

`propose_update` in `crates/contract/src/lib.rs` collects a deposit from the caller equal to `ProposedUpdates::required_deposit(&update)` and stores the entry: [1](#0-0) 

The required deposit is computed from the serialized size of the update (including the full contract WASM binary for code upgrades): [2](#0-1) 

When `vote_update` crosses the threshold and calls `do_update`, the winning entry is removed and then **all remaining entries are bulk-cleared** with no refund: [3](#0-2) 

The `bytes_used` field is stored in `UpdateEntry` but is never read back during cleanup — there is no code path that iterates over the cleared entries and issues `Promise::new(proposer).transfer(deposit)` for each one. [4](#0-3) 

There is no `withdraw_proposal` or `cancel_proposal` method in the contract ABI. The only way proposals are ever removed is via `do_update`, which does not refund.

### Impact Explanation

Any participant who proposed a non-winning update permanently loses their storage deposit. For a contract-code update, `bytes_used` includes the full WASM binary (potentially hundreds of KB) plus 128 × `sizeof(AccountId)` for votes, making the required deposit potentially tens to hundreds of NEAR tokens. Once `do_update` fires for a competing proposal, those tokens are irrecoverably locked inside the MPC contract. This matches the **Medium** allowed impact: balance/accounting invariant break — the contract holds funds it can never return to their rightful owners.

### Likelihood Explanation

The scenario is realistic in any governance round where two or more participants independently propose different updates (e.g., one proposes a code upgrade, another proposes a config change). When one crosses threshold, the other's deposit is silently destroyed. No attacker privilege is required — any current participant can trigger this by proposing a competing update.

### Recommendation

In `do_update`, before calling `self.entries.clear()`, iterate over the remaining entries and refund each proposer's deposit. The `bytes_used` field already stored in `UpdateEntry` can be used to compute the refund amount via `required_deposit(entry.bytes_used)`. A proposer `AccountId` must also be stored at proposal time (analogous to how `propose_update` already captures `proposer` from `voter_or_panic()`) so the refund target is known.

### Proof of Concept

1. Participant A calls `propose_update` with a contract-code update, attaching 50 NEAR (required deposit for a large WASM).
2. Participant B calls `propose_update` with a config update, attaching 1 NEAR.
3. Threshold participants vote for B's config update via `vote_update`.
4. `do_update` executes: removes B's entry, then calls `self.entries.clear()` which silently drops A's entry.
5. A's 50 NEAR deposit remains in the contract balance forever — no refund is issued, no recovery function exists. [5](#0-4)

### Citations

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

**File:** crates/contract/src/update.rs (L161-174)
```rust
impl ProposedUpdates {
    pub fn required_deposit(update: &Update) -> NearToken {
        required_deposit(bytes_used(update))
    }

    /// Propose an update given the new contract code and/or config.
    pub fn propose(&mut self, update: Update) -> UpdateId {
        let bytes_used = bytes_used(&update);

        let id = self.id.generate();
        self.entries.insert(id, UpdateEntry { update, bytes_used });

        id
    }
```

**File:** crates/contract/src/update.rs (L195-226)
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
