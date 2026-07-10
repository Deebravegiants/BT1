### Title
Missing `payload_hash` Consistency Check in `respond_verify_foreign_tx` Enables Cross-Chain Replay of Foreign-Tx Signatures - (File: crates/contract/src/lib.rs)

### Summary
`respond_verify_foreign_tx` verifies that the submitted signature is cryptographically valid over `response.payload_hash`, but never checks that `response.payload_hash` is actually the canonical hash of `ForeignTxSignPayload{request, values}` for the specific `request` stored on-chain. A single malicious MPC leader can replay a threshold signature obtained for one foreign-chain request as the response to a completely different pending request, delivering a forged verification attestation to the waiting caller.

### Finding Description
The analog vulnerability class from the QuantAMM report is **incorrect/incomplete validation that allows an invalid value to pass a correctness check by reusing or omitting the check for the relevant parameter**. In QuantAMM, `_firstInt >= MIN32` was checked in place of each of `_thirdInt … _eighthInt`. In this codebase the same structural flaw appears in `respond_verify_foreign_tx`: the signature is verified against `response.payload_hash` (a caller-supplied value), but the contract never verifies that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload{ request, values }))` for the `request` that is actually pending.

The relevant code path is:

```rust
// crates/contract/src/lib.rs  lines 718-734
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← taken from the response, not recomputed

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // ← only proves sig covers *this* hash
    &secp_pk,               //   not that this hash covers *this* request
)
.is_ok()
``` [1](#0-0) 

Compare with the regular `respond` path, where the payload hash is taken from the on-chain `request`, not from the response:

```rust
// crates/contract/src/lib.rs  lines 600-608
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,           // ← derived from the stored request, not the response
    &expected_public_key,
)
``` [2](#0-1) 

The signed payload is defined as `SHA-256(borsh(ForeignTxSignPayload{ request, values }))`: [3](#0-2) 

The `request` field inside `ForeignTxSignPayloadV1` carries the chain-specific `tx_id` and extractor list: [4](#0-3) 

The conversion from `VerifyForeignTransactionRequestArgs` to the stored `VerifyForeignTransactionRequest` does not derive or store any commitment to the expected payload hash: [5](#0-4) 

After the (incomplete) signature check passes, the contract resolves the yield for `request` and delivers the unchecked `response` to the original caller: [6](#0-5) 

### Impact Explanation
A single malicious MPC node acting as signing leader for request B obtains the combined threshold signature `sig_B` over `hash(request_B, values_B)`. It then calls `respond_verify_foreign_tx(request = A, response = { payload_hash = hash(request_B, values_B), signature = sig_B })` for a different pending request A. The contract:

1. Verifies `sig_B` over `hash(request_B, values_B)` — **passes** (the signature is genuinely valid).
2. Looks up request A in `pending_verify_foreign_tx_requests` — **found**.
3. Delivers `{ payload_hash = hash(request_B, values_B), signature = sig_B }` to the caller of request A.

The caller of request A receives a `VerifyForeignTransactionResponse` that attests to the finality of transaction B, not transaction A. Any bridge contract that does not independently recompute and compare the expected `payload_hash` (as the SDK's `ForeignChainSignatureVerifier` does) will accept this as proof that transaction A was verified, enabling invalid bridge execution or double-spend conditions. [7](#0-6) 

The SDK-level check is the only guard; the on-chain contract provides none.

### Likelihood Explanation
The attacker must be a single attested MPC participant who has served as signing leader for at least one prior `verify_foreign_tx` request (giving them access to a combined threshold signature). No threshold-level collusion is required. The `respond_verify_foreign_tx` endpoint is open to any attested participant: [8](#0-7) 

Bridge integrators who rely on the contract's on-chain acceptance as the sole proof of correctness (without calling `ForeignChainSignatureVerifier`) are directly exploitable.

### Recommendation
Before accepting the response, recompute the expected payload hash from the on-chain `request` and the node-supplied `values`, and assert equality with `response.payload_hash`. Because the contract does not currently receive `values`, the simplest fix is to require the responding node to also submit the `values` alongside the signature, so the contract can verify:

```
assert response.payload_hash == SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))
```

Alternatively, bind the signature to the request by including the `request` hash as an additional domain-separation prefix in the signed message, so a signature produced for request B is cryptographically invalid for request A.

### Proof of Concept
1. User submits `verify_foreign_transaction(request_A)` — contract stores request A.
2. User submits `verify_foreign_transaction(request_B)` — contract stores request B.
3. Malicious leader processes request B honestly, obtaining `sig_B = ECDSA_sign(hash(request_B, values_B))`.
4. Malicious leader calls:
   ```
   respond_verify_foreign_tx(
     request  = request_A,
     response = { payload_hash: hash(request_B, values_B), signature: sig_B }
   )
   ```
5. Contract verifies `sig_B` over `hash(request_B, values_B)` — valid. Resolves yield for request A.
6. Caller of request A receives `{ payload_hash: hash(request_B, values_B), signature: sig_B }` — a forged attestation for transaction B delivered as the result of transaction A's verification request.

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

**File:** crates/contract/src/lib.rs (L697-705)
```rust
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L718-734)
```rust
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L48-64)
```rust
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
```
