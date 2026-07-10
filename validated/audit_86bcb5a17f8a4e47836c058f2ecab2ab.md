### Title
Node-Controlled `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (`File: crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` accepts `response.payload_hash` as a caller-supplied value and only checks that the MPC signature is valid over that hash. It never verifies that `payload_hash` was derived from the pending `request` stored in the contract. A single Byzantine MPC node (below threshold) can reuse a legitimate MPC signature obtained for one foreign-chain request to resolve a completely different pending request, delivering a forged attestation to the caller.

### Finding Description

**Root cause — caller-controlled parameter that should be derived from stored state**

In `respond` (regular signatures), the payload is taken from the stored `SignatureRequest`:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
```

The contract owns the payload; the node cannot substitute it. [1](#0-0) 

In `respond_verify_foreign_tx`, the payload hash is taken directly from the node-supplied `response`:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
).is_ok()
```

The contract only checks: *"is this a valid MPC signature over this hash?"* It never checks: *"does this hash correspond to the pending `request`?"* [2](#0-1) 

The `payload_hash` that should be verified is `SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))`. The contract has `request` but not `extracted_values`, so it cannot recompute the hash — but it also does nothing to bind the supplied hash to the request. [3](#0-2) 

**Attack path**

1. Two requests are pending: `request_A` (legitimate deposit) and `request_B` (attacker-controlled or a second legitimate deposit the attacker wants to double-serve).
2. The MPC network processes `request_A` honestly. The leader node obtains `(payload_hash_A, signature_A)` where `payload_hash_A = SHA-256(borsh(ForeignTxSignPayload { request_A, values_A }))`.
3. The malicious node (one Byzantine participant, below threshold) calls:
   ```
   respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: signature_A })
   ```
4. The contract checks: is `signature_A` valid over `payload_hash_A` using the MPC public key? **Yes** — the MPC network did sign it.
5. `request_B` is pending, so `resolve_yields_for` succeeds and the yield for `request_B` is resumed with `{ payload_hash_A, signature_A }`.
6. The caller of `request_B` receives a `VerifyForeignTransactionResponse` containing a valid MPC signature, but the `payload_hash` attests to `request_A`'s data, not `request_B`'s.

The caller cannot detect the substitution: `ForeignTxSignPayloadV1` includes the extracted values, which are not returned to the caller, so the caller cannot reconstruct the expected `payload_hash` to compare. [4](#0-3) 

### Impact Explanation

A bridge contract using `verify_foreign_transaction` to gate fund releases (the primary stated use case) would receive a structurally valid MPC-signed response for a request it submitted, but the `payload_hash` inside attests to a different foreign-chain transaction. The bridge contract has no way to detect this: it cannot reconstruct the expected hash without the extracted values, which are not included in the response. This enables a single Byzantine MPC node to cause invalid bridge execution — releasing funds for a non-existent or unfinalized foreign deposit — matching the **High** impact category: *"forged foreign-chain verification that causes invalid bridge execution or double-spend conditions."*

### Likelihood Explanation

Requires only one Byzantine MPC node (below the signing threshold) and two concurrently pending `verify_foreign_transaction` requests. Both conditions are realistic in production: the MPC network is designed to tolerate up to `n - threshold` Byzantine nodes, and concurrent foreign-chain verification requests are expected in any active bridge deployment. No privileged access, key material, or network-level attack is needed.

### Recommendation

The contract must bind `response.payload_hash` to the stored `request`. Two complementary approaches:

1. **Include extracted values in the response.** Change `VerifyForeignTransactionResponse` to carry `extracted_values: Vec<ExtractedValue>` alongside `payload_hash`. In `respond_verify_foreign_tx`, recompute `SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))` on-chain and assert it equals `response.payload_hash` before accepting the response. This mirrors how `respond` derives the payload from the stored request rather than trusting the node.

2. **Alternatively, store a commitment at request time.** If on-chain recomputation is too expensive, have nodes commit to the `payload_hash` during the MPC protocol and store that commitment in `pending_verify_foreign_tx_requests` at request time, then verify the response hash matches the stored commitment.

### Proof of Concept

```
// Setup: two pending requests exist
contract.verify_foreign_transaction(request_args_A);  // request_A pending
contract.verify_foreign_transaction(request_args_B);  // request_B pending

// Honest flow produces a valid signature for request_A
let payload_A = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request_A.request.clone(),
    values: vec![ExtractedValue::BitcoinExtractedValue(
        BitcoinExtractedValue::BlockHash([0xAA; 32].into()),
    )],
});
let payload_hash_A = payload_A.compute_msg_hash().unwrap();
let (sig_A, rec_id) = mpc_key.sign_prehash_recoverable(&payload_hash_A.0).unwrap();

// Byzantine node submits request_A's signature as the response for request_B
let forged_response = VerifyForeignTransactionResponse {
    payload_hash: payload_hash_A,   // hash of request_A's data
    signature: dtos::SignatureResponse::Secp256k1(
        dtos::K256Signature::from_ecdsa_recoverable(&sig_A, rec_id),
    ),
};

// Contract accepts: signature is valid over payload_hash_A, request_B is pending
contract.respond_verify_foreign_tx(request_B, forged_response)
    .expect("accepted — no binding check between payload_hash and request");

// Caller of request_B now holds a valid MPC signature that attests to request_A's data
```

The contract's only checks — attested participant, valid signature, pending request — all pass. The missing check is that `payload_hash` was derived from `request_B`. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L600-608)
```rust
                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

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
