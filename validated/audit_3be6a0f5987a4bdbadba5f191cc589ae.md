### Title
Single Participant Can Permanently Block Removal of Compromised Launcher Hash or OS Measurement — (`File: crates/contract/src/lib.rs`)

---

### Summary

`vote_remove_launcher_hash` and `vote_remove_os_measurement` require **unanimous** votes from all current participants to remove a compromised TEE component from the allowed set. A single participant running the compromised launcher or OS measurement can permanently block its removal by simply refusing to call the function, leaving the compromised component in the allowed set indefinitely and preserving their own ability to produce valid attestations and participate in signing.

---

### Finding Description

Both `vote_remove_launcher_hash` and `vote_remove_os_measurement` enforce a unanimity condition:

```rust
// Removal requires ALL participants to vote
let total_participants = threshold_parameters.participants().len() as u64;
if votes >= total_participants {
    let removed = self.tee_state.remove_launcher_image(&launcher_hash);
``` [1](#0-0) 

```rust
// Removal requires ALL participants to vote
let total_participants = threshold_parameters.participants().len() as u64;
if votes >= total_participants {
    let removed = self.tee_state.remove_measurement(&measurement);
``` [2](#0-1) 

The design documentation explicitly identifies `vote_remove_launcher_hash` as the intended mechanism for handling a compromised launcher:

> "Compromised launcher | Unanimous `vote_remove_launcher_hash`, as today."



However, the unanimity requirement means that the very participant whose launcher is compromised — and who has the strongest incentive to block removal — can do so by simply never calling the function. No active attack is required; passive non-participation is sufficient.

The launcher hash and OS measurement are part of the sealing key derivation chain. A compromised launcher that remains in the allowed set continues to produce attestations that the contract accepts as valid via `submit_participant_info` and `reverify_and_cleanup_participants`. The malicious participant therefore retains a valid `TeeQuoteStatus` and continues to be admitted to signing rounds via `assert_caller_is_attested_participant_and_protocol_active`. [3](#0-2) 

There is no alternative removal path in the current production code. The TTL-based auto-expiry described in `docs/design/auto-remove-launcher-hashes-design.md` is explicitly a draft proposal and is not implemented.



---

### Impact Explanation

A participant running a compromised launcher can block the removal of that launcher hash indefinitely. The compromised launcher continues to be accepted for attestations, the participant retains a valid TEE status, and continues to participate in threshold signing operations. This breaks the production safety invariant that the network can revoke trust in a compromised TEE component. If the compromised launcher enables access to sealed key shares (which it may, since the launcher is part of the sealing key derivation material), the impact escalates to unauthorized access to MPC key shares.

**Impact: Medium** — participant-state manipulation that breaks the production safety invariant governing TEE component revocation, without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The attacker's action is purely passive: do not call `vote_remove_launcher_hash`. A participant who discovers their launcher is compromised has a direct incentive to block its removal (to avoid being kicked out of the signing set). The condition is reachable by any single current participant, strictly below the signing threshold, with no collusion required.

---

### Recommendation

Replace the unanimity requirement for `vote_remove_launcher_hash` and `vote_remove_os_measurement` with the signing threshold (the same threshold used for `vote_add_launcher_hash` and `vote_add_os_measurement`). The rationale for unanimity — that removal invalidates attestations of nodes running that launcher — does not outweigh the security risk of allowing a single compromised participant to block the revocation of a compromised TEE component. Alternatively, provide a threshold-based emergency removal path that does not require the vote of the participant whose launcher is being revoked.

---

### Proof of Concept

1. Network has N=5 participants, threshold T=3. All participants run launcher hash `H`.
2. Launcher `H` is discovered to be compromised (e.g., it leaks key shares).
3. Participants P1–P4 call `vote_remove_launcher_hash(H)`. Vote count = 4, but `total_participants = 5`, so `4 >= 5` is false — removal does not occur.
4. P5 (running the compromised launcher) simply never calls `vote_remove_launcher_hash`.
5. `H` remains in `allowed_launcher_images` indefinitely.
6. P5 continues to call `submit_participant_info` hourly with a quote from launcher `H`, which the contract accepts as valid.
7. P5 retains a valid `TeeQuoteStatus` and continues to be admitted to signing rounds via `assert_caller_is_attested_participant_and_protocol_active`, participating in threshold signature production. [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L1467-1495)
```rust
    /// Vote to remove a launcher image hash from the allowed set. Requires ALL participants
    /// to vote for removal, since this invalidates attestations of nodes running that launcher.
    #[handle_result]
    pub fn vote_remove_launcher_hash(
        &mut self,
        launcher_hash: LauncherImageHash,
    ) -> Result<(), Error> {
        log!(
            "vote_remove_launcher_hash: signer={}, launcher_hash={:?}",
            env::signer_account_id(),
            launcher_hash,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = LauncherVoteAction::Remove(launcher_hash);
        let votes = self.tee_state.vote_launcher(action, &participant);

        // Removal requires ALL participants to vote
        let total_participants = threshold_parameters.participants().len() as u64;
        if votes >= total_participants {
            let removed = self.tee_state.remove_launcher_image(&launcher_hash);
            log!("launcher hash remove result: {}", removed);
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1524-1552)
```rust
    /// Vote to remove an OS measurement set from the allowed list. Requires ALL participants
    /// to vote for removal.
    #[handle_result]
    pub fn vote_remove_os_measurement(
        &mut self,
        measurement: ContractExpectedMeasurements,
    ) -> Result<(), Error> {
        log!(
            "vote_remove_os_measurement: signer={}, measurement={:?}",
            env::signer_account_id(),
            measurement,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = MeasurementVoteAction::Remove(measurement.clone());
        let votes = self.tee_state.vote_measurement(action, &participant);

        // Removal requires ALL participants to vote
        let total_participants = threshold_parameters.participants().len() as u64;
        if votes >= total_participants {
            let removed = self.tee_state.remove_measurement(&measurement);
            log!("OS measurement remove result: {}", removed);
        }

        Ok(())
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

**File:** crates/contract/src/tee/tee_state.rs (L466-498)
```rust
    /// whose TLS key matches an attested node belonging to the caller account.
    ///
    /// Handles multiple participants per account and supports legacy mock nodes.
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
