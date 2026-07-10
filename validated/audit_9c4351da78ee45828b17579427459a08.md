### Title
Attached Deposit Permanently Stuck in Contract When Existing Participant Updates Attestation - (File: crates/contract/src/lib.rs)

### Summary

`submit_participant_info` is marked `#[payable]`, so it accepts an attached NEAR deposit from any caller. However, the refund path is gated behind a condition that is `false` for existing participants performing an attestation update. Any deposit attached in that scenario is silently absorbed by the contract with no refund issued.

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
    // ... cost check and refund logic ...
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
``` [1](#0-0) 

When an **existing participant** (already in the participant set, so `caller_is_not_participant = false`) calls the function to **renew or update** their attestation, `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant`, making `is_new_attestation = false`. [2](#0-1) 

Both conditions are `false`, so `attestation_storage_must_be_paid_by_caller = false`, and the entire `if` block — including the refund — is skipped. Any NEAR tokens attached to the call are permanently retained by the contract. [3](#0-2) 

The function is declared `#[payable]` with no unconditional refund guard outside the conditional block, unlike the `sign` and `request_app_private_key` paths which call `require_deposit` unconditionally and always refund excess. [4](#0-3) 

### Impact Explanation

Any NEAR tokens attached by an existing participant during an attestation renewal are permanently locked in the MPC contract. There is no administrative withdrawal path. This is a direct, permanent loss of user funds that breaks the deposit-accounting invariant: the contract accepts value it has no right to keep and provides no mechanism to recover it.

This maps to: **Medium — balance/accounting invariant broken without relying on network-level DoS or operator misconfiguration.**

### Likelihood Explanation

Attestation renewal is a routine, recurring operation. Participants must re-submit when their TEE certificate expires or when a new allowed MPC image is deployed. The function is marked `#[payable]`, which signals to callers (and tooling) that a deposit is expected. A participant who attaches even 1 yoctoNEAR (a common pattern to satisfy full-access-key requirements) during a renewal will lose that deposit. The scenario requires no special privileges — any current participant triggers it on every routine attestation update.

### Recommendation

Add an unconditional refund of any excess deposit at the top of `submit_participant_info`, mirroring the `require_deposit` helper used by `sign` and `request_app_private_key`. The simplest fix is to call `require_deposit(NearToken::from_yoctonear(0), &account_id)` before the conditional block, which refunds the full attached amount when no storage cost is owed, and refunds the excess when storage cost is owed. [5](#0-4) 

### Proof of Concept

1. Participant `alice.near` has previously called `submit_participant_info` and is a current protocol participant.
2. Alice's TEE certificate expires; she must renew by calling `submit_participant_info` again.
3. Alice attaches `1 NEAR` to the call (e.g., following documentation that says a deposit is required, or because her tooling always attaches a deposit).
4. Inside the function:
   - `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant` (existing TLS key overwritten). [6](#0-5) 
   - `is_new_attestation = false`, `caller_is_not_participant = false`.
   - `attestation_storage_must_be_paid_by_caller = false`.
   - The `if` block is skipped entirely; no refund is issued. [7](#0-6) 
5. The call succeeds (`Ok(())`), the attestation is updated, and Alice's `1 NEAR` is permanently locked in the MPC contract.

### Citations

**File:** crates/contract/src/lib.rs (L122-141)
```rust
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
