### Title
Attached NEAR deposit permanently locked in `MpcContract` when existing participant re-submits attestation - (File: crates/contract/src/lib.rs)

### Summary

`submit_participant_info` silently absorbs any attached NEAR deposit when an existing, already-attested participant re-submits their attestation. The deposit-handling block is guarded by `attestation_storage_must_be_paid_by_caller`, which evaluates to `false` for existing participants performing routine re-attestation. When that guard is `false`, the entire block — including the refund path — is skipped, and any attached deposit is permanently locked in the contract with no recovery mechanism.

### Finding Description

In `submit_participant_info`, after `add_participant` succeeds, the contract computes:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... storage cost check ...
    // Refund the difference if the proposer attached more than required
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
// ← No else branch: if false, attached deposit is silently consumed
``` [1](#0-0) 

When `attestation_storage_must_be_paid_by_caller` is `false` — i.e., the caller is already a recognized participant (`voter_account()` succeeds) **and** the insertion result is `UpdatedExistingParticipant` — the entire `if` block is bypassed. There is no `else` branch to refund the attached deposit. Any NEAR attached to the call is permanently locked in the contract.

The `add_participant` function in `tee_state.rs` returns `UpdatedExistingParticipant` whenever the same account re-submits a valid attestation for an already-registered TLS key:

```rust
Ok(match insertion {
    Some(_previous_attestation) => ParticipantInsertion::UpdatedExistingParticipant,
    None => ParticipantInsertion::NewlyInsertedParticipant,
})
``` [2](#0-1) 

This re-submission path is the **normal, expected, production operation**: the MPC node re-submits its attestation on a 1-hour cadence and on attestation-removal events. [3](#0-2) 

The function is `#[payable]`, so the NEAR runtime accepts any attached deposit without restriction. The contract's own README states that excess deposits are automatically refunded for `sign` and `request_app_private_key`, establishing a clear design intent that callers should not lose funds to the contract. [4](#0-3) 

### Impact Explanation

Any NEAR attached to a `submit_participant_info` call by an existing participant is permanently locked in the contract with no recovery path. The contract has no admin withdrawal function, no sweep mechanism, and no way for the caller to reclaim the deposit after the fact. This breaks the production accounting invariant that callers receive refunds for deposits exceeding the actual cost, and results in direct, permanent loss of the caller's NEAR tokens.

This maps to the **Medium** allowed impact: "Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."

### Likelihood Explanation

The MPC node's `periodic_attestation_submission` task attaches `0` by default for re-submissions, so automated node operation is not affected. However, the production documentation explicitly instructs operators to call `submit_participant_info` manually with `--deposit` for first-time joins. An operator who is already a participant but re-runs the manual command (e.g., after a key rotation, after being removed and re-added, or simply by mistake) will have their deposit permanently locked. The function is also callable by any external account, and the `#[payable]` attribute provides no guard against over-attachment.

### Recommendation

Add an `else` branch that refunds the full attached deposit when `attestation_storage_must_be_paid_by_caller` is `false`:

```rust
if attestation_storage_must_be_paid_by_caller {
    // existing storage cost check + partial refund
} else {
    // No storage cost for existing participants re-submitting:
    // refund the entire attached deposit.
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

Alternatively, consolidate the refund logic after the `if` block by computing the actual cost in both branches and always refunding `attached - cost`.

### Proof of Concept

1. Participant `alice.near` has already submitted a valid attestation and is a recognized voter (`voter_account()` returns `Ok`).
2. `alice.near` calls `submit_participant_info` again (routine hourly re-attestation) and attaches `1 NEAR` (e.g., an operator running the manual command without knowing the exact cost).
3. `add_participant` succeeds and returns `UpdatedExistingParticipant`.
4. `is_new_attestation = false`, `caller_is_not_participant = false` → `attestation_storage_must_be_paid_by_caller = false`.
5. The `if` block is skipped entirely. No refund is issued.
6. `alice.near` loses `1 NEAR` permanently to the contract. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-849)
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
```

**File:** crates/contract/src/tee/tee_state.rs (L199-202)
```rust
        Ok(match insertion {
            Some(_previous_attestation) => ParticipantInsertion::UpdatedExistingParticipant,
            None => ParticipantInsertion::NewlyInsertedParticipant,
        })
```

**File:** crates/contract/README.md (L57-57)
```markdown
Both `sign` and `request_app_private_key` require a **deposit of at least 1 yoctonear**. Any excess deposit is automatically refunded.
```
