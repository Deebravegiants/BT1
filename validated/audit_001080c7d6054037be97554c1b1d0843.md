### Title
`respond_verify_foreign_tx` Accepts Arbitrary `payload_hash` Without Binding It to the Pending Request — (`File: crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid over the caller-supplied `response.payload_hash`, but never checks that `response.payload_hash` was actually derived from the `ForeignChainRpcRequest` stored in the pending request. A single Byzantine attested participant (below threshold) can replay a legitimately-produced `(payload_hash, signature)` pair from a completed request T1 as the response to a different pending request T2, causing the contract to resolve T2 with T1's signed data.

### Finding Description

`verify_foreign_transaction` checks at submission time that the requested chain is supported and enqueues a yield-resume request keyed on the full `VerifyForeignTransactionRequest` (which includes `domain_id`, `payload_version`, and `ForeignChainRpcRequest`). [1](#0-0) 

When an MPC node later calls `respond_verify_foreign_tx`, the contract:

1. Verifies the caller is an attested participant.
2. Fetches the domain's root public key.
3. Verifies `response.signature` over `response.payload_hash` using that key.
4. Resolves all pending yields for `request` with the full `response`. [2](#0-1) 

**The contract never reconstructs or checks that `response.payload_hash` equals `ForeignTxSignPayload::compute_msg_hash(request.request, extracted_values)`.**

The `payload_hash` is supposed to commit to the `ForeignChainRpcRequest` (tx_id, chain, extractors) and the extracted values: [3](#0-2) 

Because the contract only verifies the signature over the caller-supplied hash — and never binds that hash to the specific request being resolved — a Byzantine attested participant can supply a `payload_hash` that was legitimately signed for a completely different foreign-chain transaction.

### Impact Explanation

**HIGH — Forged foreign-chain verification enabling invalid bridge execution or double-spend.**

A bridge contract that calls `verify_foreign_transaction` and trusts the returned `VerifyForeignTransactionResponse` to confirm a specific foreign-chain transaction will receive a response whose `payload_hash` corresponds to a *different* transaction. The MPC network's signature is genuine (it was produced for T1), but it is being presented as proof that T2 was verified. Any downstream logic that uses the signed `payload_hash` to extract verified values (block hash, logs, etc.) will process T1's data while believing it processed T2's data, enabling double-spend or invalid bridge state transitions.

### Likelihood Explanation

**Medium.** The attacker must be a single Byzantine attested MPC participant — a realistic threat model for a Byzantine-fault-tolerant system. The attacker needs only:

1. Observe a completed `verify_foreign_transaction` response on-chain (public data).
2. Have a second, different request pending in the contract for the same domain.
3. Call `respond_verify_foreign_tx` with the recycled `(payload_hash, signature)` pair.

No threshold collusion is required. The signature is already public after T1 completes.

### Recommendation

In `respond_verify_foreign_tx`, reconstruct the expected `payload_hash` from the pending request's `ForeignChainRpcRequest` and verify that `response.payload_hash` matches it before accepting the response. Because the contract cannot independently query the foreign chain, the binding must be enforced structurally: the `payload_hash` must commit to the exact `ForeignChainRpcRequest` stored in the pending map, and the contract must verify this commitment at response time.

Concretely, store the expected `payload_hash` alongside the pending yield at submission time (computed deterministically from the request parameters), and assert `response.payload_hash == stored_expected_hash` inside `respond_verify_foreign_tx`.

### Proof of Concept

**Setup:**
- Domain D (ForeignTx, CaitSith) with root public key `PK_D`.
- Two pending requests in `pending_verify_foreign_tx_requests`:
  - T1: `{domain_id: D, request: BitcoinRpcRequest{tx_id: [0xAA;32], ...}}`
  - T2: `{domain_id: D, request: BitcoinRpcRequest{tx_id: [0xBB;32], ...}}`

**Step 1 — Legitimate completion of T1:**

The MPC network processes T1, computes `H1 = ForeignTxSignPayload::V1{request: R1, values: [BlockHash([0x11;32])]}.compute_msg_hash()`, and produces threshold signature `sig_H1` over `H1` using `PK_D`. An honest node calls:

```
respond_verify_foreign_tx(T1, {payload_hash: H1, signature: sig_H1})
```

The contract resolves T1. `H1` and `sig_H1` are now public on-chain.

**Step 2 — Byzantine replay against T2:**

A Byzantine attested participant calls:

```
respond_verify_foreign_tx(T2, {payload_hash: H1, signature: sig_H1})
```

**Contract execution path:**

```rust
// Line 716: gets PK_D (same domain)
let public_key = self.public_key_extended(domain.0.into())?;

// Lines 726-734: verifies sig_H1 over H1 using PK_D → PASSES
// (sig_H1 is a valid threshold signature over H1)
near_mpc_signature_verifier::verify_ecdsa_signature(sig_H1, H1, PK_D) → Ok

// Line 749: resolves T2 with {payload_hash: H1, signature: sig_H1}
pending_requests::resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &T2, ...)
``` [4](#0-3) 

**Result:** The caller of T2 receives `{payload_hash: H1, signature: sig_H1}` — a signed attestation that T2 was verified, but `H1` commits to T1's `ForeignChainRpcRequest` (tx_id `[0xAA;32]`) and T1's extracted values. Any bridge contract processing this response will act on T1's data while believing it verified T2.

### Citations

**File:** crates/contract/src/lib.rs (L526-542)
```rust
        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }
```

**File:** crates/contract/src/lib.rs (L715-753)
```rust
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
