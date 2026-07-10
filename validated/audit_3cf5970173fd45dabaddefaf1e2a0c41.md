### Title
`respond_verify_foreign_tx` Does Not Validate `payload_hash` Against the Pending Request, Enabling Cross-Request Signature Replay — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` contract method verifies that the submitted ECDSA signature is valid over the caller-supplied `response.payload_hash`, but never verifies that `payload_hash` is actually derived from the pending `VerifyForeignTransactionRequest` stored on-chain. A single Byzantine attested participant (below the signing threshold) can replay a threshold signature produced for a legitimately resolved request R1 to resolve a completely different pending request R2, delivering a forged foreign-chain verification attestation to R2's caller.

---

### Finding Description

The `respond_verify_foreign_tx` function at `crates/contract/src/lib.rs` lines 691–754 performs the following checks:

1. Caller is an attested participant.
2. Protocol is running.
3. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key.
4. `request` exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What it does **not** check is that `response.payload_hash` is the canonical hash of `SHA-256(borsh(ForeignTxSignPayload { request, values }))` for the specific `request` being resolved. The contract cannot recompute this hash because the `values` (extracted foreign-chain observations) are never stored on-chain — they exist only in the MPC nodes' memory during signing. [2](#0-1) 

The canonical payload hash is computed node-side from `(request, observed_values)` and signed by the threshold network. The contract receives only the hash and signature, and has no way to re-derive the hash from the request alone. [3](#0-2) 

Because the contract only checks `verify_ecdsa_signature(sig, payload_hash, root_pk)` and `request ∈ pending_map`, a valid `(payload_hash, signature)` pair produced for any prior request R1 can be submitted as the response for any other pending request R2 that shares the same domain. The contract will accept it, drain R2's yield queue, and return the false `{payload_hash_R1, signature_R1}` to R2's caller. [4](#0-3) 

The SDK helper `ForeignChainSignatureVerifier::verify_signature` does perform the missing check — it recomputes the expected hash from `(request, expected_values)` and compares it to `response.payload_hash` — but this check lives off-chain in the client SDK, not in the contract. [5](#0-4) 

Any bridge or NEAR smart contract that trusts the MPC contract's resolved response without independently re-verifying `payload_hash` against its own expected values will accept the forged attestation.

---

### Impact Explanation

**High — Forged foreign-chain verification enabling invalid bridge execution.**

The MPC contract's `verify_foreign_transaction` / `respond_verify_foreign_tx` flow is the trust anchor for bridge inbound flows (e.g., Omnibridge). A bridge contract that calls `verify_foreign_transaction(tx_id=Y)` and receives a response expects the MPC network to have attested that transaction Y occurred on the foreign chain with the requested properties. After this attack, the bridge receives a response whose `payload_hash` encodes a completely different transaction (tx_id=X), but the signature is valid. A bridge that does not re-verify `payload_hash` against its own expected values will conclude that tx Y was verified and release funds, enabling a double-spend or invalid bridge execution.

Additionally, once R2 is resolved with the false response, it is permanently removed from `pending_verify_foreign_tx_requests` and can never be legitimately re-resolved, permanently corrupting the request lifecycle for R2. [6](#0-5) 

---

### Likelihood Explanation

**Moderate.** The attacker must be a single attested MPC participant (below the signing threshold). No threshold collusion is required. The attacker:

1. Observes any on-chain `respond_verify_foreign_tx` call for a legitimately resolved request R1, extracting `(payload_hash_R1, signature_R1)` from the transaction arguments (all on-chain, public).
2. Submits a new `verify_foreign_transaction(R2)` for a different foreign-chain transaction (e.g., a non-existent or under-confirmed tx).
3. Immediately calls `respond_verify_foreign_tx(R2, {payload_hash_R1, signature_R1})`.

Steps 1–3 require no cryptographic capability beyond being an attested participant. The signature is fully reusable because the contract performs no nonce, request-binding, or domain-separation check on `payload_hash`. [7](#0-6) 

---

### Recommendation

The contract must bind `payload_hash` to the specific pending request being resolved. Since the contract cannot recompute the full `ForeignTxSignPayload` hash (it lacks `values`), the recommended fix is to include a commitment to the `request` in the signed payload in a way the contract can verify independently of `values`. Two concrete options:

1. **Require the responder to submit `values` alongside `payload_hash`**: The contract recomputes `SHA-256(borsh(ForeignTxSignPayload { request, values }))` and asserts it equals `response.payload_hash`. This is the most robust fix and mirrors how the SDK's `verify_signature` works.

2. **Bind the request hash into the signed payload at a fixed offset**: Change `ForeignTxSignPayload` so that the first 32 bytes of the Borsh encoding are always `SHA-256(borsh(request))`. The contract can then verify `payload_hash` starts with the expected request commitment. This avoids transmitting `values` on-chain but requires a protocol change.

Option 1 is analogous to the Beacon-Kit recommendation: retrieve the authoritative source of truth (extracted values) and validate the submitted response against it during the resolution step.

---

### Proof of Concept

**Setup**: MPC network is running with participants P1 (attacker), P2, P3 (threshold = 2). Domain 0 is a ForeignTx domain (Secp256k1).

**Step 1 — Observe a legitimate resolution:**
Alice submits `verify_foreign_transaction(Bitcoin, tx_id=X, extractors=[BlockHash])`. The MPC network queries Bitcoin, observes `block_hash=H_X`, computes `payload_hash_1 = SHA-256(borsh(ForeignTxSignPayload{request_X, [H_X]}))`, and produces threshold signature `sig_1`. P1 (or any observer) reads `(payload_hash_1, sig_1)` from the on-chain `respond_verify_foreign_tx` transaction.

**Step 2 — Submit a fraudulent request:**
P1 (attested participant) calls `verify_foreign_transaction(Bitcoin, tx_id=Y, extractors=[BlockHash])` where tx Y does not exist on Bitcoin (or has 0 confirmations). This creates a pending entry for request R2 in `pending_verify_foreign_tx_requests`.

**Step 3 — Replay the signature:**
P1 calls `respond_verify_foreign_tx(request=R2, response={payload_hash=payload_hash_1, signature=sig_1})`.

**Contract execution:**
- `assert_caller_is_attested_participant_and_protocol_active()` → passes (P1 is attested).
- `verify_ecdsa_signature(sig_1, payload_hash_1, root_pk)` → passes (sig_1 is a valid threshold signature over payload_hash_1).
- `pending_verify_foreign_tx_requests.get(R2)` → found.
- `resolve_yields_for(R2, serialize({payload_hash_1, sig_1}))` → R2's yield is resumed with the false response.

**Result:** The caller of R2 receives `{payload_hash_1, sig_1}`. `payload_hash_1` encodes tx X's block hash, not tx Y's. A bridge contract that checks only `verify_ecdsa_signature(sig_1, payload_hash_1, root_pk)` without re-verifying `payload_hash_1` against its expected values for tx Y will conclude that tx Y was verified and release funds. R2 is permanently removed from the pending map. [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** crates/contract/src/lib.rs (L691-754)
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

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-47)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L54-87)
```rust
    pub(super) async fn make_verify_foreign_tx_leader(
        &self,
        id: SignatureId,
    ) -> anyhow::Result<((dtos::ForeignTxSignPayload, Signature), VerifyingKey)> {
        let foreign_tx_request = self.verify_foreign_tx_request_store.get(id).await?;

        let domain_data = self
            .ecdsa_signature_provider
            .domain_data(foreign_tx_request.domain_id)?;
        let (presignature_id, presignature) = domain_data.presignature_store.take_owned().await;
        let participants = presignature.participants.clone();
        let channel = self.ecdsa_signature_provider.new_channel_for_task(
            VerifyForeignTxTaskId::VerifyForeignTx {
                id,
                presignature_id,
            },
            participants,
        )?;

        let response_payload = self
            .execute_foreign_chain_request(
                &foreign_tx_request.request,
                foreign_tx_request.payload_version,
            )
            .await?;

        let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

        let response = self
            .ecdsa_signature_provider
            .make_signature_leader_given_parameters(sign_request, presignature, channel)
            .await?;
        Ok(((response_payload, response.0), response.1))
    }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L41-89)
