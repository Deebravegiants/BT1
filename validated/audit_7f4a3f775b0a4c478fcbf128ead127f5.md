### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Resolved Request — Forged Foreign-Chain Verification via Cross-Request Replay - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` accepts a caller-supplied `response.payload_hash` and verifies only that the signature is valid over that hash under the root public key. It never checks that `payload_hash` is actually `SHA-256(borsh(ForeignTxSignPayload{request, extracted_values}))` for the specific `request` being resolved. A single Byzantine participant below the signing threshold who has participated in any prior legitimate `verify_foreign_tx` signing session can replay that session's `(sig, hash)` pair against any other pending `verify_foreign_tx` request, delivering a forged response that resolves the yield and permanently blocks the legitimate response.

---

### Finding Description

**Root cause — `respond_verify_foreign_tx` (crates/contract/src/lib.rs:718–753)**

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← attacker-supplied

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,                                            // ← root key, no derivation
)
.is_ok()
``` [1](#0-0) 

The contract takes `payload_hash` from the response (fully attacker-controlled) and verifies only that the ECDSA signature is valid over it under the root public key. It does not verify that `payload_hash` equals `SHA-256(borsh(ForeignTxSignPayloadV1 { request: <the request being resolved>, values: <observed values> }))`.

**Contrast with `respond` (regular sign path)**

In `respond`, the payload hash is taken from the *stored request* (not from the response), and the signature is verified against the *derived* key (account + path specific tweak):

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
let expected_public_key = derive_key_secp256k1(&affine, &request.tweak)...;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response, payload_hash, &expected_public_key,
)
``` [2](#0-1) 

The `verify_foreign_tx` path bypasses both protections: the payload hash is caller-supplied, and the key is the undifferentiated root key (tweak = `[0u8; 32]`). [3](#0-2) 

**Why a single below-threshold participant can execute this**

`assert_caller_is_attested_participant_and_protocol_active` checks only that the caller is *one* attested participant in the current epoch — not that threshold-many participants agreed on the response: [4](#0-3) 

The threshold requirement is enforced off-chain during the MPC signing protocol. Once a valid `(sig, hash)` pair is produced by a legitimate session, any single participant who was present in that session possesses it and can submit it unilaterally to the contract.

**The cross-request replay**

`ForeignTxSignPayloadV1` binds the hash to a specific `ForeignChainRpcRequest` and its extracted values: [5](#0-4) 

A Byzantine participant P who participated in a legitimate session for request R1 (producing `hash1 = SHA-256(borsh({R1.request, V1}))`) can call:

```
respond_verify_foreign_tx(R2, { payload_hash: hash1, signature: sig })
```

The contract checks: is `sig` valid over `hash1` under the root key? Yes — it was legitimately produced. It then resolves R2's yield with `{ payload_hash: hash1, signature: sig }` and removes R2 from `pending_verify_foreign_tx_requests`. The legitimate response for R2 can never be submitted. [6](#0-5) 

---

### Impact Explanation

**High — Forged foreign-chain verification enabling invalid bridge execution**

The `verify_foreign_transaction` flow exists specifically to let bridge contracts trust that a foreign-chain event (e.g., an Ethereum deposit) actually occurred before minting or releasing funds. The forged response delivers a `payload_hash` that is cryptographically valid (the signature checks out under the root key) but corresponds to a *different* transaction's observed values.

A bridge contract that checks only the ECDSA signature validity (without also verifying `payload_hash == SHA-256(borsh({expected_request, expected_values}))`) will accept the forged attestation and execute the bridge action — minting tokens, releasing funds, or crediting a deposit — for a transaction that was never actually verified.

Even for bridge contracts that do use the SDK's `ForeignChainSignatureVerifier::verify_signature()` (which does check the hash): [7](#0-6) 

the yield is permanently consumed. The legitimate response for R2 can never be delivered, permanently blocking the user's bridge operation. This is a guaranteed request-lifecycle corruption invariant break.

---

### Likelihood Explanation

- **Entry requirement:** The attacker must be a single Byzantine participant in the MPC network — below the signing threshold. No collusion with other participants is needed beyond normal threshold participation in a legitimate session.
- **Trigger:** The attacker participates in any legitimate `verify_foreign_tx` signing session (which they would do as a normal participant). Once they have the resulting `(sig, hash)` pair, they can replay it against any concurrently pending `verify_foreign_tx` request.
- **No special privileges:** `respond_verify_foreign_tx` is callable by any single attested participant. The contract does not require threshold-many callers.
- **Realistic scenario:** A bridge with active traffic will have multiple concurrent `verify_foreign_tx` requests pending. A Byzantine participant can selectively poison high-value requests by replaying a low-value session's signature.

---

### Recommendation

The contract must verify that `response.payload_hash` is bound to the specific `request` being resolved. Since the extracted values are not stored on-chain, two approaches are viable:

1. **Include extracted values in the response and verify on-chain.** Add `values: Vec<ExtractedValue>` to `VerifyForeignTransactionResponse`, compute `expected_hash = SHA-256(borsh(ForeignTxSignPayloadV1 { request, values }))` inside `respond_verify_foreign_tx`, and assert `expected_hash == response.payload_hash` before accepting the response.

2. **Bind the signed payload to the on-chain request identifier.** Change the signing payload to `SHA-256(borsh({ receipt_id, request, values }))` where `receipt_id` is the unique NEAR receipt ID stored with the pending request. The contract can then verify that the hash is bound to the correct receipt without needing the extracted values.

Either fix closes the cross-request replay channel by making a valid `(sig, hash)` pair for R1 cryptographically unusable for R2.

---

### Proof of Concept

```
Setup:
  - MPC network with 3 participants, threshold = 2
  - Byzantine participant P is participant #1
  - Two pending verify_foreign_tx requests:
      R1: Bitcoin tx_id = [0x01; 32], extractor = BlockHash
      R2: Bitcoin tx_id = [0x02; 32], extractor = BlockHash  ← victim

Step 1: P participates in the legitimate signing session for R1.
  - Threshold protocol runs with P + participant #2.
  - Resulting: hash1 = SHA-256(borsh({R1.request, [BlockHash([0xAA;32])]}))
               sig1  = ECDSA_root_key(hash1)

Step 2: P calls respond_verify_foreign_tx(R2, { payload_hash: hash1, signature: sig1 })
  - assert_caller_is_attested_participant_and_protocol_active() → OK (P is attested)
  - verify_ecdsa_signature(sig1, hash1, root_key) → OK (legitimately produced)
  - resolve_yields_for(pending_verify_foreign_tx_requests, R2, response) → R2 yield consumed

Step 3: R2's caller receives { payload_hash: hash1, signature: sig1 }
  - hash1 encodes R1's tx_id and block hash, not R2's
  - A bridge contract checking only signature validity accepts the forged attestation
  - The legitimate response for R2 can never be submitted (request removed from map)
```

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

**File:** crates/contract/src/lib.rs (L718-734)
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1478-1480)
```rust
pub enum ForeignTxSignPayload {
    V1(ForeignTxSignPayloadV1),
}
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L53-64)
```rust
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
