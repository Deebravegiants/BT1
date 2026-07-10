### Title
Excess Deposit Not Refunded in `submit_participant_info` When Caller Is an Existing Participant — (File: `crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is a `#[payable]` function that conditionally handles deposit refunds. When an existing participant re-submits their attestation (an update, not a new insertion), the branch that checks and refunds the deposit is skipped entirely. Any NEAR attached by the caller is silently retained by the contract, breaking the accounting invariant that excess deposits must be returned to callers.

---

### Finding Description

`submit_participant_info` (lines 756–852) computes whether the caller must pay for storage:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... compute cost, check deposit >= cost, refund excess ...
}
``` [1](#0-0) 

When `attestation_storage_must_be_paid_by_caller` evaluates to `false` — i.e., the caller **is** an existing participant **and** the submission is an update (not a new insertion) — the entire deposit-handling block is bypassed. The function returns `Ok(())` without issuing any refund. Because the function is marked `#[payable]`, any NEAR attached to the call is accepted and permanently retained by the contract.

Compare this with the analogous pattern in `propose_update` (lines 1326–1331) and `require_deposit` (lines 134–138), both of which unconditionally refund any excess deposit:

```rust
if let Some(diff) = attached.checked_sub(required)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(proposer).transfer(diff).detach();
}
``` [2](#0-1) 

No equivalent refund path exists in `submit_participant_info` for the `!attestation_storage_must_be_paid_by_caller` branch. [3](#0-2) 

---

### Impact Explanation

The contract accumulates NEAR that belongs to callers. Participants periodically re-submit attestations (e.g., to refresh an expiring TEE quote before the `tee_upgrade_deadline_duration` elapses). Any deposit attached during such a re-submission — even 1 yoctonear, which is the standard minimum for `#[payable]` calls — is silently forfeited. Over many participants and many re-submission cycles this constitutes a systematic, irreversible drain of participant funds into the contract with no recovery path. This breaks the production accounting invariant that `#[payable]` functions must refund unused deposits.

**Impact class:** Medium — balance/accounting invariant violation causing direct, permanent fund loss for participants, with no reliance on network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

Participants must re-submit attestations regularly as TEE quotes expire. The function is `#[payable]`, which by NEAR convention signals that a deposit is expected; callers routinely attach at least 1 yoctonear. Node automation scripts that always attach a small deposit (as is standard practice) will silently lose that deposit on every re-submission. The trigger condition (`is_existing_participant && !is_new_attestation`) is the normal steady-state path for any node that has already registered once.

---

### Recommendation

Add an unconditional refund of any attached deposit in the `else` branch (or after the `if` block) so that callers who are not required to pay storage always receive their deposit back:

```rust
} else {
    // Caller is an existing participant updating their attestation;
    // no storage cost is owed — refund the full attached deposit.
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

Alternatively, restructure the deposit logic to always call a helper analogous to `require_deposit` that refunds any amount above the computed cost (which is zero in this branch).

---

### Proof of Concept

1. Deploy the contract and initialize it with participant `alice`.
2. `alice` calls `submit_participant_info` a second time (re-submission / attestation refresh) and attaches `NearToken::from_yoctonear(100)`.
3. Because `alice` is already a participant (`voter_account()` succeeds → `caller_is_not_participant = false`) and the insertion result is `UpdatedExistingParticipant` (`is_new_attestation = false`), `attestation_storage_must_be_paid_by_caller` is `false`.
4. The deposit-handling `if` block is skipped entirely.
5. The function returns `Ok(())`. `alice`'s balance is reduced by 100 yoctonear; the contract balance increases by 100 yoctonear. No refund promise is ever scheduled.
6. The 100 yoctonear is permanently locked in the contract with no withdrawal mechanism. [4](#0-3)

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

**File:** crates/contract/src/lib.rs (L1326-1331)
```rust
        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```
