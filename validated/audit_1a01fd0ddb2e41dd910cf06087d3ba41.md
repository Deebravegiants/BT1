Now I have a complete picture of the code. Let me analyze the exact deposit accounting flow.

### Title
Deposits for Non-Winning Proposals Permanently Lost When `do_update` Clears All Entries — (`crates/contract/src/update.rs`)

### Summary

`do_update` unconditionally clears every pending proposal entry after executing the winning update, but neither the `UpdateEntry` struct nor the clearing logic tracks or refunds the storage deposits paid by non-winning proposers. Those NEAR tokens are permanently absorbed into the contract balance with no recovery path.

### Finding Description

`propose_update` enforces a mandatory deposit equal to `env::storage_byte_cost() * bytes_used(update)` and only refunds the *excess* above that required amount immediately: [1](#0-0) 

The `required` portion stays in the contract. The `UpdateEntry` struct that is stored per proposal contains only the update payload and its byte size — **no proposer account ID**: [2](#0-1) 

When `do_update` is called after threshold votes are reached, it removes the winning entry, then calls `self.entries.clear()` and `self.vote_by_participant.clear()` with no refund logic for the cleared entries: [3](#0-2) 

Because the proposer's `AccountId` is never stored in `UpdateEntry`, it is structurally impossible to issue refunds at clearing time. The freed storage reduces the contract's on-chain storage obligation, but the corresponding NEAR tokens remain in the contract balance forever.

The existing test `test_proposed_updates_do_update_clears_all_state` explicitly verifies that all entries are wiped, but makes no assertion about deposit refunds — confirming this is the intended (but flawed) design: [4](#0-3) 

### Impact Explanation

Every participant who proposes a non-winning update loses their full storage deposit permanently. For a contract binary update (e.g., 1 MB of WASM), `storage_byte_cost() * 1_000_000` is on the order of 1 NEAR. There is no admin function, no cancel-proposal path, and no recovery mechanism. The contract balance invariant — *every `propose_update` deposit is either refunded or consumed by the winning update* — is broken.

### Likelihood Explanation

This triggers under normal operation whenever two or more proposals coexist and one reaches threshold. It does not require adversarial intent: any participant who proposes an update while another proposal is already pending and subsequently wins is silently penalized. The sandbox test `test_propose_update_contract_many` already exercises exactly this scenario (two proposals, one wins) and confirms all proposals are cleared, but does not check for refunds: [5](#0-4) 

### Recommendation

Store the proposer's `AccountId` inside `UpdateEntry`. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining (non-winning) entries and emit `Promise::new(entry.proposer).transfer(required_deposit(entry.bytes_used))` for each. This restores the accounting invariant without changing the threshold-voting logic.

### Proof of Concept

1. Two participants each call `propose_update` with distinct payloads, each attaching the required deposit.
2. Threshold participants vote for proposal B until `do_update` fires.
3. Assert that proposal A's entry is gone and that no `Transfer` action was emitted to A's proposer account.
4. Assert the contract balance increased by `required_deposit(A)` — confirming permanent absorption.

The unit test `test_proposed_updates_do_update_clears_all_state` already proves step 3 (entries cleared, no refund) at the unit level; a sandbox integration test mirroring `test_propose_update_contract_many` can confirm the balance delta at the NEAR runtime level. [6](#0-5)

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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L248-299)
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
```
