### Title
`respond_verify_foreign_tx` Does Not Validate `payload_hash` Against Request Contents, Enabling Cross-Request Response Replay - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_verify_foreign_tx` function validates the caller (attested participant) and the cryptographic signature (valid for `response.payload_hash`), but never validates that `response.payload_hash` is actually derived from the `request` parameter supplied in the same call. A single Byzantine MPC node below the signing threshold can replay a previously produced, on-chain-visible response from one foreign-chain verification request to resolve a completely different pending request, delivering a forged attestation to the waiting caller.

### Finding Description

`respond_verify_foreign_tx` at `crates/contract/src/lib.rs:691–754` accepts two independent arguments: a `VerifyForeignTransactionRequest` (the chain query the user submitted) and a `VerifyForeignTransactionResponse` (containing `payload_hash` and `signature`). The function performs two checks before resolving the pending yield:

1. The caller is an attested participant.
2. The signature is a valid ECDSA signature over `response.payload_hash` under the **root public key**. [1](#0-0) 

It then calls `resolve_yields_for` keyed on `request`, resuming every yield that was parked under that request key with the serialised `response` bytes. [2](#0-1) 

The critical gap: **the contract never verifies that `response.payload_hash` is the hash of a `ForeignTxSignPayload` whose embedded `request` field matches the `request` argument**. Per the design, `payload_hash` is supposed to be `SHA-256(borsh(ForeignTxSignPayload { request, values }))`. [3](#0-2) 

Because `request` and `response.payload_hash` are never bound together on-chain, a caller can supply any `request` key that has a pending yield and any previously valid `(payload_hash, signature)` pair, and the contract will accept it.

This is the direct analog of the BunniZone finding: the zone validated only the fulfiller identity, not the order contents. Here, the contract validates only the caller identity and a signature over an **unconstrained** hash, not the relationship between that hash and the request being resolved.

Contrast this with the regular `respond` function, where the signature is verified over `request.payload` under the key derived from `request.tweak` — the payload and the key derivation are both taken from the same `request` struct, so they cannot be mixed. [4](#0-3) 

### Impact Explanation

A single malicious MPC node (below the signing threshold) can:

1. Observe any previous on-chain `respond_verify_foreign_tx` call and extract its `payload_hash` (H₂) and `signature` (σ₂). These are public NEAR receipts.
2. Wait for a victim user to submit `verify_foreign_transaction(tx_id = T₁)`, creating a pending yield.
3. Call `respond_verify_foreign_tx(request = T₁, response = {payload_hash = H₂, signature = σ₂})`.
4. The contract verifies σ₂ over H₂ against the root key — this passes because σ₂ was legitimately produced by the MPC network for a prior request.
5. `resolve_yields_for` resumes the yield for T₁ with the serialised response `{payload_hash = H₂, signature = σ₂}`.
6. The user's callback receives a valid MPC root-key signature, but one that attests to a **different** transaction (T₂), not T₁.

Bridge contracts that consume this response and verify only that the signature is valid over `payload_hash` — without independently recomputing the expected hash from T₁ — will accept the forged attestation. This enables invalid bridge execution (e.g., minting tokens on NEAR for a foreign deposit that was never made or was already claimed). [5](#0-4) 

### Likelihood Explanation

**Medium-High.** The attacker is a single Byzantine MPC node — a realistic threat model for a t-of-n threshold system. No threshold collusion is required: the attacker only needs to be an attested participant (one node) and to have observed any prior legitimate `respond_verify_foreign_tx` receipt on-chain. All NEAR receipts are public. The attack is deterministic and requires no brute-force or timing luck.

### Recommendation

In `respond_verify_foreign_tx`, bind `response.payload_hash` to the `request` contents before accepting the response. Two concrete options:

1. **Include `extracted_values` in the response DTO** and have the contract recompute `SHA-256(borsh(ForeignTxSignPayload { request, values }))`, then assert it equals `response.payload_hash`. This makes the contract the authoritative verifier of the hash.
2. **Embed the request hash inside the signed payload** (e.g., as a domain-separation prefix), so that a signature produced for T₂ is cryptographically invalid for T₁ even if the raw `payload_hash` bytes are reused.

Either approach closes the gap by making the signature inseparable from the specific request it was produced for, mirroring how `respond` ties the signature to `request.payload` and `request.tweak`.

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(tx_id = T1, extractors = [BlockHash])
   → pending yield Y1 stored under key K1 = hash(T1)

2. Eve (malicious MPC node) observes a prior on-chain receipt:
   respond_verify_foreign_tx(request = T2, response = {payload_hash = H2, sig = σ2})
   where σ2 = ECDSA_root_key(H2) — legitimately produced by the MPC network.

3. Eve calls:
   respond_verify_foreign_tx(
     request  = T1,          // matches Alice's pending yield
     response = { payload_hash = H2, signature = σ2 }  // replayed from T2
   )

4. Contract checks:
   a. Eve is an attested participant          → PASS
   b. verify_ecdsa(σ2, H2, root_pk)          → PASS (σ2 was honestly produced)
   c. resolve_yields_for(K1, serialize({H2, σ2})) → resumes Y1

5. Alice's callback receives {payload_hash = H2, signature = σ2}.
   H2 encodes T2's block-hash, not T1's.

6. Alice's bridge contract calls:
   verify_ecdsa(σ2, H2, root_pk) → PASS
   // If it does NOT check H2 == SHA256(borsh({T1, expected_values})),
   // it accepts the forged attestation and mints tokens for T1.
``` [6](#0-5) [7](#0-6)

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

**File:** docs/foreign-chain-transactions.md (L165-188)
```markdown
### Sign Payload Serialization

The MPC network signs a canonical hash derived from the request and its observed results.
The payload is versioned to allow future format changes without breaking existing verifiers.
Only the hash is included in the response to stay within NEAR's promise data limits.

```rust
pub enum ForeignTxSignPayload {
    V1(ForeignTxSignPayloadV1),
}

pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

The 32-byte `msg_hash` that nodes sign is computed as:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```

Callers select the payload version via `VerifyForeignTransactionRequestArgs::payload_version`.
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
