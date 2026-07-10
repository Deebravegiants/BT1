### Title
Single Byzantine Participant Can Deliver Fabricated CKD Response, Bypassing Threshold Requirement - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd()` function in the MPC contract performs no output verification for the `AppPublicKey` (privately-verifiable) CKD variant. Any single attested participant — strictly below the signing threshold — can call `respond_ckd()` with a valid pending request key but a completely fabricated `CKDResponse`, draining the pending queue and delivering a wrong confidential key to the user. This bypasses the t-of-n threshold requirement for confidential key derivation.

### Finding Description

`respond_ckd()` handles responses to confidential key derivation requests. For the `AppPublicKeyPV` variant it calls `ckd_output_check()` to verify the response is consistent with the master public key and the user's ephemeral key pair. For the `AppPublicKey` (privately-verifiable, legacy) variant the check is entirely absent:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

After this match block, `resolve_yields_for` is called unconditionally, draining the entire fan-out queue for that request key and resuming every waiting yield with the (potentially fabricated) response bytes: [2](#0-1) 

The only guards on `respond_ckd()` are that the caller must be an attested participant and the protocol must be running or resharing: [3](#0-2) 

There is no check that the caller is the designated leader for the request, no check that the response was produced by the threshold protocol, and no check that `big_y` or `big_c` are consistent with the MPC master key.

By contrast, `respond()` for threshold signatures always verifies the signature cryptographically before touching the queue: [4](#0-3) 

The `CKDRequest` key stored in `pending_ckd_requests` is derived from `(app_public_key, domain_id, predecessor_id, derivation_path)`, all of which are observable on-chain from the original `request_app_private_key()` call: [5](#0-4) 

The `AppPublicKey` variant is not deprecated — it is the "privately verifiable" legacy format still documented and accepted by the contract: [6](#0-5) 

### Impact Explanation

A single Byzantine attested participant (1-of-n, strictly below the reconstruction threshold t) can:

1. Observe a pending `request_app_private_key()` call with `AppPublicKey` variant on-chain.
2. Reconstruct the exact `CKDRequest` key from the public call arguments.
3. Call `respond_ckd(request, fabricated_response)` where `fabricated_response` contains arbitrary `big_y` and `big_c` BLS12-381 points.
4. The contract accepts the call, drains the pending queue, and delivers the fabricated response to the user.

The user's application receives a `CKDResponse` that is not derived from the MPC master key. Decrypting `big_c` with the user's secret scalar `a` produces garbage. If the user derives a wallet address from this wrong key and deposits funds, those funds are permanently inaccessible — no party holds the corresponding private key. This constitutes permanent freezing of user funds and is a direct bypass of the threshold-signature requirement: the t-of-n threshold protocol is circumvented by a single participant acting alone.

### Likelihood Explanation

The attack requires only that the adversary is an attested participant — a condition that is already satisfied by any node in the MPC network. The request parameters needed to construct the correct `CKDRequest` key are fully public on-chain. No special cryptographic capability, no colluding peers, and no privileged access are needed. The cost is a single on-chain transaction (one `respond_ckd` call). The attacker can repeat this for every new `AppPublicKey` CKD request submitted by any user.

### Recommendation

1. **Reject `AppPublicKey` variant in `respond_ckd`** unless a cryptographic output check can be performed. If the contract cannot verify the output (because it lacks the user's secret key), the variant should be deprecated for new requests and `respond_ckd` should panic on it.
2. **Enforce leader-only response submission**: add an on-chain check that the caller is the deterministically selected leader for the given request ID, consistent with the off-chain leader-selection logic in `PendingRequests`.
3. **Require multi-party commit-reveal**: require at least threshold participants to submit matching response commitments before the queue is drained, mirroring the threshold guarantee enforced off-chain.

### Proof of Concept

```
// 1. User submits a CKD request with AppPublicKey variant
user.call(contract, "request_app_private_key", {
    derivation_path: "mykey",
    app_public_key: "bls12381g1:<user_ephemeral_pk>",   // AppPublicKey variant
    domain_id: 4
}, deposit=1_yocto)

// 2. Attacker (any attested participant) observes the request on-chain,
//    reconstructs the CKDRequest key, and calls respond_ckd with garbage:
attacker.call(contract, "respond_ckd", {
    request: {
        app_public_key: { AppPublicKey: "<user_ephemeral_pk>" },
        domain_id: 4,
        app_id: hash(user_account_id || "mykey")
    },
    response: {
        big_y: "bls12381g1:<random_point>",   // fabricated
        big_c: "bls12381g1:<random_point>"    // fabricated
    }
})

// 3. Contract accepts the call (no output check for AppPublicKey variant),
//    drains the queue, and delivers the fabricated response to the user.
// 4. User receives a wrong confidential key; funds sent to a derived address
//    are permanently inaccessible.
```

### Citations

**File:** crates/contract/src/lib.rs (L153-155)
```rust
    pending_signature_requests: LookupMap<SignatureRequest, Vec<YieldIndex>>,
    pending_ckd_requests: LookupMap<CKDRequest, Vec<YieldIndex>>,
    pending_verify_foreign_tx_requests: LookupMap<VerifyForeignTransactionRequest, Vec<YieldIndex>>,
```

**File:** crates/contract/src/lib.rs (L586-644)
```rust
        let signature_is_valid = match (&response, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                // generate the expected public key
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");
                let affine = *k256::PublicKey::try_from(&secp_pk)
                    .expect("stored key is always valid")
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
            }
            (
                dtos::SignatureResponse::Ed25519 { signature },
                PublicKeyExtended::Ed25519 {
                    edwards_point: public_key_edwards_point,
                    ..
                },
            ) => {
                let derived_public_key_edwards_point = derive_public_key_edwards_point_ed25519(
                    &public_key_edwards_point,
                    &request.tweak,
                );
                let derived_public_key_32_bytes =
                    dtos::Ed25519PublicKey::from(derived_public_key_edwards_point.compress());

                let message = request.payload.as_eddsa().expect("Payload is not EdDSA");

                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    message,
                    &derived_public_key_32_bytes,
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

**File:** crates/contract/src/lib.rs (L653-666)
```rust
    #[handle_result]
    pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L675-682)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }
```

**File:** crates/contract/src/lib.rs (L684-689)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/README.md (L118-121)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
```
