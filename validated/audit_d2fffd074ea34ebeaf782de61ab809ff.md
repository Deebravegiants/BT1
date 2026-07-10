### Title
`respond_verify_foreign_tx` Accepts Replayed Signatures for Arbitrary Payload Hashes — (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_verify_foreign_tx` contract method validates that the submitted ECDSA signature is valid for `response.payload_hash`, but never validates that `response.payload_hash` is the correct hash for the given `request`. A single Byzantine MPC participant (below threshold) that has previously received a threshold-produced signature for any payload hash `H` can replay that signature against any pending `verify_foreign_transaction` request, causing the contract to resolve the yield with a forged `payload_hash` and a valid-looking signature.

### Finding Description

In `crates/contract/src/lib.rs`, the `respond_verify_foreign_tx` function performs the following checks:

1. Caller is an attested participant (single-node check, no threshold required).
2. The ECDSA signature in `response` is valid for `response.payload_hash` under the domain's root public key.
3. The `request` key exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What is **never** checked: that `response.payload_hash` is the canonical hash of `ForeignTxSignPayload::V1 { request, values }` for the specific `request` being resolved. The contract has no access to the off-chain `extracted_values`, so it cannot recompute the expected hash itself. This is the structural gap.

Contrast this with the regular `respond` path for `sign` requests, where the contract stores the exact payload in the `SignatureRequest` and can verify the signature is over the correct message. For `verify_foreign_transaction`, the signed payload includes off-chain-extracted values that the contract never sees, so the binding between `request` and `payload_hash` is never enforced on-chain. [2](#0-1) 

The node-side code computes the payload hash correctly from `(request, extracted_values)`: [3](#0-2) 

But the contract never re-derives or cross-checks this hash.

### Impact Explanation

A Byzantine MPC participant (one node, strictly below threshold) that has previously participated in any threshold signing round for a `verify_foreign_transaction` request receives the final threshold signature `sig_H` for payload hash `H` as a normal protocol output. It can then:

1. Wait for a new, unrelated `verify_foreign_transaction` request for transaction `T2` to appear in the pending map.
2. Call `respond_verify_foreign_tx(request = T2, response = { payload_hash = H, signature = sig_H })`.
3. The contract verifies `sig_H` is valid for `H` under the root key — it is — and resolves the yield for `T2` with the forged response.

The caller of `verify_foreign_transaction` (e.g., a bridge contract) receives `{ payload_hash = H, signature = sig_H }` where `H` encodes a completely different transaction's data. Because `payload_hash` is an opaque hash and the `extracted_values` are never returned on-chain, the bridge contract cannot distinguish the forged response from a legitimate one. It can only verify the ECDSA signature against `payload_hash`, which passes.

This enables forged foreign-chain verification: the bridge contract is made to believe that transaction `T2` was verified and that specific values were extracted from it, when in fact the signed attestation covers a different transaction entirely. This directly enables invalid bridge execution (e.g., releasing funds for a transaction that was never confirmed, or releasing funds with incorrect extracted values such as a wrong block hash or log data).

### Likelihood Explanation

- The attacker is a single Byzantine MPC participant, which is explicitly within the allowed threat model ("Byzantine participant strictly below the signing threshold").
- No TEE compromise is required; the node simply retains the threshold signature it legitimately received during a prior signing round.
- The attack window is any time a new `verify_foreign_transaction` request is pending and the Byzantine node races to call `respond_verify_foreign_tx` before honest nodes do. Since `resolve_yields_for` removes the entry on first response, the Byzantine node only needs to win the race once per target request.
- The attacker controls the timing of its own NEAR transaction submission, making the race winnable in practice.

### Recommendation

The contract must bind `response.payload_hash` to the `request` on-chain. Two approaches:

1. **Store the expected payload hash at request time**: When `verify_foreign_transaction` is called, compute and store `hash(request)` (the request-only prefix). At response time, verify that `response.payload_hash` starts with or is derived from this stored prefix. This requires a deterministic, prefix-structured hash scheme.

2. **Include the full payload in the response and verify on-chain**: Return `extracted_values` alongside the signature and recompute `ForeignTxSignPayload::V1 { request, values }.compute_msg_hash()` in `respond_verify_foreign_tx`, then assert it equals `response.payload_hash`. This is the cleanest fix and mirrors how `respond` works for regular sign requests.

### Proof of Concept

```
// Setup: Byzantine node B has previously participated in signing for request T1,
// obtaining sig_H1 for payload_hash H1 = hash(T1, extracted_values_1).

// Step 1: Honest user submits a new request for transaction T2.
contract.verify_foreign_transaction(T2_args);
// pending_verify_foreign_tx_requests now contains T2 -> [yield_id]

// Step 2: Byzantine node B calls respond with T2 as the request key
// but H1 (from T1's signing round) as the payload_hash.
contract.respond_verify_foreign_tx(
    request = VerifyForeignTransactionRequest { T2 fields },
    response = VerifyForeignTransactionResponse {
        payload_hash: H1,          // hash of T1's data, not T2's
        signature: sig_H1,         // valid threshold signature for H1
    }
);

// Contract checks:
// 1. Caller is attested participant: PASS (B is a legitimate node)
// 2. verify_ecdsa_signature(sig_H1, H1, root_pk): PASS (sig_H1 is valid for H1)
// 3. pending map contains T2: PASS
// -> resolve_yields_for(T2, serialize({payload_hash: H1, signature: sig_H1}))

// Result: T2's caller receives {payload_hash: H1, signature: sig_H1}.
// The bridge contract verifies sig_H1 against H1: PASS.
// The bridge contract cannot detect that H1 encodes T1's data, not T2's.
// Bridge executes based on forged attestation.
``` [4](#0-3) [5](#0-4)

### Citations

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L336-347)
```rust
        };
        let payload = match payload_version {
            dtos::ForeignTxPayloadVersion::V1 => {
                dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
                    request: request.clone(),
                    values,
                })
            }
            _ => bail!("unsupported payload_version"),
        };
        Ok(payload)
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
