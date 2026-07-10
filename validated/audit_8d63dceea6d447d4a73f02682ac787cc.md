### Title
`respond_verify_foreign_tx` Accepts Any Valid MPC Signature Regardless of Which Request It Was Produced For — Cross-Request Foreign-Chain Verification Replay - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid for the caller-supplied `response.payload_hash`, but never checks that `payload_hash` is the canonical hash of the `ForeignTxSignPayload` that corresponds to the `request` being answered. A single Byzantine participant (below the signing threshold) can replay any previously observed, legitimately-produced `VerifyForeignTransactionResponse` to resolve a completely different pending foreign-transaction request, delivering a forged verification outcome to the waiting caller.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs two independent checks and then resolves the yield:

```rust
// 1. Verify signature is valid for the caller-supplied payload_hash
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
).is_ok()

// 2. Resolve the yield for `request`
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [1](#0-0) 

There is no step that recomputes `SHA-256(borsh(ForeignTxSignPayload{request, values}))` from the stored `request` and checks it equals `response.payload_hash`. The contract therefore cannot distinguish between:

- A response whose `payload_hash` was produced by signing the correct payload for `request`, and
- A response whose `payload_hash` was produced by signing the payload for a completely different request.

The signed data structure `ForeignTxSignPayloadV1` contains only the `ForeignChainRpcRequest` and the extracted values:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [2](#0-1) 

It does not include the NEAR contract address, the `domain_id`, or any binding to the specific pending yield being resolved. This is the structural analog of the reported vulnerability: just as the BLS wallet signatures omit the wallet address and can therefore be replayed across wallets, `ForeignTxSignPayload` omits any per-request or per-contract binding and can therefore be replayed across pending requests.

### Impact Explanation

A Byzantine participant calls `respond_verify_foreign_tx(request_B, response_A)` where `response_A` is a legitimately-produced response for a different pending request `request_A`. The contract:

1. Confirms the signature in `response_A` is valid for `response_A.payload_hash` — **true**, because it was honestly produced.
2. Confirms `request_B` exists in `pending_verify_foreign_tx_requests` — **true**, because the victim submitted it.
3. Resolves the yield for `request_B` with `response_A`.

The victim's callback receives `VerifyForeignTransactionResponse { payload_hash: hash(payload_A), signature: sig_A }`. The signature is valid, but it attests to a completely different foreign transaction. Any downstream contract that uses the returned `payload_hash` + signature to authorize a bridge action (e.g., releasing funds, minting tokens) without independently reconstructing and verifying the payload will act on forged evidence. Even a careful caller is permanently denied a correct response for `request_B` because the yield has been consumed.

**Impact class**: High — forged foreign-chain verification causing invalid bridge execution or double-spend conditions.

### Likelihood Explanation

- Requires only a **single** Byzantine participant (below the signing threshold) who can call `respond_verify_foreign_tx`.
- All past `VerifyForeignTransactionResponse` values are publicly visible on-chain; no secret material is needed.
- The attacker needs only to wait for any pending request to target and any prior valid response to replay.
- No threshold collusion, no key leakage, no network-level attack is required.

### Recommendation

Inside `respond_verify_foreign_tx`, after verifying the signature, recompute the expected payload hash from the stored request and assert it matches `response.payload_hash`:

```rust
// Recompute the canonical hash for this request
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    // values must be re-derived or stored alongside the pending request
    values: ...,
});
let expected_hash = expected_payload.compute_msg_hash()?;
if response.payload_hash != expected_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

Alternatively, include the NEAR contract address (`env::current_account_id()`) and the `domain_id` inside `ForeignTxSignPayloadV1` so that every signature is cryptographically bound to the specific contract instance and domain that requested it, preventing cross-request and cross-contract replay.

### Proof of Concept

**Setup**: Two pending foreign-tx requests exist on the contract:
- `request_A`: Bitcoin `tx_id = [0xAA; 32]`, `confirmations = 6`, `extractors = [BlockHash]`
- `request_B`: Bitcoin `tx_id = [0xBB; 32]`, `confirmations = 6`, `extractors = [BlockHash]`

**Step 1**: The MPC network honestly processes `request_A` and a participant calls:
```
respond_verify_foreign_tx(request_A, response_A)
```
where `response_A = { payload_hash: H_A, signature: sig_A }` and `H_A = SHA-256(borsh(ForeignTxSignPayloadV1 { request: request_A, values: [BlockHash([0x11;32])] }))`.

**Step 2**: The Byzantine participant observes `response_A` on-chain (it is public). Before the MPC network processes `request_B`, the attacker calls:
```
respond_verify_foreign_tx(request_B, response_A)
```

**Step 3**: The contract executes `respond_verify_foreign_tx`:
- `verify_ecdsa_signature(sig_A, H_A, root_pk)` → **valid** (honest signature).
- `request_B` is in `pending_verify_foreign_tx_requests` → **found**.
- Yield for `request_B` is resolved with `response_A`.

**Step 4**: The caller of `request_B` receives `{ payload_hash: H_A, signature: sig_A }`. The signature is valid, but `H_A` attests to Bitcoin transaction `[0xAA;32]`, not `[0xBB;32]`. Any bridge contract that does not independently verify `H_A` against the expected payload will act on forged data. The yield for `request_B` is permanently consumed; the victim cannot obtain a correct response. [3](#0-2) [2](#0-1) [4](#0-3)

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
