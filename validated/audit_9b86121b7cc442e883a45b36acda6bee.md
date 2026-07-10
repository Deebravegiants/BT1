### Title
Deposit Not Refunded to Existing Participant on Attestation Re-Submission - (File: `crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is marked `#[payable]` and contains a deposit-refund path, but that path is gated behind a condition that is `false` for existing participants performing routine attestation renewals. Any deposit attached by an existing participant during a re-submission is silently consumed by the contract and never returned.

---

### Finding Description

`submit_participant_info` computes whether the caller must pay for storage:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... deposit check and refund of excess
}
``` [1](#0-0) 

When an **existing participant** re-submits their attestation (e.g., after a TEE firmware update), `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant`, so `is_new_attestation` is `false`. [2](#0-1) 

`caller_is_not_participant` is also `false` because the caller is already a participant. Therefore `attestation_storage_must_be_paid_by_caller` evaluates to `false`, the entire deposit-handling block is skipped, and any `attached_deposit` is permanently retained by the contract with no refund issued.

The function is declared `#[payable]`, so the NEAR runtime accepts any deposit without restriction: [3](#0-2) 

The comment in the code acknowledges an intentional asymmetry for freed storage bytes, but does not address the case where a deposit is attached for a re-submission at all: [4](#0-3) 

---

### Impact Explanation

MPC nodes are automated services that periodically re-submit attestations (e.g., after TEE firmware upgrades, which are a normal operational lifecycle event). The node software cannot always know in advance whether its submission will be treated as new or as an update; it may attach a deposit to ensure the transaction succeeds regardless. In the update path, that deposit is silently forfeited to the contract. Over many re-submissions across multiple participants, this constitutes a steady, unrecoverable drain of participant funds — a production accounting invariant break where a `#[payable]` function accepts value it never returns.

This maps to the **Medium** allowed impact: *balance or contract execution-flow manipulation that breaks production safety/accounting invariants*.

---

### Likelihood Explanation

TEE firmware updates are a routine operational event for every MPC node. The node software (`crates/node`) is responsible for calling `submit_participant_info` and determining the deposit amount. Because the contract's storage cost is only knowable after the call executes, a conservative node implementation will attach a deposit buffer. Every such re-submission by an existing participant silently loses that buffer. The condition is reachable by any participant without any privileged access or collusion.

---

### Recommendation

Move the refund logic outside the `attestation_storage_must_be_paid_by_caller` guard so that any excess deposit is always returned to the caller, regardless of whether storage payment was required:

```rust
let attached = env::attached_deposit();

if attestation_storage_must_be_paid_by_caller {
    let storage_used = env::storage_usage().saturating_sub(initial_storage);
    let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
    if attached < cost {
        return Err(...);
    }
    // refund only the storage-cost excess
    if let Some(diff) = attached.checked_sub(cost) && diff > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(diff).detach();
    }
} else if attached > NearToken::from_yoctonear(0) {
    // no storage cost required; refund the entire deposit
    Promise::new(account_id).transfer(attached).detach();
}
```

---

### Proof of Concept

1. Participant `alice.near` is already registered (first call returned `NewlyInsertedParticipant`).
2. Alice's TEE firmware is updated; her node calls `submit_participant_info` again, attaching `1_000_000_000_000_000_000_000_000` yoctoNEAR (1 NEAR) as a deposit buffer.
3. `add_participant` returns `UpdatedExistingParticipant` → `is_new_attestation = false`.
4. `voter_account()` succeeds → `caller_is_not_participant = false`.
5. `attestation_storage_must_be_paid_by_caller = false || false = false`.
6. The `if attestation_storage_must_be_paid_by_caller` block is skipped entirely.
7. The function returns `Ok(())`.
8. Alice's 1 NEAR deposit is permanently held by the contract; no `Promise::transfer` is ever issued. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-851)
```rust
        let caller_is_not_participant = self.voter_account().is_err();
        let is_new_attestation = matches!(
            attestation_insertion_result,
            ParticipantInsertion::NewlyInsertedParticipant
        );

        let attestation_storage_must_be_paid_by_caller =
            is_new_attestation || caller_is_not_participant;

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

**File:** crates/contract/src/tee/tee_state.rs (L199-202)
```rust
        Ok(match insertion {
            Some(_previous_attestation) => ParticipantInsertion::UpdatedExistingParticipant,
            None => ParticipantInsertion::NewlyInsertedParticipant,
        })
```
