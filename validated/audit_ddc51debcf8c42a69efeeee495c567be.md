### Title
`respond_verify_foreign_tx` Accepts Payload Hash Unbound to the Pending Request, Enabling Cross-Request Signature Replay - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that `response.signature` is a valid MPC signature over `response.payload_hash`, but never checks that `response.payload_hash` was actually derived from the `request` argument. A single Byzantine attested participant can reuse any previously observed valid MPC signature (from a prior `verify_foreign_transaction` response) to satisfy an unrelated pending request, delivering a forged verification attestation to the caller.

### Finding Description

The `respond_verify_foreign_tx` entry point in `crates/contract/src/lib.rs` performs two independent checks:

1. It verifies the signature is valid for `response.payload_hash` against the ForeignTx domain root public key.
2. It resolves the yield for the pending `request`.

```rust
// crates/contract/src/lib.rs:718-753
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // ← taken verbatim from the response, never tied to `request`
    &secp_pk,
).is_ok()
...
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,               // ← used only as a map key, not cross-checked against payload_hash
    serde_json::to_vec(&response).unwrap(),
)
```

The contract never computes or checks that `response.payload_hash == SHA-256(borsh(ForeignTxSignPayload { request, values }))`. The two inputs — `request` and `response.payload_hash` — are validated in complete isolation.

By contrast, the off-chain SDK helper `ForeignChainSignatureVerifier::verify_signature` in `crates/near-mpc-sdk/src/foreign_chain.rs` explicitly performs this binding check:

```rust
// crates/near-mpc-sdk/src/foreign_chain.rs:48-63
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: self.request,
    values: self.expected_extracted_values,
});
let expected_payload_hash = expected_payload.compute_msg_hash()...;
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
```

The on-chain contract — the only authoritative gatekeeper — omits this check entirely.

**Attack path:**

1. The MPC network legitimately processes a `verify_foreign_transaction` for `tx_id=W`, producing `payload_hash=Z` and `signature=S` (both publicly visible on-chain after the `respond_verify_foreign_tx` call).
2. A user submits a new `verify_foreign_transaction` for `tx_id=X` (a different, unverified transaction).
3. A single Byzantine attested participant calls `respond_verify_foreign_tx` with:
   - `request` = the pending request for `tx_id=X` (satisfies the map lookup)
   - `response.payload_hash` = `Z` (from the `tx_id=W` signing)
   - `response.signature` = `S` (from the `tx_id=W` signing)
4. The contract accepts: signature `S` is valid for `Z` ✓, and the request for `tx_id=X` is pending ✓.
5. The caller receives `(payload_hash=Z, signature=S)` — a valid MPC attestation that actually attests to `tx_id=W`, not `tx_id=X`.

The `ForeignTxSignPayload` structure encodes the request inside the signed hash (`request` is a field of `ForeignTxSignPayloadV1`), so the signature over `Z` cryptographically attests to `tx_id=W`. The caller has no on-chain mechanism to detect the substitution.

### Impact Explanation

A bridge or omnibridge contract that calls `verify_foreign_transaction` to gate inbound asset minting or cross-chain state transitions receives a cryptographically valid MPC signature that attests to the wrong foreign-chain transaction. The caller cannot distinguish this from a legitimate response because the signature genuinely verifies against the MPC public key. This enables:

- **Forged foreign-chain verification**: an attacker can make the MPC network appear to have verified an arbitrary unverified transaction.
- **Invalid bridge execution / double-spend**: a bridge contract that mints tokens upon receiving a valid MPC attestation for a deposit transaction can be triggered with a replayed attestation from a different (already-processed) deposit, enabling double-minting.

This matches the allowed impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass … that causes invalid bridge execution or double-spend conditions."*

### Likelihood Explanation

- The attacker must be a single attested participant (TEE-attested node), which is a realistic Byzantine participant profile explicitly listed in scope.
- No threshold collusion is required; the attacker only reuses a signature already produced by the honest majority and published on-chain.
- All inputs needed for the attack (prior `payload_hash` and `signature`) are publicly readable from NEAR transaction history.
- The attack is repeatable: every new pending `verify_foreign_transaction` request is a fresh opportunity.

### Recommendation

The contract must bind `response.payload_hash` to `request` before accepting the response. Because the contract does not know the extracted values, the response must carry them so the contract can recompute and verify the hash:

1. Extend `VerifyForeignTransactionResponse` to include the full `ForeignTxSignPayload` (or at minimum the `Vec<ExtractedValue>`).
2. In `respond_verify_foreign_tx`, recompute `expected_hash = payload.compute_msg_hash()` and assert `expected_hash == response.payload_hash` **and** `payload.request == request.request`.
3. Verify the signature against `expected_hash` (not the caller-supplied `response.payload_hash`).

This mirrors the check already present in the SDK's `ForeignChainSignatureVerifier::verify_signature` and closes the gap between off-chain and on-chain validation.

### Proof of Concept

**Setup**: Two-participant network; participant P1 is Byzantine.

1. User A calls `verify_foreign_transaction` for `Bitcoin(tx_id=W)`. The MPC network signs and P1 (as leader) calls `respond_verify_foreign_tx`, publishing `(payload_hash=Z, sig=S)` on-chain.

2. User B calls `verify_foreign_transaction` for `Bitcoin(tx_id=X)` (a deposit that never occurred on Bitcoin).

3. P1 reads `Z` and `S` from NEAR transaction history and calls:
   ```
   respond_verify_foreign_tx(
     request  = { chain: Bitcoin, tx_id: X, extractors: [BlockHash] },
     response = { payload_hash: Z, signature: S }
   )
   ```

4. Contract check at `crates/contract/src/lib.rs:729-734`:
   - `verify_ecdsa_signature(S, Z, root_pk)` → **valid** ✓
   - `resolve_yields_for(pending_requests, request_for_X, response)` → **resolves** ✓

5. User B's callback receives `(payload_hash=Z, sig=S)`. Their bridge contract calls `verify_ecdsa_signature(S, Z, root_pk)` → valid. Bridge mints tokens for a Bitcoin deposit (`tx_id=X`) that never happened. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L718-753)
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

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
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
