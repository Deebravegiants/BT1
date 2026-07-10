### Title
`respond_verify_foreign_tx` Accepts Caller-Supplied `payload_hash` Without Binding It to the Submitted Request - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid MPC signature over `response.payload_hash`, but never checks that `response.payload_hash` was actually derived from the `request` argument. A single Byzantine MPC node (attested participant, below signing threshold) can replay a valid signature produced for a prior legitimate request to resolve any pending foreign-tx request with a fabricated `payload_hash`, bypassing the foreign-chain verification guarantee.

### Finding Description

The `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs` performs the following checks:

1. Caller is an attested participant.
2. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key.
3. A pending request matching `request` exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What it does **not** check is that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request: request.request, values: <actual observed values> }))`. The hash is taken verbatim from the caller-supplied `response` struct: [2](#0-1) 

Compare this with the regular `respond` function, where the hash is taken from the **stored** request payload, not from the response: [3](#0-2) 

The signed payload is defined as `SHA-256(borsh(ForeignTxSignPayload { request, values }))`, where `values` are the extracted on-chain observations: [4](#0-3) 

Because the contract never re-derives or validates the hash against the stored request, any valid MPC signature over any 32-byte value is accepted as a valid response for any pending foreign-tx request.

### Impact Explanation

**Impact: High** — forged foreign-chain verification / invalid bridge execution.

A Byzantine MPC node that has participated in at least one legitimate signing round possesses a valid root-key signature `S` over hash `H = SHA-256(borsh(ForeignTxSignPayload { request: A, values: [...] }))`. It can call `respond_verify_foreign_tx` for any pending request `B` with `response.payload_hash = H` and `response.signature = S`. The contract accepts the call, removes request `B` from `pending_verify_foreign_tx_requests`, and delivers `{ payload_hash: H, signature: S }` to the caller of request `B`.

The caller receives a `VerifyForeignTransactionResponse` whose `payload_hash` corresponds to a completely different transaction's observed values. Any bridge contract that does not independently re-derive and compare the expected hash (e.g., one that does not use `ForeignChainSignatureVerifier::verify_signature` from the SDK) will treat this as a valid attestation of on-chain state that was never actually verified. [5](#0-4) 

The SDK-side check is caller-optional and not enforced by the contract.

### Likelihood Explanation

**Likelihood: Medium.**

The attacker must be an attested MPC participant (requires passing TEE attestation). However, once attested, a single node can:

1. Participate honestly in signing any legitimate foreign-tx request `A` to obtain `(H, S)`.
2. Submit `respond_verify_foreign_tx` for any other pending request `B` with `payload_hash = H, signature = S`.

No threshold collusion is required beyond what honest nodes already

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

**File:** crates/contract/src/lib.rs (L718-747)
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L47-64)
```rust
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
```
