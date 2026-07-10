### Title
Missing Deposit Refund in `submit_participant_info` for Existing-Participant Re-attestation Path - (File: crates/contract/src/lib.rs)

### Summary
`submit_participant_info` is a `#[payable]` function that conditionally handles deposit refunds. When an existing participant re-submits their attestation (the `UpdatedExistingParticipant` path), the deposit-check-and-refund block is entirely skipped. Any NEAR attached to such a call is permanently locked in the contract with no recovery mechanism.

### Finding Description
In `submit_participant_info`, the deposit handling is gated on a boolean:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... check deposit, refund excess ...
}
// else: silent return, attached deposit is never refunded
```

`is_new_attestation` is `true` only when `add_participant` returns `ParticipantInsertion::NewlyInsertedParticipant`. When the same participant re-submits (e.g., after a TEE upgrade or key rotation), `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant`, so `is_new_attestation = false`. If the caller is already a participant, `caller_is_not_participant = false` as well. The combined condition is `false`, the `if` block is skipped, and any attached deposit is silently consumed by the contract.

The two variants of `ParticipantInsertion` are: [1](#0-0) 

`add_participant` returns `UpdatedExistingParticipant` whenever the TLS key already exists in `stored_attestations`: [2](#0-1) 

Back in `lib.rs`, the deposit branch is only entered when `attestation_storage_must_be_paid_by_caller` is `true`: [3](#0-2) 

The function is declared `#[payable]`, so NEAR can be attached freely: [4](#0-3) 

Every other payable function in the contract (`sign`, `request_app_private_key`, `verify_foreign_transaction`, `propose_update`) unconditionally refunds excess deposits. The `require_deposit` helper explicitly documents this invariant: [5](#0-4) 

### Impact Explanation
Any NEAR attached to a re-attestation call by an existing participant is permanently locked in the contract. There is no withdrawal or sweep function. The contract's own accounting invariant — that excess deposits are always refunded — is violated for this specific code path. This constitutes a permanent freezing of caller-owned funds within the chain-signature contract.

**Impact: Medium** — balance/accounting invariant broken; funds permanently locked without network-level DoS or operator misconfiguration.

### Likelihood Explanation
Re-attestation is a routine, expected operation (TEE upgrades, key rotations). The function is `#[payable]`, so attaching a deposit is syntactically valid and easy to do accidentally (e.g., copy-pasting a CLI command that included a deposit for the initial registration). The vulnerable path (`UpdatedExistingParticipant` + caller is participant) is the normal steady-state path for any long-running node.

### Recommendation
Add an unconditional deposit refund for the case where `attestation_storage_must_be_paid_by_caller` is `false`. The simplest fix mirrors the pattern already used in `require_deposit`:

```rust
} else {
    // Existing participant re-submitting: no storage cost, refund any deposit.
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

Alternatively, assert `env::attached_deposit() == 0` in this branch to make the invariant explicit and fail fast.

### Proof of Concept
1. Participant `alice.near` calls `submit_participant_info` for the first time with a valid attestation and 1 NEAR deposit. `add_participant` returns `NewlyInsertedParticipant`; `is_new_attestation = true`; deposit check runs; excess is refunded. ✓
2. Alice's TEE certificate expires. She calls `submit_participant_info` again with a refreshed attestation and accidentally attaches 1 NEAR. `add_participant` returns `UpdatedExistingParticipant`; `is_new_attestation = false`; `caller_is_not_participant = false` (she is a participant); `attestation_storage_must_be_paid_by_caller = false`; the `if` block is skipped; the function returns `Ok(())`; the 1 NEAR is permanently locked in the contract. [6](#0-5)

### Citations

**File:** crates/contract/src/tee/tee_state.rs (L46-50)
```rust
#[derive(Debug)]
pub(crate) enum ParticipantInsertion {
    NewlyInsertedParticipant,
    UpdatedExistingParticipant,
}
```

**File:** crates/contract/src/tee/tee_state.rs (L191-202)
```rust
        let insertion = self.stored_attestations.insert(
            tls_pk,
            NodeAttestation {
                node_id,
                verified_attestation,
            },
        );

        Ok(match insertion {
            Some(_previous_attestation) => ParticipantInsertion::UpdatedExistingParticipant,
            None => ParticipantInsertion::NewlyInsertedParticipant,
        })
```

**File:** crates/contract/src/lib.rs (L110-141)
```rust
/// Checks that the caller attached at least `minimum_deposit` and refunds any excess.
///
/// A non-zero deposit is required so that the transaction must be signed by a
/// full-access key (or a function-call access key whose `deposit` allowance is
/// explicitly set). This prevents a **malicious frontend** from silently
/// submitting signature requests on behalf of a user via a restricted
/// function-call access key, because such keys cannot attach deposits by
/// default. In other words, requiring a deposit ensures the user (or their
/// full-access key) explicitly authorised the call.
///
/// See the "Deposit requirement" section in the contract README for more
/// details.
fn require_deposit(minimum_deposit: NearToken, predecessor: &AccountId) {
    let deposit = env::attached_deposit();
    match deposit.checked_sub(minimum_deposit) {
        None => {
            env::panic_str(
                &InvalidParameters::InsufficientDeposit {
                    attached: deposit.as_yoctonear(),
                    required: minimum_deposit.as_yoctonear(),
                }
                .to_string(),
            );
        }
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
        }
    }
}
```

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
