### Title
Irrecoverable Storage Deposits in `propose_update` — No Refund on Execution or Clearing - (File: `crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

### Summary

When a participant calls `propose_update`, they must attach a NEAR deposit sized to cover the on-chain storage cost of the update entry. When the update is eventually executed via `do_update`, all stored entries are cleared — freeing the storage — but the deposited NEAR is never returned to any proposer. There is no withdrawal or rescue function anywhere in the contract. The deposited NEAR is permanently locked.

### Finding Description

`propose_update` in `lib.rs` enforces a deposit equal to `ProposedUpdates::required_deposit(&update)`, which is `storage_byte_cost × bytes_used`. Any excess above that exact amount is immediately refunded to the proposer. [1](#0-0) 

The `required_deposit` calculation in `update.rs` accounts for the serialized code or config size plus a fixed overhead for 128 participant-vote slots: [2](#0-1) 

When `vote_update` reaches threshold, `do_update` is called. It removes the winning entry and then calls `self.entries.clear()` and `self.vote_by_participant.clear()`, wiping every other pending proposal and all votes: [3](#0-2) 

Clearing these `IterableMap` collections frees the on-chain storage, reducing the contract's storage obligation. However, **no `Promise::transfer` is issued to any proposer**. The NEAR tokens that were deposited to cover that storage remain in the contract's balance with no path to recovery.

There is no `withdraw`, `rescue`, or equivalent function anywhere in the contract's public API. The only transfer paths are the immediate excess-refund calls in `propose_update`, `submit_participant_info`, and `require_deposit` — none of which fire after storage is freed. [4](#0-3) 

### Impact Explanation

Every successful contract upgrade permanently locks the proposer's storage deposit inside the MPC contract. For a contract-code update, `bytes_used` includes the full WASM binary (potentially hundreds of kilobytes to megabytes), making the locked deposit non-trivial. The funds are not stolen by an attacker but are irrecoverable by the rightful owner, breaking the accounting invariant that storage deposits are refundable when the storage they cover is freed. This matches the **Medium** allowed impact: *balance or contract execution-flow manipulation that breaks production safety/accounting invariants*.

### Likelihood Explanation

Every contract upgrade execution triggers this loss. Contract upgrades are a routine governance operation in the MPC network. The proposer is always a legitimate participant who paid a real deposit; the loss is deterministic and unconditional on every `do_update` call.

### Recommendation

In `do_update`, before clearing entries, iterate over all stored `UpdateEntry` values and issue a `Promise::transfer` of `required_deposit(entry.bytes_used)` back to the original proposer. Since the proposer's account ID is not currently stored in `UpdateEntry`, it must be added at proposal time. Alternatively, refund only the winning proposer (whose entry is removed first) and accept that competing proposers' deposits are forfeited — but this should be an explicit documented policy, not an accidental omission.

```rust
// In do_update, before entries.clear():
for (_, entry) in self.entries.iter() {
    if let Some(proposer) = &entry.proposer {
        let refund = required_deposit(entry.bytes_used);
        Promise::new(proposer.clone()).transfer(refund).detach();
    }
}
self.entries.clear();
```

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB WASM binary. Required deposit ≈ `1_000_000 × storage_byte_cost` ≈ ~10 NEAR. Excess is refunded; exactly ~10 NEAR stays in the contract.
2. Participant B calls `propose_update` with a config update. Required deposit ≈ small amount. Stays in contract.
3. Threshold of participants call `vote_update` for A's proposal.
4. `do_update` executes: removes A's entry, calls `self.entries.clear()` (removes B's entry too), calls `self.vote_by_participant.clear()`.
5. Storage is freed. Neither A nor B receives any refund.
6. ~10+ NEAR is permanently locked in the MPC contract with no recovery path. [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L122-141)
```rust
fn require_deposit(minimum_deposit: NearToken, predecessor: &AccountId) {
    let deposit = env::attached_deposit();
    match deposit.checked_sub(minimum_deposit) {
        None => {
            env::panic_str(
                &InvalidParameters::InsufficientDeposit {
                    attached: deposit.as_yoctonear(),
                    required: minimum_deposit.as_yoctonear(),
                }
                .to_string(),
            );
        }
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
        }
    }
}
```

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
