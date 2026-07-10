### Title
Excess Deposit Not Refunded in `submit_participant_info` Re-submission Path - (File: crates/contract/src/lib.rs)

### Summary
The `submit_participant_info` function is `#[payable]` and accepts any attached deposit, but only executes refund logic when `attestation_storage_must_be_paid_by_caller` is `true`. When an existing participant re-submits their attestation (the normal periodic re-attestation flow), this condition is `false` and any excess deposit is silently retained by the contract with no refund issued.

### Finding Description
In `submit_participant_info`, the deposit-handling block is guarded by a boolean: [1](#0-0) 

`attestation_storage_must_be_paid_by_caller` is `true` only when `is_new_attestation || caller_is_not_participant`. When an existing, already-attested participant re-submits (the routine periodic re-attestation path), both conditions are `false`, so the entire block — including the excess-refund branch — is skipped entirely: [2](#0-1) 

Because the function is declared `#[payable]`, the NEAR runtime accepts any deposit amount without restriction. Any NEAR attached beyond zero in this code path is permanently absorbed by the contract with no mechanism to recover it.

This is structurally identical to the reported Solidity pattern: one entry point (`submit_participant_info` re-submission) silently keeps excess value while the analogous new-participant path correctly refunds it.

### Impact Explanation
Any NEAR tokens attached by a participant node during a routine re-attestation call are permanently locked in the MPC contract. Because MPC nodes re-submit attestations on a recurring schedule (driven by `attestation-resubmission-interval` in the node), a misconfigured or buggy node client that attaches a non-zero deposit on re-submission will lose those funds irreversibly. The contract has no admin withdrawal path for such stranded deposits, so the funds are permanently frozen — matching the "permanent freezing of funds" criterion at the Medium level (balance/accounting invariant broken without requiring DoS or operator collusion).

### Likelihood Explanation
MPC nodes periodically re-submit attestations automatically. Any node software bug, configuration error, or future API change that causes a non-zero deposit to be attached on re-submission will silently strand funds. The call path is reachable by any existing participant without any privileged access.

### Recommendation
Add an unconditional excess-refund step that runs regardless of the `attestation_storage_must_be_paid_by_caller` branch, mirroring the pattern used in `require_deposit`:

```rust
// After the conditional storage-cost block:
let attached = env::attached_deposit();
let cost_charged = if attestation_storage_must_be_paid_by_caller { cost } else { NearToken::from_yoctonear(0) };
if let Some(diff) = attached.checked_sub(cost_charged)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

Alternatively, restructure the function to call `require_deposit(NearToken::from_yoctonear(0), &account_id)` unconditionally so the shared helper always handles the refund.

### Proof of Concept
1. Deploy the MPC contract with one participant already registered (existing attestation stored).
2. Call `submit_participant_info` from that participant's account, attaching `1 NEAR` as deposit.
3. Observe: `attestation_insertion_result` is `ParticipantInsertion::UpdatedExistingParticipant` (not `NewlyInsertedParticipant`), so `is_new_attestation = false`.
4. `caller_is_not_participant = false` because `self.voter_account()` succeeds.
5. `attestation_storage_must_be_paid_by_caller = false` → the entire deposit block is skipped.
6. The call succeeds, the attestation is updated, and the `1 NEAR` deposit is permanently retained by the contract with no refund promise issued. [3](#0-2)

### Citations

**File:** crates/contract/src/lib.rs (L756-852)
```rust
    /// (Prospective) Participants can submit their tee participant information through this
    /// endpoint.
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
        &mut self,
        proposed_participant_attestation: dtos::Attestation,
        tls_public_key: dtos::Ed25519PublicKey,
    ) -> Result<(), Error> {
        let proposed_participant_attestation =
            proposed_participant_attestation.try_into_contract_type()?;

        let account_key = env::signer_account_pk();
        let account_id = Self::assert_caller_is_signer();

        log!(
            "submit_participant_info: signer={}, proposed_participant_attestation={:?}, account_key={:?}",
            account_id,
            proposed_participant_attestation,
            account_key
        );

        // Save the initial storage usage to know how much to charge the proposer for the storage
        // used
        let initial_storage = env::storage_usage();

        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        // The node always signs submissions with an Ed25519 key
        // (`near_signer_key`), so the signer key here is Ed25519 in practice.
        // Reject non-Ed25519 signer keys rather than silently storing a value
        // we could never match against in `is_caller_an_attested_participant`.
        let account_public_key = dtos::Ed25519PublicKey::try_from(&account_key).map_err(|_| {
            InvalidParameters::InvalidTeeRemoteAttestation {
                reason: "signer account key must be Ed25519".to_string(),
            }
        })?;

        // Add the participant information to the contract state
        let attestation_insertion_result = self
            .tee_state
            .add_participant(
                NodeId {
                    account_id: account_id.clone(),
                    tls_public_key,
                    account_public_key,
                },
                proposed_participant_attestation,
                tee_upgrade_deadline_duration,
            )
            .map_err(|err| {
                let reason = match &err {
                    AttestationSubmissionError::InvalidAttestation(_) => {
                        format!("TeeQuoteStatus is invalid: {err}")
                    }
                    AttestationSubmissionError::TlsKeyOwnedByOtherAccount => err.to_string(),
                };
                InvalidParameters::InvalidTeeRemoteAttestation { reason }
            })?;

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
    }
```
