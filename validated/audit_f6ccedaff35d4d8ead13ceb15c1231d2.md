### Title
Absence of Recency Check for `MockAttestation::Valid` Enables Permanent TEE Bypass by Any Participant - (File: crates/mpc-attestation/src/attestation.rs)

### Summary

`MockAttestation::Valid` carries no expiry timestamp and passes all re-verification checks unconditionally and indefinitely. Because `submit_participant_info` accepts `Attestation::Mock(MockAttestation::Valid)` in production with no guard, any participant can permanently bypass the TEE attestation requirement by submitting this variant, breaking the invariant that all signing participants must run in a verified Intel TDX enclave.

### Finding Description

The `Attestation` enum has two variants: `Dstack` (real TEE quote) and `Mock` (test/bypass). For `Dstack` attestations, `AcceptedAttestation::dstack()` stamps an `expiry_timestamp_seconds = current_timestamp_seconds + DEFAULT_EXPIRATION_DURATION_SECONDS` (currently 1 day): [1](#0-0) 

During periodic re-verification (`re_verify`), the `Dstack` branch checks `expiry_timestamp_seconds < timestamp_seconds` and rejects expired entries: [2](#0-1) 

For `MockAttestation::Valid`, however, `verify_constraints` returns `Ok(())` immediately with **no timestamp check**: [3](#0-2) 

And `AcceptedAttestation::mock()` stores the raw `MockAttestation` with **no expiry field**: [4](#0-3) 

When `re_verify` is called on a stored `VerifiedAttestation::Mock(MockAttestation::Valid)`, it delegates to `verify_constraints` which returns `Ok(())` unconditionally — the entry **never expires**: [5](#0-4) 

The production `submit_participant_info` method accepts `dtos::Attestation` (which includes the `Mock` variant) with no guard rejecting it in production: [6](#0-5) 

`add_participant` calls `attestation.verify_locally(...)` passing `Self::current_time_seconds()` — but for `MockAttestation::Valid` this timestamp is never used: [7](#0-6) 

The design documentation explicitly acknowledges `MockAttestation` remains in production code: *"Attestation::Mock stays in this iteration."* [8](#0-7) 

### Impact Explanation

The TEE attestation system exists to guarantee that all MPC participants run inside a genuine Intel TDX enclave, protecting key shares from exposure. A participant who submits `Attestation::Mock(MockAttestation::Valid)` to `submit_participant_info`:

1. Passes all verification checks (no timestamp, no DCAP quote, no measurements required).
2. Gets stored as `VerifiedAttestation::Mock(MockAttestation::Valid)` — an entry that **never expires** and always passes `re_verify`.
3. Maintains their TEE-attested status indefinitely, satisfying `assert_caller_is_attested_participant_and_protocol_active` for all signing operations.
4. Can run the MPC node outside a TEE while the contract treats them as fully attested.

This breaks the production safety invariant that all signing participants must be running in a verified TEE environment. If a colluding subset of participants (below threshold) all adopt this bypass, they can operate outside TEE protections, potentially exposing key shares in plaintext memory.

This maps to: **Medium — participant-state manipulation that breaks production safety/accounting invariants.**

### Likelihood Explanation

The entry path is a single direct call to a public, payable contract method. Any existing participant can execute it at any time with no special tooling. The `MockAttestation::Valid` variant is a named, documented enum arm in the public DTO type (`near-mpc-contract-interface`), making it trivially discoverable. No collusion, leaked keys, or operator access is required — only participant status, which is a normal operational role.

### Recommendation

1. **Reject `MockAttestation` in production**: Add a compile-time or runtime guard in `submit_participant_info` (or `add_participant`) that rejects `Attestation::Mock(_)` unless a `#[cfg(test)]` or explicit feature flag is active.
2. **Enforce expiry on `MockAttestation::WithConstraints`**: The `expiry_timestamp_seconds` field is `Option<u64>` — a `None` value means no expiry check at all. Require a non-`None` expiry for any mock attestation accepted outside tests.
3. **Track the TODO**: The comment `// TODO(#1639): extract timestamp from certificate itself` on `ValidatedDstackAttestation.expiry_timestamp_seconds` indicates the expiry is currently computed from the block clock rather than the certificate. Until resolved, the expiry window is the only recency control for Dstack attestations and must not be bypassable via the Mock path.

### Proof of Concept

```rust
// Any participant account calls submit_participant_info with MockAttestation::Valid.
// No deposit beyond storage cost, no TEE hardware, no quote, no measurements.
let bypass_attestation = Attestation::Mock(MockAttestation::Valid);
contract.submit_participant_info(bypass_attestation, my_tls_key);

// Result: stored_attestations now contains VerifiedAttestation::Mock(MockAttestation::Valid)
// for this participant. re_verify() will return Ok(()) for this entry at any future
// block timestamp — the entry never expires. verify_tee() sees this participant as
// fully attested. The participant can sign indefinitely without running in a TEE.
```

The root cause is in `crates/mpc-attestation/src/attestation.rs` at the `MockAttestation::Valid` arm of `verify_constraints` (line 142) and `AcceptedAttestation::mock()` (lines 85–90), mirroring exactly the pattern in the external report: external data (attestation) is accepted without verifying its recency/timestamp. [9](#0-8) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/mpc-attestation/src/attestation.rs (L24-28)
```rust
/// How long an accepted attestation stays trusted before it must be
/// re-verified via [`VerifiedAttestation::re_verify`]. Nodes resubmit hourly,
/// well within this window, so valid attestations refresh in time.
// TODO(#1639): extract timestamp from certificate itself
pub const DEFAULT_EXPIRATION_DURATION_SECONDS: u64 = 60 * 60 * 24; // 1 day
```

**File:** crates/mpc-attestation/src/attestation.rs (L70-78)
```rust
        // TODO(#1639): extract timestamp from certificate itself
        let expiration_timestamp_seconds =
            current_timestamp_seconds + DEFAULT_EXPIRATION_DURATION_SECONDS;
        Self {
            attestation: VerifiedAttestation::Dstack(ValidatedDstackAttestation {
                mpc_image_hash,
                launcher_compose_hash,
                expiry_timestamp_seconds: expiration_timestamp_seconds,
                measurements,
```

**File:** crates/mpc-attestation/src/attestation.rs (L84-91)
```rust
    /// Assembles the acceptance for a verified `Mock` attestation.
    fn mock(mock_attestation: &MockAttestation) -> Self {
        Self {
            attestation: VerifiedAttestation::Mock(mock_attestation.clone()),
            advisory_ids: Vec::new(),
        }
    }
}
```

**File:** crates/mpc-attestation/src/attestation.rs (L141-143)
```rust
        match self {
            MockAttestation::Valid => Ok(()),
            MockAttestation::Invalid => Err(VerificationError::InvalidMockAttestation),
```

**File:** crates/mpc-attestation/src/attestation.rs (L229-236)
```rust
                let attestation_has_expired = *expiration_timestamp_seconds < timestamp_seconds;

                if attestation_has_expired {
                    return Err(VerificationError::Custom(format!(
                        "The attestation expired at t = {:?}, time_now = {:?}",
                        expiration_timestamp_seconds, timestamp_seconds
                    )));
                }
```

**File:** crates/mpc-attestation/src/attestation.rs (L248-254)
```rust
            Self::Mock(mock_attestation) => mock_attestation.verify_constraints(
                timestamp_seconds,
                allowed_mpc_docker_image_hashes,
                allowed_launcher_docker_compose_hashes,
                allowed_measurements,
            ),
        }
```

**File:** crates/contract/src/lib.rs (L760-815)
```rust
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
```

**File:** crates/contract/src/tee/tee_state.rs (L166-175)
```rust
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
```

**File:** docs/design/attestation-verifier-contract.md (L616-616)
```markdown
`Attestation::Mock` stays in this iteration. The stub eventually supersedes it — both let tests bypass real `dcap-qvl` — but removing `Mock` is a separate cleanup, not in scope here.
```
