### Title
Proposer's Storage Deposit Permanently Locked in Contract When `propose_update` Entries Are Cleared — (`crates/contract/src/update.rs`, `crates/contract/src/lib.rs`)

### Summary
`propose_update` requires callers to attach a deposit sized to cover the storage cost of the proposal. When `do_update` executes the winning proposal it clears **all** pending entries and votes, freeing that storage — but no deposit is ever refunded to any proposer. The NEAR tokens are permanently locked in the contract with no retrieval path.

### Finding Description
In `propose_update`, the caller must attach at least `ProposedUpdates::required_deposit(&update)` NEAR, which is computed from the byte-size of the serialised update payload:

```rust
let attached = env::attached_deposit();
let required = ProposedUpdates::required_deposit(&update);
// ...
let id = self.proposed_updates.propose(update);
// Refund the difference if the proposer attached more than required.
if let Some(diff) = attached.checked_sub(required) && diff > NearToken::from_yoctonear(0) {
    Promise::new(proposer).transfer(diff).detach();
}
``` [1](#0-0) 

Only the *excess* above `required` is refunded; the `required` portion stays in the contract. When `vote_update` reaches threshold it calls `do_update`, which removes the winning entry and then bulk-clears every other pending proposal and all votes:

```rust
pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
    let entry = self.entries.remove(id)?;
    // Clear all entries as they might be no longer valid
    self.entries.clear();
    self.vote_by_participant.clear();
    // ...
}
``` [2](#0-1) 

`UpdateEntry` stores only the update payload and its byte-count — not the proposer's `AccountId` or the deposit amount:

```rust
self.entries.insert(id, UpdateEntry { update, bytes_used });
``` [3](#0-2) 

Because neither the proposer identity nor the deposit amount is persisted, `do_update` has no information with which to issue refunds. The freed storage staking is absorbed into the contract's balance and is irrecoverable by the original depositors.

This is the direct analog of the Curves M-01 pattern: in Curves, `protocolFee` is subtracted from the sell price but never forwarded to `protocolFeeDestination`; here, the deposit is deducted from the proposer to cover storage, but when that storage is freed the deposit is not returned — it remains in the contract with no withdrawal mechanism.

### Impact Explanation
Every successful governance upgrade permanently destroys the proposer's deposit. For a full contract binary the deposit can reach several NEAR (the sandbox tests use `CURRENT_CONTRACT_DEPLOY_DEPOSIT` and the devnet CLI defaults to 8 NEAR). [4](#0-3)  When multiple participants each propose a competing update before threshold is reached, `entries.clear()` wipes all of them simultaneously, locking every proposer's deposit in a single call. There is no admin escape-hatch or sweep function in the contract. This breaks the accounting invariant that storage-staking deposits are returned when the storage they cover is freed — an invariant the contract upholds correctly in every other payable method (`submit_participant_info`, `require_deposit` for sign/CKD requests, etc.).

### Likelihood Explanation
Contract upgrades are a routine governance operation; the devnet tooling, E2E test cluster, and operator guides all exercise `propose_update` / `vote_update` as a standard workflow. [5](#0-4)  Every upgrade cycle silently destroys the proposer's deposit. Because participants are expected to propose competing updates (the code explicitly comments "Clear all entries as they might be no longer valid"), multiple deposits are lost per upgrade cycle.

### Recommendation
Add `proposer: AccountId` and `attached_deposit: NearToken` fields to `UpdateEntry`. In `do_update`, before clearing `self.entries`, iterate over all remaining entries and schedule `Promise::new(entry.proposer).transfer(entry.attached_deposit)` for each. The winning entry's deposit should also be refunded (storage is freed when the entry is removed). This mirrors the refund pattern already used in `submit_participant_info` and `propose_update`'s own excess-refund path.

### Proof of Concept
1. Participant A calls `propose_update` with a 5 NEAR deposit (sized for a ~500 KB contract binary). The `required` portion (e.g. 4.9 NEAR) is retained; 0.1 NEAR excess is refunded.
2. Participants B and C each call `propose_update` with their own competing proposals, each depositing ~1 NEAR.
3. Participants vote; A's proposal reaches threshold.
4. `vote_update` calls `do_update(A_id, gas)`:
   - `self.entries.remove(A_id)` — A's entry removed, storage freed, **no refund issued**.
   - `self.entries.clear()` — B's and C's entries removed, storage freed, **no refunds issued**.
5. A loses ~4.9 NEAR, B and C each lose ~1 NEAR. All amounts are permanently locked in the contract balance with no retrieval path.

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

**File:** crates/contract/src/update.rs (L167-173)
```rust
    pub fn propose(&mut self, update: Update) -> UpdateId {
        let bytes_used = bytes_used(&update);

        let id = self.id.generate();
        self.entries.insert(id, UpdateEntry { update, bytes_used });

        id
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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L219-224)
```rust
    let execution = mpc_signer_accounts[0]
        .call(contract.id(), method_names::PROPOSE_UPDATE)
        .args_borsh((invalid_contract_proposal(),))
        .max_gas()
        .deposit(CONTRACT_DEPLOY)
        .transact()
```

**File:** crates/e2e-tests/src/cluster.rs (L926-991)
```rust
    /// Propose a contract code update and cast votes until `vote_update` reports
    /// the threshold reached. Pair with [`Self::ensure_deployed_code`]: the deploy
    /// and `migrate()` promise runs asynchronously, and a panicking `migrate`
    /// rolls the deploy back without changing the threshold-reached signal.
    pub async fn propose_and_vote_contract_update(&self, new_wasm: &[u8]) -> anyhow::Result<()> {
        anyhow::ensure!(
            !self.nodes.is_empty(),
            "cannot propose contract update with no nodes"
        );

        let propose_args = ProposeUpdateArgsBorsh {
            code: Some(new_wasm),
            config: None,
        };
        let proposer_client = self.operator_client_for(PROPOSER_NODE_INDEX)?;
        let outcome = self
            .contract
            .call_from_borsh_with_deposit(
                &proposer_client,
                method_names::PROPOSE_UPDATE,
                propose_args,
                CONTRACT_UPDATE_GAS,
                CONTRACT_UPDATE_DEPOSIT,
            )
            .await
            .context("failed to call propose_update")?;
        anyhow::ensure!(
            outcome.is_success(),
            "propose_update failed: {:?}",
            outcome.failure_message()
        );
        let proposal_id: UpdateId = outcome
            .json()
            .context("propose_update did not return a JSON UpdateId")?;

        for (i, _) in self.nodes.iter().enumerate() {
            let client = self.operator_client_for(i)?;
            let vote_outcome = self
                .contract
                .call_from(
                    &client,
                    method_names::VOTE_UPDATE,
                    json!({ "id": proposal_id }),
                )
                .await
                .with_context(|| format!("node {i} failed to call vote_update"))?;
            anyhow::ensure!(
                vote_outcome.is_success(),
                "vote_update from node {i} failed: {:?}",
                vote_outcome.failure_message()
            );
            let update_applied: bool = vote_outcome
                .json()
                .with_context(|| format!("vote_update from node {i} returned non-bool"))?;
            if update_applied {
                anyhow::ensure!(
                    i + 1 == self.threshold,
                    "expected exactly {} votes to apply update, got {}",
                    self.threshold,
                    i + 1,
                );
                tracing::info!(votes = i + 1, "contract code update vote threshold reached");
                return Ok(());
            }
        }
        anyhow::bail!("contract code update was not applied after votes from every node")
```
