### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Submitted `request`, Enabling Cross-Request Signature Replay by a Byzantine Participant — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid threshold signature over `response.payload_hash`, but it never checks that `response.payload_hash` was actually derived from the `request` argument supplied in the same call. A single Byzantine attested participant (strictly below the signing threshold) can replay a legitimately-produced threshold signature from one pending foreign-transaction verification request to satisfy a completely different pending request, causing the victim caller to receive a valid MPC signature that attests to the wrong foreign-chain data.

---

### Finding Description

The vulnerability class from the external report is: *a value is computed/transformed from an input, but the original/stale input is used in the subsequent critical operation instead of the post-transformation value*. The analog here is the inverse: the contract receives a `payload_hash` that is supposed to be derived from `request`, but it never enforces that binding — it uses `request` only as a lookup key while blindly trusting the caller-supplied `payload_hash`.

**Flow of `verify_foreign_transaction` / `respond_verify_foreign_tx`:**

1. A user calls `verify_foreign_transaction(request_args)`. The contract converts the args into a `VerifyForeignTransactionRequest` (containing `domain_id`, `payload_version`, and the chain-specific `ForeignChainRpcRequest`) and stores a yield keyed by that request.
2. MPC nodes independently query the foreign chain, extract values, compute `payload_hash = SHA-256(borsh(ForeignTxSignPayloadV1 { request, values }))`, and produce a threshold signature over that hash.
3. The leader node calls `respond_verify_foreign_tx(request, response)` where `response = { payload_hash, signature }`.

**The contract's verification in `respond_verify_foreign_tx` (lines 718–743):**

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,   // ← taken directly from the response, never tied to `request`
    &secp_pk,
)
.is_ok()
```

The contract only checks: *"is `response.signature` a valid threshold signature over `response.payload_hash`?"* It does **not** check: *"was `response.payload_hash` computed from this specific `request`?"*

After the signature check passes, the contract resolves all queued yields for `request` with the full `response` bytes (line 749–753):

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
```

**Contrast with `respond` for regular signatures (lines 600–608):**

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,          // ← taken from `request`, not from a caller-supplied field
    &expected_public_key,
)
```

In `respond`, the payload being verified is extracted directly from the `request` struct, so the signature is inherently bound to the request. `respond_verify_foreign_tx` breaks this invariant by accepting a caller-supplied `payload_hash` that is never cross-checked against `request`.

---

### Impact Explanation

A Byzantine attested participant (one node, strictly below threshold) who has observed or participated in the threshold signing of request B (for `tx_id=Y`) possesses the full `(payload_hash_B, sig_B)` pair. They can call:

```
respond_verify_foreign_tx(request = A, response = { payload_hash_B, sig_B })
```

where `request=A` is a different pending request (for `tx_id=X`). The contract:
1. Verifies `sig_B` over `payload_hash_B` → **passes** (it is a genuine threshold signature).
2. Looks up the pending yield for `request=A` → **found**.
3. Resolves the yield with `{ payload_hash_B, sig_B }`.

The caller who submitted request A receives a valid MPC threshold signature, but it attests to `tx_id=Y`'s extracted values, not `tx_id=X`'s. Any downstream bridge or NEAR contract that trusts this response will accept fabricated foreign-chain state. This enables forged foreign-chain verification and potential double-spend or invalid bridge execution — matching the **High** impact tier: *"Cross-chain replay, forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- The attacker must be an attested MPC participant (one Byzantine node below threshold suffices).
- The attacker needs two concurrent pending requests on the same `ForeignTx` domain (trivially achievable: they can submit one themselves).
- No threshold collusion is required; the attacker simply reuses a legitimately-produced threshold signature.
- All pending requests are observable on-chain, so the attacker can pick any victim request.

---

### Recommendation

The contract must recompute the expected `payload_hash` from the `request` and the extracted values, then assert it matches `response.payload_hash`. Because the current response DTO omits `extracted_values` (to stay within NEAR promise-data limits), the fix requires including them in the response so the contract can verify the binding:

```rust
// In respond_verify_foreign_tx, after receiving response:
let expected_payload_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.extracted_values.clone(), // add this field to the response DTO
})
.compute_msg_hash()?;

if expected_payload_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

Alternatively, restructure the response so the contract derives `payload_hash` itself (analogous to how `respond` derives the payload from `request.payload`), removing the caller-supplied `payload_hash` field entirely.

---

### Proof of Concept

1. Attacker (Byzantine attested participant) submits `verify_foreign_transaction` for `tx_id=Y` (request B).
2. Victim submits `verify_foreign_transaction` for `tx_id=X` (request A) — both are now pending.
3. MPC nodes process request B honestly, producing `(payload_hash_B, sig_B)`.
4. Attacker (having participated in signing) calls:
   ```
   respond_verify_foreign_tx(
       request = VerifyForeignTransactionRequest { tx_id: X, ... },  // request A
       response = VerifyForeignTransactionResponse {
           payload_hash: payload_hash_B,   // hash of tx_id=Y's data
           signature: sig_B,               // valid threshold sig over payload_hash_B
       }
   )
   ```
5. Contract at line 729 verifies `sig_B` over `payload_hash_B` → valid.
6. Contract at line 749 resolves request A's yield with `{ payload_hash_B, sig_B }`.
7. Victim's NEAR contract receives a valid MPC attestation for `tx_id=Y`'s block hash, believing it is for `tx_id=X`. A bridge acting on this would process a fraudulent inbound transfer. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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
