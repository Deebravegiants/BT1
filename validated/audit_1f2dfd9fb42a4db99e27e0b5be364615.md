### Title
`respond_verify_foreign_tx` Accepts Attested-Participant-Supplied `payload_hash` Without Binding It to the Pending Request — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted ECDSA signature is valid over `response.payload_hash`, but it never checks that `response.payload_hash` is actually the canonical hash of `ForeignTxSignPayload{request, ...}` for the pending `request`. A single malicious attested participant acting as signing leader can recycle a legitimately-produced threshold signature (obtained for a real foreign-chain transaction) and submit it as the response to a *different* pending `verify_foreign_transaction` request. The contract accepts the call, resolves the yield, and the caller receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes a completely different transaction — defeating the entire purpose of the foreign-chain verification gate.

---

### Finding Description

**Root cause — `respond_verify_foreign_tx` in `crates/contract/src/lib.rs` lines 718–747:**

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← taken from the response, not derived from `request`

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // ← only checks sig(payload_hash) is valid
    &secp_pk,
)
.is_ok()
```

The contract checks only that `signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key. It does **not** verify that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload{ request, extracted_values }))` for the `request` parameter that was used to look up the pending yield.

**Contrast with the regular `respond` function (lines 600–608):**

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
// payload_hash is taken from the stored request, not from the response
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,           // ← bound to the original request
    &expected_public_key,
)
```

In `respond`, the hash is extracted from the *stored request*, making it impossible to substitute a hash from a different request. `respond_verify_foreign_tx` has no equivalent binding.

**How the signed payload is constructed (node side, `crates/node/src/providers/verify_foreign_tx/sign.rs` lines 30–47):**

```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    ...
    Ok(SignatureRequest { payload: Payload::Ecdsa(payload_bytes), tweak: Tweak::new([0u8; 32]), ... })
}
```

`ForeignTxSignPayload::V1` embeds the full `ForeignChainRpcRequest` (including `tx_id`) and the extracted values. The hash therefore encodes which transaction was verified. The contract never re-derives this hash from the `request` argument it receives.

**Attack path (single malicious attested participant, no threshold collusion):**

1. Attacker submits `verify_foreign_transaction(request_A)` — a legitimate request for a real foreign-chain transaction (e.g., a real Bitcoin deposit).
2. The MPC network runs the threshold signing protocol; the malicious leader participates honestly and obtains `(payload_hash_A, signature_A)` — a valid threshold signature over `SHA-256(borsh(ForeignTxSignPayload{request_A, extracted_values_A}))`.
3. The malicious leader stores `(payload_hash_A, signature_A)`.
4. Attacker submits `verify_foreign_transaction(request_B)` — a fraudulent request for a non-existent or already-spent foreign-chain transaction.
5. The malicious leader calls `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: signature_A })`.
6. The contract:
   - Confirms `request_B` is in `pending_verify_foreign_tx_requests` ✓
   - Verifies `signature_A` over `payload_hash_A` under the root public key ✓ (it is a valid threshold signature)
   - Calls `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &request_B, serde_json::to_vec(&response))` ✓
7. The caller of `request_B` receives `VerifyForeignTransactionResponse{ payload_hash: payload_hash_A, signature: signature_A }`.
8. The caller verifies the signature — it is valid. The caller cannot distinguish `payload_hash_A` from a hash of `request_B`'s data because `payload_hash` is an opaque 32-byte SHA-256 digest.

The bridge contract (Omnibridge inbound flow) then authorises a NEAR-side action (e.g., minting tokens) based on a fraudulent attestation.

**No threshold collusion is required.** The malicious leader already holds `(payload_hash_A, signature_A)` from step 2, where it participated honestly alongside the other nodes. Reusing that pair for a different request is a unilateral act.

**Missing test coverage (analog to the external report):** There is no unit test in `crates/contract/src/lib.rs` or `crates/contract/tests/sandbox/foreign_chain_request.rs` that verifies the contract *rejects* a `respond_verify_foreign_tx` call where `response.payload_hash` does not correspond to the `request` argument. All existing tests supply a correctly-derived hash, so the missing binding check is never exercised.

---

### Impact Explanation

