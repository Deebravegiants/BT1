### Title
Proposer's Storage Deposit Permanently Frozen in Contract on Update Execution - (`crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

### Summary

When a participant calls `propose_update()`, they attach a NEAR deposit to cover storage staking for the uploaded contract code or config. When the threshold of votes is reached and `do_update()` executes, all entries are cleared (freeing storage), but the proposer's deposit is **never returned**. The `UpdateEntry` struct does not record the proposer's account ID, so there is no way to identify or refund the original depositor. The deposit — up to ~40 NEAR for a full contract binary — is permanently frozen in the MPC contract's balance.

### Finding Description

`propose_update()` in `crates/contract/src/lib.rs` requires a deposit proportional to the size of the uploaded update: [1](#0-0) 

Only the **excess** above `required` is refunded immediately to `proposer`. The exact `required` amount stays in the contract to cover storage staking for the `UpdateEntry`.

`UpdateEntry` stores only the update payload and `bytes_used` — **no proposer account ID**: [2](#0-1) 

When `vote_update()` reaches threshold, it calls `do_update()`: [3](#0-2) 

`do_update()` removes the winning entry and clears **all** entries and votes, freeing the storage. The freed storage staking is released back to the **contract's** balance — not to the proposer. There is no refund call anywhere in this path. The proposer's deposit is permanently absorbed into the contract.

The deposit magnitude is confirmed by tests and tooling: [4](#0-3) 

A full contract upload (up to ~1.5 MB) requires up to ~40 NEAR in deposit.

### Impact Explanation

The proposer's deposit — potentially tens of NEAR — is permanently frozen in the MPC contract's balance with no recovery path. This breaks the accounting invariant that storage-staking deposits should be returned to the depositor when the storage is freed. The funds are not stolen by an adversary but are irrecoverably locked, matching the M-17 pattern of permanent fund freezing due to the absence of a recipient/refund mechanism.

This maps to: **Medium — balance/accounting invariant broken in production contract execution flow.**

### Likelihood Explanation

Every successful contract upgrade triggers this loss. Participants are expected to propose upgrades regularly (e.g., for TEE image updates, config changes). The proposer is always a current participant (a legitimate, non-malicious actor), and the loss occurs automatically upon threshold approval — no adversarial action is required. The only precondition is a successful governance vote, which is the normal operating path.

### Recommendation

1. Add a `proposer: AccountId` field to `UpdateEntry` so the depositor's identity is preserved.
2. In `do_update()`, after clearing entries, schedule a `Promise::new(entry.proposer).transfer(refund_amount)` for the winning entry's proposer (and optionally for all cleared non-winning entries as well).
3. Alternatively, store a `BTreeMap<UpdateId, (AccountId, NearToken)>` alongside `entries` to track who paid what, and sweep refunds on `do_update`.

### Proof of Concept

1. Participant A calls `propose_update` with a 40 NEAR deposit for a full contract binary. The exact `required` deposit (e.g., 38 NEAR) stays in the contract; 2 NEAR excess is refunded immediately.
2. Threshold participants call `vote_update`. On the threshold vote, `do_update` is triggered.
3. `do_update` calls `self.entries.clear()` and `self.vote_by_participant.clear()`, freeing all storage. The 38 NEAR of freed storage staking is credited back to the **contract's** balance.
4. Participant A's 38 NEAR is now permanently part of the contract's balance. There is no function to claim it back, and the `UpdateEntry` that was removed contained no record of Participant A's account ID. [5](#0-4) [6](#0-5)

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

**File:** crates/contract/src/update.rs (L132-135)
```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L59-70)
```rust
    let execution = mpc_signer_accounts[0]
        .call(contract.id(), method_names::PROPOSE_UPDATE)
        .args_borsh((ProposeUpdateArgs {
            code: Some(vec![0; 1536 * 1024 - 400]), //3900 seems to not work locally
            config: None,
        },))
        .max_gas()
        .deposit(NearToken::from_near(40))
        .transact()
        .await
        .unwrap();
    dbg!(&execution);
```
