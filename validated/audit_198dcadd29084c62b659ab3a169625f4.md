### Title
Unbound `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay by a Single Byzantine Participant — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` using the root public key, but never checks that `response.payload_hash` is the correct hash for the supplied `request`. Because the signed `ForeignTxSignPayload` does not bind to the `VerifyForeignTransactionRequest` identity (domain, payload version, or the full request key), a single Byzantine attested participant can replay any previously observed valid MPC signature against any different pending foreign-tx request, forging a verification attestation without threshold cooperation.

---

### Finding Description

**Root cause 1 — missing request-to-hash binding in `respond_verify_foreign_tx`**

In `crates/contract/src/lib.rs` the function accepts a caller-supplied `response.payload_hash` and only checks that the signature over it is valid:

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

There is no step that re-derives the expected hash from `request` and asserts `response.payload_hash == expected`. The contract then immediately resolves the pending yield for `request` with the unverified response payload.

Compare this with the regular `respond` path, where the payload hash is taken directly from the stored `request` (not from the response), and the signature is verified against a *derived* key that cryptographically binds to the requester's account ID and derivation path — making cross-request reuse impossible.

**Root cause 2 — `ForeignTxSignPayload` does not include the request identity**

`ForeignTxSignPayloadV1` in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs` contains only:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

It does not include `domain_id`, `payload_version`, or any field that uniquely identifies the `VerifyForeignTransactionRequest` key used in `pending_verify_foreign_tx_requests`. Two requests for different transactions on the same chain with the same extractor set but different `domain_id` or `payload_version` produce different pending-map keys yet the signed payload is identical in structure.

**Root cause 3 — zero tweak (root key, no derivation)**

`build_signature_request` in `crates/node/src/providers/verify_foreign_tx/sign.rs` always sets:

```rust
tweak: Tweak::new([0u8; 32]),
```

This means every foreign-tx signing round uses the bare root key. Unlike regular `sign()` requests — where the tweak encodes the requester's account ID and path, making each signature request-specific — all foreign-tx signatures are interchangeable across any pending request that shares the same domain.

---

### Impact Explanation

A Byzantine attested participant (single node, strictly below the signing threshold) can:

1. Observe any completed `respond_verify_foreign_tx` transaction on-chain (all NEAR transactions are public), extracting `payload_hash_A` and `sig_A` produced for request A (tx_id = X).
2. Submit `respond_verify_foreign_tx(request = B, response = {payload_hash: payload_hash_A, signature: sig_A})` for a *different* pending request B (tx_id = Y).
3. The contract accepts the call: `sig_A` is a valid root-key signature over `payload_hash_A`, the participant is attested, and request B exists in `pending_verify_foreign_tx_requests`.
4. Request B's pending yield is resolved and the caller receives `{payload_hash: payload_hash_A, signature: sig_A}` — an attestation that the MPC network verified transaction X, delivered as the answer to a query about transaction Y.

If the downstream bridge contract or application verifies the signature against the root public key without also re-deriving the expected `payload_hash` from the original request (as `ForeignChainSignatureVerifier::verify_signature` in the SDK does), it will accept a forged attestation that a different foreign-chain transaction occurred. This enables invalid bridge execution or double-spend conditions. Even when the caller does re-verify, the pending yield is permanently consumed, forcing a costly resubmission.

---

### Likelihood Explanation

The attack requires only that the adversary is an attested MPC participant — a Byzantine participant strictly below the signing threshold. No brute force, no threshold collusion, and no key material beyond what is already visible on-chain is needed. Valid `respond_verify_foreign_tx` transactions are publicly observable on NEAR, so the attacker passively collects reusable `(payload_hash, signature)` pairs from every legitimate signing round. The only prerequisite is that a victim's request is pending at the time of the replay submission. Given that bridge services submit many concurrent requests, this condition is routinely satisfied.

---

### Recommendation

**Option A (preferred) — bind the full `VerifyForeignTransactionRequest` into the signed payload.**
Extend `ForeignTxSignPayloadV1` to include `domain_id` and `payload_version` (or the full `VerifyForeignTransactionRequest`). The contract can then re-derive the expected hash prefix from the known `request` fields and reject any response whose `payload_hash` was not computed over the correct request identity.

**Option B — verify `payload_hash` against `request` in `respond_verify_foreign_tx`.**
Include the extracted `values` in the `VerifyForeignTransactionResponse` so the contract can recompute `SHA-256(borsh(ForeignTxSignPayload { request: request.request, values: response.values }))` and assert it equals `response.payload_hash` before resolving the yield.

**Option C — use a non-zero, request-specific tweak.**
Derive the signing key from a tweak that encodes the `VerifyForeignTransactionRequest` (analogous to how `sign()` derives from predecessor + path). This makes each signature cryptographically bound to its originating request and non-transferable to any other pending entry.

---

### Proof of Concept

**Setup**: Two pending requests exist:
- Request A: `{request: Bitcoin(tx_id=X, extractors=[BlockHash]), domain_id=0, payload_version=V1}`
- Request B: `{request: Bitcoin(tx_id=Y, extractors=[BlockHash]), domain_id=0, payload_version=V1}`

**Step 1**: The MPC network legitimately processes request A. The coordinator calls:
```
respond_verify_foreign_tx(
  request = A,
  response = {payload_hash: H(borsh({Bitcoin(tx_id=X,...), [block_hash_X]})), signature: sig_A}
)
```
This transaction is publicly visible on NEAR.

**Step 2**: The Byzantine participant extracts `(payload_hash_A, sig_A)` from the on-chain transaction.

**Step 3**: The Byzantine participant calls:
```
respond_verify_foreign_tx(
  request = B,                  // pending request for tx_id=Y
  response = {payload_hash: payload_hash_A, signature: sig_A}  // reused from request A
)
```

**Step 4**: The contract at `crates/contract/src/lib.rs:726-734` verifies:
- `sig_A` is a valid root-key signature over `payload_hash_A` ✓ (it is)
- Request B exists in `pending_verify_foreign_tx_requests` ✓ (it does)
- No check that `payload_hash_A` corresponds to request B ✗ (missing)

**Step 5**: `pending_requests::resolve_yields_for` at line 749 resolves request B's yield with `{payload_hash: payload_hash_A, signature: sig_A}`. The caller of request B receives an attestation for transaction X instead of transaction Y. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L586-608)
```rust
        let signature_is_valid = match (&response, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                // generate the expected public key
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");
                let affine = *k256::PublicKey::try_from(&secp_pk)
                    .expect("stored key is always valid")
                    .as_affine();
                let expected_public_key =
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L39-47)
```rust
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
