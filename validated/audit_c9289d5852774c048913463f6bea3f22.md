### Title
`accept_requests` Not Reset by `submit_participant_info()` Enables Persistent Signing Blockade After Attestation Renewal — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `accept_requests` boolean flag gates every user-facing signing operation in the MPC contract. It is set to `false` by `verify_tee()` when fewer than `threshold` participants hold valid TEE attestations. However, `submit_participant_info()` — the function that stores or renews a participant's attestation — never updates `accept_requests`. This means that once the flag is cleared, the contract remains blocked even after all participants have successfully renewed their attestations, until `verify_tee()` is explicitly called again. A single Byzantine participant (below the signing threshold) can exploit the timing gap to extend the blockade.

---

### Finding Description

`MpcContract::check_request_preconditions()` enforces a hard gate on all user-facing calls (`sign`, `request_app_private_key`, `verify_foreign_transaction`):

```rust
// 4. Refuse the request if the contract is not currently accepting requests
if !self.accept_requests {
    env::panic_str(&TeeError::TeeValidationFailed.to_string())
}
``` [1](#0-0) 

`accept_requests` is set to `false` inside `verify_tee()` when the surviving valid-attestation set would drop below the governance threshold:

```rust
self.accept_requests = false;
return Ok(false);
``` [2](#0-1) 

It is set back to `true` only in two branches of `verify_tee()`:

```rust
TeeValidationResult::Full => {
    self.accept_requests = true;
    ...
}
...
self.accept_requests = true; // Partial but above threshold
``` [3](#0-2) 

`submit_participant_info()` — the function every node calls hourly to renew its attestation — stores a fresh `VerifiedAttestation` into `tee_state.stored_attestations` but **never touches `accept_requests`**. There is no code path in `submit_participant_info()` that re-evaluates the TEE state and restores the flag. [4](#0-3) 

The design documentation confirms nodes submit attestations every 7 days and call `verify_tee()` every 2 days:

> "Periodic renewal — every 7 days a fresh quote is generated and resubmitted … Collective verification — every 2 days, any participant can trigger `verify_tee()`" [5](#0-4) 

This creates the following exploitable window:

1. Attestations for ≥ (N − threshold + 1) participants expire naturally (7-day window).
2. A Byzantine participant (below threshold, still a registered voter) calls `verify_tee()` before the honest nodes renew. The Partial branch fires, the threshold check fails, and `accept_requests = false`.
3. Honest participants immediately renew via `submit_participant_info()`. All attestations are now valid again.
4. **`accept_requests` remains `false`** — `submit_participant_info()` does not re-evaluate or restore it.
5. Every `sign` / `request_app_private_key` / `verify_foreign_transaction` call panics with `TeeValidationFailed` until the next scheduled `verify_tee()` call (up to 2 days later).

---

### Impact Explanation

All threshold-signature issuance and foreign-chain verification is halted for the duration of the blockade. Pending yield-resume requests time out on-chain (200-block window), causing depositors to lose their 1 yoctoNEAR deposits and receive no signature. The MPC network is effectively non-functional for end users during this window. This matches the allowed Medium impact: **"request-lifecycle … manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."**

---

### Likelihood Explanation

A single Byzantine participant (one of N registered voters, strictly below the signing threshold) can trigger this by calling `verify_tee()` at any moment when ≥ 1 participant's attestation has lapsed but not yet been renewed. Because attestations expire on a fixed 7-day cadence and renewal is not atomic with expiry, this window is predictable and repeatable. No threshold collusion, key material, or privileged access is required — only a valid NEAR account that is a registered participant.

---

### Recommendation

`submit_participant_info()` should re-evaluate the TEE state after successfully storing a renewed attestation and, if the result is now `TeeValidationResult::Full`, set `accept_requests = true`. Concretely, after the `tee_state.add_participant(...)` call succeeds, invoke `reverify_and_cleanup_participants` against the current participant set and restore `accept_requests` if all participants are now valid. This mirrors the recommendation in the external report: the functions that change the underlying state (`addTrait`, `removeTrait` → `submit_participant_info`) should also update the gating parameter (`lastMonitoredAt` → `accept_requests`).

---

### Proof of Concept

```
Setup: 3 participants, threshold = 2.
       Attestations for participants P2 and P3 expire at block T.

T+1:   Byzantine participant P1 calls verify_tee().
       reverify_and_cleanup_participants returns Partial{valid=[P1]}.
       remaining=1 < threshold=2 → accept_requests = false.

T+2:   P2 calls submit_participant_info(fresh_attestation).
       stored_attestations[P2.tls_key] = fresh VerifiedAttestation.
       accept_requests unchanged (still false).

T+3:   P3 calls submit_participant_info(fresh_attestation).
       stored_attestations[P3.tls_key] = fresh VerifiedAttestation.
       accept_requests unchanged (still false).

T+4:   User calls sign(...) with 1 yoctoNEAR deposit.
       check_request_preconditions: !accept_requests → panic TeeValidationFailed.
       Deposit is consumed; no signature produced.

T+4 … T+2days: All sign/ckd/verify_foreign_tx calls fail identically.
               Network is fully blocked despite all 3 attestations being valid.

Recovery: only when a participant next calls verify_tee() (scheduled every 2 days).
```

The root cause is confirmed at: [1](#0-0) [3](#0-2) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L1709-1743)
```rust
            TeeValidationResult::Full => {
                self.accept_requests = true;
                log!("All participants have an accepted Tee status");
                Ok(true)
            }
            TeeValidationResult::Partial {
                participants_with_valid_attestation,
            } => {
                let remaining = participants_with_valid_attestation.len();
                // Defense in depth: the surviving participant set must keep the full
                // threshold relation intact — the GovernanceThreshold must still sit
                // within its bounds for the smaller set (in particular it must not
                // exceed the remaining participant count or the upper cap) and must
                // remain at least every domain's ReconstructionThreshold (the kickout
                // keeps the existing per-domain thresholds). Otherwise we refuse and
                // wait for manual intervention.
                let max_reconstruction_threshold =
                    max_reconstruction_threshold(running_state.domains.domains());
                if let Err(err) = ThresholdParameters::validate_governance_against_reconstruction(
                    u64::try_from(remaining).expect("participant count fits in u64"),
                    current_params.threshold(),
                    max_reconstruction_threshold,
                ) {
                    log!(
                        "Kicking out participants with an invalid TEE status would break the threshold relation ({:?}); {} participants remain with a valid TEE status. This requires manual intervention. We will not accept new signature requests as a safety precaution.",
                        err,
                        remaining,
                    );
                    self.accept_requests = false;
                    return Ok(false);
                }

                // here, we set it to true, because at this point, we have at least `threshold`
                // number of participants with an accepted Tee status.
                self.accept_requests = true;
```

**File:** crates/contract/src/tee/tee_state.rs (L74-86)
```rust
pub struct TeeState {
    pub(crate) allowed_docker_image_hashes: AllowedDockerImageHashes,
    pub(crate) allowed_launcher_images: AllowedLauncherImages,
    pub(crate) votes: CodeHashesVotes,
    pub(crate) launcher_votes: LauncherHashVotes,
    /// Mapping of TLS public key of a participant to its [`NodeAttestation`].
    /// Attestations are stored for any valid participant that has submitted one, not
    /// just for the currently active participants. Callers must not assume this map is
    /// small; use the key-indexed accessors rather than scanning the whole collection.
    pub(crate) stored_attestations: IterableMap<Ed25519PublicKey, NodeAttestation>,
    pub(crate) allowed_measurements: AllowedMeasurements,
    pub(crate) measurement_votes: MeasurementVotes,
}
```

**File:** crates/contract/src/tee/tee_state.rs (L238-277)
```rust
    pub fn reverify_and_cleanup_participants(
        &mut self,
        participants: &Participants,
        tee_upgrade_deadline_duration: Duration,
    ) -> TeeValidationResult {
        self.allowed_docker_image_hashes
            .cleanup_expired_hashes(tee_upgrade_deadline_duration);

        let participants_with_valid_attestation: Vec<_> = participants
            .participants()
            .iter()
            .filter(|(_, _, participant_info)| {
                // Use the stored NodeId (keyed by TLS public key) so the real
                // `account_public_key` participates in re-verification. If
                // there is no stored attestation for this TLS key, the
                // participant is invalid.
                let Some(node_id) = self.find_node_id_by_tls_key(&participant_info.tls_public_key)
                else {
                    return false;
                };

                let tee_status =
                    self.reverify_participants(&node_id, tee_upgrade_deadline_duration);

                matches!(tee_status, TeeQuoteStatus::Valid)
            })
            .cloned()
            .collect();

        if participants_with_valid_attestation.len() != participants.len() {
            let participants_with_valid_attestation =
                Participants::init(participants.next_id(), participants_with_valid_attestation);

            TeeValidationResult::Partial {
                participants_with_valid_attestation,
            }
        } else {
            TeeValidationResult::Full
        }
    }
```

**File:** docs/tee-lifecycle.md (L186-208)
```markdown
2. **Periodic attestation** — Every 7 days, generates a fresh TDX attestation quote and submits it to the governance contract via [`submit_participant_info()`][submit-participant-info]. Includes exponential backoff retries. (Reference: [`periodic_attestation_submission`][periodic-attestation])

3. **Monitor attestation removal** — Watches the contract for changes to the attested nodes list. If this node's attestation is removed (e.g., due to image hash rotation), resubmits immediately. (Reference: [`monitor_attestation_removal`][monitor-attestation-removal])

4. **Poll foreign chain policy** — Subscribes to the governance contract's [`get_foreign_chain_policy()`][get-foreign-chain-policy] view method via the Contract State Subscriber. Provides the active [`ForeignChainPolicy`][foreign-chain-policy-type] to consumers — for the MPC node this feeds [foreign transaction verification][foreign-tx-verification], for the Archive Signer it configures the validation SDK's RPC providers. (Reference: the MPC node currently fetches this [on-demand in the coordinator][coordinator-fcp]; the TEE Context will move it to continuous polling.)

[foreign-tx-verification]: foreign-chain-transactions.md

[foreign-chain-policy-type]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/contract-interface/src/types/foreign_chain.rs#L570
[coordinator-fcp]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/node/src/coordinator.rs#L378
[allowed-docker-image-hashes]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/contract/src/lib.rs#L1624
[allowed-launcher-compose-hashes]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/contract/src/lib.rs#L1638
[submit-participant-info]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/contract/src/lib.rs#L820
[get-foreign-chain-policy]: https://github.com/near/mpc/blob/ce53324f472aa89fdf702d7482211bbdb6a44967/crates/contract/src/lib.rs#L1663

## Attestation

After boot, every service must continuously prove to the governance contract that it is running an approved image inside a genuine TDX enclave. The attestation lifecycle is the same for all three services:

1. **Initial attestation** — the service generates a TDX quote that binds its identity (TLS public key) to the enclave measurements and submits it to the governance contract.
2. **Periodic renewal** — every 7 days a fresh quote is generated and resubmitted, so the contract always holds a recent proof.
3. **Removal monitoring** — if the contract removes the node's attestation (e.g., after an image-hash rotation), the service detects this and resubmits immediately.
4. **Collective verification** — every 2 days, any participant can trigger `verify_tee()` on the governance contract to re-validate all stored attestations and evict nodes whose image hashes are no longer on the approved list.
```
