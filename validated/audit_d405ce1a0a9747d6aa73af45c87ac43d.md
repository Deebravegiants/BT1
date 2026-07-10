### Title
Hardcoded Attestation Expiry Window Allows TEE Certificates to Remain Trusted Beyond Their Actual Validity Period - (File: crates/mpc-attestation/src/attestation.rs)

---

### Summary

The `DEFAULT_EXPIRATION_DURATION_SECONDS` constant is hardcoded in `crates/mpc-attestation/src/attestation.rs` and blindly applied to every accepted Dstack (TDX) attestation at submission time. The contract never extracts the actual validity period embedded in the TDX certificate itself. This is the direct analog of the USDC-peg assumption: just as that contract assumed USDC ≡ $1 instead of querying the oracle, this contract assumes every TDX attestation is valid for exactly 86 400 seconds instead of reading the certificate's own expiry. When Intel updates TCB collateral (e.g., after a platform vulnerability), the underlying certificate becomes invalid, but the stored `expiry_timestamp_seconds` continues to pass `re_verify` for up to one full day, allowing the affected node to keep participating in threshold signing.

---

### Finding Description

`AcceptedAttestation::dstack` in `crates/mpc-attestation/src/attestation.rs` stamps every accepted Dstack attestation with a fixed expiry:

