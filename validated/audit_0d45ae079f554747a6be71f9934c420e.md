### Title
`respond_verify_foreign_tx` Does Not Validate `payload_hash` Against the Pending Request — (`File: crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` accepts a caller-supplied `response.payload_hash` and only checks that the MPC signature is valid over that hash. It never verifies that the hash is actually derived from the pending request stored on-chain. A single Byzantine attested participant (below the signing threshold) can reuse a legitimate threshold signature produced for a different request to resolve any pending `verify_foreign_transaction` request with fabricated foreign-chain attestation data.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs the following validation:

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

The contract verifies that `response.signature` is a valid MPC signature over `response.payload_hash`. However, it never checks that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 { request: <the pending request>, values: <actual extracted values> })))`. [2](#0-1) 

The `payload_hash` is entirely caller-controlled. The contract only checks:
1. The caller is an attested participant.
2. The signature is valid over the supplied `payload_hash`.
3. The supplied `request` key exists in `pending_verify_foreign_tx_requests`. [3](#0-2) 

After passing these checks, `resolve_yields_for` drains the entire fan-out queue for the pending request and delivers the unvalidated response to all waiting callers. [4](#0-3) 

Contrast this with the regular `respond` function, where the payload hash is taken from the stored `request.payload` (committed on-chain at submission time), not from the response:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(signature_response, payload_hash, &expected_public_key)
``` [5](#0-4) 

For `respond_verify_foreign_tx`, no equivalent binding exists.

### Impact Explanation

A single Byzantine attested participant can execute the following cross-request response substitution:

1. Two requests R1 and R2 are concurrently pending in `pending_verify_foreign_tx_requests`.
2. The MPC network (threshold of honest nodes) legitimately signs `hash(R2, values2)` for request R2. The Byzantine participant receives this threshold signature as part of normal protocol operation.
3. The Byzantine participant calls `respond_verify_foreign_tx(request=R1, response={payload_hash=hash(R2, values2), signature=sig_over_hash_R2_values2})`.
4. The contract accepts: the signature is valid over `payload_hash`, and R1 is pending. It drains all yields for R1 and delivers the R2 response to every caller waiting on R1.
5. The honest response for R1 can never be submitted — the pending entry has been permanently removed.

The user of R1 receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes R2's `ForeignChainRpcRequest` (different `tx_id`, different extracted values) and R2's extracted values. The signature is cryptographically valid. A downstream bridge contract that does not independently reconstruct and compare the expected `payload_hash` — which requires knowing the extracted values the MPC network observed, information not included in the response — will accept this as a valid attestation of R1's foreign-chain state. [6](#0-5) 

The `near-mpc-sdk` provides a `verify_signature` helper that does perform this check client-side:

```rust
let payload_is_correct = expected_payload_hash == response.payload_hash;
``` [7](#0-6) 

But this is not enforced by the contract. Bridge contracts that omit this check — or that cannot independently determine the expected extracted values — will accept forged attestations. This enables invalid bridge execution and potential double-spend conditions.

### Likelihood Explanation

- The attacker needs only to be a single attested participant, which is below the signing threshold. No collusion is required.
- The attacker does not forge any cryptographic material; they reuse a legitimate threshold signature produced by the honest majority for a different request.
- In any production bridge deployment, multiple `verify_foreign_transaction` requests will be pending simultaneously, making R1 and R2 co-pending a routine condition.
- The attacker must race the honest `respond_verify_foreign_tx` call for R1, but since the attacker already holds the signature for R2 (received during normal MPC participation), they can submit immediately after R2's signing completes.

### Recommendation

The contract should verify that `response.payload_hash` is consistent with the pending request. Since the contract cannot know the extracted `values` (they are determined off-chain), the minimal fix is to require the responder to also supply the `values` and have the contract recompute and compare the hash:

```rust
// Require responder to supply extracted values
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(),
}).compute_msg_hash()?;

if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

Alternatively, the contract could store a commitment to the expected `payload_hash` prefix (i.e., the Borsh encoding of the request portion) at submission time and verify that `response.payload_hash` is consistent with it, though this requires a partial-preimage check that is non-trivial with SHA-256.

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(R1 = {tx_id: 0xAA...})  → pending
2. Bob   submits verify_foreign_transaction(R2 = {tx_id: 0xBB...})  → pending
3. MPC network signs hash(R2, {block_hash: 0xCC...}) → sig_R2
   (Byzantine participant P receives sig_R2 as part of normal protocol)
4. P calls respond_verify_foreign_tx(
       request = R1,                          // resolves Alice's pending yield
       response = {
           payload_hash = hash(R2, {block_hash: 0xCC...}),
           signature    = sig_R2,             // valid MPC signature, wrong request
       }
   )
5. Contract: sig_R2 valid over payload_hash? ✓  R1 pending? ✓  → resolves R1.
6. Alice's bridge contract receives response attesting to tx_id=0xBB's block_hash,
   not tx_id=0xAA's. If it skips payload_hash verification, it processes the wrong tx.
7. Honest respond_verify_foreign_tx for R1 now fails: RequestNotFound.
```

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

**File:** crates/contract/src/lib.rs (L691-753)
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
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L57-63)
```rust
        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
```
