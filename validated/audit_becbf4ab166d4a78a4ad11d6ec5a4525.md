### Title
Proposer's Deposit Permanently Locked When `do_update` Clears All Pending Proposals Without Refund - (File: `crates/contract/src/update.rs`)

### Summary

When `propose_update` is called, a participant must attach a deposit proportional to the size of the update (storage cost). When any update reaches threshold and `do_update` is executed, it unconditionally clears **all** pending proposals and their associated storage — but never refunds the deposits of the non-winning proposers. There is no `cancel_update` or deposit-recovery function. Proposers permanently lose their locked NEAR tokens.

### Finding Description

`propose_update` is gated by `voter_or_panic()` and requires an attached deposit calculated by `ProposedUpdates::required_deposit(&update)`: [1](#0-0) 

The deposit is absorbed into the contract's balance; only the *excess* above the required amount is immediately refunded to the proposer: [2](#0-1) 

When any update reaches threshold via `vote_update`, `do_update` is called. It removes the winning entry and then **clears every other pending proposal** with no deposit refund: [3](#0-2) 

There is no `cancel_update` endpoint, no per-proposal deposit tracking, and no refund path for cleared proposals. The NEAR tokens paid by non-winning proposers are permanently absorbed into the contract balance.

Two concrete scenarios trigger this:

1. **Concurrent proposals**: Multiple participants each call `propose_update` with their own deposit. Once one proposal reaches threshold and `do_update` fires, all other proposals are wiped and their deposits are gone.
2. **Resharing removes the proposer**: A participant proposes an update with a large deposit, then a resharing completes that removes them from the participant set. Even if they wanted to cancel, no such function exists. When any subsequent update executes, their deposit is cleared with no refund.

The `remove_non_participant_update_votes` cleanup after resharing only removes *votes*, not proposals or their deposits: [4](#0-3) 

### Impact Explanation

**Medium.** This breaks the production accounting invariant that deposited funds are recoverable. For a contract binary update, the required deposit scales with the binary size. A WASM binary of several hundred kilobytes at NEAR's storage cost of ~10 yoctoNEAR/byte yields a deposit in the range of several NEAR tokens per proposer. In a network with multiple participants each proposing competing updates (a realistic governance scenario), every non-winning proposer permanently loses their deposit. The funds are not stolen by an attacker but are irrecoverably locked in the contract balance with no on-chain path to retrieve them.

### Likelihood Explanation

**Medium.** The scenario requires at least two concurrent `propose_update` calls with different payloads, which is a normal governance pattern (e.g., two operators independently propose different config or code updates). It also arises naturally after any resharing that changes the participant set while a proposal is pending. Neither condition requires adversarial intent — both are expected operational events.

### Recommendation

Track the deposit amount per proposal entry and refund it to the original proposer when the entry is cleared. Concretely:

1. Add a `proposer: AccountId` and `deposit: NearToken` field to `UpdateEntry`.
2. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue `Promise::new(entry.proposer).transfer(entry.deposit)` for each.
3. Alternatively, expose a `cancel_update(id: UpdateId)` endpoint (callable by the original proposer regardless of current participant status) that removes the entry and refunds the deposit.

### Proof of Concept

1. Participant A (current participant) calls `propose_update` with a 500 KB contract binary, attaching the required deposit (~5 NEAR).
2. Participant B calls `propose_update` with a different config update, attaching a smaller deposit.
3. Threshold participants vote for B's proposal via `vote_update`.
4. `vote_update` calls `do_update`, which executes:
   ```rust
   self.entries.clear();          // A's entry (and deposit) wiped
   self.vote_by_participant.clear();
   ```
5. Participant A's ~5 NEAR deposit is now permanently in the contract balance with no recovery path — no `cancel_update`, no per-entry refund, no cleanup promise that returns funds. [3](#0-2) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L1772-1800)
```rust
    /// Cleans update votes from non-participants after resharing.
    /// Can only be called by participants or by the contract itself.
    #[handle_result]
    pub fn remove_non_participant_update_votes(&mut self) -> Result<(), Error> {
        log!(
            "remove_non_participant_update_votes: signer={}",
            env::signer_account_id()
        );

        let participants = match &self.protocol_state {
            ProtocolContractState::Running(state) => state.parameters.participants(),
            _ => {
                return Err(InvalidState::ProtocolStateNotRunning.into());
            }
        };

        // Authorize the caller: allow self-calls (the cleanup promise spawned after a
        // successful resharing, where the predecessor is the contract account) and
        // direct calls from a current participant. Reject everyone else so that
        // non-participants cannot drive this cleanup.
        let caller = env::predecessor_account_id();
        let is_self_call = caller == env::current_account_id();
        if !is_self_call && !participants.is_participant_given_account_id(&caller) {
            return Err(InvalidState::NotParticipant { account_id: caller }.into());
        }

        self.proposed_updates
            .remove_non_participant_votes(participants);
        Ok(())
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