```rust
// TODO(#1639): extract timestamp from certificate itself
let expiration_timestamp_seconds =
    current_timestamp_seconds + DEFAULT_EXPIRATION_DURATION_SECONDS;
``` [1](#0-0) [2](#0-1) 

`DEFAULT_EXPIRATION_DURATION_SECONDS` is hardcoded to `60 * 60 * 24` (one day). The TDX certificate itself carries its own validity window (derived from the PCCS collateral's `nextUpdate` field and the quote's signing-key lifetime), but the code never reads it — the TODO comment explicitly acknowledges this gap.

The stored `ValidatedDstackAttestation.expiry_timestamp_seconds` is the only time-based gate used by `re_verify`:

```rust
let attestation_has_expired = *expiration_timestamp_seconds < timestamp_seconds;
if attestation_has_expired {
    return Err(VerificationError::Custom(format!(
        "The attestation expired at t = {:?}, time_now = {:?}",
        expiration_timestamp_seconds, timestamp_seconds
    )));
}
``` [3](#0-2) 

`re_verify` does **not** re-run DCAP verification; it only checks the stored timestamp and the allowlist membership. So once a Dstack attestation is accepted, the only way it can be evicted before its stored expiry is if the node's image hash or measurements are removed from the allowlist — not if Intel's TCB collateral changes.

The `submit_participant_info` entry point in the contract calls `tee_state.add_participant`, which calls `verify_locally`, which calls `AcceptedAttestation::dstack` with the block timestamp, producing the hardcoded-window expiry that is then persisted: [4](#0-3) 

The node-side `tx_sender.rs` also hard-assumes the same constant when reverse-engineering the submission time from the stored expiry, compounding the coupling: [5](#0-4) 

---

### Impact Explanation

When Intel publishes a TCB update that downgrades or revokes a platform's TCB level (a routine occurrence after microarchitectural vulnerability disclosures), any node whose quote was accepted before the update will have its underlying certificate invalidated by Intel's standards. Because the contract never re-checks DCAP and only compares `now` against the stored `expiry_timestamp_seconds`, the node continues to pass `verify_tee` and `re_verify` for up to 24 hours after the TCB update. During that window the node remains an active, attested participant and can contribute signature shares to threshold signing operations — including `verify_foreign_transaction` flows — that it should no longer be authorized to join. This breaks the production safety invariant that only nodes running on a currently-valid, Intel-endorsed TEE platform may participate in the MPC network, constituting a participant-state and contract execution-flow manipulation.

---

### Likelihood Explanation

Intel issues TCB updates multiple times per year. The PCCS collateral (`tcb_info`, `qe_identity`, PCK CRL) is re-signed on roughly a 30-day cycle, and the node already enforces a 7-day freshness bound on collateral at submission time (`MAX_COLLATERAL_AGE`). A node operator who submits an attestation shortly before a TCB update is published will have their stored entry remain trusted for up to one day after the update, with no action required on their part. The window is bounded but deterministic and predictable by anyone monitoring Intel's PCS feed.

---

### Recommendation

Implement TODO #1639: extract the actual certificate validity timestamp from the TDX quote or its associated PCCS collateral (e.g., the minimum of `tcb_info.nextUpdate`, `qe_identity.nextUpdate`, and the PCK certificate's `notAfter` field) and use that as `expiry_timestamp_seconds` instead of `current_timestamp + DEFAULT_EXPIRATION_DURATION_SECONDS`. The hardcoded constant should become a **maximum cap** (i.e., `min(cert_expiry, current_time + DEFAULT_EXPIRATION_DURATION_SECONDS)`) rather than the sole source of truth, so that a certificate whose actual validity is shorter than one day is never trusted beyond its real expiry.

---

### Proof of Concept

1. At block time `T`, node N calls `submit_participant_info` with a valid Dstack attestation. DCAP verification passes; the contract stores `expiry_timestamp_seconds = T + 86400`.
2. At time `T + 1 hour`, Intel publishes a TCB update that downgrades N's platform. Any new `submit_participant_info` from N would now fail DCAP verification.
3. `verify_tee` is called at `T + 2 hours`. It calls `re_verify` on N's stored entry. `re_verify` checks `T+2h < T+86400` → **passes**. N remains an active participant.
4. N continues to contribute signature shares to `sign` and `verify_foreign_transaction` requests for the remaining ~22 hours, despite its TEE platform being considered insecure by Intel's current TCB standards.
5. The root cause is the hardcoded `DEFAULT_EXPIRATION_DURATION_SECONDS` at `crates/mpc-attestation/src/attestation.rs:28` and its unconditional application in `AcceptedAttestation::dstack` at lines 71–72, rather than reading the certificate's own validity bound. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/mpc-attestation/src/attestation.rs (L24-28)
```rust
/// How long an accepted attestation stays trusted before it must be
/// re-verified via [`VerifiedAttestation::re_verify`]. Nodes resubmit hourly,
/// well within this window, so valid attestations refresh in time.
// TODO(#1639): extract timestamp from certificate itself
pub const DEFAULT_EXPIRATION_DURATION_SECONDS: u64 = 60 * 60 * 24; // 1 day
```

**File:** crates/mpc-attestation/src/attestation.rs (L63-82)
```rust
    fn dstack(
        mpc_image_hash: NodeImageHash,
        launcher_compose_hash: LauncherDockerComposeHash,
        measurements: ExpectedMeasurements,
        advisory_ids: Vec<String>,
        current_timestamp_seconds: u64,
    ) -> Self {
        // TODO(#1639): extract timestamp from certificate itself
        let expiration_timestamp_seconds =
            current_timestamp_seconds + DEFAULT_EXPIRATION_DURATION_SECONDS;
        Self {
            attestation: VerifiedAttestation::Dstack(ValidatedDstackAttestation {
                mpc_image_hash,
                launcher_compose_hash,
                expiry_timestamp_seconds: expiration_timestamp_seconds,
                measurements,
            }),
            advisory_ids,
        }
    }
```

**File:** crates/mpc-attestation/src/attestation.rs (L203-212)
```rust
pub struct ValidatedDstackAttestation {
    pub mpc_image_hash: NodeImageHash,
    pub launcher_compose_hash: LauncherDockerComposeHash,
    // TODO(#1639): This timestamp can not come from the contract,
    // but should be extracted from the certificate itself.
    pub expiry_timestamp_seconds: u64,
    /// The measurements that were verified during initial attestation.
    /// Stored so that re-verification can check they are still in the allowed set.
    pub measurements: ExpectedMeasurements,
}
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

**File:** crates/contract/src/lib.rs (L796-815)
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
```

**File:** crates/node/src/indexer/tx_sender.rs (L267-282)
```rust
                        // TODO(#1637): extract expiration timestamp from the certificate itself,
                        // instead of using heuristics.
                        let expiry_timestamp_seconds =
                            verified_dstack_attestation.expiry_timestamp_seconds;

                        let Some(attestation_duration_since_unix_epoch) = expiry_timestamp_seconds
                            .checked_sub(DEFAULT_EXPIRATION_DURATION_SECONDS)
                            .map(Duration::from_secs)
                        else {
                            tracing::error!(
                                ?expiry_timestamp_seconds,
                                "could not calculate attestation storage time"
                            );

                            return Ok(TransactionStatus::NotExecuted);
                        };
```
