### Title
Permanent Loss of Proposal Deposits on `do_update` Execution — (`File: crates/contract/src/update.rs`)

### Summary
When any contract update reaches threshold and executes, `do_update` unconditionally clears **all** pending proposals from storage but never refunds the deposits paid by proposers of the non-executed proposals. Those deposits are permanently locked in the contract.

### Finding Description
`propose_update` requires each proposer to attach a deposit proportional to the storage cost of their proposal (WASM binary size + overhead). The exact required amount is kept by the contract; only the excess is refunded at proposal time. [1](#0-0) 

When any proposal reaches threshold and `vote_update` triggers `do_update`, the implementation removes the winning entry and then calls `self.entries.clear()` and `self.vote_by_participant.clear()`, wiping every other pending proposal from storage. [2](#0-1) 

No refund is issued to the proposers of the cleared entries. The `bytes_used` field stored in each `UpdateEntry` is never consulted for a refund calculation. [3](#0-2) 

There is no `remove_proposal` endpoint and `remove_update_vote` only removes the vote record, not the proposal entry or its deposit. [4](#0-3) 

### Impact Explanation
Every participant who proposed an update that was not the one executed permanently loses their deposit. For a WASM contract binary (potentially hundreds of kilobytes), the required deposit is calculated as `storage_byte_cost × bytes_used`, which at NEAR's current storage pricing can reach several NEAR tokens per proposal. With multiple concurrent proposals (the system explicitly supports this), the total locked value can be material. The funds are irrecoverably locked in the contract with no withdrawal path.

This breaks the production accounting invariant: storage deposits must be returned when the storage they cover is freed.

### Likelihood Explanation
This occurs on every successful contract upgrade. The system is designed to allow multiple concurrent proposals, and the test suite explicitly exercises this scenario (`test_propose_update_contract_many`). Any participant who proposes an update that is not the one that ultimately passes loses their deposit. A Byzantine participant below the signing threshold can amplify the damage by proposing a large WASM binary, forcing other participants to also pay large deposits for their own competing proposals, all of which are wiped when the threshold proposal executes.

### Recommendation
Before calling `self.entries.clear()`, iterate over all remaining entries and issue a `Promise::new(proposer).transfer(deposit)` refund for each. The `bytes_used` field already stored in `UpdateEntry` provides the information needed to reconstruct the deposit amount (`env::storage_byte_cost().saturating_mul(entry.bytes_used)`). Alternatively, store the proposer's `AccountId` alongside each entry so the refund target is unambiguous.

### Proof of Concept
1. Participant A calls `propose_update` with a 500 KB WASM binary, attaching the required deposit (~5 NEAR).
2. Participant B calls `propose_update` with a different WASM binary, attaching its required deposit.
3. Threshold participants vote for B's proposal; `vote_update` calls `do_update(&id_B, gas)`.
4. `do_update` removes B's entry, then calls `self.entries.clear()` — A's entry is deleted.
5. No refund promise is created for A. A's ~5 NEAR deposit is permanently locked in the contract. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L1395-1404)
```rust
    /// Removes an update vote by the caller
    /// panics if the contract is not in a running state or if the caller is not a participant
    pub fn remove_update_vote(&mut self) {
        log!("remove_update_vote: signer={}", env::signer_account_id(),);
        let ProtocolContractState::Running(_running_state) = &self.protocol_state else {
            env::panic_str("protocol must be in running state");
        };
        let voter = self.voter_or_panic();
        self.proposed_updates.remove_vote(&voter);
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
