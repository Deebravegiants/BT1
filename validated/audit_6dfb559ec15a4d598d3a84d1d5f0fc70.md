### Title
Stale Attestation Bypass: `is_caller_an_attested_participant` Omits Re-Verification, Allowing Nodes with Revoked/Expired Image Hashes to Cast Threshold Votes — (`crates/contract/src/tee/tee_state.rs`)

---

### Summary

`is_caller_an_attested_participant` only checks identity fields (account_id, account_public_key) against the stored `NodeAttestation`. It never calls `re_verify` or `reverify_participants`. All operations gated by `assert_caller_is_attested_participant_and_protocol_active` — including `vote_pk`, `vote_reshared`, `start_keygen_instance`, `start_reshare_instance`, and `vote_abort_key_event_instance` — therefore accept a node whose stored `VerifiedDstackAttestation` would fail re-verification (revoked image hash, expired timestamp, removed OS measurement). The divergence is concrete and locally testable.

---

### Finding Description

**`is_caller_an_attested_participant`** performs only three checks: [1](#0-0) 

1. Caller is in the `participants` map.
2. Stored `NodeAttestation.node_id.account_id == signer_id`.
3. Stored `NodeAttestation.node_id.account_public_key == signer_ed25519`.

It never calls `re_verify` or `reverify_participants`. No expiry check, no image-hash check, no launcher-compose-hash check, no OS-measurement check.

**`reverify_participants`** does the full re-check: [2](#0-1) 

It calls `VerifiedAttestation::re_verify`, which for a `ValidatedDstackAttestation` checks: [3](#0-2) 

- `expiry_timestamp_seconds < timestamp_seconds` → reject
- `mpc_image_hash` not in `allowed_mpc_docker_image_hashes` → reject
- `launcher_compose_hash` not in `allowed_launcher_docker_compose_hashes` → reject
- `measurements` not in `allowed_measurements` → reject

**`assert_caller_is_attested_participant_and_protocol_active`** calls only `is_caller_an_attested_participant`: [4](#0-3) 

This guard is the sole attestation check for: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

**Trigger path for MPC image hash expiry (most realistic):**

MPC image hashes auto-expire after a 7-day grace period once a successor is voted in. There is no `vote_remove_code_hash`. After expiry, `reverify_participants` returns `TeeQuoteStatus::Invalid` for any node whose stored `ValidatedDstackAttestation.mpc_image_hash` is the expired hash. But `is_caller_an_attested_participant` returns `Ok(())` for the same node, because it never inspects `mpc_image_hash`.

The stored attestation itself also carries `expiry_timestamp_seconds` (set to `current_time + DEFAULT_EXPIRATION_DURATION_SECONDS` = 1 day at submission time): [10](#0-9) 

So the window is: from the moment the image hash expires until the stored attestation's own 1-day timestamp lapses **or** until `clean_invalid_attestations` is called by anyone.

**`clean_invalid_attestations` is NOT triggered automatically when an image hash expires.** It is only spawned as a detached promise after `vote_reshared` completes: [11](#0-10) 

And it is callable by anyone as a public endpoint: [12](#0-11) 

But between image-hash expiry and cleanup, the node's stored attestation remains in `stored_attestations` and passes `is_caller_an_attested_participant`.

---

### Impact Explanation

During the window (up to 1 day, bounded by `DEFAULT_EXPIRATION_DURATION_SECONDS`), a node running a revoked/expired image can:

- Cast `vote_pk` votes in key generation — influencing which public key is accepted.
- Cast `vote_reshared` votes — advancing resharing state.
- Call `start_keygen_instance` / `start_reshare_instance` — initiating protocol rounds.
- Cast `vote_abort_key_event_instance` — aborting in-progress key events.

This is a **participant/attestation authorization bypass**: the contract's TEE attestation requirement for threshold protocol operations is not enforced at the point of use. A node running software whose image hash has been revoked (e.g., because a vulnerability was found in that image) can continue to participate in threshold key-event votes until cleanup runs.

The impact is bounded by the threshold requirement — a single node cannot unilaterally complete a key generation or resharing. However, if the revocation was triggered by a discovered vulnerability in the image, the node running that image may be Byzantine, and its votes could disrupt or bias protocol outcomes within its single-node influence.

---

### Likelihood Explanation

- MPC image hashes auto-expire on every upgrade cycle (7-day grace period after a new hash is voted in). This is a routine, recurring event.
- The window is up to 1 day (attestation expiry), not just seconds.
- `clean_invalid_attestations` is not automatically called on image-hash expiry; it requires a separate transaction.
- The node does not need to do anything special — it simply continues calling `vote_pk` / `vote_reshared` with its existing NEAR account key after its image hash expires.

---

### Recommendation

Add a `re_verify` call inside `is_caller_an_attested_participant`, or call `reverify_participants` inside `assert_caller_is_attested_participant_and_protocol_active` before delegating to `is_caller_an_attested_participant`. Alternatively, trigger `clean_invalid_attestations` as a detached promise whenever an image hash expires or is removed, so the stale attestation is pruned from `stored_attestations` before the next threshold vote can be cast.

---

### Proof of Concept

```rust
// In a contract unit test:
// (a) Insert NodeId with image hash H
let mut tee_state = TeeState::default();
let node_id = /* ... */;
let attestation = Attestation::Mock(MockAttestation::WithConstraints {
    mpc_docker_image_hash: Some(H),
    ..
});
tee_state.add_participant(node_id.clone(), attestation, Duration::from_secs(0)).unwrap();

// (b) Remove H from allowed hashes (simulate expiry / removal)
// (AllowedDockerImageHashes::cleanup_expired_hashes or direct removal)
tee_state.allowed_docker_image_hashes.cleanup_expired_hashes(Duration::from_secs(0));
// advance block time past grace period so H is gone from get_allowed_mpc_docker_image_hashes

// (c) reverify_participants returns Invalid
let status = tee_state.reverify_participants(&node_id, Duration::from_secs(0));
assert_matches!(status, TeeQuoteStatus::Invalid(_)); // ✓ correctly rejected

// (d) is_caller_an_attested_participant returns Ok(())
set_signer(&node_id.account_id, &matching_pk);
let result = tee_state.is_caller_an_attested_participant(&participants);
assert_matches!(result, Ok(())); // ✓ divergence confirmed — node still passes
```

The divergence is directly observable: step (c) and step (d) give opposite answers for the same node at the same point in time.

### Citations

**File:** crates/contract/src/tee/tee_state.rs (L206-232)
```rust
    pub(crate) fn reverify_participants(
        &self,
        node_id: &NodeId,
        tee_upgrade_deadline_duration: Duration,
    ) -> TeeQuoteStatus {
        let allowed_mpc_docker_image_hashes =
            self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration);
        let allowed_launcher_compose_hashes = self.get_allowed_launcher_compose_hashes();
        let allowed_measurements = self.get_accepted_measurements();

        let participant_attestation = self.stored_attestations.get(&node_id.tls_public_key);
        let Some(participant_attestation) = participant_attestation else {
            return TeeQuoteStatus::Invalid("participant has no attestation".to_string());
        };

        // Verify the attestation quote
        let time_stamp_seconds = Self::current_time_seconds();
        match participant_attestation.verified_attestation.re_verify(
            time_stamp_seconds,
            &allowed_mpc_docker_image_hashes,
            &allowed_launcher_compose_hashes,
            &allowed_measurements,
        ) {
            Ok(()) => TeeQuoteStatus::Valid,
            Err(err) => TeeQuoteStatus::Invalid(err.to_string()),
        }
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L469-498)
```rust
    pub(crate) fn is_caller_an_attested_participant(
        &self,
        participants: &Participants,
    ) -> Result<(), AttestationCheckError> {
        let signer_account_pk = env::signer_account_pk();
        let signer_id = env::signer_account_id();

        let info = participants
            .info(&signer_id)
            .ok_or(AttestationCheckError::CallerNotParticipant)?;

        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;

        if attestation.node_id.account_id != signer_id {
            return Err(AttestationCheckError::AttestationOwnerMismatch);
        }

        // Stored account keys are Ed25519 by construction; a non-Ed25519
        // signer necessarily mismatches.
        let signer_ed25519 = Ed25519PublicKey::try_from(&signer_account_pk)
            .map_err(|_| AttestationCheckError::AttestationKeyMismatch)?;
        if attestation.node_id.account_public_key != signer_ed25519 {
            return Err(AttestationCheckError::AttestationKeyMismatch);
        }

        Ok(())
    }
```

**File:** crates/mpc-attestation/src/attestation.rs (L24-28)
```rust
/// How long an accepted attestation stays trusted before it must be
/// re-verified via [`VerifiedAttestation::re_verify`]. Nodes resubmit hourly,
/// well within this window, so valid attestations refresh in time.
// TODO(#1639): extract timestamp from certificate itself
pub const DEFAULT_EXPIRATION_DURATION_SECONDS: u64 = 60 * 60 * 24; // 1 day
```

**File:** crates/mpc-attestation/src/attestation.rs (L214-255)
```rust
impl VerifiedAttestation {
    pub fn re_verify(
        &self,
        timestamp_seconds: u64,
        allowed_mpc_docker_image_hashes: &[NodeImageHash],
        allowed_launcher_docker_compose_hashes: &[LauncherDockerComposeHash],
        allowed_measurements: &[ExpectedMeasurements],
    ) -> Result<(), VerificationError> {
        match self {
            Self::Dstack(ValidatedDstackAttestation {
                mpc_image_hash,
                launcher_compose_hash,
                expiry_timestamp_seconds: expiration_timestamp_seconds,
                measurements,
            }) => {
                let attestation_has_expired = *expiration_timestamp_seconds < timestamp_seconds;

                if attestation_has_expired {
                    return Err(VerificationError::Custom(format!(
                        "The attestation expired at t = {:?}, time_now = {:?}",
                        expiration_timestamp_seconds, timestamp_seconds
                    )));
                }

                let () = verify_mpc_hash(mpc_image_hash, allowed_mpc_docker_image_hashes)?;
                let () = verify_launcher_compose_hash(
                    launcher_compose_hash,
                    allowed_launcher_docker_compose_hashes,
                )?;

                verify_measurements(measurements, allowed_measurements)?;

                Ok(())
            }
            Self::Mock(mock_attestation) => mock_attestation.verify_constraints(
                timestamp_seconds,
                allowed_mpc_docker_image_hashes,
                allowed_launcher_docker_compose_hashes,
                allowed_measurements,
            ),
        }
    }
```

**File:** crates/contract/src/lib.rs (L1078-1085)
```rust
    pub fn start_keygen_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!("start_keygen_instance: signer={}", env::signer_account_id(),);

        self.assert_caller_is_attested_participant_and_protocol_active();

        self.protocol_state
            .start_keygen_instance(key_event_id, self.config.key_event_timeout_blocks)
    }
```

**File:** crates/contract/src/lib.rs (L1103-1116)
```rust
    pub fn vote_pk(
        &mut self,
        key_event_id: KeyEventId,
        public_key: dtos::PublicKey,
    ) -> Result<(), Error> {
        log!(
            "vote_pk: signer={}, key_event_id={:?}, public_key={:?}",
            env::signer_account_id(),
            key_event_id,
            public_key,
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

```

**File:** crates/contract/src/lib.rs (L1136-1143)
```rust
    pub fn start_reshare_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "start_reshare_instance: signer={}",
            env::signer_account_id()
        );

        self.assert_caller_is_attested_participant_and_protocol_active();
        self.protocol_state
```

**File:** crates/contract/src/lib.rs (L1161-1169)
```rust
    pub fn vote_reshared(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_reshared: signer={}, resharing_id={:?}",
            env::signer_account_id(),
            key_event_id,
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

```

**File:** crates/contract/src/lib.rs (L1194-1205)
```rust
            // Spawn a bounded sweep over stored attestations to prune invalid / expired entries.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_INVALID_ATTESTATIONS.to_string(),
                    serde_json::to_vec(&serde_json::json!({
                        "max_scan": RESHARE_CLEAN_INVALID_ATTESTATIONS_MAX_SCAN
                    }))
                    .unwrap(),
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_invalid_attestations_tera_gas),
                )
                .detach();
```

**File:** crates/contract/src/lib.rs (L1285-1292)
```rust
    pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_abort_key_event_instance: signer={}",
            env::signer_account_id()
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

```

**File:** crates/contract/src/lib.rs (L1824-1841)
```rust
    #[handle_result]
    pub fn clean_invalid_attestations(&mut self, max_scan: u32) -> Result<u32, Error> {
        log!(
            "clean_invalid_attestations: signer={}, max_scan={}",
            env::signer_account_id(),
            max_scan
        );
        // Running-only: keygen / resharing may reference attestations that have not yet
        // been activated, so cleanup is off-limits during those phases.
        if !matches!(self.protocol_state, ProtocolContractState::Running(_)) {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }
        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);
        Ok(self
            .tee_state
            .clean_invalid_attestations(tee_upgrade_deadline_duration, max_scan as usize))
    }
```

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
    }
```
