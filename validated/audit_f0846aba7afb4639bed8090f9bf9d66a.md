### Title
Unvalidated `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Replay of Stale Foreign-Chain Attestations — (File: `crates/contract/src/lib.rs`)

---

### Summary

`MpcContract::respond_verify_foreign_tx` verifies only that `response.signature` is a valid ECDSA signature over the caller-supplied `response.payload_hash`. It never recomputes or validates that `payload_hash` is the canonical hash of `ForeignTxSignPayload` derived from the accompanying `request`. A single Byzantine attested participant can replay a previously observed on-chain response — carrying a stale `payload_hash` — against a newly queued pending request that shares the same request key, causing the caller to receive a forged foreign-chain attestation.

---

### Finding Description

`respond_verify_foreign_tx` performs the following validation:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
```

It then resolves all queued yields for the matching request key with the raw `response`:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
```

The contract never checks that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values: <actual observed values> }))`. The `payload_hash` is entirely attacker-controlled; the only constraint is that the submitted signature must verify over it under the MPC root public key.

The `ForeignTxSignPayload` that nodes actually sign contains only `request` and `values` — no per-submission nonce, entropy, or timestamp:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

This means a response produced for request R at time T₁ (with extracted values V₁, producing `payload_hash_old`) is cryptographically indistinguishable from a correct response for the same request R at time T₂ (with extracted values V₂, producing `payload_hash_new`), as far as the contract is concerned. Both carry a valid MPC root-key signature; the contract accepts whichever arrives first.

**Replay attack path:**

1. User submits `verify_foreign_transaction` for Bitcoin tx T. MPC network signs `payload_hash_old = SHA256(borsh({ request: T, values: [BlockHash(H₁)] }))`. Leader calls `respond_verify_foreign_tx`; the response is recorded on-chain.
2. A blockchain reorganization occurs; tx T is now in block H₂ (or unconfirmed).
3. User resubmits the identical `verify_foreign_transaction` request (same tx_id, same extractors, same domain). A new yield is queued under the same request key.
4. A Byzantine attested participant reads the old on-chain response (step 1) and calls `respond_verify_foreign_tx(request=R, response={payload_hash: payload_hash_old, signature: sig_old})`.
5. The contract checks: pending request for R exists ✓; signature valid over `payload_hash_old` ✓. It resolves the yield and delivers `payload_hash_old` to the caller.
6. The caller receives an attestation that tx T is in block H₁ — a block that may no longer be canonical.

---

### Impact Explanation

The caller (e.g., an Omnibridge contract) receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes stale or fabricated extracted values. If the bridge contract trusts this hash to gate minting or settlement, it can be made to:

- **Accept a reorganized-away deposit** — minting tokens for a transaction that is no longer confirmed on the foreign chain (double-spend).
- **Attest incorrect extracted values** (block hash, amount, program ID) — enabling invalid bridge execution.

This matches the allowed High impact: *"Cross-chain replay, forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- **Attacker role**: Any single attested MPC participant. No threshold collusion required; the old response is publicly visible on-chain after step 1.
- **Preconditions**: (a) The same `ForeignChainRpcRequest` key is submitted more than once (normal after a timeout or reorg); (b) the foreign chain state changes between submissions (blockchain reorganizations are routine on Bitcoin and EVM chains).
- **No cryptographic work required**: The attacker simply re-broadcasts an already-valid on-chain transaction.

Likelihood is **Medium**: reorganizations are infrequent but well-known events; the attack requires only one Byzantine participant out of N, and the old response is always publicly available.

---

### Recommendation

Bind each `verify_foreign_transaction` submission to a unique, unpredictable nonce (e.g., the NEAR receipt ID or a random entropy value already present in the indexer's `VerifyForeignTxRequest`). Include this nonce in `ForeignTxSignPayloadV1` so that the hash is unique per submission:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
    pub nonce: [u8; 32],   // receipt_id or per-request entropy
}
```

Store the nonce in the pending-request map entry and validate in `respond_verify_foreign_tx` that the nonce embedded in the response's `payload_hash` matches the stored nonce. This makes every response non-replayable across submissions.

---

### Proof of Concept

**Step 1** — Submit request and observe the on-chain response:

```
User → verify_foreign_transaction({ tx_id: T, extractors: [BlockHash], domain_id: D })
MPC  → respond_verify_foreign_tx(request=R, response={ payload_hash: H_old, sig: S_old })
       // H_old = SHA256(borsh({ request: R, values: [BlockHash(block1)] }))
       // S_old is a valid MPC root-key signature over H_old
       // Both are now publicly visible on-chain
```

**Step 2** — Reorg occurs; user resubmits:

```
User → verify_foreign_transaction({ tx_id: T, extractors: [BlockHash], domain_id: D })
       // New yield queued under the same request key R
```

**Step 3** — Byzantine participant replays the old response:

```rust
// Attacker reads H_old and S_old from the NEAR blockchain (step 1 tx)
contract.respond_verify_foreign_tx(
    request = R,                                    // matches pending key
    response = VerifyForeignTransactionResponse {
        payload_hash: H_old,                        // stale hash (block1)
        signature: S_old,                           // valid sig over H_old
    }
)
// Contract checks: sig valid over H_old ✓, pending request for R ✓
// Resolves yield → caller receives H_old (attesting block1, which is reorganized away)
```

**Step 4** — Bridge contract is deceived:

```rust
// Bridge calls ForeignChainSignatureVerifier::verify_signature with
// expected_extracted_values = [BlockHash(block1)]  ← attacker chose block1 intentionally
// Verification passes; bridge mints tokens for a tx no longer on the canonical chain
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

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
