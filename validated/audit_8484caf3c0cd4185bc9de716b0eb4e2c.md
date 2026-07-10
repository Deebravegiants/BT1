### Title
Non-Winning Update Proposal Deposits Permanently Locked on `do_update` Execution — (`File: crates/contract/src/update.rs`)

---

### Summary

`propose_update` collects a NEAR deposit from each proposer to cover storage costs, but `do_update` bulk-clears all competing proposals without refunding their depositors. Because the `UpdateEntry` struct never records the proposer's account ID, there is no refund path. Every participant who proposed a non-winning update permanently loses their deposited NEAR when any update reaches threshold.

---

### Finding Description

`propose_update` in `lib.rs` requires each caller to attach a deposit equal to `ProposedUpdates::required_deposit(&update)`, which is computed as `storage_byte_cost × bytes_used`. For a contract binary update, `bytes_used` includes the full code length plus overhead for 128 participant-vote slots, making the deposit potentially 10+ NEAR for a typical ~1 MB WASM binary. [1](#0-0) 

The exact-required portion of the deposit is retained by the contract; only the excess is refunded to the proposer. The proposer's `AccountId` is **not** stored in the `UpdateEntry`: [2](#0-1) 

When `vote_update` reaches threshold it calls `do_update`, which removes the winning entry and then bulk-clears every other proposal and every vote with no refund logic: [3](#0-2) 

Because the proposer's identity was never stored, the contract has no information about who to refund. The NEAR tokens from all non-winning proposals remain in the contract's balance permanently, with no withdrawal or reclaim mechanism exposed in the API. [4](#0-3) 

---

### Impact Explanation

This matches the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."*

Every participant who proposed a competing update loses their full storage deposit — potentially 10+ NEAR per proposal — the moment any other update is executed. The loss is irreversible: there is no `withdraw_proposal`, no refund callback, and no way to recover the funds after `entries.clear()` runs. The contract's balance grows by the sum of all non-winning deposits, permanently.

---

### Likelihood Explanation

The scenario is realistic and expected in normal operation. The test `test_propose_update_contract_many` explicitly exercises multiple simultaneous proposals, and `only_one_vote_from_participant` shows participants voting for different competing proposals. In any governance round where more than one participant proposes an update (common when participants disagree on which binary to deploy), all but one proposer will lose their deposit when the winning proposal executes. [5](#0-4) 

---

### Recommendation

Store the proposer's `AccountId` inside `UpdateEntry` at proposal time:

```rust
pub(crate) struct UpdateEntry {
    pub(super) update: Update,
    pub(super) bytes_used: u128,
    pub(super) proposer: AccountId,   // add this
}
```

In `do_update`, before calling `self.entries.clear()`, iterate over the remaining entries and issue a `Promise::new(entry.proposer).transfer(required_deposit(entry.bytes_used))` for each one. This mirrors the pattern already used in `propose_update` for excess-deposit refunds. [6](#0-5) 

---

### Proof of Concept

1. Alice (participant) calls `propose_update` with a 1 MB contract binary, attaching ~10 NEAR. The contract keeps exactly `required_deposit` ≈ 10 NEAR; Alice's `AccountId` is not stored.
2. Bob (participant) calls `propose_update` with a different binary, also attaching ~10 NEAR. Same outcome.
3. Charlie, Dave, … (threshold participants) vote for Bob's proposal. `vote_update` reaches threshold and calls `do_update(bob_id, gas)`.
4. `do_update` removes Bob's entry, then calls `self.entries.clear()` — Alice's entry is deleted with no refund.
5. Alice's ~10 NEAR is permanently locked in the contract balance. She has no reclaim path. [7](#0-6) [8](#0-7)

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

**File:** crates/contract/src/update.rs (L167-174)
```rust
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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L246-304)
```rust
// TODO(#496): Investigate flakiness of this test
#[tokio::test]
async fn test_propose_update_contract_many() {
    let SandboxTestSetup {
        contract,
        mpc_signer_accounts,
        ..
    } = SandboxTestSetup::builder()
        .with_protocols(ALL_PROTOCOLS)
        .build()
        .await;
    dbg!(contract.id());

    const PROPOSAL_COUNT: usize = 2;
    let mut proposals = Vec::with_capacity(PROPOSAL_COUNT);
    // Try to propose multiple updates to check if they are being proposed correctly
    // and that we can have many at once living in the contract state.
    for i in 0..PROPOSAL_COUNT {
        let execution = mpc_signer_accounts[i % mpc_signer_accounts.len()]
            .call(contract.id(), method_names::PROPOSE_UPDATE)
            .args_borsh(current_contract_proposal())
            .max_gas()
            .deposit(CURRENT_CONTRACT_DEPLOY_DEPOSIT)
            .transact()
            .await
            .unwrap();

        assert!(
            execution.is_success(),
            "failed to propose update [i={i}]; {execution:#?}"
        );
        let proposal_id = execution.json().expect("unable to convert into UpdateId");
        proposals.push(proposal_id);
    }

    // Vote for the last proposal
    vote_update_till_completion(&contract, &mpc_signer_accounts, proposals.last().unwrap()).await;

    // Ensure all proposals are removed after update
    for proposal in proposals {
        let voter = mpc_signer_accounts.first().unwrap();
        let execution = voter
            .call(contract.id(), method_names::VOTE_UPDATE)
            .args_json(serde_json::json!({
                "id": proposal,
            }))
            .gas(GAS_FOR_VOTE_UPDATE)
            .transact()
            .await
            .unwrap();
        dbg!(&execution);

        assert!(execution.is_failure());
    }

    // Let's check that we can call into the state and see all the proposals.
    let state: ProtocolContractState = get_state(&contract).await;
    dbg!(state);
}
```
