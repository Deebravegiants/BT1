### Title
Proposal Deposits Permanently Locked When `do_update` Clears All Pending Proposals - (File: `crates/contract/src/update.rs`)

### Summary
The `propose_update` function collects a storage deposit from each proposer, but when any update reaches threshold and `do_update` is executed, it clears **all** pending proposals without refunding the deposits paid by proposers of non-executed proposals. Those NEAR tokens are permanently locked in the contract with no recovery path.

### Finding Description

`propose_update` in `crates/contract/src/lib.rs` requires a deposit proportional to the storage consumed by the proposal. For a full contract binary (~1.5 MB), this is on the order of 40 NEAR (as confirmed by sandbox tests using `CURRENT_CONTRACT_DEPLOY_DEPOSIT`). [1](#0-0) 

The deposit is computed by `ProposedUpdates::required_deposit`, which calls `bytes_used` — a function that accounts for the full serialized size of the update payload plus a fixed overhead for votes. [2](#0-1) 

When `do_update` is called after threshold is reached, it removes the winning entry and then calls `self.entries.clear()` and `self.vote_by_participant.clear()`, wiping every other pending proposal from storage. [3](#0-2) 

The freed storage bytes are reclaimed by the NEAR runtime and credited back to the contract's own balance — but the NEAR tokens originally deposited by the proposers of the cleared (non-executed) proposals are **never returned to those proposers**. They accumulate silently in the contract's balance.

There is no `cancel_proposal`, `withdraw_proposal`, or any other function that allows a proposer to reclaim their deposit. The only deposit-related logic in `propose_update` is a refund of the *excess* above the required amount at submission time. [4](#0-3) 

The `remove_update_vote` function only removes a vote record; it does not touch the proposal entry or its associated deposit. [5](#0-4) 

### Impact Explanation

Every contract upgrade cycle where more than one proposal exists results in permanent loss of NEAR for the proposers of non-executed proposals. The locked amount scales with the size of the proposed binary (up to ~40 NEAR per proposal for a maximum-size contract). Because the contract has no privileged owner or admin role, and because the only governance path to add a refund function is another `propose_update` cycle (which itself requires a deposit), the locked funds cannot be recovered without a successful upgrade — a circular dependency.

This breaks the production accounting invariant that deposited NEAR for storage should be returned when that storage is freed.

### Likelihood Explanation

Multiple concurrent proposals are a normal operational scenario: different participants may independently propose different contract versions or config changes. The `test_propose_update_contract_many` sandbox test explicitly exercises this multi-proposal path. Every time a threshold-crossing `vote_update` call executes `do_update`, all non-winning proposals are silently cleared and their deposits are lost. [6](#0-5) 

### Recommendation

Before clearing non-executed entries in `do_update`, iterate over `self.entries` and issue a `Promise::new(proposer_account).transfer(entry.deposit)` for each entry that is not the winning one. This requires storing the proposer's `AccountId` alongside each `UpdateEntry` at proposal time. Alternatively, expose a `cancel_proposal(id: UpdateId)` function that allows the original proposer to withdraw their entry and receive a full refund.

### Proof of Concept

1. Participant A calls `propose_update` with a 1.5 MB contract binary, attaching ~40 NEAR deposit. Proposal ID = 0 is stored.
2. Participant B calls `propose_update` with a different binary, attaching ~40 NEAR deposit. Proposal ID = 1 is stored.
3. Threshold participants call `vote_update(id: 1)`. `do_update` executes: it removes entry 1, then calls `self.entries.clear()` (removing entry 0) and `self.vote_by_participant.clear()`.
4. Participant A's ~40 NEAR deposit is now part of the contract's balance. There is no function to retrieve it.
5. Participant A has permanently lost ~40 NEAR with no recourse. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L1300-1334)
```rust
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

**File:** crates/contract/src/lib.rs (L1397-1404)
```rust
    pub fn remove_update_vote(&mut self) {
        log!("remove_update_vote: signer={}", env::signer_account_id(),);
        let ProtocolContractState::Running(_running_state) = &self.protocol_state else {
            env::panic_str("protocol must be in running state");
        };
        let voter = self.voter_or_panic();
        self.proposed_updates.remove_vote(&voter);
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
