### Title
Unverified `payload_hash` Binding in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay by a Single Byzantine Participant - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is valid over the caller-supplied `response.payload_hash`, but never verifies that `payload_hash` was actually computed from the specific `request` parameter being resolved. A single malicious attested participant (below signing threshold) can replay a legitimate threshold signature produced for `request_A` to resolve a completely different pending `request_B`, delivering a forged foreign-chain attestation to `request_B`'s callers.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs two independent operations:

**Step 1 — Signature check (lib.rs:718–743):**
```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // caller-supplied
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // only checks: sig is valid over THIS hash
    &secp_pk,               // root public key
).is_ok()
```

**Step 2 — Request resolution (lib.rs:749–753):**
```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,               // caller-supplied request key
    serde_json::to_vec(&response).unwrap(),
)
``` [1](#0-0) 

The contract verifies the signature is valid over `payload_hash`, but **never verifies** that `payload_hash == SHA256(borsh(ForeignTxSignPayload::V1 { request: request.request.clone(), values: observed_values }))` for the specific `request` being resolved.

The `ForeignTxSignPayloadV1` struct that the MPC nodes sign binds both the original request and the observed extracted values:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [2](#0-1) 

The contract has no way to reconstruct this hash (it does not know `values`), and it never attempts to. The `payload_hash` is accepted as an opaque 32-byte blob whose only constraint is that the signature over it is valid.

The SDK-level verifier (`ForeignChainSignatureVerifier::verify_signature`) does enforce this binding, but it is an off-chain helper for downstream contracts — the on-chain MPC contract itself does not:

```rust
let expected_payload_hash = expected_payload.compute_msg_hash()...;
let payload_is_correct = expected_payload_hash == response.payload_hash;
``` [3](#0-2) 

---

### Impact Explanation

A single malicious attested participant (strictly below the signing threshold) can:

1. Observe a legitimate threshold signature `sig_A` produced for `request_A` — either as the leader node that assembled it, or by reading the on-chain `respond_verify_foreign_tx` call for `request_A` after it is submitted.
2. Call `respond_verify_foreign_tx(request = request_B, response = { payload_hash = H(request_A, values_A), signature = sig_A })` while `request_B` is still pending.
3. The contract accepts the call: `sig_A` is a valid threshold signature over `H(request_A, values_A)` using the root key.
4. `request_B`'s pending yield queue is drained and every waiting caller receives `{ payload_hash = H(request_A, values_A), signature = sig_A }` — an attestation that commits to `request_A`'s foreign-chain data, not `request_B`'s.
5. `request_B` is permanently removed from the pending map; it cannot be re-processed.

For bridge contracts that use the MPC network to *discover* extracted values (e.g., "what block hash was this tx included in?") rather than to *confirm* known values, the caller cannot independently verify the `payload_hash` without the extracted values. Such contracts would accept the forged attestation and could release funds or execute state transitions based on incorrect foreign-chain data.

This matches: **High — forged foreign-chain verification that causes invalid bridge execution.**

---

### Likelihood Explanation

- Requires only **one** malicious attested participant — well below the signing threshold.
- The attacker needs a valid threshold signature for any prior `request_A`. This is available on-chain in every successful `respond_verify_foreign_tx` transaction, or can be obtained by the leader node before submission.
- The attack is a simple contract call with no special tooling.
- Any pending `request_B` with the same domain is a valid target.

---

### Recommendation

The contract must bind `response.payload_hash` to the `request` parameter before accepting the response. Since the contract does not know the extracted `values`, the recommended fix is to have the MPC nodes include the extracted values in the response, allowing the contract to recompute and verify the hash:

```rust
// In respond_verify_foreign_tx, after signature verification:
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.extracted_values.clone(), // add to response DTO
}).compute_msg_hash()?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

Alternatively, the signed payload could be restructured so that the `request` hash is a separately verifiable prefix, allowing the contract to check request binding without knowing `values`.

---

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(request = request_A) → pending
2. Bob   submits verify_foreign_transaction(request = request_B) → pending

3. MPC network (threshold) produces:
     sig_A  = Sign_root( H(request_A, values_A) )
   Leader node is about to call respond_verify_foreign_tx for request_A.

4. Malicious attested participant (single node) intercepts sig_A
   (or reads it from the mempool / on-chain after step 3 completes for request_A)
   and calls:
     respond_verify_foreign_tx(
       request  = request_B,
       response = { payload_hash = H(request_A, values_A), signature = sig_A }
     )

5. Contract checks:
   a. Caller is attested participant          ✓
   b. verify_ecdsa_signature(sig_A,
        H(request_A, values_A), root_key)    ✓  (valid threshold sig)
   c. resolve_yields_for(request_B, response) ✓  (request_B is pending)

6. Bob's yield resolves with:
     { payload_hash = H(request_A, values_A), signature = sig_A }
   — an attestation for request_A's foreign-chain data, not request_B's.

7. Bob's bridge contract verifies:
     verify_ecdsa_signature(sig_A, H(request_A, values_A), root_key) → OK
   and, lacking the extracted values, cannot detect the mismatch.
   It proceeds to execute based on request_A's foreign-chain state.

8. request_B is permanently removed from the pending map.
   Bob cannot obtain a correct attestation.
``` [4](#0-3) [5](#0-4) [2](#0-1)

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

**File:** crates/contract/src/pending_requests.rs (L43-59)
```rust
pub(crate) fn push_pending_yield<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: K,
    data_id: CryptoHash,
) where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
    }
    queue.push(YieldIndex { data_id });
```
