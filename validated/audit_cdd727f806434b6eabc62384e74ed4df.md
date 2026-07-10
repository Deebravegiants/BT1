### Title
Deposits for Superseded Update Proposals Are Permanently Locked in Contract — (File: `crates/contract/src/update.rs`)

### Summary

When `do_update` executes a winning governance proposal, it unconditionally clears **all** stored proposal entries via `self.entries.clear()`. The NEAR deposits paid by proposers of the non-winning (cleared) proposals are never refunded and are permanently locked in the contract's balance. Because `UpdateEntry` does not record the proposer's account ID, there is no recovery path even in principle.

### Finding Description

`propose_update` in `crates/contract/src/lib.rs` is a `#[payable]` method that requires a deposit calculated as `storage_byte_cost × bytes_used(update)` to cover on-chain storage for the proposal entry. [1](#0-0) 

The excess above the required amount is refunded to the proposer, but the required portion stays in the contract's balance: [2](#0-1) 

`bytes_used` over-provisions storage to account for up to 128 participant votes per entry, making the required deposit non-trivial for large contract binaries: [3](#0-2) 

When `vote_update` reaches threshold it calls `do_update`, which removes the winning entry and then **clears every other entry** in a single sweep: [4](#0-3) 

`UpdateEntry` stores only the update payload and its byte count — not the proposer's account ID: [5](#0-4) 

Because the proposer identity is not persisted, `do_update` has no information with which to issue refunds for the cleared entries. The deposits are absorbed into the contract's general balance with no recovery mechanism.

### Impact Explanation

Every participant whose proposal is cleared by a competing proposal's execution permanently loses their storage deposit. For a 1 MB contract binary the deposit is approximately 10 NEAR (10^6 bytes × 10^19 yoctoNEAR/byte). With multiple competing proposals in flight simultaneously — a realistic governance scenario — multiple proposers each lose this amount. The funds are irrecoverable: there is no `withdraw`, `recover_deposit`, or equivalent method in the contract, and the proposer identity is not stored.

This breaks the production accounting invariant that "deposits paid to cover storage are returned when that storage is freed."

### Likelihood Explanation

Competing proposals are a normal governance event: participants may independently propose different contract upgrades or config changes before consensus is reached. The NEAR MPC network has a small, known participant set, making simultaneous proposals plausible during any upgrade cycle. No adversarial intent is required — the loss occurs as a side-effect of ordinary threshold governance.

### Recommendation

Store the proposer's `AccountId` inside `UpdateEntry`. In `do_update`, before calling `self.entries.clear()`, iterate over the remaining entries and schedule a `Promise::new(entry.proposer).transfer(refund_amount)` for each one, where `refund_amount` is `storage_byte_cost × entry.bytes_used`. This mirrors the refund pattern already used in `propose_update` itself and in `submit_participant_info`.

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB contract binary, attaching the required ~10 NEAR deposit. The deposit is retained by the contract; only the excess is refunded.
2. Participant B calls `propose_update` with a different binary, also paying ~10 NEAR.
3. A threshold of participants call `vote_update` for B's proposal ID.
4. `vote_update` calls `do_update(&id_B, gas)`.
5. `do_update` removes entry B, then calls `self.entries.clear()` — deleting entry A — and `self.vote_by_participant.clear()`.
6. A's ~10 NEAR deposit remains in the contract's balance. A has no way to recover it; the contract has no record of who paid for entry A. [6](#0-5) [7](#0-6)

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
