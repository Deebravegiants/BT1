Now I have a complete picture. Let me verify the node-side deposit attachment behavior for `submit_participant_info`.

### Title
Excess Deposit Permanently Locked in Contract on Existing-Participant Attestation Update — (`File: crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is a `#[payable]` function. Its deposit-handling block is guarded by `attestation_storage_must_be_paid_by_caller`. When an existing, active participant re-submits their attestation (e.g., for a TEE upgrade), that flag evaluates to `false` and the entire deposit-handling block — including the refund path — is skipped. Any NEAR tokens attached to the call are silently absorbed by the contract with no refund, breaking on-chain accounting invariants.

---

### Finding Description

In `crates/contract/src/lib.rs`, `submit_participant_info` is declared `#[payable]`: [1](#0-0) 

After `add_participant` succeeds, the contract computes a guard flag: [2](#0-1) 

The flag is `true` only when the insertion is brand-new **or** the caller is not yet a governance participant. When an existing, active participant updates their attestation, `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant`: [3](#0-2) 

…making `is_new_attestation = false` and `caller_is_not_participant = false`, so `attestation_storage_must_be_paid_by_caller = false`. The entire deposit block — including the refund — is skipped: [4](#0-3) 

The function returns `Ok(())` and any attached deposit remains in the contract permanently. The inline comment explains only the *freed-bytes* asymmetry, not the missing unconditional refund for the update path: [5](#0-4) 

Compare with the correct pattern used in `propose_update`, which always refunds excess regardless of branch: [6](#0-5) 

---

### Impact Explanation

Any NEAR tokens attached to an attestation-update call by an existing participant are permanently locked in the MPC contract. Because the contract is the custodian of the MPC network's on-chain balance (storage deposits, fee tokens, etc.), silently accumulating unaccounted NEAR breaks the production safety/accounting invariant that only intentional storage deposits should reside in the contract. This matches the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

The node software calls `submit_participant_info` automatically on startup and during TEE upgrades. The sandbox helper does not attach a deposit, and no explicit deposit is set in the node-side call path (`crates/node/src/tee/remote_attestation.rs`). However:

1. The function is publicly `#[payable]` — any caller (including a misconfigured node, an operator script, or a future SDK integration) may attach tokens.
2. TEE upgrades are a routine, recurring operation; every upgrade cycle is a new exposure window.
3. The NEAR SDK's default behavior for `#[payable]` functions is to accept whatever is attached; there is no guard that rejects a non-zero deposit on the update path.

Likelihood is **Low** (most automated calls attach zero), but the path is fully reachable by an unprivileged participant with no collusion required.

---

### Recommendation

Add an unconditional refund for any attached deposit when `attestation_storage_must_be_paid_by_caller` is `false`, mirroring the pattern already used in `propose_update`:

```rust
// After the if-block, always refund any deposit not consumed by storage:
let attached = env::attached_deposit();
if attached > NearToken::from_yoctonear(0) {
    Promise::new(account_id).transfer(attached).detach();
}
```

Alternatively, add a `#[deposit(0)]` guard (or an explicit `assert!(env::attached_deposit() == 0)`) on the update branch to reject non-zero deposits outright, making the accounting invariant impossible to violate.

---

### Proof of Concept

1. Deploy the contract with one active participant (`alice.near`).
2. `alice.near` calls `submit_participant_info` with a valid updated attestation and attaches `1 NEAR`.
3. `add_participant` returns `UpdatedExistingParticipant`; `voter_account()` succeeds for `alice.near`.
4. `attestation_storage_must_be_paid_by_caller = false || false = false`.
5. The deposit block is skipped; `Ok(())` is returned.
6. `alice.near`'s balance decreases by `1 NEAR`; the contract balance increases by `1 NEAR` with no corresponding state entry tracking it.
7. The `1 NEAR` is permanently locked — no withdrawal mechanism exists for untracked contract balance.

### Citations

**File:** crates/contract/src/lib.rs (L756-760)
```rust
    /// (Prospective) Participants can submit their tee participant information through this
    /// endpoint.
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-824)
```rust
        let caller_is_not_participant = self.voter_account().is_err();
        let is_new_attestation = matches!(
            attestation_insertion_result,
            ParticipantInsertion::NewlyInsertedParticipant
        );

        let attestation_storage_must_be_paid_by_caller =
            is_new_attestation || caller_is_not_participant;
```

**File:** crates/contract/src/lib.rs (L826-851)
```rust
        if attestation_storage_must_be_paid_by_caller {
            // `saturating_sub`: if a re-submission shrinks the entry, charge nothing
            // rather than underflow. Intentional asymmetry: we do not refund freed bytes
            // either — the caller already paid for the larger entry, and we'd rather
            // accept that asymmetry than open a refund path for payload-shrinking games.
            let storage_used = env::storage_usage().saturating_sub(initial_storage);
            let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
            let attached = env::attached_deposit();

            if attached < cost {
                return Err(InvalidParameters::InsufficientDeposit {
                    attached: attached.as_yoctonear(),
                    required: cost.as_yoctonear(),
                }
                .into());
            }

            // Refund the difference if the proposer attached more than required
            if let Some(diff) = attached.checked_sub(cost)
                && diff > NearToken::from_yoctonear(0)
            {
                Promise::new(account_id).transfer(diff).detach();
            }
        }

        Ok(())
```

**File:** crates/contract/src/lib.rs (L1326-1331)
```rust
        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```

**File:** crates/contract/src/tee/tee_state.rs (L199-202)
```rust
        Ok(match insertion {
            Some(_previous_attestation) => ParticipantInsertion::UpdatedExistingParticipant,
            None => ParticipantInsertion::NewlyInsertedParticipant,
        })
```
