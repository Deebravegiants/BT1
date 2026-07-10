### Title
Pending Signature Requests Become Permanently Unresolvable When Resharing Removes Signing-Threshold Participants - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()` functions each call `assert_caller_is_attested_participant_and_protocol_active()`, which during `Resharing` state checks the caller against the **new proposed participant set**, not the old one. Old participants who hold the key shares but are being removed from the set cannot call `respond()` during resharing. If enough old participants are removed to drop below the signing threshold, all pending requests queued before resharing started become permanently unresolvable and time out.

This is the direct analog of the Wormhole guardian-set-change bug: a validity check passes at request-queue time (Running state, old participant set), but the same check re-runs at response time against a changed set (Resharing state, new participant set), causing the queued request to fail.

---

### Finding Description

When a user calls `sign()`, the contract queues a yield-resume promise and stores the request in `pending_signature_requests`. This succeeds because `check_request_preconditions()` only verifies the contract is in Running state and `accept_requests == true`. [1](#0-0) 

Later, an MPC node calls `respond()` to deliver the computed signature. Before resolving the yield, `respond()` calls `assert_caller_is_attested_participant_and_protocol_active()`: [2](#0-1) 

That helper reads `active_participants()` from the current protocol state. The contract's own documentation states:

> **Resharing → uses new participants from resharing proposal** [3](#0-2) 

So during `Resharing`, `active_participants()` returns the **new proposed set**, not the old one. Old participants who are being removed are rejected by the attestation check even though they are the only nodes that hold valid key shares for the current epoch.

The same pattern applies to `respond_ckd()` and `respond_verify_foreign_tx()`: [4](#0-3) [5](#0-4) 

The `ResharingContractState` preserves the old running state but does not expose old participants as valid callers for `respond*`: [6](#0-5) 

Key resharing preserves the public key (the node code explicitly asserts this): [7](#0-6) 

This means new participants cannot produce valid signatures during resharing (they have no key shares yet), while old participants who are being removed cannot call `respond()`. The only nodes that can both produce a valid signature AND call `respond()` are those in the intersection of old and new participant sets.

---

### Impact Explanation

If the intersection of old and new participant sets falls below the signing threshold — a normal governance scenario when rotating out compromised or offline nodes — every pending `sign`, `request_app_private_key`, and `verify_foreign_transaction` request queued before resharing started becomes permanently unresolvable. These requests time out via NEAR's yield-resume mechanism, causing the user's original transaction to fail. The deposit attached to the request is consumed and not returned to the user.

This matches the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."*

The pending-request map entries remain in contract storage until the yield timeout fires, at which point `return_signature_and_clean_state_on_success` is called with `Err(PromiseError::Failed)` and `fail_on_timeout` is scheduled: [8](#0-7) 

---

### Likelihood Explanation

Resharing is a routine governance operation triggered by `vote_new_parameters()` whenever participants need to be added or removed. The scenario where removed participants constitute a majority (dropping the remaining overlap below threshold) is realistic when rotating out a compromised cohort. No attacker action is required; the vulnerability is triggered by normal governance. The `verify_tee()` function can also autonomously trigger resharing when TEE attestations expire: [9](#0-8) 

This makes the trigger reachable without any privileged operator action beyond the threshold vote already required for resharing.

---

### Recommendation

In `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()`, replace the single `assert_caller_is_attested_participant_and_protocol_active()` call with a check that accepts callers who are attested participants in **either** the old (previous running) set or the new proposed set during `Resharing` state. Concretely:

- Add a helper `assert_caller_is_attested_participant_for_signing()` that, when the state is `Resharing`, checks membership against `previous_running_state.parameters.participants()` (the set that holds key shares) rather than the new proposed set.
- Alternatively, store the full pending request alongside the epoch ID at queue time and reject `respond()` calls whose epoch does not match the epoch at queue time, then re-queue the request after resharing completes.

The `ResharingContractState` already carries `previous_running_state`, so the old participant set is available on-chain: [10](#0-9) 

---

### Proof of Concept

1. Contract is in `Running` state with participants `{A, B, C}`, threshold 2. Epoch = 1.
2. User calls `sign(payload)` → yield queued, `pending_signature_requests` entry created.
3. Governance votes `vote_new_parameters` to replace `{A, B, C}` with `{D, E, F}` (full rotation). Contract transitions to `Resharing`.
4. Nodes `A`, `B`, `C` compute the threshold signature for the pending request (they hold epoch-1 key shares).
5. Node `A` calls `respond(request, signature)`.
6. `assert_caller_is_attested_participant_and_protocol_active()` calls `active_participants()` → returns `{D, E, F}` (new proposed set). Node `A` is not in `{D, E, F}` → **panic: "Caller must be an attested participant"**.
7. Nodes `D`, `E`, `F` have no epoch-1 key shares and cannot produce a valid signature. Any `respond()` call from them would fail the `signature_is_valid` check at line 642.
8. The yield times out. `return_signature_and_clean_state_on_success` is called with `Err`. `fail_on_timeout` fires. User's transaction fails and deposit is lost. [11](#0-10) [12](#0-11)

### Citations

**File:** crates/contract/src/lib.rs (L392-397)
```rust
        self.enqueue_yield_request(
            method_names::RETURN_SIGNATURE_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_signature_request(request, id),
        );
