### Title
Deposits from Competing `propose_update` Proposals Are Permanently Locked When `do_update` Clears All Entries — (File: `crates/contract/src/update.rs`)

### Summary

When `do_update` executes a winning contract/config update, it calls `self.entries.clear()` to remove all competing proposals from storage. The storage bytes are freed (returning balance to the contract account), but the NEAR deposits originally paid by the proposers of the cleared proposals are never refunded. Those funds are permanently locked inside the MPC contract with no recovery path.

### Finding Description

`propose_update` is a `#[payable]` function that requires a deposit proportional to the storage cost of the proposed update: [1](#0-0) 

The required deposit is computed as: [2](#0-1) 

For a contract WASM update, `bytes_used` includes the full code length plus overhead for 128 participant-vote slots, making the required deposit on the order of **10+ NEAR per megabyte of WASM**. Only the excess above the required amount is refunded to the proposer at submission time; the required portion is retained by the contract.

When `vote_update` reaches threshold, it calls `do_update`, which: [3](#0-2) 

`self.entries.clear()` removes every pending proposal from the `IterableMap`, freeing the storage and crediting the released bytes back to the **contract's own balance**. However, there is no code anywhere in `do_update`, `vote_update`, or any other contract method that transfers those freed funds back to the original proposers. The proposers of the cleared proposals have no mechanism to reclaim their deposits.

### Impact Explanation

Every participant whose proposal is cleared by a competing update permanently loses their storage deposit. With a typical 1–5 MB WASM binary, each affected proposer loses 10–50 NEAR. Because multiple participants can independently propose updates (the contract allows it and the sandbox tests exercise it), a single governance round can silently destroy tens to hundreds of NEAR belonging to honest MPC node operators. The funds accumulate in the contract's balance with no withdrawal or governance path to recover them.

This breaks the production safety/accounting invariant that a participant's deposit is returned when their proposal is not executed.

### Likelihood Explanation

The scenario is routine: participants propose competing updates (e.g., different WASM versions or config values), one reaches threshold, and `do_update` clears the rest. The sandbox test `test_propose_update_contract_many` explicitly exercises multiple simultaneous proposals and confirms all are removed after one executes — but never checks that deposits are refunded. The loss is silent and automatic on every successful governance upgrade where more than one proposal was pending.

### Recommendation

In `do_update`, before calling `self.entries.clear()`, iterate over the remaining entries and schedule a `Promise::new(original_proposer).transfer(deposit)` for each cleared proposal. The proposer's account ID must be stored in `UpdateEntry` at proposal time (it is currently absent). Alternatively, store the deposit amount alongside the entry and refund it during the clear sweep.

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB WASM, attaching ~10 NEAR deposit. Contract stores `UpdateEntry` for proposal `id=0`.
2. Participant B calls `propose_update` with a different 1 MB WASM, attaching ~10 NEAR deposit. Contract stores `UpdateEntry` for proposal `id=1`.
3. Threshold participants vote for `id=1`. `vote_update` calls `do_update(&id=1, gas)`.
4. Inside `do_update`:
   - `self.entries.remove(&id=1)` — removes B's entry, storage freed → contract balance +10 NEAR.
   - `self.entries.clear()` — removes A's entry, storage freed → contract balance +10 NEAR.
   - No `Promise::transfer` is issued for A's 10 NEAR.
5. A's 10 NEAR is now permanently locked in the contract. No contract method exists to recover it. [4](#0-3) [5](#0-4)

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
