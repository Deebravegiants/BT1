### Title
Malicious Leader Can Deliver Forged Foreign-Chain Verification Response by Substituting Payload Hash — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that `response.signature` is a valid ECDSA signature over `response.payload_hash` under the root public key. It does **not** verify that `response.payload_hash` is the correct hash for the submitted `request`. A single malicious leader node — strictly below the signing threshold — can obtain a valid threshold signature over `payload_hash_A` (produced during the normal protocol for `request_A`) and submit it as the response to a different pending `request_B`. The contract accepts it, and every caller waiting on `request_B` receives a forged `VerifyForeignTransactionResponse` whose `payload_hash` commits to a completely different foreign-chain transaction.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs the following check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,          // ← root key, not a derived key
)
.is_ok()
``` [1](#0-0) 

After this check passes, the contract resolves all pending yields for the caller-supplied `request` with the full `response`:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The `VerifyForeignTransactionRequest` key stored in `pending_verify_foreign_tx_requests` contains the full foreign-chain RPC request (e.g., Bitcoin `tx_id`, `confirmations`, `extractors`): [3](#0-2) 

The `VerifyForeignTransactionResponse` contains `payload_hash` and `signature`. The correct `payload_hash` is `SHA-256(borsh(ForeignTxSignPayload{request, extracted_values}))`. The contract never recomputes or cross-checks this hash against the stored `request`. Any `payload_hash` with a valid root-key signature is accepted and forwarded to all waiting callers.

Compare with `respond` for regular sign requests, where the payload is taken directly from the stored `request` and the signature is verified against a key derived from that request's tweak — making substitution impossible: [4](#0-3) 

---

### Impact Explanation

A caller who submits `verify_foreign_transaction(request_B)` receives a `VerifyForeignTransactionResponse` whose `payload_hash` commits to a completely different foreign-chain transaction (`request_A`). Any downstream bridge contract that trusts the MPC contract's delivery — without independently recomputing the expected payload hash from the original request — will authorize an operation based on fabricated verification data. This constitutes **forged foreign-chain verification enabling invalid bridge execution**, matching the High impact category.

---

### Likelihood Explanation

The attack requires only a single malicious MPC participant acting as the signing-round leader. No threshold collusion is needed: the threshold participants sign `payload_hash_A` as part of the normal protocol for `request_A`; the leader alone decides which pending `request` to pair that signature with when calling `respond_verify_foreign_tx`. Any participant can be elected leader. The preconditions (two concurrent pending requests) are routine in production.

---

### Recommendation

In `respond_verify_foreign_tx`, enforce that `response.payload_hash` is consistent with the stored `request`. Two options:

1. **Include extracted values in the response.** Require the response to carry the `Vec<ExtractedValue>` alongside the hash. The contract recomputes `SHA-256(borsh(ForeignTxSignPayload{request, extracted_values}))` and asserts it equals `response.payload_hash` before accepting the response.

2. **Bind the payload hash to the request at submission time.** Have the leader commit to the payload hash before the threshold protocol begins (e.g., via a two-phase submit/respond), so the contract can verify the hash matches what was committed for that specific request.

Option 1 is simpler and consistent with the existing `ForeignTxSignPayload` structure already used by `ForeignChainSignatureVerifier::verify_signature` in the SDK. [5](#0-4) 

---

### Proof of Concept

1. Alice submits `verify_foreign_transaction(request_A)` for Bitcoin `tx_A`. Bob submits `verify_foreign_transaction(request_B)` for Bitcoin `tx_B`. Both are queued in `pending_verify_foreign_tx_requests`.

2. The MPC network runs the threshold protocol for `request_A`. Nodes query Bitcoin for `tx_A`, extract values, compute `payload_hash_A = SHA-256(borsh(ForeignTxSignPayload{request_A, extracted_values_A}))`, and produce a valid threshold signature `sig_A` over `payload_hash_A`.

3. The malicious leader calls:
   ```
   respond_verify_foreign_tx(
       request  = request_B,          // Bob's pending request
       response = { payload_hash_A, sig_A }  // signature for tx_A
   )
   ```

4. The contract executes:
   - `assert_caller_is_attested_participant_and_protocol_active()` → passes (leader is a valid participant).
   - `verify_ecdsa_signature(sig_A, payload_hash_A, root_key)` → **passes** (signature is genuinely valid).
   - No check that `payload_hash_A` corresponds to `request_B`.
   - `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &request_B, response)` → Bob's yield is resumed with `{payload_hash_A, sig_A}`.

5. Bob's caller receives `VerifyForeignTransactionResponse{ payload_hash: payload_hash_A, signature: sig_A }`. The response carries a valid MPC signature, but it commits to `tx_A`'s data, not `tx_B`'s. Any bridge contract that uses this response to authorize a cross-chain action for `tx_B` does so on forged verification evidence. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L155-155)
```rust
    pending_verify_foreign_tx_requests: LookupMap<VerifyForeignTransactionRequest, Vec<YieldIndex>>,
```

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

**File:** crates/contract/src/lib.rs (L692-754)
```rust
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
