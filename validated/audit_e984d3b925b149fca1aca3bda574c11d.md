### Title
Existing-Participant Deposit Silently Retained in `submit_participant_info` — (File: crates/contract/src/lib.rs)

---

### Summary

`submit_participant_info` is marked `#[payable]` and therefore accepts an arbitrary NEAR deposit from any caller. However, the deposit-check-and-refund block is guarded by a condition that is `false` for existing participants performing an attestation update. Any deposit attached in that code path is permanently transferred to the contract with no refund path.

---

### Finding Description

The function computes a guard flag:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [1](#0-0) 

The refund logic is only executed when that flag is `true`:

```rust
if attestation_storage_must_be_paid_by_caller {
    let storage_used = env::storage_usage().saturating_sub(initial_storage);
    let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
    let attached = env::attached_deposit();
    ...
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
``` [2](#0-1) 

When an **existing participant** re-submits their attestation (e.g., to rotate their TLS key or refresh their TEE quote), both `is_new_attestation` and `caller_is_not_participant` are `false`. The flag is `false`, the entire block is skipped, and `env::attached_deposit()` is never inspected or returned. There is no `else` branch and no unconditional refund.

The function signature is:

```rust
#[payable]
#[handle_result]
pub fn submit_participant_info(
    &mut self,
    proposed_participant_attestation: dtos::Attestation,
    tls_public_key: dtos::Ed25519PublicKey,
) -> Result<(), Error> {
```

<cite repo="Linkmegit/mpc--015" path="crates/contract/src/

### Citations

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

**File:** crates/contract/src/lib.rs (L826-849)
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
```
