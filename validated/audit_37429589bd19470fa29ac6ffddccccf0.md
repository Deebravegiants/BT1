### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Submitted `request` — Allowing Cross-Request Signature Replay by a Single Byzantine Participant - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` contract method verifies that the supplied `response.payload_hash` carries a valid MPC signature, but **never checks that `payload_hash` actually commits to the `request` that is being resolved**. A single Byzantine-but-below-threshold MPC participant can replay any previously issued `VerifyForeignTransactionResponse` (which is public on-chain) against a different pending request, causing the contract to resolve that request with a hash that attests to a completely different foreign-chain transaction.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` accepts two independent arguments:

- `request: VerifyForeignTransactionRequest` — the pending foreign-chain query (chain, tx_id, extractors, finality, domain).
- `response: VerifyForeignTransactionResponse` — contains `payload_hash: Hash256` and a `signature`.

The function performs exactly two checks before resolving the yield:

1. **Signature validity**: the ECDSA signature in `response` is valid over `response.payload_hash` under the domain's root public key.
2. **Request existence**: `request` is present in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What is **never checked** is whether `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request: request.request, values: <observed> }))`. The contract stores only the `ForeignChainRpcRequest` in the pending map; it has no record of what `payload_hash` the MPC nodes should have produced for that request. [2](#0-1) 

The intended binding is defined in the design document and the node-side code:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload { request, values }))
``` [3](#0-2) 

Because the contract never enforces this binding, `payload_hash` and `request` are completely decoupled at the contract level — an exact structural analog to the external report's "data for swap might not match its inputs" class.

---

### Impact Explanation

A single Byzantine MPC participant (below the signing threshold) who has observed any previously issued `VerifyForeignTransactionResponse` on-chain can:

1. Wait for a victim's `verify_foreign_transaction` for **tx_A** to be queued.
2. Reuse the already-published `{payload_hash_B, sig_B}` from a prior legitimate response for **tx_B**.
3. Call `respond_verify_foreign_tx(request = tx_A_request, response = {payload_hash: hash_B, signature: sig_B})`.

All contract checks pass:
- `sig_B` is a valid MPC signature over `hash_B` ✓
- `tx_A_request` exists in `pending_verify_foreign_tx_requests` ✓

The yield for tx_A is resolved and the caller receives `{payload_hash: hash_B, signature: sig_B}` — a valid MPC signature that attests to **tx_B's** foreign-chain state, not tx_A's. Any downstream bridge contract that trusts the MPC contract's response (a reasonable assumption) will accept this as proof that tx_A was finalized, enabling a **forged foreign-chain verification** and potential double-spend or invalid bridge execution.

This matches the allowed High impact: *"Cross-chain replay, forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- **Entry path is unprivileged within the MPC threat model**: the system is explicitly designed to tolerate Byzantine participants below the signing threshold. A single malicious-but-registered participant can call `respond_verify_foreign_tx` unilaterally.
- **No threshold collusion required**: the attacker reuses a signature already produced by the honest majority for a different request. No new signing ceremony is needed.
- **Signatures are public**: every `VerifyForeignTransactionResponse` is emitted on-chain and is trivially observable.
- **No TEE break required**: the attacker is a legitimate, attested participant; they call the contract directly. [4](#0-3) 

---

### Recommendation

Inside `respond_verify_foreign_tx`, recompute the expected `payload_hash` prefix from the `request` fields and reject any response whose `payload_hash` does not commit to the correct `request`. Because the `values` (extracted chain data) are not stored on-chain, the simplest fix is to include the `ForeignChainRpcRequest` as a prefix in the hash and verify it:

```rust
// Reconstruct the prefix that must appear in any valid payload hash for this request.
// The full hash is SHA-256(borsh(ForeignTxSignPayload { request, values })).
// At minimum, verify that payload_hash was produced for *this* request by
// storing the expected hash alongside the pending request, or by requiring
// the responder to also supply the `values` so the contract can recompute
// and verify the hash itself.
```

Concretely, the pending-request map should store the `payload_hash` that the MPC nodes committed to (passed back alongside the response), and `respond_verify_foreign_tx` should assert `response.payload_hash == stored_payload_hash`. Alternatively, require the responder to supply the full `ForeignTxSignPayload` (including `values`), recompute the hash on-chain, and verify both the hash binding and the signature. [5](#0-4) 

---

### Proof of Concept

**Setup**: MPC network is running. Domain `D` has root key `K`. Two foreign-chain transactions exist: `tx_A` (victim's) and `tx_B` (attacker's prior request, already processed).

**Step 1** — Attacker observes the on-chain response for `tx_B`:
```
response_B = VerifyForeignTransactionResponse {
    payload_hash: H_B,   // SHA-256(borsh(ForeignTxSignPayload { request: tx_B, values: [...] }))
    signature: sig_B,    // valid MPC ECDSA signature over H_B under K
}
```

**Step 2** — Victim submits `verify_foreign_transaction(tx_A)`. Contract stores `tx_A_request` in `pending_verify_foreign_tx_requests`.

**Step 3** — Attacker (a registered, attested MPC participant) calls:
```
respond_verify_foreign_tx(
    request = tx_A_request,
    response = { payload_hash: H_B, signature: sig_B }
)
```

**Step 4** — Contract evaluation:
- `verify_ecdsa_signature(sig_B, H_B, K)` → **OK** (sig_B is a valid signature over H_B)
- `pending_verify_foreign_tx_requests.get(tx_A_request)` → **found**
- `resolve_yields_for(tx_A_request, serialize(response_B))` → **yield resolved**

**Step 5** — Victim's NEAR contract receives `response_B` as the result of its `verify_foreign_transaction(tx_A)` call. `response_B.payload_hash` is `H_B` (attesting to `tx_B`'s state), not `H_A`. The victim's contract, trusting the MPC contract's output, treats this as proof that `tx_A` was finalized — enabling fraudulent bridge execution. [6](#0-5) [7](#0-6)

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
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
