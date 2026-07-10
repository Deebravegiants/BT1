### Title
`respond_verify_foreign_tx` Accepts Caller-Supplied `payload_hash` Without Binding It to the Pending Request - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_verify_foreign_tx` contract method verifies only that the submitted ECDSA signature is valid over the caller-supplied `response.payload_hash`. It never re-derives or cross-checks that `payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload{request, extracted_values}))` for the specific pending request being resolved. A single Byzantine attested participant can therefore recycle a legitimately-produced `(payload_hash, signature)` pair from any prior signing and submit it as the response for a completely different pending request, causing the contract to deliver a forged foreign-chain attestation to the waiting caller.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs the following checks before resolving a pending yield:

1. Caller is an attested participant (`assert_caller_is_attested_participant_and_protocol_active`).
2. The ECDSA signature in the response is valid over `response.payload_hash` against the domain's root public key. [1](#0-0) 

What is **absent** is any check that `response.payload_hash` is the canonical hash for the specific `request` argument that was looked up in `pending_verify_foreign_tx_requests`. The sign payload is defined as:

```
payload_hash = SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))
``` [2](#0-1) 

Because `request` is embedded inside the hash, a hash produced for request R1 is cryptographically distinct from the correct hash for request R2. The contract, however, never recomputes the expected hash from the pending request; it simply trusts whatever 32-byte value the responding participant supplies.

The responding participant is a single node — there is no on-chain quorum requirement for `respond_verify_foreign_tx`. The threshold signing protocol guarantees the signature was produced by ≥ t nodes, but it does not prevent one of those nodes from later re-submitting the resulting `(hash, sig)` pair against a different pending request entry. [3](#0-2) 

The SDK helper `ForeignChainSignatureVerifier::verify_signature` does perform the binding check on the client side, but this is optional and not enforced by the contract. [4](#0-3) 

### Impact Explanation

The Omnibridge inbound flow is the primary production use-case: a bridge contract submits `verify_foreign_transaction` for a specific foreign-chain transaction and then releases funds only after receiving a valid MPC attestation. If a Byzantine participant can substitute the attestation for a different transaction, the bridge contract receives a signature that is cryptographically valid (the MPC network did sign it) but semantically wrong (it attests to a different tx). A bridge contract that checks only signature validity — which is the natural and documented usage — would be deceived into releasing funds for an unverified or non-existent transaction.

This maps directly to the allowed impact: **forged foreign-chain verification causing invalid bridge execution or double-spend conditions**.

### Likelihood Explanation

- Requires exactly **one** Byzantine attested participant, strictly below the signing threshold.
- The attacker needs a previously produced `(payload_hash, signature)` pair. Every completed signing produces one; the final signature is submitted on-chain and is publicly observable.
- No special timing, network access, or key material beyond normal node operation is required.
- A pending request from any user is sufficient as the target; the attacker does not need to control the submitting account.

### Recommendation

The contract must re-derive the expected `payload_hash` from the pending request before accepting the response. Since the extracted values are not currently included in the response DTO, the fix requires extending `VerifyForeignTransactionResponse` to carry the extracted values and then performing the binding check on-chain:

```rust
// In respond_verify_foreign_tx, after retrieving the pending request:
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.extracted_values.clone(), // new field
});
let expected_hash = expected_payload.compute_msg_hash()
    .map_err(|_| RespondError::PayloadHashComputationFailed)?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

This mirrors the check already present in the SDK's `verify_signature` and closes the gap between off-chain and on-chain validation.

### Proof of Concept

1. **Setup**: MPC network is running with participants P1 (honest) … Pn (Byzantine = Pn). Two users submit requests:
   - Alice submits `verify_foreign_transaction` for Bitcoin tx **T1** → pending request **R1** is stored.
   - Bob submits `verify_foreign_transaction` for Bitcoin tx **T2** (fraudulent / non-existent) → pending request **R2** is stored.

2. **Legitimate signing for R1**: Nodes query Bitcoin RPC, extract block hash B1, compute `H1 = SHA-256(borsh({R1, [BlockHash(B1)]}))`, and run threshold ECDSA. The final signature `sig_H1` is produced. Honest node P1 calls `respond_verify_foreign_tx(R1, {payload_hash: H1, sig: sig_H1})` — Alice's yield resolves correctly.

3. **Attack**: Byzantine node Pn, having observed `(H1, sig_H1)`, now calls:
   ```
   respond_verify_foreign_tx(R2, { payload_hash: H1, signature: sig_H1 })
   ```
   The contract checks:
   - Pn is an attested participant ✓
   - `verify_ecdsa_signature(sig_H1, H1, root_pk)` → valid ✓
   - R2 is in `pending_verify_foreign_tx_requests` ✓
   - **No check that H1 is the correct hash for R2** ✗

   Bob's yield resolves with `{payload_hash: H1, signature: sig_H1}`.

4. **Bridge exploitation**: Bob's bridge contract receives the response, verifies `sig_H1` over `H1` (valid), and — lacking the extracted values needed to recompute the expected hash — treats the response as a valid attestation for T2. Funds are released for a transaction that was never verified.

<cite repo="Tylerpinwa/m

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
