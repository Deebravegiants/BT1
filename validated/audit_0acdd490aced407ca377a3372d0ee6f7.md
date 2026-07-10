### Title
Missing `payload_hash` Binding to `request` in `respond_verify_foreign_tx` Allows Cross-Request Signature Replay - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` accepts a caller-supplied `response.payload_hash` and only verifies that the ECDSA signature is valid over that hash against the **root** public key. It never validates that `payload_hash` is the SHA-256 Borsh hash of `ForeignTxSignPayload{ request: <the pending request>, values: <...> }`. A single Byzantine attested participant can replay any previously observed valid `(payload_hash, signature)` pair as the response to a different pending foreign-tx request, causing the contract to resolve that request with a forged payload hash.

### Finding Description

In `respond_verify_foreign_tx`, the signature check is:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

`payload_hash` is taken verbatim from the caller-supplied `response`, and `secp_pk` is the **root** (un-tweaked) public key. The contract never checks that `payload_hash == SHA-256(borsh(ForeignTxSignPayload{ request: <the pending request>, values: <...> }))`.

Contrast this with the regular `respond` function, where the payload is read from the stored `request.payload` (set by the user at submission time) and the signature is verified against the **derived** key (root key tweaked by `request.tweak`), which cryptographically binds the signature to the specific request:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,   // derived key, not root
)
``` [2](#0-1) 

For `respond_verify_foreign_tx`, no such binding exists. The `request` argument is only used as a lookup key into `pending_verify_foreign_tx_requests` to find and drain the queued yields:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [3](#0-2) 

The `response` (including the unvalidated `payload_hash`) is serialised and forwarded to every waiting caller without any check that `payload_hash` is consistent with `request`.

The `ForeignTxSignPayload` hash is defined as `SHA-256(borsh(ForeignTxSignPayload{ request, values }))`, where `values` are the extracted foreign-chain observations:

```rust
pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
    let mut hasher = sha2::Sha256::new();
    borsh::BorshSerialize::serialize(self, &mut hasher)?;
    Ok(Hash256(hasher.finalize().into()))
}
``` [4](#0-3) 

Because `request` is embedded inside the Borsh-serialised payload, a signature produced for `(request_A, values_A)` is cryptographically distinct from one for `(request_B, values_B)`. However, the contract never recomputes or checks this relationship — it accepts any `(payload_hash, signature)` pair that is valid under the root key, regardless of which request it was originally produced for.

### Impact Explanation

A single Byzantine attested participant (below the signing threshold) can:

1. Observe any previously submitted, on-chain `respond_verify_foreign_tx` call for request A, obtaining the valid `(payload_hash_A, sig_A)` pair. These are public NEAR transactions.
2. Wait for (or submit) a `verify_foreign_transaction(request_B)` for a different transaction B — one that did not actually occur, or occurred with different parameters.
3. Call `respond_verify_foreign_tx(request = request_B, response = { payload_hash: payload_hash_A, signature: sig_A })`.
4. The contract passes all checks (valid signature over `payload_hash_A` under root key; `request_B` has a pending entry) and resolves every queued yield for `request_B` with the forged response.

Every caller waiting on `request_B` receives `VerifyForeignTransactionResponse{ payload_hash: payload_hash_A, signature: sig_A }` — a response that attests to the observations of transaction A, not transaction B. Any bridge contract that does not independently recompute and validate `payload_hash` (e.g., does not use `ForeignChainSignatureVerifier` from the SDK) will accept this as a valid attestation of transaction B, enabling invalid bridge execution or double-spend. [5](#0-4) 

### Likelihood Explanation

The attacker requires only one attested MPC participant account (a Byzantine participant strictly below the signing threshold). The `(payload_hash, signature)` material needed for the replay is publicly visible on-chain from any prior legitimate `respond_verify_foreign_tx` call. No threshold collusion, key leakage, or TEE attack is required. The only prerequisite is that a pending `verify_foreign_transaction` request for the target transaction exists in the contract, which the attacker can arrange by submitting one themselves (paying only 1 yoctoNEAR deposit).

### Recommendation

Require the responding node to submit the extracted `values` alongside the response, and have the contract recompute and validate:

```rust
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(),
}).compute_msg_hash()?;
require!(expected_hash == response.payload_hash, "payload_hash does not match request+values");
```

This binds `payload_hash` to the specific `request` and prevents cross-request replay. Alternatively, at minimum, the contract should validate that the Borsh prefix of the preimage of `payload_hash` encodes the submitted `request`, which requires the node to provide the full preimage.

### Proof of Concept

1. Legitimate flow: MPC nodes process `verify_foreign_transaction(request_A)` and one node calls `respond_verify_foreign_tx(request_A, { payload_hash_A, sig_A })`. This is recorded on-chain.

2. Attacker (one Byzantine attested participant) submits `verify_foreign_transaction(request_B)` for a transaction that did not occur (paying 1 yoctoNEAR). `request_B` is now pending in `pending_verify_foreign_tx_requests`.

3. Attacker calls:
   ```
   respond_verify_foreign_tx(
     request = request_B,
     response = { payload_hash: payload_hash_A, signature: sig_A }
   )
   ```

4. Contract execution path:
   - `assert_caller_is_signer()` — passes (attacker is a direct caller) [6](#0-5) 
   - `assert_caller_is_attested_participant_and_protocol_active()` — passes (attacker is an attested participant) [7](#0-6) 
   - `verify_ecdsa_signature(sig_A, payload_hash_A, root_key)` — passes (sig_A is a valid signature over payload_hash_A) [8](#0-7) 
   - `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &request_B, serialised_response)` — passes (request_B is pending), drains all queued yields for request_B with the forged response [3](#0-2) 

5. Every caller waiting on `request_B` receives `{ payload_hash: payload_hash_A, signature: sig_A }` — an attestation of transaction A's observations, not transaction B's. A bridge contract that does not call `ForeignChainSignatureVerifier::verify_signature` will accept this as proof that transaction B occurred with transaction A's extracted values.

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

**File:** crates/contract/src/lib.rs (L697-697)
```rust
        let signer = Self::assert_caller_is_signer();
```

**File:** crates/contract/src/lib.rs (L705-705)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L726-734)
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

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