```rust
impl ForeignChainSignatureVerifier {
    pub fn verify_signature(
        self,
        response: &VerifyForeignTransactionResponse,
        // TODO(#2232): don't use interface API types for public keys
        public_key: &PublicKey,
    ) -> Result<(), VerifyForeignChainError> {
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
        let verification_result = match (public_key, &response.signature) {
            (
                PublicKey::Secp256k1(secp256k1_public_key),
                SignatureResponse::Secp256k1(k256_signature),
            ) => near_mpc_signature_verifier::verify_ecdsa_signature(
                k256_signature,
                &expected_payload_hash,
                secp256k1_public_key,
            ),
            (PublicKey::Ed25519(ed25519_public_key), SignatureResponse::Ed25519 { signature }) => {
                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    expected_payload_hash.as_slice(),
                    ed25519_public_key,
                )
            }
            // TODO(#2234): improve types so these errors can't happen
            (PublicKey::Bls12381(_bls12381_g2_public_key), _) => {
                return Err(VerifyForeignChainError::UnexpectedSignatureScheme);
            }
            _ => return Err(VerifyForeignChainError::UnexpectedSignatureScheme),
        };

        verification_result.map_err(|_| VerifyForeignChainError::SignatureVerificationFailed)
    }
```

**File:** crates/contract/src/pending_requests.rs (L62-88)
```rust
/// Resume every yield queued for `request` with `response_bytes`, draining the
/// fan-out map in one pass. Returns `Err(RequestNotFound)` if the map held no entry.
///
/// Resuming a yield that has already timed out is a no-op at the SDK level.
pub(crate) fn resolve_yields_for<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: &K,
    response_bytes: Vec<u8>,
) -> Result<(), Error>
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();

    if resumed > 0 {
        Ok(())
    } else {
        Err(InvalidParameters::RequestNotFound.into())
    }
}
```
