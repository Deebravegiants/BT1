### Title
Deposits for Non-Executed `propose_update` Proposals Are Permanently Frozen When Any Proposal Is Executed - (File: crates/contract/src/update.rs)

### Summary
When `do_update` executes a winning proposal, it unconditionally clears **all** pending proposals and their associated state. The NEAR deposits paid by proposers of the non-executed proposals are never refunded and have no recovery path, permanently freezing them in the MPC contract.

### Finding Description

`propose_update` requires a deposit proportional to the size of the submitted update (WASM binary or config). The deposit is calculated as `storage_byte_cost × bytes_used`, where `bytes_used` includes the update payload plus a fixed overhead for 128 participant votes. For a typical contract binary (~1 MB), this amounts to roughly 10 NEAR per proposal. [1](#0-0) 

The deposit is accepted and retained in the contract. Only the excess above the required amount is refunded immediately.

When `vote_update` reaches threshold, it calls `do_update`: [2](#0-1) 

`do_update` removes the winning entry, then calls `self.entries.clear()` and `self.vote_by_participant.clear()`, discarding every other pending proposal. No refund is issued to any of the other proposers. The `UpdateEntry` struct does not even record the proposer's account ID, making a retroactive refund impossible: [3](#0-2) 

There is no function in the contract to sweep or recover these accumulated deposits. The README confirms the clearing behavior is intentional: [4](#0-3) 

The test `test_proposed_updates_do_update_clears_all_state` explicitly verifies that all entries are wiped, but no test checks that deposits are returned: [5](#0-4) 

### Impact Explanation

Every NEAR token deposited for a non-executed proposal is permanently frozen in the chain-signature contract. For a 1 MB WASM binary, the required deposit is approximately 10 NEAR per proposal. With multiple competing proposals (which the contract explicitly supports, as shown by `test_propose_update_contract_many`), the total frozen amount scales linearly with the number of proposals that lose the vote. There is no admin function, sweep method, or governance path to recover these funds. [6](#0-5) 

This matches the **Medium** impact class: balance and accounting invariant broken — deposited NEAR that should be recoverable is permanently locked in the contract.

### Likelihood Explanation

Contract upgrades are a routine governance operation. Multiple participants may independently propose competing updates (e.g., different versions of the same binary, or a binary vs. a config update). The clearing of all proposals on execution is documented and expected behavior, meaning every upgrade cycle that has more than one active proposal silently destroys the non-winning deposits. No special attacker capability is required — any participant (voter) who calls `propose_update` is exposed.

### Recommendation

1. Store the proposer's `AccountId` in `UpdateEntry` alongside `bytes_used`.
2. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue `Promise::new(entry.proposer).transfer(required_deposit(entry.bytes_used))` for each.
3. Alternatively, track deposits in a separate `LookupMap<UpdateId, (AccountId, NearToken)>` and refund on clearing.
4. Add a test asserting that proposers of non-executed proposals receive their deposits back after `do_update` is called.

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB WASM binary, attaching ~10 NEAR. The deposit is accepted; `UpdateEntry { update: Contract([...]), bytes_used: ~1_000_000 }` is stored.
2. Participant B calls `propose_update` with a different 1 MB WASM binary, attaching ~10 NEAR. A second entry is stored.
3. Participants vote for B's proposal until threshold is reached. `vote_update` calls `do_update(&id_B, gas)`.
4. Inside `do_update`: entry B is removed and executed; `self.entries.clear()` wipes entry A; `self.vote_by_participant.clear()` wipes all votes.
5. Participant A's ~10 NEAR remains in the contract balance. No refund is issued. No recovery function exists. The funds are permanently frozen. [7](#0-6)

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

**File:** crates/contract/src/update.rs (L547-615)
```rust
    /// Asserts that [`ProposedUpdates::do_update`] clears all entries and votes.
    #[test]
    fn test_proposed_updates_do_update_clears_all_state() {
        // Given: multiple update proposals with votes from different accounts
        let mut proposed_updates = ProposedUpdates::default();

        let update_0 = Update::Contract([0; 1000].into());
        let update_id_0 = proposed_updates.propose(update_0.clone());

        let update_1 = Update::Contract([1; 1000].into());
        let update_id_1 = proposed_updates.propose(update_1.clone());

        let update_2 = Update::Config(dummy_config(1));
        let update_id_2 = proposed_updates.propose(update_2.clone());

        let account_0 = gen_account_id();
        let account_1 = gen_account_id();
        let account_2 = gen_account_id();

        proposed_updates.vote(&update_id_0, account_0.clone());
        proposed_updates.vote(&update_id_1, account_1.clone());
        proposed_updates.vote(&update_id_2, account_2.clone());

        let before: TestUpdateVotes = (&proposed_updates).try_into().unwrap();
        let expected_before = TestUpdateVotes {
            id: 3,
            votes: BTreeMap::from([
                (account_0.clone(), 0),
                (account_1.clone(), 1),
                (account_2.clone(), 2),
            ]),
            entries: BTreeMap::from([
                (
                    0,
                    UpdateEntry {
                        update: update_0.clone(),
                        bytes_used: bytes_used(&update_0),
                    },
                ),
                (
                    1,
                    UpdateEntry {
                        update: update_1.clone(),
                        bytes_used: bytes_used(&update_1),
                    },
                ),
                (
                    2,
                    UpdateEntry {
                        update: update_2.clone(),
                        bytes_used: bytes_used(&update_2),
                    },
                ),
            ]),
        };
        assert_eq!(before, expected_before);

        // When: executing an update
        proposed_updates.do_update(&update_id_1, Gas::from_tgas(100));

        // Then: all state is cleared (entries and votes)
        let after: TestUpdateVotes = (&proposed_updates).try_into().unwrap();
        let expected_after = TestUpdateVotes {
            id: 3,
            votes: BTreeMap::new(),
            entries: BTreeMap::new(),
        };
        assert_eq!(after, expected_after);
    }
```

**File:** crates/contract/README.md (L49-52)
```markdown
## Contract Updates

Participants can propose and vote on contract updates (code or configuration changes). When an update receives sufficient votes and is executed (via the `vote_update` endpoint which calls `do_update` internally), all pending update proposals and votes are cleared as they are no longer be valid after the contract migration. The update ID counter is preserved across migrations as part of the contract state to avoid race conditions where multiple participants might propose updates with colliding IDs immediately after an upgrade.

```

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L248-304)
```rust
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
