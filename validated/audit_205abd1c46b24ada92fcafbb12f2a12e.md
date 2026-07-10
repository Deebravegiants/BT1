### Title
`respond_verify_foreign_tx` Accepts Replayed Signatures Over Arbitrary `payload_hash` Without Binding to the Pending Request — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the MPC signature in the response is valid over `response.payload_hash` using the root public key, but it never verifies that `response.payload_hash` is the canonical hash of `ForeignTxSignPayload{request, extracted_values}` for the specific pending `request`. A single Byzantine attested participant (strictly below the signing threshold) can reuse any previously obtained valid root-key signature — from any prior legitimate `verify_foreign_transaction` call — to resolve a different (or stale-data) pending request, delivering a forged verification result to every waiting caller.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs the following signature check:

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

The contract verifies only that `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key. It does **not** verify that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))` for the specific `request` being resolved.

The canonical payload that MPC nodes are supposed to sign is:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
// msg_hash = SHA-256(borsh(ForeignTxSignPayload))
``` [2](#0-1) 

The MPC nodes sign with a zero tweak (root key, no derivation):

```rust
tweak: Tweak::new([0u8; 32]),
``` [3](#0-2) 

This contrasts with the regular `respond` path, which derives the expected public key from `(predecessor, path)` via `derive_key_secp256k1(&affine, &request.tweak)`, cryptographically binding the signature to the specific caller and derivation path. [4](#0-3) 

Because `respond_verify_foreign_tx` uses the root key with no binding to the request content, **any** valid root-key signature over **any** 32-byte value passes the check. A Byzantine attested participant who has previously observed a legitimate `(payload_hash_A, signature_A)` pair — from any prior `verify_foreign_transaction` call — can call:

```
respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: signature_A })
```

where `request_B` is any currently pending request. The contract will:
1. Confirm `request_B` is pending ✓
2. Confirm the caller is an attested participant ✓
3. Confirm `signature_A` is valid over `payload_hash_A` under the root key ✓
4. Resolve all yields queued under `request_B` with the forged response ✓ [5](#0-4) 

The `args_into_verify_foreign_tx_request` conversion confirms no binding tweak is computed from the caller or request content at submission time:

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
``` [6](#0-5) 

The design document itself acknowledges a `tweak` field in `VerifyForeignTransactionRequest` and a separate `derive_foreign_tx_tweak` function intended to bind the signing key to the request, but neither is present in the production contract or node code. [7](#0-6) 

---

### Impact Explanation

The `verify_foreign_transaction` flow is the foundation of the Omnibridge inbound path: NEAR contracts use the returned `(payload_hash, signature)` to attest that a specific foreign-chain transaction finalized with specific extracted values (block hash, log data, etc.). A forged response delivers an incorrect `payload_hash` — one that encodes stale extracted values or values from a completely different transaction — to every caller waiting on `request_B`. A bridge contract that trusts this attestation will process a cross-chain event based on fabricated on-chain state, enabling double-spend or invalid mint conditions.

The SDK's `ForeignChainSignatureVerifier::verify_signature` does check `expected_payload_hash == response.payload_hash`, but this is a client-side SDK helper, not an on-chain enforcement. The contract itself is the authoritative source of truth and it delivers the forged hash without rejection. [8](#0-7) 

**Impact class**: High — forged foreign-chain verification / cross-chain replay causing invalid bridge execution.

---

### Likelihood Explanation

The attack requires exactly one Byzantine attested participant (strictly below the signing threshold). No threshold collusion is needed: the attacker only replays a signature that was already produced by the honest network during a prior legitimate request. The attacker does not need to forge a new signature or compromise any key material. Any attested participant who has ever observed a `respond_verify_foreign_tx` transaction on-chain (all such transactions are public NEAR receipts) has access to a valid `(payload_hash, signature)` pair they can replay. As the protocol becomes more decentralized and the participant set grows, the probability of at least one Byzantine participant increases.

---

### Recommendation

The contract must bind the accepted `payload_hash` to the specific pending `request`. Two complementary mitigations:

1. **Require the responder to supply `extracted_values`** in the response, and have the contract independently compute `expected_hash = SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))`, then assert `response.payload_hash == expected_hash` before accepting the signature. This is the strongest fix.

2. **Alternatively, apply a request-binding tweak** (as the design document already specifies via `derive_foreign_tx_tweak`) so that the signing key is derived from the request content, making a signature over `payload_hash_A` invalid for any key derived from `request_B`.

---

### Proof of Concept

**Setup**: Two-participant network. Participant P1 is Byzantine.

**Step 1** — Obtain a legitimate signature:
```
User calls: verify_foreign_transaction({ tx_id: TX_A, chain: Bitcoin, extractors: [BlockHash] })
MPC network responds honestly: payload_hash_A = SHA256(borsh({TX_A, [BlockHash(H1)]})), signature_A
```

**Step 2** — A different user submits a new request:
```
User2 calls: verify_foreign_transaction({ tx_id: TX_B, chain: Bitcoin, extractors: [BlockHash] })
→ pending in contract as request_B
```

**Step 3** — Byzantine participant P1 replays the old signature:
```
P1 calls: respond_verify_foreign_tx(
    request = request_B,
    response = { payload_hash: payload_hash_A, signature: signature_A }
)
```

**Step 4** — Contract validation (all pass):
- `request_B` is pending ✓
- P1 is an attested participant ✓
- `verify_ecdsa_signature(signature_A, payload_hash_A, root_pk)` → valid ✓
- `payload_hash_A` is NOT checked against `request_B` ✗ (missing check)

**Step 5** — All yields queued under `request_B` are resolved with `{ payload_hash_A, signature_A }`. User2's bridge contract receives a signed attestation claiming TX_B's block hash is H1 (from TX_A's verification), enabling invalid bridge execution.

### Citations

**File:** crates/contract/src/lib.rs (L596-608)
```rust
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

**File:** docs/foreign-chain-transactions.md (L271-286)
```markdown
const FOREIGN_TX_TWEAK_DERIVATION_PREFIX: &str =
    "near-mpc-recovery v0.1.0 foreign-tx epsilon derivation:";

pub fn derive_sign_tweak(predecessor_id: &AccountId, path: &str) -> Tweak {
    let hash: [u8; 32] = derive_from_path(SIGN_TWEAK_DERIVATION_PREFIX, predecessor_id, path);
    Tweak::new(hash)
}

pub fn derive_foreign_tx_tweak(predecessor_id: &AccountId, path: &str) -> Tweak {
    let hash: [u8; 32] = derive_from_path(FOREIGN_TX_TWEAK_DERIVATION_PREFIX, predecessor_id, path);
    Tweak::new(hash)
}
```

This ensures key material used for validated foreign transactions is **always** distinct from
general-purpose `sign()` keys, even if the same account and derivation path are reused.
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
