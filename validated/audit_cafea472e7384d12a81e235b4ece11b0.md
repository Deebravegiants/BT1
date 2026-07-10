### Title
`respond_verify_foreign_tx` Does Not Validate `response.payload_hash` Against the `request` Content — (`crates/contract/src/lib.rs`)

---

### Summary

`MpcContract::respond_verify_foreign_tx` verifies that `response.signature` is a valid threshold signature over the caller-supplied `response.payload_hash`, but never checks that `response.payload_hash` is actually derived from the `request` that is being resolved. A Byzantine MPC leader node can obtain a legitimate threshold signature for one pending foreign-tx request (R1) and submit it as the response for a *different* pending request (R2), causing the contract to attest to a foreign-chain transaction that was never actually verified for R2.

---

### Finding Description

The `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs` (lines 691–754) performs the following steps:

1. Asserts the caller is an attested participant.
2. Fetches the root public key for `request.domain_id`.
3. Verifies `response.signature` is a valid ECDSA signature over `response.payload_hash` using the **root** public key (zero tweak, as confirmed by `build_signature_request` at `crates/node/src/providers/verify_foreign_tx/sign.rs:43`).
4. Calls `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &request, …)` to deliver the response to every caller waiting on `request`.

**The missing check**: the contract never validates that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, observed_values }))`. The `payload_hash` field is entirely caller-controlled. The contract only checks that the signature is self-consistent with the hash — not that the hash is consistent with the request being resolved.

Compare this with the regular `respond` function (lines 564–651), where the signature is verified against `request.payload` — a field that is part of the stored request itself, so a signature for one request cannot pass verification for a different request. No such binding exists for `respond_verify_foreign_tx`.

The design intent (documented in `docs/foreign-chain-transactions.md` lines 165–189) is that `payload_hash = SHA-256(borsh(ForeignTxSignPayload { request, values }))`. The contract cannot recompute this hash because it does not know the extracted `values`. However, it also does not require the node to submit `values` so it can verify the hash, leaving the binding entirely unenforced on-chain.

---

### Impact Explanation

A Byzantine MPC leader node (a single participant, strictly below the signing threshold) can execute the following attack:

1. **Obtain a legitimate threshold signature for R1.** The leader coordinates the MPC signing protocol for a real pending request R1. Honest followers send their partial signatures; the leader assembles the full threshold signature `sig_A` over `hash_A = SHA-256(borsh({R1, values_A}))`.

2. **Submit the signature for a different pending request R2.** Instead of calling `respond_verify_foreign_tx(R1, {hash_A, sig_A})`, the leader calls `respond_verify_foreign_tx(R2, {hash_A, sig_A})`.

3. **Contract accepts the forged response.** The contract checks: is `sig_A` a valid signature over `hash_A` under the root key? Yes — so `signature_is_valid = true`. It then resolves R2 with `{payload_hash: hash_A, signature: sig_A}`.

4. **Caller of R2 receives a forged attestation.** The response claims the MPC network verified R2 and signed `hash_A`. But `hash_A` encodes R1's transaction data and extracted values, not R2's. Any downstream bridge contract that does not independently recompute the expected hash (using `ForeignChainSignatureVerifier::verify_signature` from `crates/near-mpc-sdk/src/foreign_chain.rs:41–89`) will accept this as proof that R2's foreign-chain transaction was verified, enabling invalid bridge execution or double-spend.

R1 is left unresolved and eventually times out — the Byzantine leader sacrifices one request to forge another.

---

### Likelihood Explanation

- The attacker must be an attested MPC participant (requires TEE attestation, a meaningful barrier).
- The attacker must be elected leader for a signing session (probabilistic, but achievable over time).
- Two pending `verify_foreign_transaction` requests must overlap (routine in a live bridge).
- No threshold collusion is required — a single Byzantine leader suffices.

Likelihood is **low-medium**: the TEE requirement raises the bar, but a compromised or malicious node operator who bypasses TEE integrity can execute this with a single signing session.

---

### Recommendation

Require the responding node to submit the extracted `values` alongside the response, and have the contract recompute and validate the hash on-chain:

```rust
// In respond_verify_foreign_tx, after verifying the signature:
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(), // newly required field
});
let expected_hash = expected_payload.compute_msg_hash()?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

This mirrors the check already present in `ForeignChainSignatureVerifier::verify_signature` (`crates/near-mpc-sdk/src/foreign_chain.rs:53–63`) and enforces the binding on-chain rather than relying on downstream callers to perform it.

---

### Proof of Concept

**Setup**: Two pending requests, R1 (Bitcoin tx `[0xAA; 32]`) and R2 (Bitcoin tx `[0xBB; 32]`), both submitted to `verify_foreign_transaction`.

**Byzantine leader actions**:
```
// Step 1: Run MPC protocol for R1 honestly, obtain (hash_A, sig_A)
hash_A = SHA256(borsh(ForeignTxSignPayload::V1 { request: R1, values: [BlockHash([0x11;32])] }))
sig_A  = threshold_sign(hash_A)   // threshold nodes participate honestly

// Step 2: Submit sig_A as the response for R2 (not R1)
respond_verify_foreign_tx(
    request = R2,
    response = VerifyForeignTransactionResponse {
        payload_hash: hash_A,   // ← hash for R1, not R2
        signature: sig_A,       // ← valid threshold sig over hash_A
    }
)
```

**Contract execution** (`crates/contract/src/lib.rs:718–753`):
- `verify_ecdsa_signature(sig_A, hash_A, root_pk)` → `Ok(())` ✓ (signature is self-consistent)
- `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &R2, serialize({hash_A, sig_A}))` → resolves R2 ✓

**Result**: The caller of R2 receives `{payload_hash: hash_A, signature: sig_A}`. The signature is cryptographically valid. The `payload_hash` encodes R1's data. Any bridge contract that does not call `ForeignChainSignatureVerifier::verify_signature` will accept this as proof that R2 was verified, enabling unauthorized bridge execution. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
