### Title
Existing Participants Can Grow Attestation Storage Without Paying — (`crates/contract/src/lib.rs`)

---

### Summary

In `submit_participant_info`, the storage-cost check is gated by a condition that evaluates to `false` for any caller who is already a protocol participant and is updating (not newly inserting) their attestation. When such a caller submits a larger attestation than the one previously stored, the contract absorbs the additional storage cost with no deposit required from the caller, breaking the storage-accounting invariant.

---

### Finding Description

`submit_participant_info` (lib.rs:756–852) follows this sequence:

1. Snapshot storage before the write: `let initial_storage = env::storage_usage();` [1](#0-0) 

2. Call `tee_state.add_participant(...)`, which unconditionally overwrites the existing `stored_attestations` entry with the new (potentially larger) `NodeAttestation`: [2](#0-1) 

3. Determine whether to charge the caller:
```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [3](#0-2) 

4. The storage-cost check — including the `env::storage_usage().saturating_sub(initial_storage)` delta calculation — is **only executed** when `attestation_storage_must_be_paid_by_caller` is `true`: [4](#0-3) 

When the caller is an **existing protocol participant** (`voter_account()` succeeds → `caller_is_not_participant = false`) and the attestation is an **update** (`add_participant` returns `UpdatedExistingParticipant` → `is_new_attestation = false`), both conditions are `false`, so `attestation_storage_must_be_paid_by_caller = false` and the entire storage-cost block is skipped.

`voter_account()` authenticates against the live protocol participant set via `self.protocol_state.authenticate_update_vote()`: [5](#0-4) 

The analog to the external report is direct: just as the pump-science fee was computed on `exact_in_amount` before `apply_buy` changed the actual SOL amount (making the fee incorrect for the "last buy" edge case), here the storage-cost accounting is bypassed for the "existing-participant update" case, where the actual storage delta can be positive.

---

### Impact Explanation

NEAR charges storage costs against the contract's own balance. When an existing participant submits a larger attestation (e.g., a TEE quote with a longer certificate chain), the contract's storage deposit is reduced without any compensating deposit from the caller. Repeated updates with growing payloads drain the contract's storage reserve. If the contract's storage deposit falls below the required minimum, NEAR will prevent further state writes — blocking new attestation submissions, pending signature requests, and governance votes — effectively freezing the MPC network's on-chain coordination layer.

This breaks the production safety/accounting invariant that callers must cover the storage they consume.

---

### Likelihood Explanation

Any existing protocol participant can trigger this. TEE attestation quotes are variable in size: they embed X.509 certificate chains whose length depends on the issuing CA hierarchy. A participant can legitimately re-submit with a quote that includes a longer chain (e.g., after a certificate rotation), or craft a submission that maximises the certificate payload within the bounds accepted by `verify_locally`. No collusion, privileged access, or network-level attack is required — only a valid participant account and a valid (but larger) attestation.

---

### Recommendation

Remove the `attestation_storage_must_be_paid_by_caller` gate and always execute the storage-cost check. When an update shrinks the entry, `env::storage_usage().saturating_sub(initial_storage)` yields `0` (due to `saturating_sub`), so no charge is applied — the existing asymmetry comment already documents this intent. When an update grows the entry, the caller is charged for the delta. This correctly handles all four cases (new/update × participant/non-participant) without special-casing.

---

### Proof of Concept

1. Alice is an active protocol participant with a stored attestation of serialized size **N** bytes.
2. Alice calls `submit_participant_info` with a new valid attestation of size **N + K** bytes (K > 0, e.g., a longer certificate chain).
3. `add_participant` overwrites Alice's entry, increasing `env::storage_usage()` by K bytes. It returns `UpdatedExistingParticipant`.
4. `is_new_attestation = false`; `voter_account()` succeeds for Alice → `caller_is_not_participant = false`.
5. `attestation_storage_must_be_paid_by_caller = false || false = false`.
6. The storage-cost block is skipped entirely. Alice's call succeeds with **zero deposit**.
7. The contract's storage deposit is reduced by `K × env::storage_byte_cost()` with no compensation.
8. Repeating this with progressively larger attestations drains the contract's storage reserve, eventually preventing any further state writes. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L780-780)
```rust
        let initial_storage = env::storage_usage();
```

**File:** crates/contract/src/lib.rs (L796-824)
```rust
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

**File:** crates/contract/src/lib.rs (L2352-2359)
```rust
    fn voter_account(&self) -> Result<AccountId, Error> {
        if !Self::caller_is_signer() {
            return Err(InvalidParameters::CallerNotSigner.into());
        }
        let voter = env::signer_account_id();
        self.protocol_state.authenticate_update_vote()?;
        Ok(voter)
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L151-202)
```rust
    pub(crate) fn add_participant(
        &mut self,
        node_id: NodeId,
        attestation: Attestation,
        tee_upgrade_deadline_duration: Duration,
    ) -> Result<ParticipantInsertion, AttestationSubmissionError> {
        let expected_report_data: ReportData = ReportDataV1::new(
            *node_id.tls_public_key.as_bytes(),
            *node_id.account_public_key.as_bytes(),
        )
        .into();

        let accepted_measurements = self.get_accepted_measurements();
        // TODO(#3264): run DCAP in the verifier contract (Promise + callback) and
        // do the post-DCAP checks here, instead of verifying locally in-WASM.
        let AcceptedAttestation {
            attestation: verified_attestation,
            advisory_ids,
        } = attestation.verify_locally(
            expected_report_data.into(),
            Self::current_time_seconds(),
            &self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration),
            &self.get_allowed_launcher_compose_hashes(),
            &accepted_measurements,
        )?;

        log_informational_advisory_ids(&advisory_ids);

        let tls_pk = node_id.tls_public_key.clone();

        // Authorization: a TLS key registered to one account must not be
        // overwritten by a submission from a different account. Without this,
        // any caller could replace any participant's stored attestation, since
        // the entry is keyed only by `tls_public_key`.
        if let Some(existing) = self.stored_attestations.get(&tls_pk)
            && existing.node_id.account_id != node_id.account_id
        {
            return Err(AttestationSubmissionError::TlsKeyOwnedByOtherAccount);
        }

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
