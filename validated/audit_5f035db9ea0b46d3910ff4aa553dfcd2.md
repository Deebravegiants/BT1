### Title
Missing Request-to-Payload-Hash Linkage in `respond_verify_foreign_tx` Enables Cross-Chain Verification Replay - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` in the MPC smart contract verifies that the submitted ECDSA signature is valid over the caller-supplied `response.payload_hash`, but never checks that `response.payload_hash` is actually derived from the `request` being resolved. A single Byzantine attested participant can replay any previously valid `VerifyForeignTransactionResponse` against any currently pending `verify_foreign_transaction` request, causing the contract to attest that an unconfirmed or fraudulent foreign-chain transaction was verified.

---

### Finding Description

In `respond_verify_foreign_tx`, the signature check is:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,   // ← taken directly from the response, not derived from `request`
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The contract only proves that `response.signature` is a valid ECDSA signature over `response.payload_hash`. It never verifies that `response.payload_hash == SHA256(borsh(ForeignTxSignPayload { request: request.request, values: ... }))`. The `payload_hash` field is entirely attacker-controlled.

The correct linkage check exists in the client-side SDK:

```rust
let expected_payload_hash = expected_payload.compute_msg_hash()...;
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [2](#0-1) 

This check is present only in `ForeignChainSignatureVerifier::verify_signature` (the off-chain SDK helper), not in the on-chain contract. The on-chain contract is the authoritative verifier; the SDK check is advisory and only protects callers who use it correctly.

The `ForeignTxSignPayload` that nodes are supposed to sign binds both the original request and the extracted values:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
// msg_hash = SHA-256(borsh(ForeignTxSignPayload))
``` [3](#0-2) 

Because the contract never recomputes this hash from `request` and checks it against `response.payload_hash`, the binding is absent at the enforcement layer.

---

### Impact Explanation

**High — Cross-chain replay / forged foreign-chain verification causing invalid bridge execution.**

A single Byzantine attested participant can:

1. Observe any previously emitted `VerifyForeignTransactionResponse` (e.g., for Bitcoin tx_id A, with `payload_hash_A` and `signature_A`). These are publicly visible on-chain.
2. Submit a new `verify_foreign_transaction` request for a different, unconfirmed or fraudulent foreign-chain transaction (tx_id B). Any account can do this for 1 yoctoNEAR.
3. Call `respond_verify_foreign_tx(request_B, old_response_A)`.

The contract passes all checks:
- Caller is an attested participant ✓ [4](#0-3) 
- `signature_A` is valid over `payload_hash_A` ✓ [5](#0-4) 
- `request_B` exists in `pending_verify_foreign_tx_requests` ✓ [6](#0-5) 

`resolve_yields_for` then resumes all callers waiting on `request_B` with the fraudulent `old_response_A`. [7](#0-6) 

The callers of `verify_foreign_transaction(tx_id_B)` receive a `VerifyForeignTransactionResponse` whose `payload_hash` corresponds to tx_id A, not tx_id B. Any downstream bridge contract that gates fund release on this attestation — and does not independently recompute and check the expected payload hash — will treat an unconfirmed or fraudulent foreign-chain transaction as verified, enabling invalid bridge execution or double-spend.

---

### Likelihood Explanation

**Medium-High.** The attacker must be a single attested MPC participant (Byzantine node below the signing threshold). This is explicitly within the allowed attacker model. No threshold collusion is required. The attack requires only:
- Observing one prior valid response (public on-chain data).
- Submitting one `verify_foreign_transaction` call (permissionless, costs 1 yoctoNEAR).
- Calling `respond_verify_foreign_tx` with the replayed response (requires being an attested participant).

The window is any time a pending request exists for the target transaction.

---

### Recommendation

In `respond_verify_foreign_tx`, before accepting the response, recompute the expected payload hash from the `request` argument and assert it matches `response.payload_hash`. Specifically, construct `ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 { request: request.request.clone(), values: <extracted_values_from_response> })`, call `compute_msg_hash()`, and require the result equals `response.payload_hash`. Alternatively, mirror the pattern already used in `respond` for regular signatures, where the contract itself derives the payload from the stored request rather than trusting the caller-supplied value.

The linkage check already exists in the SDK's `ForeignChainSignatureVerifier::verify_signature` and should be lifted into the on-chain contract enforcement path. [8](#0-7) 

---

### Proof of Concept

**Setup:** MPC network is running. A legitimate Bitcoin tx_id A has been verified; the response `(payload_hash_A, signature_A)` is on-chain.

**Step 1 — Attacker submits a fraudulent request (as any user):**
```
verify_foreign_transaction({
    domain_id: <foreign_tx_domain>,
    payload_version: V1,
    request: BitcoinRpcRequest { tx_id: B, confirmations: 2, extractors: [BlockHash] }
})
```
This creates a pending entry in `pending_verify_foreign_tx_requests` for `request_B`.

**Step 2 — Byzantine participant replays the old response:**
```
respond_verify_foreign_tx(
    request = request_B,
    response = VerifyForeignTransactionResponse {
        payload_hash: payload_hash_A,   // hash of tx_id A's payload
        signature: signature_A,          // valid MPC signature over payload_hash_A
    }
)
```

**Step 3 — Contract validation (all pass):**
- `assert_caller_is_attested_participant_and_protocol_active()` → passes (Byzantine node is attested).
- `verify_ecdsa_signature(signature_A, payload_hash_A, root_pk)` → passes (signature is genuinely valid).
- `resolve_yields_for(&request_B, ...)` → finds the pending entry, resumes all waiting callers.

**Step 4 — Result:**
The caller of `verify_foreign_transaction(tx_id_B)` receives `VerifyForeignTransactionResponse { payload_hash: payload_hash_A, signature: signature_A }`. The contract has attested that tx_id B was verified, but the signed payload actually corresponds to tx_id A. Any bridge contract that does not recompute the expected hash from tx_id B will accept this as a valid attestation of tx_id B's confirmation. [9](#0-8) [10](#0-9)

### Citations

**File:** crates/contract/src/lib.rs (L705-705)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
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

**File:** crates/contract/src/pending_requests.rs (L66-88)
```rust
pub(crate) fn resolve_yields_for<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: &K,
    response_bytes: Vec<u8>,
) -> Result<(), Error>
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();

    if resumed > 0 {
        Ok(())
    } else {
        Err(InvalidParameters::RequestNotFound.into())
    }
}
```
