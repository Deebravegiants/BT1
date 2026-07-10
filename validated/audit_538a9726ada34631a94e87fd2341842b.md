### Title
Storage Deposit Permanently Locked When TEE Attestation Expires and Is Cleaned Up — (`File: crates/contract/src/lib.rs`, `crates/contract/src/tee/tee_state.rs`)

---

### Summary

`submit_participant_info` charges the caller a storage deposit proportional to the bytes consumed by the new attestation entry. When that attestation later expires and is evicted by `clean_invalid_attestations`, the freed storage bytes are silently absorbed into the contract's balance with no refund issued to the original depositor. The storage deposit is permanently locked in the contract.

---

### Finding Description

`submit_participant_info` measures storage growth before and after inserting the attestation entry and charges the caller exactly that cost: [1](#0-0) 

The deposit is consumed by the contract account (NEAR's storage-staking model). No per-depositor accounting is kept — the contract records only the `NodeAttestation` struct, not who paid for it.

`clean_invalid_attestations` (callable by anyone while the contract is `Running`) iterates `stored_attestations`, identifies entries whose `re_verify` fails (expired timestamp, stale image hash, etc.), and removes them: [2](#0-1) 

The removal frees the storage bytes and increases the contract's available balance, but no `Promise::new(original_depositor).transfer(freed_cost)` is ever issued. The original depositor's funds are permanently locked.

The same sweep is triggered automatically after every successful reshare via a promise chain spawned from `vote_reshared`, so the lock-up occurs even without an explicit external call to `clean_invalid_attestations`.

The code comment in `submit_participant_info` acknowledges an intentional asymmetry for re-submission size changes, but makes no design statement about expiry-driven cleanup: [3](#0-2) 

---

### Impact Explanation

Every MPC node operator (or prospective participant) who calls `submit_participant_info` pays a storage deposit. TEE attestations have a finite `expiry_timestamp_seconds`. Once the attestation expires and `clean_invalid_attestations` runs, the storage is freed but the deposit is not returned. The contract's balance grows by the freed amount; the depositor's balance shrinks permanently.

NEAR storage costs ~10 yoctoNEAR per byte. A `NodeAttestation` entry (containing `NodeId` with three Ed25519 keys plus a `VerifiedAttestation` with quote data) is on the order of hundreds to thousands of bytes, placing the per-entry loss in the milliNEAR-to-NEAR range. Because nodes are expected to periodically re-attest (potentially with new TLS keys, each creating a new entry), the cumulative loss compounds over the lifetime of the network.

This breaks the production accounting invariant that a caller who pays for storage should recover that deposit when the storage is freed — a standard NEAR contract pattern. The impact maps to **Medium**: balance/accounting invariant broken without relying on DoS or operator misconfiguration.

---

### Likelihood Explanation

Likelihood is **High**. Every attestation has a finite expiry. The node software periodically re-submits attestations; if a new TLS key is used, a new storage deposit is charged. The old entry is eventually evicted by `clean_invalid_attestations` (called automatically post-reshare or by any external caller). No special attacker action is required — the loss occurs as a normal consequence of the attestation lifecycle for every participant.

---

### Recommendation

Track the depositor and the amount paid per `stored_attestations` entry (e.g., add a parallel `LookupMap<Ed25519PublicKey, (AccountId, NearToken)>`). In `clean_invalid_attestations`, after removing each invalid entry, issue a `Promise::new(depositor).transfer(freed_cost)` to return the freed storage cost to the original payer. Alternatively, adopt the standard NEAR storage-management pattern (NEP-145) so callers can explicitly withdraw their freed storage deposit.

---

### Proof of Concept

1. Account `alice.near` calls `submit_participant_info` with a valid attestation whose `expiry_timestamp_seconds = now + 5`. The contract charges `alice.near` the storage cost (e.g., 0.01 NEAR) and stores the entry.
2. Five seconds pass; the attestation expires.
3. Any account calls `clean_invalid_attestations(max_scan: 100)`.
4. `tee_state.stored_attestations.remove(&alice_tls_pk)` executes — the entry is deleted, freeing the storage bytes.
5. The contract's balance increases by 0.01 NEAR. `alice.near`'s balance is unchanged from step 2. The 0.01 NEAR is permanently locked in the contract with no recovery path.

The sandbox test `clean_invalid_attestations__should_remove_expired_entries` confirms the eviction path executes end-to-end but contains no assertion that the depositor's balance is restored, confirming the absence of any refund: [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L778-848)
```rust
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
```

**File:** crates/contract/src/tee/tee_state.rs (L406-433)
```rust
    pub fn clean_invalid_attestations(
        &mut self,
        tee_upgrade_deadline_duration: Duration,
        max_scan: usize,
    ) -> u32 {
        let has_invalid_attestation = |node_id: &NodeId| {
            !matches!(
                self.reverify_participants(node_id, tee_upgrade_deadline_duration),
                TeeQuoteStatus::Valid
            )
        };

        // Materialize candidates before any mutation to avoid iterator invalidation.
        let invalid_tls_keys: Vec<Ed25519PublicKey> = self
            .stored_attestations
            .iter()
            .take(max_scan)
            .filter(|(_, node_attestation)| has_invalid_attestation(&node_attestation.node_id))
            .map(|(tls_pk, _)| tls_pk.clone())
            .collect();

        let removed = u32::try_from(invalid_tls_keys.len())
            .expect("u32 should always be convertible from usize on wasm32");

        for tls_pk in invalid_tls_keys {
            self.stored_attestations.remove(&tls_pk);
        }
        removed
```

**File:** crates/contract/tests/sandbox/tee.rs (L356-430)
```rust
/// **`clean_invalid_attestations` end-to-end** — an attestation whose expiry has passed
/// is evicted from `stored_attestations` when the endpoint is invoked. Restores the
/// functional cleanup-path coverage previously asserted via `clean_tee_status`.
#[tokio::test]
async fn clean_invalid_attestations__should_remove_expired_entries() -> Result<()> {
    // `verify()` at insert time rejects attestations that are already expired, so the
    // expiring attestation is submitted with an expiry a few seconds in the future and
    // the test then fast-forwards past it. 100 blocks is enough that the block
    // timestamp reliably advances past a 5-second expiry window.
    const ATTESTATION_EXPIRY_SECONDS: u64 = 5;
    const BLOCKS_TO_FAST_FORWARD: u64 = 100;

    // Given
    let SandboxTestSetup {
        worker,
        contract,
        mut mpc_signer_accounts,
        ..
    } = SandboxTestSetup::builder()
        .with_protocols(ALL_PROTOCOLS)
        .build()
        .await;

    // Submit a structurally-valid attestation for every current participant so those
    // entries survive the sweep.
    let participants: Participants =
        (&assert_running_return_participants(&contract).await?).into_contract_type();
    let participant_uids = build_sandbox_node_ids(&participants, &mpc_signer_accounts);
    submit_tee_attestations(&contract, &mut mpc_signer_accounts, &participant_uids).await?;

    // Submit an attestation from a non-participant that will expire shortly.
    let (stale_accounts, _stale_participants) = gen_accounts(&worker, 1).await;
    let stale_account = &stale_accounts[0];
    let stale_tls_key: dtos::Ed25519PublicKey = p2p_tls_key().into();
    let block_info = worker.view_block().await?;
    let expiry_timestamp_seconds =
        block_info.timestamp() / 1_000_000_000 + ATTESTATION_EXPIRY_SECONDS;
    let expiring_attestation = Attestation::Mock(MockAttestation::WithConstraints {
        mpc_docker_image_hash: None,
        launcher_docker_compose_hash: None,
        expiry_timestamp_seconds: Some(expiry_timestamp_seconds),
        expected_measurements: None,
    });
    let submit_result = submit_participant_info(
        stale_account,
        &contract,
        &expiring_attestation,
        &stale_tls_key,
    )
    .await?;
    assert!(submit_result.is_success());

    let before_cleanup = get_tee_accounts(&contract).await?;
    assert_eq!(before_cleanup.len(), participant_uids.len() + 1);

    // Advance past the expiry.
    worker.fast_forward(BLOCKS_TO_FAST_FORWARD).await?;

    // When: any account calls `clean_invalid_attestations` with a scan budget large enough
    // to cover every stored entry.
    let scan_budget: u32 = (before_cleanup.len() as u32) + 1;
    let result = contract
        .as_account()
        .call(contract.id(), method_names::CLEAN_INVALID_ATTESTATIONS)
        .args_json(serde_json::json!({ "max_scan": scan_budget }))
        .transact()
        .await?;
    assert!(result.is_success());

    // Then: the expired entry is evicted while the valid participant entries remain.
    let after_cleanup = get_tee_accounts(&contract).await?;
    assert_eq!(after_cleanup, participant_uids);

    Ok(())
}
```
