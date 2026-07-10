### Title
Deposits for Non-Executed Update Proposals Are Permanently Lost When `do_update` Clears All Entries - (File: crates/contract/src/update.rs)

### Summary
When a contract update reaches threshold and `do_update` is executed, it clears **all** pending proposal entries — not just the winning one. Proposers of non-executed proposals paid a storage deposit via `propose_update` that is never refunded, permanently locking their NEAR tokens in the contract.

### Finding Description
`propose_update` in `crates/contract/src/lib.rs` requires each proposer to attach a deposit covering the estimated storage cost of their proposal:

```rust
let attached = env::attached_deposit();
let required = ProposedUpdates::required_deposit(&update);
if attached < required { ... }
// Refund only the excess; the required amount stays in the contract.
```

The required deposit is computed from `bytes_used`, which for a contract-code proposal includes the full wasm blob size:

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
```

When `vote_update` reaches threshold it calls `do_update`, which removes the winning entry and then **clears every other entry unconditionally**:

```rust
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    // Clear all entries as they might be no longer valid
    self.entries.clear();           // ← all other proposals deleted
    self.vote_by_participant.clear();
    ...
}
```

There is no code path that refunds the deposits of the proposers whose entries are cleared. The `UpdateEntry` struct stores `bytes_used` but it is never used to compute a refund on deletion. No `cancel_proposal` or equivalent function exists that would let a proposer reclaim their deposit before `do_update` fires.

### Impact Explanation
Every participant who called `propose_update` for a proposal that was not the one ultimately executed permanently loses their deposited NEAR. For a typical contract wasm of ~500 KB, the required deposit is on the order of several NEAR tokens (at `~10^-5 NEAR/byte`). This is a direct, permanent loss of funds controlled by the MPC contract, matching the **Medium** impact tier: "Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."

### Likelihood Explanation
Medium. Multiple competing proposals are a realistic governance scenario (e.g., two participants independently propose different contract versions or configs). Every time this occurs and one proposal wins, all other proposers lose their deposits. The trigger requires no special privilege beyond being a current participant, and no threshold-level collusion.

### Recommendation
When `do_update` clears non-executed entries, iterate over them and issue a `Promise::transfer` refund to each original proposer. Because the proposer's account ID is not currently stored in `UpdateEntry`, it must be added:

```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
    pub(super) proposer: AccountId,   // add this
}
```

Then in `do_update`, before `self.entries.clear()`, iterate and refund:

```rust
for (_, entry) in self.entries.iter() {
    let refund = required_deposit(entry.bytes_used);
    Promise::new(entry.proposer.clone()).transfer(refund).detach();
}
self.entries.clear();
```

### Proof of Concept
1. Participant A calls `propose_update` with a 500 KB wasm, attaching ~5 NEAR deposit. Entry `id=0` is stored.
2. Participant B calls `propose_update` with a different wasm, attaching ~5 NEAR deposit. Entry `id=1` is stored.
3. Threshold participants vote for `id=1`; `vote_update` calls `do_update(&id=1, ...)`.
4. `do_update` removes entry `id=1`, then calls `self.entries.clear()` which deletes entry `id=0`.
5. Participant A's ~5 NEAR deposit remains in the contract balance with no refund path. The storage is freed but the tokens are not returned. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
