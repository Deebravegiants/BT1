### Title
TEE Verifier Account Voted In But Never Dispatched in `submit_participant_info` — (`crates/contract/src/lib.rs`)

---

### Summary

The `MpcContract` stores a `tee_verifier_account_id: Option<AccountId>` field that participants can set via a threshold governance vote (`vote_tee_verifier_change`). The design intent — documented in `docs/design/attestation-verifier-contract.md` and tracked by `TODO(#3639)` — is that once a verifier is voted in, `submit_participant_info` will dispatch DCAP quote verification to that external contract. However, the actual `submit_participant_info` implementation never reads `tee_verifier_account_id` and always falls through to the in-WASM `verify_locally()` path. The field is explicitly annotated "Not yet used to dispatch verification." The governance vote succeeds and updates state, but has zero effect on the verification path.

---

### Finding Description

`MpcContract` declares:

```rust
/// The verifier contract account trusted for DCAP verification, or [`None`]
/// until participants vote one in. Not yet used to dispatch verification.
// TODO(#3639): once participants have voted a verifier in, make this
// non-optional via a migration that requires it be set.
tee_verifier_account_id: Option<AccountId>,
tee_verifier_votes: TeeVerifierVotes,
``` [1](#0-0) 

The contract exposes `vote_tee_verifier_change` (registered in `method_names.rs`) and `withdraw_tee_verifier_vote` (implemented at line 1655), giving participants a complete governance round-trip to elect a trusted external verifier. [2](#0-1) 

When the threshold is reached the design document specifies that `submit_participant_info` should call:

```rust
Promise::new(self.tee_verifier_account_id.clone())
    .function_call("verify_quote".into(), ...)
    .then(Self::ext(...).resolve_verification(account_id));
``` [3](#0-2) 

Instead, the production `submit_participant_info` calls `self.tee_state.add_participant(...)`, which internally calls `attestation.verify_locally(...)` and never touches `tee_verifier_account_id`:

```rust
// TODO(#3264): run DCAP in the verifier contract (Promise + callback) and
// do the post-DCAP checks here, instead of verifying locally in-WASM.
let AcceptedAttestation { ... } = attestation.verify_locally(...)?;
``` [4](#0-3) 

The standalone `tee-verifier` contract (`crates/tee-verifier/src/lib.rs`) is already implemented and tested, but `mpc-contract` never calls it. [5](#0-4) 

---

### Impact Explanation

**Medium.** The broken invariant is: *a threshold governance vote to change the TEE verifier should re-route future attestation verification to the elected contract.* Because `tee_verifier_account_id` is never read by `submit_participant_info`, the vote is a silent no-op. Two concrete consequences:

1. **Verifier rotation is non-functional.** The design document explicitly describes verifier rotation as the primary remediation path when a DCAP signature-chain flaw is discovered. If such a flaw allows a non-genuine TEE to pass `verify_locally()`, participants cannot fix it by voting in a patched verifier — the old in-WASM path continues regardless.

2. **Governance state diverges from enforcement state.** Participants who reach threshold on `vote_tee_verifier_change` believe they have changed the security policy governing future attestations. They have not. Any subsequent `submit_participant_info` call is still verified by the old in-WASM code, breaking the production safety invariant that governance votes take effect.

This does not require threshold-or-above collusion; it is a structural gap in the implementation that any observer can confirm by reading the contract code.

---

### Likelihood Explanation

The governance infrastructure (`vote_tee_verifier_change`, `withdraw_tee_verifier_vote`, `tee_verifier_votes`) is fully wired and callable by any active participant. The gap is invisible at the call-site: the vote transaction succeeds, `tee_verifier_account_id` is updated in state, and no error is returned. Participants have no on-chain signal that the elected verifier is not being used. The likelihood that this gap persists into a production incident is elevated precisely because the governance path appears to work.

---

### Recommendation

Wire `tee_verifier_account_id` into `submit_participant_info` as described in `docs/design/attestation-verifier-contract.md`: when `tee_verifier_account_id` is `Some`, use the yield-resume pattern to dispatch `verify_quote` to the external verifier contract and run post-DCAP checks in the `resolve_verification` callback; fall back to `verify_locally()` only when it is `None` (i.e., before any verifier has been voted in). Until this is done, `vote_tee_verifier_change` should either be disabled or emit a clear on-chain warning that the vote has no enforcement effect.

---

### Proof of Concept

1. Participant calls `vote_tee_verifier_change(candidate_account_id, expected_code_hash)` until threshold is reached. `tee_verifier_account_id` is set to `candidate_account_id` in contract state.
2. A node calls `submit_participant_info(dstack_attestation, tls_pk)`.
3. Execution enters `tee_state.add_participant(...)` → `attestation.verify_locally(...)`. The field `self.tee_verifier_account_id` is never read; no cross-contract call is made.
4. The attestation is accepted or rejected solely by the in-WASM `dcap_qvl::verify::verify` path, identical to the pre-vote behavior.
5. The elected verifier contract receives zero calls. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L167-172)
```rust
    /// The verifier contract account trusted for DCAP verification, or [`None`]
    /// until participants vote one in. Not yet used to dispatch verification.
    // TODO(#3639): once participants have voted a verifier in, make this
    // non-optional via a migration that requires it be set.
    tee_verifier_account_id: Option<AccountId>,
    tee_verifier_votes: TeeVerifierVotes,
```

**File:** crates/contract/src/lib.rs (L795-815)
```rust
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
```

**File:** crates/near-mpc-contract-interface/src/method_names.rs (L33-34)
```rust
pub const VOTE_TEE_VERIFIER_CHANGE: &str = "vote_tee_verifier_change";
pub const WITHDRAW_TEE_VERIFIER_VOTE: &str = "withdraw_tee_verifier_vote";
```

**File:** docs/design/attestation-verifier-contract.md (L438-453)
```markdown
                // Cross-contract call to the verifier. Its `.then` callback
                // (`resolve_verification`) is the bridge that turns the
                // verifier's response into a `promise_yield_resume` on the
                // yield this method registered above.
                Promise::new(self.tee_verifier_account_id.clone())
                    .function_call(
                        "verify_quote".into(),
                        borsh::to_vec(&(quote, collateral)).unwrap(),
                        NearToken::from_yoctonear(0),
                        Gas::from_tgas(VERIFIER_GAS_TGAS),
                    )
                    .then(
                        Self::ext(env::current_account_id())
                            .with_static_gas(Gas::from_tgas(RESOLVE_GAS_TGAS))
                            .resolve_verification(account_id),
                    );
```

**File:** crates/contract/src/tee/tee_state.rs (L150-175)
```rust
    /// Adds a participant attestation for the given node iff the attestation succeeds verification.
    pub(crate) fn add_participant(
        &mut self,
        node_id: NodeId,
        attestation: Attestation,
        tee_upgrade_deadline_duration: Duration,
    ) -> Result<ParticipantInsertion, AttestationSubmissionError> {
        let expected_report_data: ReportData = ReportDataV1::new(
            *node_id.tls_public_key.as_bytes(),
            *node_id.account_public_key.as_bytes(),
        )
        .into();

        let accepted_measurements = self.get_accepted_measurements();
        // TODO(#3264): run DCAP in the verifier contract (Promise + callback) and
        // do the post-DCAP checks here, instead of verifying locally in-WASM.
        let AcceptedAttestation {
            attestation: verified_attestation,
            advisory_ids,
        } = attestation.verify_locally(
            expected_report_data.into(),
            Self::current_time_seconds(),
            &self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration),
            &self.get_allowed_launcher_compose_hashes(),
            &accepted_measurements,
        )?;
```

**File:** crates/tee-verifier/src/lib.rs (L49-63)
```rust
    pub fn verify_quote(
        &self,
        #[serializer(borsh)] quote: QuoteBytes,
        #[serializer(borsh)] collateral: Collateral,
    ) -> VerificationResult {
        let now_seconds = env::block_timestamp_ms() / 1000;
        let quote_bytes: Vec<u8> = quote.into_dcap_type();
        let collateral = collateral.into_dcap_type();
        match dcap_qvl::verify::verify(&quote_bytes, &collateral, now_seconds) {
            Ok(report) => VerificationResult::Verified(report.into_interface_type()),
            Err(err) => {
                VerificationResult::Rejected(VerifierError::DcapVerification(err.to_string()))
            }
        }
    }
```
