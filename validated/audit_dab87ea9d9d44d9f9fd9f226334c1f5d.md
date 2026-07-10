### Title
Unprivileged Caller Can Evict Active Participant Attestations via `clean_invalid_attestations` - (File: crates/contract/src/lib.rs)

### Summary

`clean_invalid_attestations` is explicitly documented as "Callable by anyone" and carries no access-control guard. Any NEAR account can invoke it to permanently delete `stored_attestations` entries — including entries belonging to **current active participants** — as long as those entries fail re-verification at the moment of the call. This is the direct analog of the GNTDeposit `withdraw` access-control gap: a state-mutating operation that should be restricted to the contract itself (or at minimum to participants) is reachable by an unprivileged external caller.

---

### Finding Description

`clean_invalid_attestations` in `crates/contract/src/lib.rs` has no caller restriction:

```rust
/// Prunes up to `max_scan` stored attestations that fail re-verification
/// (expired or referencing stale whitelists). Returns the number of entries
/// removed. Callable by anyone while the protocol is in `Running`.
#[handle_result]
pub fn clean_invalid_attestations(&mut self, max_scan: u32) -> Result<u32, Error> {
    ...
    Ok(self.tee_state.clean_invalid_attestations(tee_upgrade_deadline_duration, max_scan as usize))
}
``` [1](#0-0) 

The inner `TeeState::clean_invalid_attestations` iterates `stored_attestations`, calls `reverify_participants` on each entry, and **permanently removes** any entry whose status is not `TeeQuoteStatus::Valid`:

```rust
let has_invalid_attestation = |node_id: &NodeId| {
    !matches!(
        self.reverify_participants(node_id, tee_upgrade_deadline_duration),
        TeeQuoteStatus::Valid
    )
};
...
for tls_pk in invalid_tls_keys {
    self.stored_attestations.remove(&tls_pk);
}
``` [2](#0-1) 

Critically, the function does **not** distinguish between non-participant entries and entries belonging to current active participants. The in-process test `clean_invalid_attestations__should_remove_expired_entries` explicitly demonstrates that a current participant's attestation is evicted: [3](#0-2) 

Contrast this with every other cleanup function in the same contract, all of which are either `#[private]` (contract-only) or explicitly restricted to participants:

- `clean_tee_status` — `#[private]`
- `clean_foreign_chain_data` — `#[private]`
- `remove_non_participant_update_votes` — restricted to `predecessor == current_account_id` or a current participant [4](#0-3) [5](#0-4) 

`clean_invalid_attestations` is the only mutating cleanup endpoint with no restriction at all.

---

### Impact Explanation

Once a participant's entry is removed from `stored_attestations`, `is_caller_an_attested_participant` returns `AttestationCheckError::AttestationNotFound` for that participant: [6](#0-5) 

`assert_caller_is_attested_participant_and_protocol_active` — which gates every signing and key-event vote — panics on that error: [7](#0-6) 

Affected participant-only methods include `respond`, `respond_ckd`, `respond_verify_foreign_tx`, `vote_pk`, `vote_reshared`, `vote_abort_key_event_instance`, `start_keygen_instance`, and `start_reshare_instance`. If the attacker evicts enough participants' attestations to drop the available signers below the signing threshold, **no further threshold signatures can be produced** until those participants re-submit attestations. Pending `sign` yield-requests will time out and fail. Additionally, `reverify_and_cleanup_participants` (called by `verify_tee`) treats a missing `stored_attestations` entry as invalid, which can trigger an unplanned resharing that further disrupts the network.

**Impact category:** Medium — participant-state manipulation that breaks production safety/accounting invariants without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The attack window opens naturally during any TEE upgrade cycle: participants submit new attestations tied to a new docker-image hash, but their old attestations expire before the new ones are submitted. An attacker monitoring the NEAR blockchain can detect the expiry (block timestamp crosses `expiry_timestamp_seconds`) and immediately call `clean_invalid_attestations(max_scan: u32::MAX)` in the same block, racing the participant's renewal transaction. The call costs only gas and requires no privileged access. The sandbox test confirms the end-to-end path is reachable on-chain: [8](#0-7) 

---

### Recommendation

Apply the same access-control pattern used by the other cleanup endpoints. Restrict `clean_invalid_attestations` to self-calls (the post-reshare promise chain) and current participants, mirroring `remove_non_participant_update_votes`:

```rust
let caller = env::predecessor_account_id();
let is_self_call = caller == env::current_account_id();
if !is_self_call && !participants.is_participant_given_account_id(&caller) {
    return Err(InvalidState::NotParticipant { account_id: caller }.into());
}
```

Alternatively, mark it `#[private]` and invoke it exclusively from the post-reshare promise chain (as is already done for `clean_tee_status` and `clean_foreign_chain_data`).

---

### Proof of Concept

1. Deploy the contract in `Running` state with N participants, each holding an attestation with `expiry_timestamp_seconds = T`.
2. Advance the block timestamp past `T` (e.g., via `worker.fast_forward`).
3. From **any** unprivileged NEAR account, call:
   ```json
   { "method": "clean_invalid_attestations", "args": { "max_scan": 1000 } }
   ```
4. Observe that all participant entries are removed from `stored_attestations` (`get_tee_accounts()` returns empty).
5. Attempt to call `respond` as any participant — the call panics with `"Caller must be an attested participant"` because `is_caller_an_attested_participant` returns `AttestationNotFound`.
6. All pending `sign` yield-requests time out; the MPC network cannot produce signatures until participants re-submit attestations. [2](#0-1) [1](#0-0)

### Citations

**File:** crates/contract/src/lib.rs (L1788-1796)
```rust
        // Authorize the caller: allow self-calls (the cleanup promise spawned after a
        // successful resharing, where the predecessor is the contract account) and
        // direct calls from a current participant. Reject everyone else so that
        // non-participants cannot drive this cleanup.
        let caller = env::predecessor_account_id();
        let is_self_call = caller == env::current_account_id();
        if !is_self_call && !participants.is_participant_given_account_id(&caller) {
            return Err(InvalidState::NotParticipant { account_id: caller }.into());
        }
```

**File:** crates/contract/src/lib.rs (L1803-1819)
```rust
    /// Private endpoint to drop votes cast by non-participants after resharing.
    /// Attestation cleanup is handled separately by [`MpcContract::clean_invalid_attestations`].
    #[private]
    #[handle_result]
    pub fn clean_tee_status(&mut self) -> Result<(), Error> {
        log!("clean_tee_status: signer={}", env::signer_account_id());

        let participants = match &self.protocol_state {
            ProtocolContractState::Running(state) => state.parameters.participants(),
            _ => {
                return Err(InvalidState::ProtocolStateNotRunning.into());
            }
        };

        self.tee_state.clean_non_participant_votes(participants);
        Ok(())
    }
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

**File:** crates/contract/src/tee/tee_state.rs (L480-483)
```rust
        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;
```

**File:** crates/contract/tests/inprocess/attestation_submission.rs (L468-502)
```rust
    // init_running seeds one mock `Valid` attestation per participant. Overwrite the
    // first participant's entry with an expiring one, and add a brand-new entry for an
    // outsider account.
    let participant_node = {
        let (account_id, _, info) = &setup.participants_list[0];
        NodeId {
            account_id: account_id.clone(),
            tls_public_key: info.tls_public_key.clone(),
            account_public_key: bogus_ed25519_public_key(),
        }
    };
    setup.submit_attestation_for_node(&participant_node, expiring_attestation.clone());

    let stale_node = NodeId {
        account_id: "stale.near".parse().unwrap(),
        tls_public_key: bogus_ed25519_public_key(),
        account_public_key: bogus_ed25519_public_key(),
    };
    setup.submit_attestation_for_node(&stale_node, expiring_attestation);

    const EXPECTED_STORED: usize = PARTICIPANT_COUNT + 1; // original mocks + outsider entry
    assert_eq!(setup.contract.get_tee_accounts().len(), EXPECTED_STORED);

    // When: time advances past the expiry and cleanup runs with a generous max_scan.
    set_system_time(NOW_NS);
    let removed = setup.contract.clean_invalid_attestations(100).unwrap();

    // Then: both entries with `expiry_timestamp_seconds` in the past are evicted; the
    // second participant's un-overwritten `Valid` mock remains.
    const EXPECTED_REMOVED: u32 = 2;
    assert_eq!(removed, EXPECTED_REMOVED);
    assert_eq!(
        setup.contract.get_tee_accounts().len(),
        EXPECTED_STORED - EXPECTED_REMOVED as usize
    );
```

**File:** crates/contract/tests/sandbox/tee.rs (L414-423)
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
```
