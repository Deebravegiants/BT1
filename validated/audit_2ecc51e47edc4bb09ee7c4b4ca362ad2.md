### Title
Permanent Loss of `propose_update` Storage Deposits When Competing Proposals Are Cleared — (`File: crates/contract/src/update.rs`)

### Summary
When any update proposal reaches threshold and `do_update` is executed, **all other pending proposals are cleared from storage without refunding the NEAR deposits** their proposers paid. Those deposits are permanently locked in the contract with no retrieval mechanism.

### Finding Description
`propose_update` in `crates/contract/src/lib.rs` requires each proposer to attach a deposit covering the storage cost of their proposal (proportional to the contract binary or config size). The deposit is retained by the contract for the lifetime of the proposal. [1](#0-0) 

When `vote_update` reaches threshold it calls `ProposedUpdates::do_update`, which removes the winning entry, then calls `self.entries.clear()` and `self.vote_by_participant.clear()` to wipe all remaining proposals: [2](#0-1) 

The `clear()` calls free the on-chain storage occupied by every competing proposal, but **no refund `Promise` is issued to any of the other proposers**. Their deposits remain in the contract balance permanently. There is no `cancel_update`, `withdraw_deposit`, or any other function in the contract API that would allow a proposer to recover their deposit after their proposal is superseded. [3](#0-2) 

The `bytes_used` field stored in each `UpdateEntry` records exactly how much storage was charged, so the information needed to compute a refund is present — it is simply never used on the clearing path. [4](#0-3) 

### Impact Explanation
Deposits for a maximum-size contract binary can reach ~40 NEAR (as exercised in the test suite). With multiple participants each proposing different updates simultaneously — a normal governance pattern — every proposer except the one whose update is executed permanently loses their deposit. The NEAR tokens are locked inside the MPC contract with no path to recovery short of a future contract upgrade that explicitly handles them. This breaks the accounting invariant that storage deposits are returned when the storage they cover is freed.

### Likelihood Explanation
This is triggered by ordinary governance: any time participants disagree on which update to execute and multiple proposals coexist, the losing proposers lose their deposits. No adversarial intent is required. The multi-proposal scenario is explicitly tested and expected. [5](#0-4) 

### Recommendation
In `do_update`, before calling `self.entries.clear()`, iterate over the remaining entries and issue a `Promise::transfer` refund to each proposer for their stored deposit. Since the proposer's `AccountId` is available as the signer at proposal time, it should be stored alongside `bytes_used` in `UpdateEntry` so the clearing path can issue the refund. Alternatively, expose a `cancel_update` endpoint that lets a proposer withdraw their deposit while their proposal is still pending.

### Proof of Concept
1. Participant A calls `propose_update` with a 1 MB contract binary, attaching ~10 NEAR deposit. `UpdateId(0)` is created.
2. Participant B calls `propose_update` with a different binary, attaching ~10 NEAR deposit. `UpdateId(1)` is created.
3. Threshold participants vote for `UpdateId(1)`. `vote_update` calls `do_update(&UpdateId(1), ...)`.
4. Inside `do_update`: `self.entries.remove(&UpdateId(1))` extracts the winning entry; `self.entries.clear()` silently drops `UpdateId(0)` and its `UpdateEntry { bytes_used: ~10 NEAR worth }`.
5. No `Promise::transfer` is issued to Participant A.
6. Participant A's ~10 NEAR is permanently locked in the contract. There is no contract method to recover it. [3](#0-2) [6](#0-5)

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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L246-283)
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

```
