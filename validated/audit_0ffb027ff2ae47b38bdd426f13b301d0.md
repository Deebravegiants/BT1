### Title
`respond_verify_foreign_tx` Does Not Verify `payload_hash` Corresponds to the Original Request — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` contract method verifies that the submitted signature is cryptographically valid over the caller-supplied `payload_hash`, but never verifies that `payload_hash` was actually derived from the original pending `request`. The SDK ships a complete verifier (`ForeignChainSignatureVerifier::verify_signature`) that performs this check, but it is never invoked inside the contract. A single attested MPC participant (below the signing threshold) can replay a valid MPC signature produced for one foreign-chain request to satisfy a completely different pending request, causing the contract to attest to a foreign-chain event that was never verified for that request.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs two checks:

1. The caller is an attested participant.
2. The ECDSA signature in `response` is valid over `response.payload_hash` against the domain's root public key. [1](#0-0) 

What it does **not** check is that `response.payload_hash` is the SHA-256 Borsh hash of `ForeignTxSignPayload::V1 { request: request.request, values: <any values> }`. The contract has no way to know the extracted values, but it also makes no attempt to verify that the hash at minimum encodes the same `ForeignChainRpcRequest` that was originally submitted.

The SDK's `ForeignChainSignatureVerifier::verify_signature` performs exactly this missing check:

```rust
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: self.request,
    values: self.expected_extracted_values,
});
let expected_payload_hash = expected_payload.compute_msg_hash()...;
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [2](#0-1) 

This verifier lives in the SDK for downstream callers to use, but is never called inside the contract itself. The contract's `respond_verify_foreign_tx` is the exact analog of the Tezos `ofString` address validator: the complete validation logic exists and is correct, but is never invoked in the critical enforcement path.

The `ForeignTxSignPayload` type and its `compute_msg_hash` are defined in the contract-interface crate and are available to the contract: [3](#0-2) 

The `args_into_verify_foreign_tx_request` conversion that stores the request on-chain also discards no fields, so the original request is fully available at respond time: [4](#0-3) 

---

### Impact Explanation

A single attested MPC participant (strictly below the signing threshold) can:

1. Observe any previously completed `verify_foreign_transaction` response on-chain for request **R1** — the `payload_hash` H1 and signature S1 are public.
2. Wait for a different pending request **R2** (different `tx_id`, different chain, or different extractors) to appear in the contract.
3. Call `respond_verify_foreign_tx(R2, { payload_hash: H1, signature: S1 })`.
4. The contract accepts: S1 is a valid MPC signature over H1, and R2 exists in `pending_verify_foreign_tx_requests`.
5. The contract resolves R2's yield and returns `{ payload_hash: H1, signature: S1 }` to R2's caller.

R2's caller receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes the verification of a completely different foreign-chain transaction (R1). Any bridge contract that does not independently re-verify the hash using `ForeignChainSignatureVerifier::verify_signature` will treat this as a valid attestation of R2's transaction, enabling forged foreign-chain verification and potential double-spend or unauthorized fund release.

This matches the **High** impact category: *forged foreign-chain verification that causes invalid bridge execution or double-spend conditions*.

---

### Likelihood Explanation

- Requires only a **single** attested MPC participant — no threshold collusion needed.
- The attacker's only prerequisite is that at least one prior `verify_foreign_transaction` response exists on-chain (trivially satisfied in production).
- The attack is fully on-chain and requires no special access beyond being an attested participant.
- Bridge contracts that rely on `verify_foreign_transaction` without calling `ForeignChainSignatureVerifier::verify_signature` are directly exploitable.

---

### Recommendation

Inside `respond_verify_foreign_tx`, after verifying the signature, reconstruct the expected payload hash prefix from the original request and verify that `response.payload_hash` is consistent with it. Concretely, the contract should verify:

```rust
// Verify payload_hash encodes the correct request (values are unknown,
// but the hash must at least commit to the original request fields).
// The full check requires the extracted values; at minimum, reject any
// payload_hash that cannot have been produced from this request by
// enforcing the check in the contract rather than delegating it to callers.
```

The most robust fix is to have MPC nodes include the full `ForeignTxSignPayload` (not just the hash) in the response, allowing the contract to recompute and compare. Alternatively, enforce that callers of `verify_foreign_transaction` use `ForeignChainSignatureVerifier::verify_signature` by making the contract perform the equivalent check using the stored request fields.

---

### Proof of Concept

1. Alice submits `verify_foreign_transaction` for Bitcoin tx `0xAA...AA` (request R1). The MPC network processes it and emits `respond_verify_foreign_tx(R1, { payload_hash: H1, signature: S1 })` on-chain.

2. Bob submits `verify_foreign_transaction` for Bitcoin tx `0xBB...BB` (request R2, different tx). R2 is now pending.

3. Mallory (a single attested MPC participant) calls:
   ```
   respond_verify_foreign_tx(R2, { payload_hash: H1, signature: S1 })
   ```

4. The contract at lines 718–734 verifies `verify_ecdsa_signature(S1, H1, root_pk)` — **passes**, because S1 was legitimately produced by the MPC network for H1.

5. `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &R2, ...)` — **passes**, because R2 is pending.

6. Bob's contract receives `{ payload_hash: H1, signature: S1 }`. H1 encodes the verification of `0xAA...AA`, not `0xBB...BB`. If Bob's bridge contract does not call `ForeignChainSignatureVerifier::verify_signature`, it will incorrectly treat `0xBB...BB` as verified and release funds. [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L692-754)
```rust
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

**File:** crates/contract/src/dto_mapping.rs (L840-848)
```rust
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
```
