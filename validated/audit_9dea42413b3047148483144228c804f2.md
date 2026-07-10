### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Pending `request`, Enabling Cross-Request Response Injection by a Single Byzantine Participant — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` contract method verifies that the MPC signature is cryptographically valid over `response.payload_hash`, but never verifies that `response.payload_hash` was actually derived from the `request` argument supplied in the same call. A single Byzantine attested participant (strictly below the signing threshold) can therefore take a legitimately-produced MPC signature for foreign transaction A and deliver it as the response to a different pending request for foreign transaction B. The caller of request B receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes transaction A's data, not transaction B's — a forged foreign-chain verification attestation.

---

### Finding Description

**Root cause — missing binding check in `respond_verify_foreign_tx`**

`respond_verify_foreign_tx` (lines 691–754 of `crates/contract/src/lib.rs`) accepts two independent arguments:

- `request: VerifyForeignTransactionRequest` — used only as a lookup key into `pending_verify_foreign_tx_requests`.
- `response: VerifyForeignTransactionResponse` — contains `payload_hash` and `signature`.

The only cryptographic check performed is:

```rust
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // taken directly from response, never tied to request
    &secp_pk,               // root public key, no tweak
)
.is_ok()
``` [1](#0-0) 

The contract confirms that `signature` is a valid ECDSA signature over `payload_hash` under the root key. It does **not** confirm that `payload_hash` was derived from `request.request` (the `ForeignChainRpcRequest`). After the signature check passes, the response is immediately fanned out to every yield queued under `request`:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

**What `payload_hash` actually encodes**

On the node side, `payload_hash` is `ForeignTxSignPayload::compute_msg_hash()`, which hashes `(ForeignChainRpcRequest, extracted_values)` — i.e., it encodes the specific tx_id and chain data that the MPC network actually verified:

```rust
Ok(SignatureRequest {
    ...
    tweak: Tweak::new([0u8; 32]),   // zero tweak → root key
    ...
})
``` [3](#0-2) 

Because `VerifyForeignTransactionRequest` contains only `{ForeignChainRpcRequest, DomainId, ForeignTxPayloadVersion}` — no caller identity, no `payload_hash` — two structurally different requests (different tx_ids) produce two different map keys, and the contract has no way to enforce that the response delivered to key B was produced for key B. [4](#0-3) 

**Exploit path**

1. Alice submits `verify_foreign_transaction({bitcoin_tx_123, domain_0, V1})` → pending under key A.
2. Bob submits `verify_foreign_transaction({bitcoin_tx_456, domain_0, V1})` → pending under key B.
3. The honest MPC network verifies `bitcoin_tx_456`, producing `(payload_hash_456, sig_456)`.
4. A single Byzantine attested participant calls:
   ```
   respond_verify_foreign_tx(
       request  = {bitcoin_tx_123, domain_0, V1},   // key A
       response = {payload_hash_456, sig_456}        // produced for key B
   )
   ```
5. The contract checks: is `sig_456` valid over `payload_hash_456` under the root key? **Yes** — the signature is genuine.
6. The contract resolves key A with `{payload_hash_456, sig_456}`.
7. Alice's yield resumes with a `VerifyForeignTransactionResponse` whose `payload_hash` encodes `bitcoin_tx_456`, not `bitcoin_tx_123`. The MPC network never verified `bitcoin_tx_123`.

The attacker requires no threshold collusion and forges no cryptographic material; they merely redirect an already-produced signature to the wrong pending request.

---

### Impact Explanation

**Classification**: Forged foreign-chain verification — High.

Alice's bridge contract receives a valid MPC signature, but the `payload_hash` it covers encodes a different transaction than the one Alice requested. Any bridge contract that does not independently recompute `ForeignTxSignPayload::compute_msg_hash(alice_request, expected_values)` and compare it to the returned `payload_hash` will accept the forged attestation as proof that `bitcoin_tx_123` was verified. This enables invalid bridge execution (e.g., releasing funds on NEAR for a foreign deposit that was never confirmed) or double-spend conditions if the same legitimate signature is replayed across multiple pending requests.

This maps directly to the allowed impact: *"Cross-chain replay, forged foreign-chain verification… that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

**Medium.** The attacker must be a single Byzantine attested participant — one compromised MPC node that has passed TEE attestation. This is strictly below the signing threshold. The attack additionally requires the honest MPC network to have already produced a valid signature for at least one other pending foreign-tx request (so there is a `(payload_hash, sig)` pair to redirect). Both conditions are realistic in a live bridge deployment where multiple foreign-tx requests are processed concurrently.

---

### Recommendation

In `respond_verify_foreign_tx`, after verifying the signature, recompute the expected `payload_hash` from `request.request` and the extracted values carried in the response, and assert equality before calling `resolve_yields_for`. Concretely:

1. Extend `VerifyForeignTransactionResponse` to include the `Vec<ExtractedValue>` alongside `payload_hash` and `signature`.
2. In `respond_verify_foreign_tx`, compute:
   ```rust
   let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
       request: request.request.clone(),
       values: response.extracted_values.clone(),
   }).compute_msg_hash()?;
   if expected_hash != response.payload_hash {
       return Err(RespondError::PayloadHashMismatch.into());
   }
   ```
3. Verify the signature over `expected_hash` (not the caller-supplied `payload_hash`).

This binds the response to the request at the contract level, eliminating the cross-request injection vector regardless of individual node behavior.

---

### Proof of Concept

```
// State: two pending requests
pending_verify_foreign_tx_requests = {
    {bitcoin_tx_123, domain_0, V1} → [yield_alice],
    {bitcoin_tx_456, domain_0, V1} → [yield_bob],
}

// Honest MPC network responds for bitcoin_tx_456:
//   payload_hash_456 = hash({bitcoin_tx_456, [BlockHash=0xdeadbeef...]})
//   sig_456 = ECDSA_sign(root_key, payload_hash_456)

// Byzantine participant (single node, below threshold) calls:
respond_verify_foreign_tx(
    request  = {bitcoin_tx_123, domain_0, V1},
    response = { payload_hash: payload_hash_456, signature: sig_456 }
)

// Contract check: verify_ecdsa_signature(sig_456, payload_hash_456, root_pk) → OK
// Contract action: resolve_yields_for({bitcoin_tx_123,...}, serialize({payload_hash_456, sig_456}))

// Result: yield_alice resumes with payload_hash encoding bitcoin_tx_456.
// Alice's bridge contract receives a valid MPC signature that attests
// to bitcoin_tx_456 being confirmed — not bitcoin_tx_123.
// If Alice's contract does not re-derive and compare payload_hash,
// it authorizes a bridge action for an unverified transaction.
``` [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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
