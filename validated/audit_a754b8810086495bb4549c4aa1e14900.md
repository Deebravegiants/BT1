### Title
Unrestricted `clean_invalid_attestations` Allows Any Caller to Evict Active Participant Attestations, Disrupting the Signing Request Lifecycle — (File: `crates/contract/src/lib.rs`)

---

### Summary

`MpcContract::clean_invalid_attestations` carries no caller restriction and is explicitly documented as "Callable by anyone while the protocol is in `Running`." An unprivileged NEAR account can invoke it at any time to sweep participant attestations out of `stored_attestations`. If timed to coincide with the window between attestation expiry and the nodes' periodic re-attestation cycle, this removes every active participant's attestation, causing all subsequent calls to `assert_caller_is_attested_participant_and_protocol_active` to fail. The result is that no participant can call `respond`, `vote_pk`, `vote_reshared`, or any other attestation-gated method, forcing every in-flight sign request to time out.

---

### Finding Description

`clean_invalid_attestations` is a public, unrestricted mutating endpoint: [1](#0-0) 

The doc-comment explicitly states "Callable by anyone while the protocol is in `Running`." No `#[private]` modifier, no participant check, no deposit requirement. Any NEAR account can call it with an arbitrary `max_scan` value.

The function delegates to `TeeState::clean_invalid_attestations`, which iterates `stored_attestations` and removes every entry whose `reverify_participants` result is not `TeeQuoteStatus::Valid`: [2](#0-1) 

Re-verification fails when an attestation's `expiry_timestamp_seconds` has passed, or when the stored docker-image / launcher / OS-measurement hash is no longer on the current whitelist. Both conditions are reachable without any privileged action by the attacker.

Every node-facing method that mutates protocol state is gated by `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to have a live entry in `stored_attestations`: [3](#0-2) 

This gate covers `respond`, `respond_ckd`, `respond_verify_foreign_tx`, `vote_pk`, `vote_reshared`, `start_keygen_instance`, and `start_reshare_instance`. [4](#0-3) 

---

### Impact Explanation

**Medium — request-lifecycle and participant-state manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration.**

1. All in-flight `sign` / `request_app_private_key` / `verify_foreign_transaction` yields time out because no participant can call the corresponding `respond*` method. Users must resubmit and pay the deposit again.
2. An ongoing key-generation or resharing ceremony stalls: `vote_pk` and `vote_reshared` are blocked, and the key-event timeout eventually fires, aborting the ceremony and requiring a full restart.
3. The `accept_requests` flag is not directly affected, so new sign requests continue to be accepted and queued — but they will also time out until participants re-attest, creating a growing backlog.

No funds are permanently lost, but the signing service is rendered non-functional for the duration of the re-attestation cycle (up to one hour per the node's periodic submission cadence noted in the design doc). [5](#0-4) 

---

### Likelihood Explanation

**Medium.** The attack requires no special privilege, no TEE, and no deposit. The attacker only needs to:

1. Monitor on-chain block timestamps to detect when participant attestations are approaching or past their `expiry_timestamp_seconds`.
2. Submit a single NEAR transaction calling `clean_invalid_attestations` with `max_scan` set to a value large enough to cover all stored entries.

The nodes re-attest on a one-hour cadence. The window between expiry and re-attestation is predictable and observable from public chain state. A motivated attacker can script this trivially.

---

### Recommendation

Apply the same access-control pattern used by the analogous cleanup functions in the same file. Either:

- Add `#[private]` to restrict calls to the contract itself (matching `clean_tee_status` and `clean_foreign_chain_data`), and spawn it as a detached promise from `vote_reshared` or another trusted internal path; or
- Restrict callers to current participants using the same guard as `remove_non_participant_update_votes`: [6](#0-5) 

The analogous private endpoints already demonstrate the correct pattern: [7](#0-6) 

---

### Proof of Concept

```
# Attacker monitors stored_attestations for expiry_timestamp_seconds < now
# Then submits:
near call v1.signer clean_invalid_attestations \
  '{"max_scan": 1000}' \
  --accountId attacker.near \
  --gas 300000000000000

# Result: all expired participant attestations are removed.
# Subsequent respond() calls from nodes fail with
# "Caller must be an attested participant".
# All pending sign yields time out after ~200 blocks.
```

The sandbox test at `crates/contract/tests/sandbox/tee.rs` lines 414–422 confirms that `contract.as_account()` (i.e., any account) can successfully call `clean_invalid_attestations` and evict entries: [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L563-581)
```rust
    #[handle_result]
    pub fn respond(
        &mut self,
        request: SignatureRequest,
        response: dtos::SignatureResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1792-1796)
```rust
        let caller = env::predecessor_account_id();
        let is_self_call = caller == env::current_account_id();
        if !is_self_call && !participants.is_participant_given_account_id(&caller) {
            return Err(InvalidState::NotParticipant { account_id: caller }.into());
        }
```

**File:** crates/contract/src/lib.rs (L1803-1807)
```rust
    /// Private endpoint to drop votes cast by non-participants after resharing.
    /// Attestation cleanup is handled separately by [`MpcContract::clean_invalid_attestations`].
    #[private]
    #[handle_result]
    pub fn clean_tee_status(&mut self) -> Result<(), Error> {
```

**File:** crates/contract/src/lib.rs (L1821-1841)
```rust
    /// Prunes up to `max_scan` stored attestations that fail re-verification (expired or
    /// referencing stale whitelists). Returns the number of entries removed. Callable by
    /// anyone while the protocol is in `Running`.
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

**File:** crates/contract/src/tee/tee_state.rs (L406-434)
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
    }
```

**File:** crates/contract/tests/sandbox/tee.rs (L414-427)
```rust
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
```
