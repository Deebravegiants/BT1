### Title
Forged Foreign-Chain Verification via Cross-Request Signature Replay in `respond_verify_foreign_tx` — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the ECDSA signature in the response is valid over `response.payload_hash`, but **never verifies that `response.payload_hash` was actually derived from the submitted `request`**. A single Byzantine MPC participant strictly below the signing threshold can reuse any previously observed valid MPC signature (from a prior, unrelated request) to resolve a pending foreign-tx request with fabricated data. The pending request is permanently consumed, and the caller receives a `VerifyForeignTransactionResponse` whose `payload_hash` does not correspond to the transaction they asked to verify — a forged foreign-chain verification.

---

### Finding Description

The root cause is in `respond_verify_foreign_tx`:

```rust
// crates/contract/src/lib.rs  lines 718–753
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← taken from caller

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // ← verified against THIS hash …
    &secp_pk,
)
.is_ok()
// … but the contract NEVER checks that payload_hash == SHA256(borsh(ForeignTxSignPayloadV1{request, values}))
// where `request` matches the pending VerifyForeignTransactionRequest.

pending_requests::resolve_yields_for(          // ← drains the queue unconditionally
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [1](#0-0) 

The intended invariant is that `payload_hash = SHA256(borsh(ForeignTxSignPayloadV1 { request, values }))`, binding the hash to the specific `request` being answered. The contract enforces the signature over the hash, but **not the binding between the hash and the request**. The `payload_hash` field is entirely attacker-controlled.

Compare with `respond`, which correctly derives the hash from the request itself:

```rust
// crates/contract/src/lib.rs  lines 600–608
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,           // ← derived from request, not from response
    &expected_public_key,
)
``` [2](#0-1) 

`respond_verify_foreign_tx` lacks this binding. The `VerifyForeignTransactionResponse` struct carries `payload_hash` as a free field: [3](#0-2) 

The fan-out drain in `resolve_yields_for` removes the entire pending queue for `request` unconditionally once the signature check passes: [4](#0-3) 

This is the direct analog of the Timelock "Depth 2" scenario: the call *succeeds* (signature is cryptographically valid), but the intended operation is unaffected (the hash does not correspond to the actual foreign transaction), and the queued state is permanently lost.

---

### Impact Explanation

**Forged foreign-chain verification (High):** A malicious participant submits `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: sig_A })`. The contract accepts it, drains the yield queue for `request_B`, and delivers `{ payload_hash_A, sig_A }` to the caller. Any bridge contract that does not independently recompute the expected `payload_hash` from `request_B` and compare will accept this as proof that `request_B`'s foreign transaction was verified — it was not. The MPC network actually attested to `request_A`'s data.

**Permanent state corruption (Medium):** Even if the bridge contract does verify the hash and rejects the response, the pending yield for `request_B` has already been drained. The caller must resubmit and pay again, and the deposit from the original call is not refunded.

---

### Likelihood Explanation

- The attacker is a **single Byzantine MPC participant strictly below the signing threshold** — exactly the adversary model the system must tolerate.
- The attacker does **not** need to forge a signature. They only need to have observed any prior valid MPC signature over any `payload_hash`. Every MPC participant observes the final signature as part of the threshold signing protocol before it is submitted on-chain.
- Any previously submitted `respond_verify_foreign_tx` call is also publicly visible on-chain, giving the attacker a growing pool of reusable `(payload_hash, signature)` pairs.
- The attack requires no special timing, no gas manipulation, and no threshold collusion.

---

### Recommendation

The contract must bind `response.payload_hash` to `request` before accepting the response. Because the contract does not know the extracted `values`, it cannot recompute the full `payload_hash`. Two viable fixes:

1. **Structured hash with a verifiable prefix.** Change the hash to `SHA256(borsh(request) || SHA256(borsh(values)))`. The contract can independently compute `SHA256(borsh(request))` and verify it is the first input to the outer hash (requires a small protocol change to expose the intermediate commitment).

2. **Include `request` in the response and verify it.** Require the MPC node to echo the `request` back in the response, and assert `response.request == request` before accepting. This is the simplest on-chain fix with no cryptographic changes.

Either approach closes the gap between "signature is valid" and "signature is valid *for this request*."

---

### Proof of Concept

```
// Setup: two pending foreign-tx requests exist on-chain.
// request_A = VerifyForeignTransactionRequest { tx_id: 0xAAAA, ... }
// request_B = VerifyForeignTransactionRequest { tx_id: 0xBBBB, ... }

// Step 1: MPC network processes request_A.
//   payload_hash_A = SHA256(borsh(ForeignTxSignPayloadV1 { request: request_A, values: [...] }))
//   sig_A = threshold_sign(payload_hash_A)
//   Malicious participant observes sig_A during the signing round.

// Step 2: Malicious participant races to call respond_verify_foreign_tx
//   with request_B but the signature from request_A.
contract.respond_verify_foreign_tx(
    request_B,                                    // pending request for tx 0xBBBB
    VerifyForeignTransactionResponse {
        payload_hash: payload_hash_A,             // hash of tx 0xAAAA's payload
        signature: sig_A,                         // valid sig over payload_hash_A
    }
);

// Step 3: Contract checks verify_ecdsa_signature(sig_A, payload_hash_A, root_pk) → OK
//   No check that payload_hash_A was derived from request_B.
//   resolve_yields_for drains the queue for request_B.

// Step 4: Caller of request_B receives { payload_hash_A, sig_A }.
//   payload_hash_A encodes tx 0xAAAA's block hash, not tx 0xBBBB's.
//   A bridge contract that skips the local hash recomputation step
//   accepts this as proof that tx 0xBBBB was verified — it was not.
//   The pending yield for request_B is permanently gone.
``` [5](#0-4) [6](#0-5)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
}
```

**File:** crates/contract/src/pending_requests.rs (L62-88)
```rust
/// Resume every yield queued for `request` with `response_bytes`, draining the
/// fan-out map in one pass. Returns `Err(RequestNotFound)` if the map held no entry.
///
/// Resuming a yield that has already timed out is a no-op at the SDK level.
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
