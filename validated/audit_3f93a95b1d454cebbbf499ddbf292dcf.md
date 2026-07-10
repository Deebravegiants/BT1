### Title
Proposers of Non-Executed Contract Updates Permanently Lose Their Storage Deposits — (`File: crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

---

### Summary

When `propose_update` is called, the proposer pays a storage deposit proportional to the update payload size. However, the `UpdateEntry` struct never records the proposer's `AccountId` or the deposit amount. When any update reaches threshold and `do_update` is called, it bulk-clears **all** entries — including every competing proposal — with no refund path. Proposers of non-executed updates permanently lose their deposits, and there is no function in the contract that allows them to recover those funds.

---

### Finding Description

`propose_update` in `lib.rs` collects a deposit from the caller:

```rust
// crates/contract/src/lib.rs:1308-1318
let attached = env::attached_deposit();
let required = ProposedUpdates::required_deposit(&update);
if attached < required {
    return Err(...);
}
let id = self.proposed_updates.propose(update);
// Refund only the *excess* above required; the required amount is kept.
```

The `propose` helper in `update.rs` stores only the payload and its byte count:

```rust
// crates/contract/src/update.rs:132-135
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
}
```

Neither the proposer's `AccountId` nor the deposit amount is persisted. When threshold votes arrive and `do_update` fires:

```rust
// crates/contract/src/update.rs:195-200
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    // Clear all entries as they might be no longer valid
    self.entries.clear();
    self.vote_by_participant.clear();
    ...
}
```

Every competing proposal is silently dropped. Because the proposer identity and deposit amount were never stored, no refund can be issued — not by the contract, not by any privileged role, and not by the proposer themselves. There is no `cancel_update`, `withdraw_update_deposit`, or equivalent function anywhere in the contract.

---

### Impact Explanation

Every participant who proposed an update that was not selected permanently loses their deposit. For a contract binary update, `required_deposit` is computed as `env::storage_byte_cost() × bytes_used`, where `bytes_used` includes the full WASM binary plus a fixed overhead for 128 participant-vote slots. A typical MPC contract binary is hundreds of kilobytes; at NEAR's storage pricing this translates to multiple NEAR tokens per proposer. In a governance round where N participants each propose a competing update, N−1 deposits are irrecoverably locked in the contract. This breaks the production accounting invariant that deposited funds are either consumed for their stated purpose or returned to the depositor.

---

### Likelihood Explanation

The scenario is a routine governance operation. Any time participants disagree on which update to apply — a common situation during protocol upgrades — multiple competing proposals will be submitted. The deposit loss is deterministic and occurs on every such governance cycle. No adversarial setup is required; the loss is an inherent consequence of the current design.

---

### Recommendation

Store the proposer's `AccountId` and the exact deposit amount inside `UpdateEntry`:

```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
    pub(super) proposer: AccountId,   // add
    pub(super) deposit: NearToken,    // add
}
```

In `do_update`, before calling `entries.clear()`, iterate over all remaining entries and schedule a `Promise::new(entry.proposer).transfer(entry.deposit)` for each one. Additionally, expose a `cancel_update(id: UpdateId)` function that lets the original proposer withdraw their deposit at any time before the update is executed, analogous to the pattern already used for excess-deposit refunds in `propose_update` itself.

---

### Proof of Concept

1. Participant A calls `propose_update` with a 500 KB WASM binary, paying ~5 NEAR deposit. `UpdateEntry` is stored with `bytes_used` but no `proposer` or `deposit` field.
2. Participant B calls `propose_update` with a different binary, paying ~5 NEAR deposit. A second `UpdateEntry` is stored.
3. Threshold participants vote for B's proposal. `vote_update` calls `do_update(&B_id, gas)`.
4. `do_update` removes B's entry, then calls `self.entries.clear()` — A's entry is dropped with no refund.
5. A's 5 NEAR is now permanently locked in the contract. A has no function to call to recover it; the proposer identity was never stored.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
