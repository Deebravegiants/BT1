### Title
`respond_verify_foreign_tx` Lacks `payload_hash`-to-Request Binding Validation, Enabling a Single Byzantine Node to Deliver Forged Foreign-Chain Verification Results - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid over `response.payload_hash`. It does **not** verify that `response.payload_hash` was computed from the `request` field that is being resolved. A single attested MPC node (strictly below the signing threshold) can reuse a legitimately-produced threshold signature from one pending request to resolve a completely different pending request, delivering a forged verification attestation to the caller.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` accepts two independent arguments: a `VerifyForeignTransactionRequest` (which identifies the pending yield to resolve) and a `VerifyForeignTransactionResponse` (which carries `payload_hash` and `signature`). The contract performs two checks:

1. The caller is an attested participant.
2. The ECDSA signature is valid over `response.payload_hash` against the root public key. [1](#0-0) 

What is **absent** is any check that `response.payload_hash` was derived from the `request` that is being resolved. The canonical hash is defined as:

```
payload_hash = SHA-256(borsh(ForeignTxSignPayload { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> }))
``` [2](#0-1) 

Because `ForeignTxSignPayloadV1` embeds the full `ForeignChainRpcRequest` (including `tx_id`, chain family, extractors, and finality), a hash computed for request R2 is cryptographically distinct from one computed for request R1. However, the contract never enforces this binding — it only checks `verify_ecdsa_signature(sig, payload_hash, root_pk)`. [3](#0-2) 

After the signature check passes, the contract unconditionally resolves the yield keyed on `request` with the unchecked `response`: [4](#0-3) 

Contrast this with the regular `respond` path, which derives the expected payload directly from the stored request and verifies the signature against it — there is no analogous free parameter: [5](#0-4) 

---

### Impact Explanation

A single Byzantine attested MPC node that has participated in the signing protocol for request R2 possesses a valid threshold signature `sig_B` over `payload_hash_B = SHA-256(borsh(ForeignTxSignPayload{R2, values_B}))`. It can call:

```
respond_verify_foreign_tx(request = R1, response = { payload_hash: payload_hash_B, signature: sig_B })
```

The contract accepts this call (signature is valid over `payload_hash_B`), resolves R1's yield, and delivers `{ payload_hash: payload_hash_B, signature: sig_B }` to R1's caller.

The `VerifyForeignTransactionResponse` returned to the caller contains only `payload_hash` and `signature` — the `observed_values` (e.g., block hash, log data) are **not** included: [6](#0-5) 

The design doc acknowledges callers must reconstruct the hash locally to verify it, but callers cannot do so without independently querying the foreign chain for the `observed_values` — which defeats the purpose of the service. Bridge contracts (the primary consumer, per the Omnibridge inbound flow use case) that accept any valid MPC-signed response as proof of their specific transaction will be deceived into treating R2's attestation as proof of R1's transaction. This enables invalid bridge execution: a Byzantine node can substitute a low-value transaction's attestation for a high-value one, causing the bridge to release funds without a legitimate corresponding deposit. [7](#0-6) 

---

### Likelihood Explanation

The attacker is a single attested MPC participant — strictly below the signing threshold. No collusion with other nodes is required. The node only needs to:

1. Participate honestly in the signing protocol for any concurrent request R2 (obtaining `sig_B` legitimately).
2. Call `respond_verify_foreign_tx` with R1's request key and R2's `(payload_hash_B, sig_B)`.

Both steps are within the capability of a single Byzantine node. The `respond_verify_foreign_tx` method is callable by any attested participant with no additional access control beyond attestation: [8](#0-7) 

The attack is especially practical when multiple `verify_foreign_transaction` requests are pending simultaneously (e.g., during high bridge traffic), as the node can freely cross-wire any two concurrent requests.

---

### Recommendation

Require the responding node to submit the full `ForeignTxSignPayload` pre-image alongside the response. The contract should:

1. Accept `payload: ForeignTxSignPayload` in the response.
2. Verify `payload.request == request.request` (binding the payload to the pending request).
3. Recompute `expected_hash = payload.compute_msg_hash()` on-chain.
4. Verify `expected_hash == response.payload_hash`.
5. Verify the signature over `expected_hash`.

This eliminates the free parameter and makes it impossible for a single node to substitute a hash from a different request. The `ForeignTxSignPayload` is small and bounded (the design already enforces strict size limits on extracted values), so including it in the response does not violate NEAR's promise data limits in practice. [9](#0-8) 

---

### Proof of Concept

**Setup**: Two concurrent pending requests:
- R1: `verify_foreign_transaction` for Bitcoin tx A (`tx_id = [0x01; 32]`, 100 BTC bridge deposit)
- R2: `verify_foreign_transaction` for Bitcoin tx B (`tx_id = [0x02; 32]`, 1 BTC bridge deposit)

**Attack**:

1. Byzantine node participates honestly in the MPC signing protocol for R2, obtaining threshold signature `sig_B` over `payload_hash_B = SHA-256(borsh(ForeignTxSignPayload { request: BitcoinRpcRequest { tx_id: [0x02;32], ... }, values: [BlockHash([...])]}))`.

2. Byzantine node calls:
   ```
   respond_verify_foreign_tx(
     request = VerifyForeignTransactionRequest { request: BitcoinRpcRequest { tx_id: [0x01;32], ... }, ... },  // R1
     response = VerifyForeignTransactionResponse { payload_hash: payload_hash_B, signature: sig_B }           // R2's data
   )
   ```

3. Contract checks: `verify_ecdsa_signature(sig_B, payload_hash_B, root_pk)` → **passes** (signature is genuinely valid).

4. Contract resolves R1's yield with `{ payload_hash: payload_hash_B, signature: sig_B }`.

5. R1's caller (bridge contract) receives the response, verifies the signature is valid (it is), and — without independently querying Bitcoin to recompute the hash — treats it as proof that Bitcoin tx A (100 BTC) was finalized.

6. Bridge releases 100 BTC worth of wrapped tokens, while only 1 BTC was actually deposited on Bitcoin. [10](#0-9) [6](#0-5)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1478-1509)
```rust
pub enum ForeignTxSignPayload {
    V1(ForeignTxSignPayloadV1),
}

#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
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

**File:** docs/foreign-chain-transactions.md (L7-10)
```markdown
This feature lets the MPC network sign payloads only after verifying a specific foreign-chain transaction, so NEAR contracts can react to external chain events without a trusted relayer. Primary use cases:

* Omnibridge inbound flow (foreign chain -> NEAR) where Chain Signatures are required to attest that a foreign transaction finalized successfully.
* Broader chain abstraction: a single MPC network verifies foreign chain state and returns small, typed observations that contracts can interpret.
```