```

**File:** crates/contract/src/lib.rs (L563-577)
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
```

**File:** crates/contract/src/lib.rs (L653-666)
```rust
    #[handle_result]
    pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L691-713)
```rust
    #[handle_result]
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1762-1765)
```rust
                let res = running_state.transition_to_resharing_no_checks(&proposed_parameters);
                if let Some(resharing) = res {
                    self.protocol_state = ProtocolContractState::Resharing(resharing);
                }
```

**File:** crates/contract/src/lib.rs (L2254-2271)
```rust
        match signature {
            Ok(signature) => PromiseOrValue::Value(signature),
            Err(_) => {
                pending_requests::pop_oldest_pending_yield(
                    &mut self.pending_signature_requests,
                    &request,
                );

                let fail_on_timeout_gas = Gas::from_tgas(self.config.fail_on_timeout_tera_gas);
                let promise = Promise::new(env::current_account_id()).function_call(
                    method_names::FAIL_ON_TIMEOUT.to_string(),
                    vec![],
                    NearToken::from_near(0),
                    fail_on_timeout_gas,
                );
                near_sdk::PromiseOrValue::Promise(promise.as_return())
            }
        }
```

**File:** crates/contract/src/lib.rs (L2377-2403)
```rust
    /// Ensures that the caller is an attested participant
    /// in the currently active protocol phase.
    ///
    /// Active phases:
    /// - `Initializing` → uses proposed participants from generating_key
    /// - `Running` → uses current active participants
    /// - `Resharing` → uses new participants from resharing proposal
    ///
    /// Panics if:
    /// - The protocol is not active (e.g., NotInitialized)
    /// - The caller is not attested or not in the relevant participants set
    /// - The caller is not the signer account
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

**File:** crates/contract/src/state/resharing.rs (L27-39)
```rust
#[near(serializers=[borsh, json])]
#[derive(Debug)]
#[cfg_attr(feature = "dev-utils", derive(Clone, PartialEq))]
pub struct ResharingContractState {
    pub previous_running_state: RunningContractState,
    pub reshared_keys: Vec<KeyForDomain>,
    pub resharing_key: KeyEvent,
    pub cancellation_requests: HashSet<AuthenticatedAccountId>,
    /// Per-domain `ReconstructionThreshold` updates carried from the accepted
    /// proposal. Applied to the [`DomainRegistry`](crate::primitives::domain::DomainRegistry)
    /// when resharing completes; empty means "keep current per-domain thresholds".
    pub per_domain_thresholds: BTreeMap<DomainId, ReconstructionThreshold>,
}
```

**File:** crates/node/src/providers/ecdsa/key_resharing.rs (L32-38)
```rust

        anyhow::ensure!(
            new_keyshare.public_key == public_key,
            "Public key should not change after key resharing"
        );

        Ok(new_keyshare)
```
