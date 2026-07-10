### Title
Deposits from Non-Winning Update Proposals Are Permanently Locked on `do_update` - (File: `crates/contract/src/update.rs`)

### Summary

When `vote_update` reaches threshold and executes `do_update`, all pending update proposals are cleared atomically. The NEAR deposits paid by proposers of non-winning proposals are never refunded and are permanently locked in the MPC contract. The `UpdateEntry` struct does not store the proposer's account ID, making refunds structurally impossible even in a future fix without a state migration.

### Finding Description

`propose_update` requires a deposit proportional to the size of the proposed contract binary or config: [1](#0-0) 

The deposit is retained by the contract (only the excess above `required` is refunded to the proposer). The `UpdateEntry` stored in `proposed_updates.entries` records only the update payload and `bytes_used` — **not the proposer's account ID**: [2](#0-1) 

When `do_update` is called upon threshold being reached, it removes the winning entry and then calls `self.entries.clear()` and `self.vote_by_participant.clear()` on all remaining proposals: [3](#0-2) 

No refund is issued to any of the cleared proposers. Because the proposer's `AccountId` is not stored in `UpdateEntry`, the contract has no record of who to refund even if the logic were added later.

The only other deposit-related path is `remove_update_vote`, which removes a participant's **vote** but does not withdraw the proposal entry or return the deposit: [4](#0-3) 

### Impact Explanation

Every participant who proposed a non-winning update loses their full deposit permanently. For a contract binary update, the deposit is computed as:

```
storage_byte_cost × (sizeof(UpdateEntry) + 128 × sizeof(AccountId) + code.len())
``` [5](#0-4) 

For a realistic contract binary (~500 KB–1 MB), this amounts to tens of NEAR tokens per proposal. The funds are held by the MPC contract with no withdrawal path, permanently reducing the contract's effective balance without any corresponding benefit. This breaks the production accounting invariant that deposited funds are either consumed for their stated purpose or returned to the depositor.

### Likelihood Explanation

The scenario is realistic in any governance round where multiple participants independently propose competing updates (e.g., different contract versions or config changes). The `test_propose_update_contract_many` sandbox test explicitly exercises this scenario — two proposals are submitted and one is executed — confirming the code path is production-reachable. Any participant below the signing threshold can trigger the loss for other proposers simply by proposing a competing update that wins. [6](#0-5) 

### Recommendation

1. **Store the proposer's `AccountId` in `UpdateEntry`** so that refunds can be issued when entries are cleared.
2. **In `do_update`, iterate over all cleared entries and transfer each proposer's deposit back** before clearing the map.
3. Alternatively, **allow proposers to withdraw their own proposal** (and receive a refund) via a new `remove_update_proposal` method, reducing the surface that `do_update` must clean up.

### Proof of Concept

1. Participant A calls `propose_update` with a 500 KB contract binary, attaching ~50 NEAR deposit. Contract stores `UpdateEntry { update: Contract([...]), bytes_used: N }` — no record of A's account.
2. Participant B calls `propose_update` with a different binary, attaching ~50 NEAR deposit.
3. Threshold participants vote for B's proposal. `vote_update` calls `do_update(&B_id, gas)`.
4. `do_update` removes B's entry, then calls `self.entries.clear()` — A's entry is dropped with no refund.
5. A's ~50 NEAR is now permanently held by the MPC contract with no recovery path. [7](#0-6)

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

**File:** crates/contract/src/update.rs (L278-295)
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
