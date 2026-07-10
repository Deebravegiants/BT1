### Title
`verify_tee` Partial-Validity Path Re-enables Signing With Expired-TEE Participants During Resharing — (File: `crates/contract/src/lib.rs`)

---

### Summary

When `verify_tee()` detects that some (but not all) participants have expired or invalid TEE attestations and the remaining valid set still satisfies the governance threshold, it simultaneously sets `accept_requests = true` **and** initiates a resharing to evict the invalid participants. During the entire resharing window — which can stall indefinitely — signing requests are accepted and processed by the **old** participant set, which includes the nodes whose TEE environments are no longer verified. This is the direct analog of the basket-mode vulnerability: a protective mode is activated, but the harmful operation (signing with unverified nodes) continues before the protection takes effect.

---

### Finding Description

In `verify_tee()`, the `TeeValidationResult::Partial` branch executes two actions in sequence:

```
// lib.rs:1741-1764
self.accept_requests = true;          // ← re-opens the signing gate
...
let res = running_state.transition_to_resharing_no_checks(&proposed_parameters);
if let Some(resharing) = res {
    self.protocol_state = ProtocolContractState::Resharing(resharing);
}
``` [1](#0-0) 

The comment on line 1741 reads: *"here, we set it to true, because at this point, we have at least `threshold` number of participants with an accepted Tee status."* This reasoning is correct for liveness, but it ignores that the **old** participant set — which still includes the nodes with expired/invalid attestations — is the one used for signing during resharing.

`ResharingContractState` retains `previous_running_state` as its signing authority:

```rust
pub struct ResharingContractState {
    pub previous_running_state: RunningContractState,
    ...
}
``` [2](#0-1) 

MPC nodes index the contract state and, while in `Resharing`, continue to process signing requests using the old participant set. This is explicitly confirmed by the integration test `test_request_during_resharing`:

> *"Tests that signature and CKD requests are processed using the previous running state's threshold while resharing is in progress."* [3](#0-2) 

And by the unit test `test_signature_requests_in_resharing_are_processed`: [4](#0-3) 

The contrast with the safe path is instructive: when the valid set falls **below** threshold, the code correctly sets `accept_requests = false` and refuses to reshare:

```rust
self.accept_requests = false;
return Ok(false);
``` [5](#0-4) 

But in the partial-above-threshold case, the gate is re-opened unconditionally before the invalid participants are actually removed.

---

### Impact Explanation

During the resharing window, threshold signatures are produced with participation from nodes whose TEE attestations have expired or been revoked. The TEE attestation is the mechanism that verifies a node is running the correct, unmodified code inside a trusted execution environment. Once an attestation expires, the node's execution environment is unverified: it could have been updated to run code that leaks key shares, biases nonce selection, or otherwise subverts the signing protocol. Because the old participant set is used for signing, these unverified nodes contribute cryptographic material (triples, presignatures, partial signatures) to every signing request accepted during resharing.

This maps to the **Medium** allowed impact: *"participant-state or contract execution-flow manipulation that breaks production safety/accounting invariants."* The TEE attestation invariant — that every active signing participant runs verified code — is broken for the duration of resharing.

---

### Likelihood Explanation

- TEE attestations expire on a fixed schedule; expiry is a routine operational event, not an exceptional one.
- `verify_tee` must be called by a participant to trigger the transition, but nodes are expected to call it periodically as part of normal operation.
- Resharing can stall (e.g., a prospective participant goes offline, or repeated attempt timeouts occur), extending the window from minutes to hours or longer.
- The window is bounded only by resharing completion or manual cancellation via `vote_cancel_resharing`.

---

### Recommendation

In the `TeeValidationResult::Partial` branch of `verify_tee`, do **not** set `accept_requests = true` before resharing completes. Two options:

1. **Conservative:** Set `accept_requests = false` when entering resharing due to TEE invalidity, and restore it to `true` only when `vote_reshared` completes and the new (fully-valid) participant set is active.
2. **Liveness-preserving:** Allow signing only with the subset of participants that have valid attestations (i.e., use `participants_with_valid_attestation` as the signing set immediately, without waiting for resharing), rather than the full old set.

---

### Proof of Concept

1. Deploy with N=5 participants, governance threshold T=3. All have valid TEE attestations.
2. Two participants' TEE certificates expire (e.g., PCCS endpoint goes stale). The remaining 3 are valid — above threshold.
3. Any participant calls `verify_tee()`. `TeeValidationResult::Partial` is returned with 3 valid participants.
4. `accept_requests = true` is set; resharing to the 3-participant set is initiated.
5. One of the 3 prospective participants goes offline. Resharing stalls; repeated attempts time out.
6. For the entire stall duration, any user can call `sign(...)` and receive a threshold signature produced with participation from the 2 nodes whose TEE environments are no longer verified.
7. Those 2 nodes, if running modified code, can exfiltrate partial key material from every signing session during this window. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L1714-1767)
```rust
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

                // do we want to adjust the threshold?
                //let n_participants_new = new_participants.len();
                //let new_threshold = (3 * n_participants_new + 4) / 5; // minimum 60%
                //let new_threshold = new_threshold.max(2); // but also minimum 2
                let new_threshold = usize::try_from(current_params.threshold().value())
                    .expect("threshold value fits in usize");

                let threshold_parameters = ThresholdParameters::new(
                    participants_with_valid_attestation,
                    Threshold::new(new_threshold as u64),
                )
                .expect("Require valid threshold parameters"); // this should never happen.
                current_params.validate_incoming_proposal(&threshold_parameters)?;
                // This resharing only changes the participant set, so the
                // per-domain reconstruction-threshold updates map is empty.
                let proposed_parameters =
                    ProposedThresholdParameters::new(threshold_parameters, BTreeMap::new());
                let res = running_state.transition_to_resharing_no_checks(&proposed_parameters);
                if let Some(resharing) = res {
                    self.protocol_state = ProtocolContractState::Resharing(resharing);
                }

                Ok(true)
```

**File:** crates/contract/src/state/resharing.rs (L30-38)
```rust
pub struct ResharingContractState {
    pub previous_running_state: RunningContractState,
    pub reshared_keys: Vec<KeyForDomain>,
    pub resharing_key: KeyEvent,
    pub cancellation_requests: HashSet<AuthenticatedAccountId>,
    /// Per-domain `ReconstructionThreshold` updates carried from the accepted
    /// proposal. Applied to the [`DomainRegistry`](crate::primitives::domain::DomainRegistry)
    /// when resharing completes; empty means "keep current per-domain thresholds".
    pub per_domain_thresholds: BTreeMap<DomainId, ReconstructionThreshold>,
```

**File:** crates/e2e-tests/tests/request_during_resharing.rs (L9-18)
```rust
/// Tests that signature and CKD requests are processed using the previous
/// running state's threshold while resharing is in progress.
///
/// Setup: 6 nodes, 5 initial participants (threshold 5). Domains cover
/// classic ECDSA (CaitSith), robust ECDSA (DamgardEtAl), EdDSA (Frost) and
/// CKD (ConfidentialKeyDerivation). Threshold is 5 because robust ECDSA
/// requires ≥ 5 signers (see `robust_ecdsa::translate_threshold`). Begin
/// resharing to all 6 with threshold 6, then kill node 5 so resharing can't
/// complete. Requests should still succeed using the old threshold of 5
/// across all signing schemes.
```

**File:** crates/node/src/tests/resharing.rs (L380-386)
```rust
/// Test that signatures during resharing
/// are also processed.
#[serial] // this test relies on metrics for timing
#[tokio::test]
#[test_log::test]
async fn test_signature_requests_in_resharing_are_processed() {
    const NUM_PARTICIPANTS: usize = 5;
```
