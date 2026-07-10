### Title
`respond_verify_foreign_tx` does not verify `response.payload_hash` corresponds to the submitted `request` — (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that the MPC signature is valid over `response.payload_hash`, but never checks that `response.payload_hash` actually encodes the `ForeignChainRpcRequest` from the pending `request`. A malicious attested MPC participant can replay a valid `(payload_hash, signature)` pair from any previous legitimate response against a different pending request, causing the contract to resolve that request with forged foreign-chain data.

### Finding Description

In `respond_verify_foreign_tx` (`crates/contract/src/lib.rs` lines 691–754), the contract performs two checks before resolving the pending yield:

1. The caller is an attested participant.
2. The MPC signature is valid over `response.payload_hash` using the domain's root public key.

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

What is **never** checked is whether `response.payload_hash` is the hash of `ForeignTxSignPayload::V1 { request: request.request, values: ... }` — i.e., that the hash actually encodes the `ForeignChainRpcRequest` (including `tx_id`) from the pending request being resolved.

The `payload_hash` is defined as:

```
payload_hash = SHA-256(borsh(ForeignTxSignPayload::V1({ request: ForeignChainRpcRequest, values: Vec<ExtractedValue> })))
```

Since the contract cannot reconstruct this hash (it does not know `values`), it has no way to bind `payload_hash` to `request.request`. The contract resolves the pending yield with whatever `response` the caller supplies, as long as the signature over `payload_hash` is valid.

**Attack path:**

1. Attacker (an attested MPC participant) observes a legitimate `respond_verify_foreign_tx` call on-chain for `request_A` (e.g., Bitcoin `tx_id = [0xAA; 32]`), recording `(payload_hash_A, sig_A)`.
2. A new `verify_foreign_transaction` request for `request_B` (Bitcoin `tx_id = [0xBB; 32]`) is submitted and enters `pending_verify_foreign_tx_requests`.
3. The attacker calls `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: sig_A })` before the honest leader responds.
4. The contract checks: is `sig_A` valid over `payload_hash_A`? **Yes.** Does `request_B` exist in the pending map? **Yes.** It resolves `request_B`'s yield with `{ payload_hash_A, sig_A }`.
5. The caller of `request_B` receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes `tx_id_A`'s data, not `tx_id_B`'s.

The SDK's `ForeignChainSignatureVerifier::verify_signature` (`crates/near-mpc-sdk/src/foreign_chain.rs` lines 41–89) does check `expected_payload_hash == response.payload_hash`, but this is a client-side helper. The contract itself — the authoritative on-chain verifier — does not enforce this invariant.

### Impact Explanation

A bridge contract calling `verify_foreign_transaction` and trusting the MPC contract's on-chain verification (a reasonable assumption) would receive a `VerifyForeignTransactionResponse` whose `payload_hash` encodes a different transaction's data. If the bridge processes the response without independently recomputing the expected hash, it would be tricked into treating an unverified foreign-chain transaction as verified. This enables forged foreign-chain attestations and invalid bridge execution (e.g., crediting a deposit that was never made on the foreign chain).

**Impact category:** High — cross-chain replay / forged foreign-chain verification causing invalid bridge execution.

### Likelihood Explanation

Any single attested MPC participant can execute this attack with no threshold collusion. The required inputs (`payload_hash`, `signature`) are public on-chain data from any prior legitimate `respond_verify_foreign_tx` call. The attacker only needs to race the honest leader for a new pending request on the same domain, which is straightforward since `verify_foreign_transaction` is a public endpoint any user can call.

### Recommendation

The contract must bind `response.payload_hash` to the pending `request`. The most direct fix is to include a commitment to the `ForeignChainRpcRequest` in the signed payload in a form the contract can verify. For example, the signed payload could be structured as:

```
payload_hash = SHA-256(borsh(request.request) || SHA-256(borsh(values)))
```

so the contract can verify `SHA-256(borsh(request.request))` is a prefix of the pre-image. Alternatively, the contract can require the responder to supply `values` alongside the response, recompute `payload_hash` itself, and reject any mismatch:

```rust
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(),
}).compute_msg_hash()?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

### Proof of Concept

```
1. Submit verify_foreign_transaction for Bitcoin tx_id=[0xAA;32] (request_A).
2. Honest nodes respond; observe on-chain: respond_verify_foreign_tx(request_A, { payload_hash_A, sig_A }).
3. Submit verify_foreign_transaction for Bitcoin tx_id=[0xBB;32] (request_B).
4. As an attested participant, call:
     respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: sig_A })
5. Contract accepts (sig_A valid over payload_hash_A; request_B in pending map).
6. Caller of request_B receives VerifyForeignTransactionResponse { payload_hash: payload_hash_A, sig_A }.
   payload_hash_A encodes tx_id=[0xAA;32], not [0xBB;32].
7. Bridge contract processing request_B's response is given forged attestation data.
``` [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```
