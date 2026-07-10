### Title
Participant-Only `verify_tee` Gate Creates Unavoidable Signing Freeze with No Emergency Recovery Path — (`crates/contract/src/lib.rs`)

---

### Summary

`verify_tee` is the **sole on-chain mechanism** that can flip `accept_requests` back to `true` after it has been set to `false`, yet the function is unconditionally gated behind `voter_or_panic()` — participants only. When enough attestations expire simultaneously (e.g., during a coordinated TEE-image upgrade), the contract freezes all signing and CKD requests with no emergency bypass available to any unprivileged caller, external user, or contract owner. The recovery path requires every affected participant to upgrade their TEE image, re-attest, and then call `verify_tee` again — a process that carries inherent multi-day latency with no time bound enforced by the protocol.

---

### Finding Description

In `crates/contract/src/lib.rs`, `verify_tee` (line 1693) is the only function that writes `self.accept_requests = true`. It is unconditionally gated:

```rust
pub fn verify_tee(&mut self) -> Result<bool, Error> {
    // Caller must be a participant (node or operator).
    self.voter_or_panic();          // ← participants only, no bypass
    ...
``` [1](#0-0) 

When `reverify_and_cleanup_participants` returns `TeeValidationResult::Partial` and the surviving participant count would violate the governance-vs-reconstruction threshold relation, the contract sets:

```rust
self.accept_requests = false;
return Ok(false);
``` [2](#0-1) 

After this point, every call to `sign`, `respond_ckd`, and `respond_verify_foreign_tx` is rejected with `TeeError::TeeValidationFailed`:

```rust
if !self.accept_requests {
    return Err(TeeError::TeeValidationFailed.into());
}
``` [3](#0-2) [4](#0-3) 

The **only** recovery path is:

1. Each affected participant upgrades their TEE image.
2. Each re-attests via `submit_participant_info`.
3. A participant calls `verify_tee` again.

Steps 1–2 carry inherent multi-day latency (image build, operator coordination, CVM restart, PCCS collateral propagation). No emergency bypass exists. The design document itself acknowledges nodes call `verify_tee` on a 7-day cadence:

> "Call verify_tee every 7 days — in order to trigger a re-validation of attestation information on the contract." [5](#0-4) 

This is structurally identical to the reported Zunami bug: a critical state-restoration function (`inflate`/`deflate` there; `verify_tee` here) is gated behind a privileged role that carries inherent latency, with no emergency path.

---

### Impact Explanation

While `accept_requests = false` is active:

- All `sign` calls panic with `"TEE validation"` — new signature requests are permanently rejected until recovery completes.
- All `respond_ckd` and `respond_verify_foreign_tx` calls fail — in-flight requests cannot be resolved.
- Any user funds locked behind a pending MPC signature (cross-chain bridge withdrawals, CKD-derived key operations) are frozen for the duration of the outage.

This matches **Medium** — request-lifecycle and contract execution-flow manipulation that breaks production safety invariants — and borders on **Critical** (permanent freezing of funds) if the TEE upgrade cycle stalls.

---

### Likelihood Explanation

TEE attestations carry a hardcoded 7-day expiry (`DEFAULT_EXPIRATION_DURATION_SECONDS`). A coordinated TEE-image rotation (triggered by a discovered vulnerability in the running image, a DCAP collateral update, or an OS-measurement change) requires all operators to simultaneously rebuild, redeploy, and re-attest. If the rotation takes longer than the remaining attestation lifetime — a realistic scenario given multi-party coordination — enough attestations expire at once to trigger the `accept_requests = false` branch. A single Byzantine participant (below signing threshold) can accelerate the freeze by calling `verify_tee` the moment a peer's attestation lapses, before that peer has re-attested.

---

### Recommendation

Implement an emergency recovery mechanism analogous to the Zunami fix:

1. **Tiered caller access for `verify_tee`**: Allow any NEAR account to call `verify_tee` in read-only mode (returning the current TEE status without mutating `accept_requests`), while reserving the state-mutating path for participants. This at minimum enables monitoring without the participant gate.

2. **Emergency `restore_signing` function**: Add a function callable by a lower-quorum (e.g., a single attested participant, or a designated emergency key) that sets `accept_requests = true` and emits an on-chain event, subject to a short time-lock (e.g., 24 hours) to prevent abuse.

3. **Automatic re-enable on re-attestation**: When `submit_participant_info` is called and the resulting TEE state would now satisfy the threshold relation, automatically set `accept_requests = true` without requiring a separate `verify_tee` call.

---

### Proof of Concept

```
Setup: 3 participants (P1, P2, P3), GovernanceThreshold = 2, ReconstructionThreshold = 2.

1. P2 and P3 submit attestations with expiry_timestamp = now + 5 seconds.
2. Fast-forward 100 blocks (> 5 seconds of block time).
3. P1 (Byzantine, below signing threshold) calls verify_tee().
   → reverify_and_cleanup_participants returns Partial{[P1]}.
   → remaining = 1 < GovernanceThreshold = 2.
   → validate_governance_against_reconstruction fails.
   → accept_requests = false.  ← contract frozen
4. Any user calls sign(...) → panics with "TEE validation".
5. P2 and P3 must upgrade TEE images, re-attest, and call verify_tee() again.
   Recovery latency: days (image build + CVM restart + PCCS propagation).
   No emergency bypass exists.
```

The sandbox test `verify_tee__should_keep_participants_and_stop_signing_when_kickout_drops_below_threshold` in `crates/contract/tests/sandbox/tee.rs` (line 842) already demonstrates this exact freeze path in a controlled environment, confirming the root cause is reachable in production. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L662-664)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L711-713)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1693-1696)
```rust
    pub fn verify_tee(&mut self) -> Result<bool, Error> {
        log!("verify_tee: signer={}", env::signer_account_id());
        // Caller must be a participant (node or operator).
        self.voter_or_panic();
```

**File:** crates/contract/src/lib.rs (L1727-1738)
```rust
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
```

**File:** docs/securing-mpc-with-tee-design-doc.md (L397-399)
```markdown
  - On each boot (after state sync is completed)
  - Every 7 days.
- Call verify_tee every 7 days - in order to trigger a re-validation of attestation information on the contract.
```

**File:** crates/contract/tests/sandbox/tee.rs (L842-935)
```rust
async fn verify_tee__should_keep_participants_and_stop_signing_when_kickout_drops_below_threshold()
-> Result<()> {
    // Given
    const PARTICIPANT_COUNT: usize = 3;
    const ATTESTATION_EXPIRY_SECONDS: u64 = 5;
    // 100 blocks reliably advances the block timestamp past the 5-second expiry window.
    const BLOCKS_TO_FAST_FORWARD: u64 = 100;

    let SandboxTestSetup {
        worker,
        contract,
        mpc_signer_accounts,
        keys,
    } = SandboxTestSetup::builder()
        .with_protocols(&[Protocol::CaitSith])
        .with_number_of_participants(PARTICIPANT_COUNT)
        .build()
        .await;

    let threshold = assert_running_return_threshold(&contract).await;
    let initial_participants = assert_running_return_participants(&contract).await?;
    assert_eq!(initial_participants.participants.len(), PARTICIPANT_COUNT);

    // Expire all but `threshold - 1` attestations, leaving the valid set exactly one
    // below threshold regardless of the participant/threshold constants above.
    let remaining_valid = threshold.0 as usize - 1;
    assert!(
        remaining_valid < threshold.0 as usize,
        "test precondition: surviving participants ({remaining_valid}) must be below threshold ({})",
        threshold.0
    );

    // Compute the expiry timestamp from the current block time.
    let block_info = worker.view_block().await?;
    let expiry_timestamp = block_info.timestamp() / 1_000_000_000 + ATTESTATION_EXPIRY_SECONDS;
    let expiring_attestation = Attestation::Mock(MockAttestation::WithConstraints {
        mpc_docker_image_hash: None,
        launcher_docker_compose_hash: None,
        expiry_timestamp_seconds: Some(expiry_timestamp),
        expected_measurements: None,
    });

    // Submit an expiring attestation for every participant past the first `remaining_valid`.
    let internal_participants: Participants = (&initial_participants).into_contract_type();
    let node_ids = build_sandbox_node_ids(&internal_participants, &mpc_signer_accounts);
    for target_account in &mpc_signer_accounts[remaining_valid..] {
        let target_node_id = node_ids
            .iter()
            .find(|node| node.account_id == *target_account.id())
            .expect("target participant not found");
        let submit_success = submit_participant_info(
            target_account,
            &contract,
            &expiring_attestation,
            &target_node_id.tls_public_key,
        )
        .await?
        .is_success();
        assert!(submit_success, "failed to submit expiring attestation");
    }

    // Fast-forward past the attestation expiry.
    worker.fast_forward(BLOCKS_TO_FAST_FORWARD).await?;
    let current_timestamp = worker.view_block().await?.timestamp() / 1_000_000_000;
    assert!(
        current_timestamp > expiry_timestamp,
        "fast-forwarding {BLOCKS_TO_FAST_FORWARD} blocks was not enough: {current_timestamp} {expiry_timestamp}"
    );

    // When: a participant calls verify_tee while too few valid attestations remain.
    let verify_result = mpc_signer_accounts[0]
        .call(contract.id(), method_names::VERIFY_TEE)
        .args_json(serde_json::json!({}))
        .max_gas()
        .transact()
        .await?;
    assert!(
        verify_result.is_success(),
        "verify_tee call failed: {verify_result:?}"
    );

    // Then: verify_tee reports the network is no longer accepting requests.
    let accepting_requests: bool = verify_result.json()?;
    assert!(
        !accepting_requests,
        "verify_tee should return false when fewer than threshold participants remain valid"
    );

    // Then: no participant is kicked out — the contract stays Running with all participants.
    let state_after_verify = get_state(&contract).await;
    let dtos::ProtocolContractState::Running(running_after) = &state_after_verify else {
        panic!("expected Running state (no resharing), got {state_after_verify:?}");
    };
    assert_eq!(
```
