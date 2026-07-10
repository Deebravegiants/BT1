### Title
`respond_verify_foreign_tx` Accepts Unconstrained `payload_hash` Not Bound to the Pending Request, Enabling Cross-Request Signature Replay by a Single Byzantine Attested Participant - (File: crates/contract/src/lib.rs)

### Summary

The `respond_verify_foreign_tx` function in the MPC smart contract verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` using the root public key, but **never verifies that `response.payload_hash` is the canonical hash of the actual `request` content**. A single Byzantine attested participant (strictly below the signing threshold) can replay any previously produced threshold signature — obtained from contract state after a legitimate prior response — to forge the verification attestation for an unrelated pending foreign-chain transaction request.

### Finding Description

In `crates/contract/src/lib.rs`, `respond_verify_foreign_tx` performs the following check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The contract only checks: *is `response.signature` a valid signature over `response.payload_hash`?* It does **not** check: *does `response.payload_hash` equal `SHA-256(borsh(ForeignTxSignPayload { request: <the pending request>, values: <observed values> }))`?*

The `ForeignTxSignPayload` that nodes are supposed to sign is defined as:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [2](#0-1) 

The contract stores the `request` in the pending map and uses it as the lookup key, but the `payload_hash` in the response is never cross-checked against that stored `request`. The `respond_verify_foreign_tx` function only requires the caller to be any attested participant — not specifically the leader: [3](#0-2) 

After a legitimate `verify_foreign_transaction` response is submitted and accepted, the full `VerifyForeignTransactionResponse` (including `payload_hash` and `signature`) is returned to the original caller via the yield/resume mechanism and is observable on-chain. A Byzantine attested participant can read this previously produced response from chain state and replay it against any new pending request.

**Attack path:**

1. User A submits `verify_foreign_transaction` for Bitcoin tx `T_A`. The MPC network honestly processes it and the leader calls `respond_verify_foreign_tx(request=R_A, response={payload_hash=H_A, sig=Sig_A})`. The contract accepts it; `H_A` and `Sig_A` are now observable on-chain.
2. User B submits `verify_foreign_transaction` for a different Bitcoin tx `T_B` (e.g., a fraudulent bridge deposit). Request `R_B` is now pending.
3. Byzantine attested participant calls `respond_verify_foreign_tx(request=R_B, response={payload_hash=H_A, sig=Sig_A})`.
4. The contract verifies: is `Sig_A` a valid signature over `H_A` under the root key? **Yes.** Does `R_B` exist in the pending map? **Yes.** The contract resolves User B's yield with `{payload_hash=H_A, sig=Sig_A}`.
5. User B's contract receives a `VerifyForeignTransactionResponse` whose `payload_hash` attests to tx `T_A`'s data, not `T_B`'s. Any downstream bridge logic that trusts the contract's attestation without independently recomputing the hash from `T_B`'s data is deceived.

This is the direct analog of the Vyper `raw_call` bug: just as Vyper accepts a `value` parameter in `raw_call` even when `is_delegate_call=True` (where `value` is semantically meaningless and silently ignored), the NEAR MPC contract accepts a `payload_hash` in `respond_verify_foreign_tx` without validating it against the `request` it is supposed to attest to — the parameter is accepted but its binding to the request is never enforced.

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can forge the foreign-chain verification attestation for any pending request. The returned `VerifyForeignTransactionResponse` carries a valid MPC threshold signature, so any bridge or downstream contract that relies on the contract's attestation without independently recomputing the expected hash from the raw transaction data will accept the forged proof. This enables **invalid bridge execution** (e.g., crediting a deposit that never occurred or was already credited) and **double-spend conditions** on the NEAR side of a cross-chain bridge.

This matches the allowed High impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

### Likelihood Explanation

- Requires only **one** Byzantine attested participant — strictly below the signing threshold. The threshold security model is supposed to tolerate this.
- The previously produced threshold signature needed for the replay is **publicly observable on-chain** after any legitimate `respond_verify_foreign_tx` call; no key leakage or TEE attack is needed.
- Any attested participant can call `respond_verify_foreign_tx` — there is no leader-only restriction on this endpoint.
- The attack is straightforward to execute once a valid signature is available on-chain.

### Recommendation

In `respond_verify_foreign_tx`, require the responding node to supply the full `ForeignTxSignPayload` (not just the hash), then:

1. Assert `payload.request() == request` (the pending request matches the payload's embedded request).
2. Recompute `expected_hash = payload.compute_msg_hash()`.
3. Verify `response.signature` over `expected_hash`.

This binds the signature to the specific pending request and eliminates the replay surface. If response-size constraints prevent including the full payload, an alternative is to include a domain-separation prefix (e.g., a hash of the `request`) inside the signed message so the contract can verify the binding without the `observed_values`.

### Proof of Concept

```rust
// 1. Honest flow: MPC signs request R_A, producing (H_A, Sig_A).
//    H_A and Sig_A are now observable on-chain.

// 2. User B submits a new request R_B (different tx_id).
contract.verify_foreign_transaction(request_args_B); // R_B is now pending

// 3. Byzantine attested participant replays the old response for R_B.
//    The contract only checks: is Sig_A valid over H_A under root_pk? YES.
//    It does NOT check: does H_A == SHA-256(borsh(ForeignTxSignPayloadV1 { request: R_B, values: ... }))?
contract.respond_verify_foreign_tx(
    request_B,                                    // matches pending entry
    VerifyForeignTransactionResponse {
        payload_hash: H_A,                        // hash of a DIFFERENT request
        signature: SignatureResponse::Secp256k1(Sig_A), // valid sig over H_A
    },
).expect("contract accepts the forged response");

// 4. User B's yield resolves with {payload_hash: H_A, sig: Sig_A}.
//    Any bridge contract that trusts this attestation is deceived.
```

The root cause is at: [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L691-706)
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

```

**File:** crates/contract/src/lib.rs (L718-743)
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
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1478-1480)
```rust
pub enum ForeignTxSignPayload {
    V1(ForeignTxSignPayloadV1),
}
```
