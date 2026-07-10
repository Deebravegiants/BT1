### Title
Storage Deposit Permanently Locked After Update Execution — (`File: crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

### Summary
`propose_update` requires a NEAR storage deposit from the proposer. When the update is executed (or superseded), `do_update` clears all proposal entries — freeing the on-chain storage — but never refunds the deposited NEAR to any proposer. There is no withdrawal function in the contract. Every successful governance update permanently locks the proposer's NEAR in the contract.

### Finding Description
`propose_update` is `#[payable]` and enforces a deposit calculated from the byte size of the proposed update: [1](#0-0) 

The required deposit is computed as: [2](#0-1) [3](#0-2) 

Excess above the required amount is refunded to the proposer: [4](#0-3) 

However, the exact required deposit is retained by the contract. When `vote_update` reaches threshold and calls `do_update`, all proposal entries are cleared: [5](#0-4) 

`self.entries.clear()` frees the storage that the deposit was meant to cover, but no `Promise::new(proposer).transfer(deposit)` is ever issued. The proposer's NEAR is permanently locked in the contract balance. There is no `withdraw` function anywhere in the contract.

A secondary instance exists in `submit_participant_info`: the function is `#[payable]` but when `attestation_storage_must_be_paid_by_caller` evaluates to `false` (caller is an existing participant re-submitting), any attached deposit is silently accepted and locked with no refund path: [6](#0-5) 

### Impact Explanation
**Medium.** Every successful contract upgrade permanently locks the proposer's NEAR storage deposit in the contract. For a realistic contract binary (e.g., 500 KB), the required deposit is approximately `500_000 * 10^19 yoctoNEAR ≈ 5 NEAR`. This breaks the production accounting invariant that storage deposits are returned when the associated storage is freed. The locked NEAR accumulates with each upgrade cycle and is irrecoverable without a contract migration.

### Likelihood Explanation
**Medium.** Contract upgrades are a normal, expected governance operation. Every upgrade cycle triggers this loss. The proposer is a legitimate participant following the documented governance flow — no error or misconfiguration is required.

### Recommendation
1. Store the proposer's `AccountId` alongside each `UpdateEntry` in `update.rs`.
2. In `do_update`, before clearing entries, iterate over all remaining entries and issue `Promise::new(entry.proposer).transfer(required_deposit(entry.bytes_used))` for each.
3. For `submit_participant_info`, add an explicit refund of any attached deposit when `attestation_storage_must_be_paid_by_caller` is `false`.

### Proof of Concept

1. Participant A calls `propose_update` with a 500 KB contract binary, attaching ~5 NEAR (the required storage deposit). The excess is refunded; exactly `required_deposit` is retained.
2. Participant B calls `propose_update` with a different update, also paying a deposit.
3. Participants vote via `vote_update` for A's proposal until threshold is reached.
4. `do_update` executes: `self.entries.remove(&id)` removes A's entry, then `self.entries.clear()` removes B's entry. All storage is freed.
5. Neither A nor B receives a refund. Both deposits are permanently locked in the contract balance.
6. No `withdraw` method exists to recover the funds. The NEAR is irrecoverable without a contract migration.

### Citations

**File:** crates/contract/src/lib.rs (L823-849)
```rust
        let attestation_storage_must_be_paid_by_caller =
            is_new_attestation || caller_is_not_participant;

        if attestation_storage_must_be_paid_by_caller {
            // `saturating_sub`: if a re-submission shrinks the entry, charge nothing
            // rather than underflow. Intentional asymmetry: we do not refund freed bytes
            // either — the caller already paid for the larger entry, and we'd rather
            // accept that asymmetry than open a refund path for payload-shrinking games.
            let storage_used = env::storage_usage().saturating_sub(initial_storage);
            let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
            let attached = env::attached_deposit();

            if attached < cost {
                return Err(InvalidParameters::InsufficientDeposit {
                    attached: attached.as_yoctonear(),
                    required: cost.as_yoctonear(),
                }
                .into());
            }

            // Refund the difference if the proposer attached more than required
            if let Some(diff) = attached.checked_sub(cost)
                && diff > NearToken::from_yoctonear(0)
            {
                Promise::new(account_id).transfer(diff).detach();
            }
        }
```

**File:** crates/contract/src/lib.rs (L1298-1316)
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
```

**File:** crates/contract/src/lib.rs (L1326-1331)
```rust
        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```

**File:** crates/contract/src/update.rs (L161-164)
```rust
impl ProposedUpdates {
    pub fn required_deposit(update: &Update) -> NearToken {
        required_deposit(bytes_used(update))
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
