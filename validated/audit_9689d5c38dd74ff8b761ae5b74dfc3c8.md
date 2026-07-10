### Title
Propose-Update Deposits Permanently Locked When Competing Proposals Are Cleared - (`crates/contract/src/update.rs`)

### Summary
When `do_update` executes a winning contract/config proposal, it unconditionally clears **all** pending proposals and their associated votes, but never refunds the NEAR deposits that other proposers paid. Those deposits are permanently locked in the MPC contract with no recovery path.

### Finding Description

`propose_update` is a `#[payable]` function that requires a deposit proportional to the size of the uploaded code or config. Only the excess above the exact required amount is refunded at proposal time; the required portion stays in the contract. [1](#0-0) 

When `vote_update` reaches threshold and calls `do_update`, the implementation removes the winning entry, then calls `self.entries.clear()` and `self.vote_by_participant.clear()` to wipe every other pending proposal: [2](#0-1) 

No refund is issued to any proposer — neither for the executed proposal nor for the cleared ones. The `UpdateEntry` struct stores only `update` and `bytes_used`; it does not record the proposer's account ID or the deposit amount, so there is no data available to drive a refund even if one were attempted: [3](#0-2) 

The test `test_proposed_updates_do_update_clears_all_state` explicitly confirms that all entries are wiped on execution, with no mention of deposit recovery: [4](#0-3) 

### Impact Explanation

Every participant who proposed a competing update loses their full required deposit permanently. For a maximum-size contract upload the deposit is 40 NEAR (as used in `test_propose_contract_max_size_upload`); even a config-only proposal costs 0.1 NEAR. In a network with multiple participants each proposing different upgrades — a normal governance scenario — all but one proposer forfeit their deposits with no recourse. This breaks the production accounting invariant that deposits paid for storage that is subsequently freed should be returned to the payer. [5](#0-4) 

### Likelihood Explanation

The scenario is a routine governance event: multiple participants independently propose different contract upgrades or config changes, each paying the required deposit. When threshold votes accumulate for one proposal and `do_update` fires, every other proposer's deposit is silently forfeited. No adversarial coordination is required; the loss occurs in normal operation whenever more than one proposal is live simultaneously. [6](#0-5) 

### Recommendation

1. Add `proposer: AccountId` and `deposit: NearToken` fields to `UpdateEntry`.
2. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue `Promise::new(entry.proposer).transfer(entry.deposit)` for each one.
3. Also refund the executed proposal's deposit after the deploy/config promise resolves (or immediately, since the storage cost is borne by the contract itself).

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB contract binary, attaching 40 NEAR.
2. Participant B calls `propose_update` with a different binary, attaching 40 NEAR.
3. Threshold participants vote for B's proposal via `vote_update`.
4. `do_update` executes B's update, calls `self.entries.clear()` — A's entry (and its 40 NEAR deposit) is erased.
5. A's 40 NEAR is now held by the MPC contract with no function that can return it. `propose_update` stores no proposer address in `UpdateEntry`, so no refund path exists. [7](#0-6)

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

**File:** crates/contract/src/update.rs (L547-614)
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
```

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L59-74)
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
    assert!(
        execution.is_success(),
        "Failed to propose update with our highest contract size"
    );
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