The `verify_foreign_transaction` / `respond_verify_foreign_tx` flow is the sole on-chain gate that prevents the MPC network from signing arbitrary payloads under the `ForeignTx` domain key. If a single malicious leader can substitute a recycled `payload_hash` for a different pending request, the gate is bypassed: the caller receives a valid MPC signature that it cannot distinguish from a legitimate attestation. For the primary use case (Omnibridge inbound flow), this enables minting NEAR-side tokens for a foreign-chain deposit that never happened, or for a deposit that was already processed — a direct theft of funds from the bridge.

This matches: **High — Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass that causes invalid bridge execution or double-spend conditions.**

---

### Likelihood Explanation

- Only **one** malicious attested participant (the signing leader) is required.
- The attacker needs no cryptographic capability beyond what a normal participant already has: they simply reuse a threshold signature they legitimately received.
- The attack is fully on-chain and requires no special infrastructure.
- The `verify_foreign_transaction` flow is the primary bridge inbound path, making it a high-value target.

---

### Recommendation

The contract must bind `response.payload_hash` to the pending `request`. The cleanest fix mirrors how `respond` handles regular signatures — derive the expected hash from the stored request rather than trusting the caller-supplied value.

Because the contract does not store the extracted values (they are only known to the nodes), the binding must be enforced differently. Two options:

**Option A — Include the `request` in the response and re-derive the hash prefix on-chain.**
Have the node include the full `ForeignTxSignPayload` (not just its hash) in the response. The contract then calls `ForeignTxSignPayload::compute_msg_hash()` and checks it equals `response.payload_hash`, and also checks that `payload.request == request`. This increases response size but is the most direct fix.

**Option B — Sign a commitment that includes the request key.**
Change the signed payload to `SHA-256(borsh(request_key) || borsh(ForeignTxSignPayload))` where `request_key` is the `VerifyForeignTransactionRequest`. The contract can then verify the hash starts with the expected request prefix — but since SHA-256 is not prefix-friendly, this requires a two-level hash: `SHA-256(SHA-256(borsh(request)) || SHA-256(borsh(ForeignTxSignPayload)))`. The contract recomputes `SHA-256(borsh(request))` from the `request` argument and checks the outer hash.

Either option eliminates the ability to recycle a signature from one request for another.

---

### Proof of Concept

The following pseudo-test demonstrates the contract accepts a recycled `payload_hash`:

```rust
// Setup: two different Bitcoin requests
let request_A_args = VerifyForeignTransactionRequestArgs {
    domain_id: domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: [0xAA; 32].into(), confirmations: 6.into(),
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
};
let request_B_args = VerifyForeignTransactionRequestArgs {
    domain_id: domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: [0xBB; 32].into(), // DIFFERENT tx_id — fraudulent request
        confirmations: 6.into(),
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
};

// Attacker submits both requests
contract.verify_foreign_transaction(request_A_args);
contract.verify_foreign_transaction(request_B_args);

// Honest MPC run for request_A produces a valid signature
let payload_A = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request_A.request.clone(),
    values: vec![ExtractedValue::BitcoinExtractedValue(
        BitcoinExtractedValue::BlockHash([0xDE; 32].into()),
    )],
});
let payload_hash_A = payload_A.compute_msg_hash().unwrap();
let (sig_A, rec_id) = root_signing_key.sign_prehash_recoverable(&payload_hash_A.0).unwrap();
let response_A = VerifyForeignTransactionResponse {
    payload_hash: payload_hash_A,
    signature: SignatureResponse::Secp256k1(K256Signature::from_ecdsa_recoverable(&sig_A, rec_id)),
};

// Malicious leader submits response_A for request_B (DIFFERENT request key)
let result = contract.respond_verify_foreign_tx(request_B, response_A.clone());

// BUG: contract accepts this — signature is valid over payload_hash_A,
// but payload_hash_A encodes request_A (tx_id=0xAA), not request_B (tx_id=0xBB)
assert!(result.is_ok()); // passes today — should be Err(InvalidSignature or similar)
```

The root cause is at: [1](#0-0) 

The missing binding check (contrast with the correct pattern in `respond`): [2](#0-1) 

The `ForeignTxSignPayload` structure that embeds the request (and whose hash the contract never re-derives): [3](#0-2) 

The node-side construction that correctly derives `payload_hash` from the request and extracted values (but the contract never re-performs this derivation): [4](#0-3)

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
