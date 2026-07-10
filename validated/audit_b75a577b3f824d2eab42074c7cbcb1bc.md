### Title
`respond_verify_foreign_tx` Verifies Signature Against Responder-Supplied `payload_hash` Without Binding It to the Original Request — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` function verifies the MPC signature against `response.payload_hash`, a value supplied by the calling node, rather than a hash computed from the original `VerifyForeignTransactionRequest`. A single malicious authenticated participant (strictly below the signing threshold) can replay a valid `(payload_hash, signature)` pair produced by the MPC network for one pending request onto a different pending request, causing the contract to resolve that request with a forged verification response.

---

### Finding Description

In `respond_verify_foreign_tx`, the on-chain signature check reads:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← taken from the response, not the request
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,                                             // ← root key, no derivation
)
.is_ok()
```

`payload_hash` is taken verbatim from the `VerifyForeignTransactionResponse` argument supplied by the calling node. The contract never checks that this hash corresponds to the transaction described in the `VerifyForeignTransactionRequest` that was originally enqueued. [1](#0-0) 

Contrast this with `respond`, where the payload is extracted from the stored **request**, not the response:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [2](#0-1) 

Here the payload comes from the request, so the on-chain check cryptographically binds the signature to the original user intent. No such binding exists in `respond_verify_foreign_tx`.

Because `respond_verify_foreign_tx` accepts any `payload_hash` the caller provides, a single malicious participant can:

1. Observe a legitimately produced `(H₁, S₁)` pair (hash + signature) from a completed `verify_foreign_transaction` response for request R₁ — this is visible on-chain.
2. Submit `respond_verify_foreign_tx` targeting a **different** pending request R₂ with `payload_hash = H₁` and `signature = S₁`.
3. The contract verifies `S₁` is valid for `H₁` under the root key — it is — and resolves R₂'s yield with the forged response. [3](#0-2) 

The user who submitted R₂ receives a response whose `payload_hash` does not correspond to their transaction, yet carries a cryptographically valid MPC signature. The `resolve_yields_for` call drains the pending queue for R₂ and delivers this forged payload to every waiting caller. [4](#0-3) 

---

### Impact Explanation

The `verify_foreign_transaction` flow is designed to let users prove that a specific foreign-chain transaction was verified by the MPC network before a signature is issued. By substituting a valid `(payload_hash, signature)` from a different transaction, a malicious participant makes the contract attest to the wrong transaction. Any downstream smart contract or bridge logic that trusts the MPC contract's response without independently re-deriving the expected hash from the original transaction will accept the forged attestation, enabling invalid bridge execution or double-spend conditions.

**Impact: High** — forged foreign-chain verification / cross-chain replay causing invalid bridge execution.

---

### Likelihood Explanation

The attacker must be an attested MPC participant (enforced by `assert_caller_is_attested_participant_and_protocol_active`), but only **one** such participant is needed — strictly below the signing threshold. [5](#0-4) 

A valid `(payload_hash, signature)` pair is observable on-chain from any previously completed `respond_verify_foreign_tx` call. Once one such pair exists, the attacker can replay it against any concurrently pending `verify_foreign_transaction` request. No threshold collusion is required.

**Likelihood: Medium** — requires a single malicious participant and at least one prior completed `verify_foreign_transaction` response on-chain.

---

### Recommendation

Compute `payload_hash` from the `request` fields (e.g., `hash(request.tx_id)`) **inside** `respond_verify_foreign_tx` rather than accepting it from the response. Verify the signature against this locally-computed hash, mirroring the pattern used in `respond` where `payload_hash` is extracted from the stored request, not the response. The `response.payload_hash` field should either be removed or validated to equal the locally-computed value before use.

---

### Proof of Concept

1. **Setup**: User A calls `verify_foreign_transaction` for transaction T₁ (hash H₁). The MPC network (threshold of nodes) signs H₁, producing S₁. A legitimate node calls `respond_verify_foreign_tx(R₁, {payload_hash: H₁, signature: S₁})`. The pair `(H₁, S₁)` is now visible on-chain in the transaction history.

2. **Target**: User B calls `verify_foreign_transaction` for transaction T₂ (hash H₂ ≠ H₁). Request R₂ is now pending in `pending_verify_foreign_tx_requests`.

3. **Attack**: Malicious participant calls `respond_verify_foreign_tx(R₂, {payload_hash: H₁, signature: S₁})`.

4. **Contract execution**:
   - `assert_caller_is_attested_participant_and_protocol_active()` → passes (attacker is a participant).
   - `verify_ecdsa_signature(S₁, H₁, root_key)` → **valid** (S₁ was produced by the MPC network for H₁).
   - `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &R₂, ...)` → R₂'s yield is resolved with `{payload_hash: H₁, signature: S₁}`.

5. **Result**: User B's contract receives a response with a valid MPC signature, but `payload_hash = H₁` (T₁'s hash), not H₂. Any bridge logic that does not independently re-derive the expected hash from T₂ will accept this as a valid MPC attestation of T₂, enabling unauthorized bridge execution. [6](#0-5)

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
