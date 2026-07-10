### Title
Proposer Deposits Permanently Locked When `do_update` Clears All Pending Proposals - (File: `crates/contract/src/update.rs`)

### Summary

`propose_update` requires a non-trivial NEAR deposit to cover storage costs for the uploaded contract binary or config. When any proposal reaches threshold and `do_update` is called, it unconditionally clears **all** pending entries and all votes. The deposits paid by every other proposer are never returned. There is no refund path, no withdrawal function, and no mechanism to recover these funds. They are permanently locked in the contract account.

### Finding Description

In `propose_update` (`crates/contract/src/lib.rs`), the caller must attach a deposit calculated by `ProposedUpdates::required_deposit`, which for a full contract binary can reach tens of NEAR: [1](#0-0) 

Only the *excess* above `required` is refunded. The `required` portion stays in the contract: [2](#0-1) 

When `vote_update` reaches threshold it calls `do_update`, which clears **every** entry and every vote in one sweep — including proposals from other participants who each paid their own deposit: [3](#0-2) 

`do_update` issues no refund to any proposer. The `UpdateEntry` struct stores `bytes_used` but that field is never read back to compute a refund: [4](#0-3) 

The deposit calculation shows the magnitude: for a 1.5 MB contract binary the required deposit is on the order of 15–40 NEAR per proposal: [5](#0-4) 

There is no `withdraw_proposal`, `cancel_proposal`, or any other function that returns a proposer's deposit. The only public removal path is `remove_update_vote`, which removes a *vote* but leaves the entry (and its locked deposit) intact: [6](#0-5) 

### Impact Explanation

Every participant who calls `propose_update` with a contract binary loses their deposit permanently the moment any other proposal reaches threshold. In a network with N participants each proposing a different upgrade candidate (a normal governance scenario), N−1 deposits are irrecoverably locked. For a 1.5 MB binary the deposit floor is ~15–40 NEAR per proposal. This is a direct, permanent loss of funds controlled by the MPC contract with no recovery path — matching the **Medium** impact class: *balance/accounting invariant broken without relying on network-level DoS or operator misconfiguration*.

### Likelihood Explanation

The trigger is ordinary governance activity. Any epoch where participants disagree on which binary to adopt (each proposing their own candidate) will silently destroy all losing proposers' deposits. The `test_propose_update_contract_many` sandbox test already demonstrates multiple simultaneous proposals existing; it does not check whether deposits are returned after the winning proposal executes. [7](#0-6) 

### Recommendation

1. Record the proposer's account ID and the exact deposit amount inside `UpdateEntry`.
2. In `do_update`, before calling `self.entries.clear()`, iterate over all remaining entries and issue a `Promise::new(entry.proposer).transfer(entry.deposit)` for each one.
3. Alternatively, add a `cancel_proposal(id)` function callable by the original proposer that removes the entry and refunds the deposit.
4. Ensure the winning proposer's deposit is also refunded after the storage is freed.

### Proof of Concept

1. Participant A calls `propose_update` with a 1 MB binary, attaching 15 NEAR. Contract stores entry `id=0`, keeps 15 NEAR.
2. Participant B calls `propose_update` with a different 1 MB binary, attaching 15 NEAR. Contract stores entry `id=1`, keeps 15 NEAR.
3. Threshold participants vote for `id=0`. `vote_update` calls `do_update(&id=0, ...)`.
4. `do_update` removes entry 0, then calls `self.entries.clear()` — entry 1 (B's proposal) is deleted with no refund.
5. Participant B's 15 NEAR is permanently locked in the contract. There is no function to recover it. [3](#0-2) [8](#0-7)

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

**File:** crates/contract/src/lib.rs (L1395-1404)
```rust
    /// Removes an update vote by the caller
    /// panics if the contract is not in a running state or if the caller is not a participant
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

**File:** crates/contract/src/update.rs (L195-200)
```rust
    pub fn do_update(&mut self, id: &UpdateId, gas: Gas) -> Option<Promise> {
        let entry = self.entries.remove(id)?;

        // Clear all entries as they might be no longer valid
        self.entries.clear();
        self.vote_by_participant.clear();
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

**File:** crates/contract/tests/sandbox/upgrade_from_current_contract.rs (L247-299)
```rust
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
```
