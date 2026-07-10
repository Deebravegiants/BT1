### Title
Attached Deposit Not Refunded on Existing-Participant Re-Attestation - (`crates/contract/src/lib.rs`)

### Summary

`submit_participant_info` is `#[payable]` and accepts an attached NEAR deposit, but the refund branch is gated behind a condition that is `false` for existing participants performing a periodic re-submission. Any deposit attached in that case is permanently locked in the contract with no recovery path.

### Finding Description

`submit_participant_info` computes a boolean flag to decide whether to charge and refund the caller:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... storage cost check and refund of excess ...
}
``` [1](#0-0) 

When the caller is an **existing participant** re-submitting an updated attestation (`is_new_attestation = false`, `caller_is_not_participant = false`), the entire `if` block is skipped. The function returns `Ok(())` without issuing any refund promise. Any NEAR attached to the call is silently absorbed by the contract.

The function is declared `#[payable]`, so the NEAR runtime accepts the deposit without complaint: [2](#0-1) 

The node re-submits attestations on a periodic cadence and on attestation-removal events. Unit tests consistently attach `NearToken::from_near(1)` when calling this method: [3](#0-2) 

The `add_participant` function confirms that re-submissions by the same account return `UpdatedExistingParticipant`, not `NewlyInsertedParticipant`: [4](#0-3) 

### Impact Explanation

Any NEAR deposit attached to a re-submission call by an existing participant is permanently locked in the contract. There is no `refundETH`-style withdrawal function, so the funds cannot be recovered. Over the node's 1-hour re-submission cadence, this accumulates silently. This breaks the production accounting invariant that `#[payable]` methods must refund excess deposits to callers.

**Impact class:** Medium — balance/accounting invariant violation that permanently locks caller funds without any network-level DoS or operator misconfiguration required.

### Likelihood Explanation

The node's `periodic_attestation_submission` task re-submits on a fixed cadence. If the node attaches any non-zero deposit (as all unit tests do), every re-submission by every existing participant silently loses that deposit. The trigger is a normal, expected production operation, not an adversarial edge case.

### Recommendation

Add an `else` branch that refunds the full attached deposit when `attestation_storage_must_be_paid_by_caller` is `false`:

```rust
if attestation_storage_must_be_paid_by_caller {
    // existing storage-cost check and partial refund
} else {
    // storage already paid; refund the entire deposit
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

Alternatively, enforce that `submit_participant_info` requires zero deposit for re-submissions by rejecting any non-zero deposit when `!attestation_storage_must_be_paid_by_caller`.

### Proof of Concept

1. Alice is an existing participant. Her attestation is already stored.
2. Alice's node re-submits via `submit_participant_info` with `attached_deposit = 1 NEAR` (matching the unit-test pattern).
3. `add_participant` returns `UpdatedExistingParticipant` → `is_new_attestation = false`.
4. `voter_account()` succeeds for Alice → `caller_is_not_participant = false`.
5. `attestation_storage_must_be_paid_by_caller = false || false = false`.
6. The `if` block is skipped entirely; `Ok(())` is returned.
7. Alice's 1 NEAR is now held by the contract with no refund path.
8. This repeats every ~1 hour per participant for the lifetime of the network. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L3993-3997)
```rust
        let participant_context = VMContextBuilder::new()
            .signer_account_id(account_id.clone())
            .predecessor_account_id(account_id.clone())
            .attached_deposit(NearToken::from_near(1))
            .build();
```

**File:** crates/contract/src/tee/tee_state.rs (L1453-1454)
```rust
        // Then: the update is accepted and the stored entry reflects the new key.
        assert_matches!(result, Ok(ParticipantInsertion::UpdatedExistingParticipant));
```
