### Title
Deposits for non-executed `propose_update` proposals are permanently locked when `do_update` clears all entries — (`File: crates/contract/src/update.rs`)

---

### Summary

When `vote_update` reaches threshold and triggers `do_update`, the implementation clears **all** pending proposals and votes unconditionally. However, the NEAR token deposits paid by proposers of the non-executed proposals are never refunded. Those deposits remain permanently locked in the contract with no sweep or recovery path.

---

### Finding Description

`propose_update` requires a deposit proportional to the byte-size of the proposed update (contract binary or config): [1](#0-0) 

The deposit is sized by `ProposedUpdates::required_deposit`, which scales with the bytes of the update payload: [2](#0-1) 

When `vote_update` reaches threshold it calls `do_update`, which removes the winning entry and then unconditionally clears **all** remaining entries and all votes: [3](#0-2) 

The `entries.clear()` call at line 199 silently discards every competing proposal. No code path refunds the deposits that were attached to those discarded proposals. The contract has no admin sweep or withdrawal function for these stranded balances.

This is structurally identical to the Ammplify M-20 root cause: a value is collected (deposit / penalty), a later operation discards the associated state without routing the value anywhere, and the funds remain permanently idle in the contract.

---

### Impact Explanation

Every NEAR token deposited for a proposal that is cleared by a competing `do_update` is permanently locked. For contract-code proposals the deposit is proportional to the binary size; a typical WASM contract of several hundred KB requires several NEAR. Multiple participants can hold competing proposals simultaneously (the contract explicitly supports this), so a single `vote_update` execution can lock the deposits of every other proposer in one atomic step.

This matches the **Medium** allowed impact: *balance/accounting invariant broken — deposits paid for proposals are permanently locked, breaking the production safety invariant that deposited funds are either used or returned.*

---

### Likelihood Explanation

The scenario requires no collusion and no privileged access. It arises naturally whenever two or more participants independently propose different updates (e.g., one proposes a code upgrade, another proposes a config change). As soon as one proposal reaches threshold, all others are cleared and their deposits are lost. This is a realistic operational condition in any active deployment with multiple participants.

---

### Recommendation

In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue a `Promise::new(proposer).transfer(deposit)` refund for each one. The proposer's account ID must be stored alongside the entry at proposal time (add a `proposer: AccountId` field to `UpdateEntry`). Alternatively, expose a `cancel_proposal(id)` endpoint that refunds the deposit and removes the entry, and document that proposers should cancel before a competing proposal executes.

---

### Proof of Concept

1. Participant A calls `propose_update` with a large contract binary (e.g., 500 KB → ~5 NEAR deposit). Deposit `D_A` is transferred to the contract.
2. Participant B calls `propose_update` with a different binary. Deposit `D_B` is transferred to the contract.
3. Threshold participants call `vote_update` for B's proposal ID.
4. `do_update` executes:
   - Removes B's `UpdateEntry` and schedules the deploy promise.
   - Calls `self.entries.clear()` — A's entry is silently dropped.
   - Calls `self.vote_by_participant.clear()`.
   - **No refund is issued for `D_A`.**
5. `D_A` is now permanently locked in the contract. There is no function in the contract that can recover it.

Relevant code path:

```
propose_update (lib.rs:1298-1334)
  → ProposedUpdates::propose (update.rs:167-173)   // stores entry, deposit held by contract
  → [threshold votes]
vote_update (lib.rs:1343-1387)
  → ProposedUpdates::do_update (update.rs:195-226)
      self.entries.remove(id)      // winning entry removed
      self.entries.clear()         // ← ALL other entries dropped, deposits never refunded
      self.vote_by_participant.clear()
``` [4](#0-3)

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

**File:** crates/contract/src/update.rs (L162-164)
```rust
    pub fn required_deposit(update: &Update) -> NearToken {
        required_deposit(bytes_used(update))
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
