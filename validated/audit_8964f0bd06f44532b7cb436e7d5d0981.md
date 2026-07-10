### Title
Missing Request-Response Binding in `respond_verify_foreign_tx` Allows a Single Byzantine Participant to Inject a Mismatched Attestation — (`crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted signature is valid over `response.payload_hash` under the root public key, but it **never checks that `response.payload_hash` is the hash of a `ForeignTxSignPayload` derived from the supplied `request`**. A single attested participant can reuse a valid `(H2, sig(H2))` pair obtained from a legitimately completed MPC flow for request R2 to resolve the pending yield for a completely different request R1, causing R1's caller to receive an attestation of R2's foreign-chain observation.

---

### Finding Description

In `respond_verify_foreign_tx` the only cryptographic check performed is:

```
verify_ecdsa_signature(sig, response.payload_hash, root_pk)
``` [1](#0-0) 

The function then immediately resolves every yield queued under `request` with the full `response` blob: [2](#0-1) 

There is no assertion of the form:

```
response.payload_hash == SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values: ... }))
```

The `ForeignTxSignPayload` that the MPC nodes actually sign binds the `ForeignChainRpcRequest` together with the extracted values: [3](#0-2) 

Because the contract never reconstructs or checks this binding, any `payload_hash` that carries a valid root-key signature is accepted regardless of which request it was originally computed for.

The access guard only requires the caller to be a single registered, TEE-attested participant: [4](#0-3) 

TEE attestation is a one-time registration check stored in contract state. It does not prevent a participant from constructing and submitting a hand-crafted NEAR transaction that pairs R1 with a response blob obtained from R2's signing session.

---

### Impact Explanation

**Attack path (concrete, single-participant):**

1. Attacker is a registered, TEE-attested MPC participant.
2. Attacker submits a legitimate `verify_foreign_transaction` for R2 and participates in the threshold signing session. The leader broadcasts the final signature; the attacker observes `(H2, sig(H2, root_pk))`.
3. A separate user has a pending `verify_foreign_transaction` for R1 (different tx, different chain state).
4. Attacker directly submits the NEAR transaction:
   ```
   respond_verify_foreign_tx(request = R1, response = { payload_hash = H2, signature = sig(H2) })
   ```
5. Contract checks: (a) caller is attested participant ✓, (b) `verify_ecdsa_signature(sig, H2, root_pk)` ✓, (c) R1 exists in `pending_verify_foreign_tx_requests` ✓ → resolves R1's yield with `{payload_hash=H2, sig(H2)}`.
6. R1's caller receives a `VerifyForeignTransactionResponse` where `payload_hash` is the hash of R2's observation, not R1's.

A bridge contract that trusts the returned `payload_hash` as an MPC attestation of R1's foreign-chain state (e.g., checking only that the signature is valid over the returned hash, without independently reconstructing the expected hash from R1's inputs) will accept a forged attestation. This enables invalid bridge execution — for example, accepting a cross-chain transfer proof that was never actually observed for the claimed transaction.

The SDK's `ForeignChainSignatureVerifier::verify_signature` does perform the binding check: [5](#0-4) 

However, this is an off-chain SDK helper that bridge contracts must opt into. The on-chain contract itself provides no such enforcement, and bridge contracts that skip this step or trust `payload_hash` directly are fully exposed.

---

### Likelihood Explanation

- Requires only **one** Byzantine attested participant — well below the signing threshold.
- The attacker does not need to forge any cryptographic material; they reuse a legitimately produced signature from a different session.
- The attacker does not need to compromise a TEE; they only need to call the contract directly with a crafted transaction after observing the output of any completed R2 signing session.
- The window is open for as long as R1's yield is pending (up to the NEAR yield timeout).

---

### Recommendation

In `respond_verify_foreign_tx`, after verifying the signature, reconstruct the minimum expected payload hash from the supplied `request` and verify that `response.payload_hash` is a valid preimage of that request. Because the extracted `values` are not available on-chain, the practical fix is to **include the `ForeignChainRpcRequest` in the signed payload hash verification** by requiring the contract to verify that `response.payload_hash` decodes to a `ForeignTxSignPayload` whose embedded `request` field matches the `request` argument — or, more simply, to have the MPC nodes sign a payload that commits to the `request` key used for the pending-yield lookup, and have the contract verify that commitment.

A minimal mitigation: require the caller to also supply the `ForeignTxSignPayload` preimage, recompute its hash on-chain, and assert equality with `response.payload_hash` before resolving the yield.

---

### Proof of Concept

```rust
// Integration test sketch (unit-test style, using existing test helpers)
//
// 1. Setup: two distinct Bitcoin requests R1 and R2.
let r1_args = VerifyForeignTransactionRequestArgs { request: bitcoin_request_with_txid([0x01; 32]), .. };
let r2_args = VerifyForeignTransactionRequestArgs { request: bitcoin_request_with_txid([0x02; 32]), .. };

// 2. Queue both requests.
contract.verify_foreign_transaction(r1_args.clone());
contract.verify_foreign_transaction(r2_args.clone());

let r1 = args_into_verify_foreign_tx_request(r1_args);
let r2 = args_into_verify_foreign_tx_request(r2_args);

// 3. Produce a valid (H2, sig) pair for R2 only.
let (payload_r2, response_r2) = sign_foreign_tx_response(
    &r2.request,
    r2_extracted_values(),
    &root_secret_key,
);
let h2 = payload_r2.compute_msg_hash().unwrap();

// 4. Byzantine participant submits R2's response against R1.
with_active_participant_and_attested_context(&contract);
let result = contract.respond_verify_foreign_tx(r1.clone(), response_r2.clone());

// 5. Assert: contract accepts the call and resolves R1's yield with H2.
assert!(result.is_ok(), "contract should accept mismatched response");
assert!(contract.get_pending_verify_foreign_tx_request(&r1).is_none(),
    "R1's yield should be resolved with R2's payload_hash");
// R1's caller now holds {payload_hash=H2, sig(H2)} — an attestation of R2, not R1.
``` [6](#0-5) [7](#0-6)

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
