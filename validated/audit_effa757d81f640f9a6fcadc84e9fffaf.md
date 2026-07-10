### Title
`respond_verify_foreign_tx()` Missing Ed25519 Match Arm Causes All Ed25519 ForeignTx Responses to Always Fail — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx()` only handles `Secp256k1` signatures in its match dispatch, while the `verify_foreign_transaction()` entry point accepts any domain with `DomainPurpose::ForeignTx` — including Ed25519 (Frost) domains. If an Ed25519 ForeignTx domain is configured, every MPC node response for that domain is permanently rejected with `SignatureSchemeMismatch`, making the entire `verify_foreign_transaction` flow for Ed25519 domains permanently non-functional.

---

### Finding Description

The `respond` function (for regular `sign()` requests) correctly handles both `Secp256k1` and `Ed25519` signature schemes: [1](#0-0) 

It matches on both:
- `(SignatureResponse::Secp256k1, PublicKeyExtended::Secp256k1)` → verifies with derived key
- `(SignatureResponse::Ed25519, PublicKeyExtended::Ed25519)` → verifies with derived Ed25519 key

However, `respond_verify_foreign_tx()` only handles the Secp256k1 arm: [2](#0-1) 

The Ed25519 case falls through to the catch-all arm, which unconditionally returns `Err(RespondError::SignatureSchemeMismatch { ... })`. There is no Ed25519 branch.

Meanwhile, `verify_foreign_transaction()` enforces only `DomainPurpose::ForeignTx` — it places no restriction on the underlying curve/protocol: [3](#0-2) 

The `DomainConfig` type allows any `Protocol` (including `Protocol::Frost` for Ed25519) to be paired with `DomainPurpose::ForeignTx`. Governance participants can vote in such a domain via `vote_add_domains()`: [4](#0-3) 

Once an Ed25519 ForeignTx domain exists:
1. Users submit `verify_foreign_transaction` requests targeting it — accepted by the contract.
2. MPC nodes observe the request, verify the foreign chain, and sign the payload hash with Ed25519.
3. Nodes call `respond_verify_foreign_tx` with an `Ed25519` signature response.
4. The contract's match hits the catch-all arm → `SignatureSchemeMismatch` error → response rejected.
5. The yield promise is never resolved; the request is permanently stuck.

This is the direct analog of the Compound M-12 bug: the same dispatch interface (`respond_verify_foreign_tx`) is used for all ForeignTx domain types, but the Ed25519 variant has a different "signature" (different match arm needed) that is absent — causing all Ed25519 ForeignTx responses to always fail.

---

### Impact Explanation

**Medium.** Any Ed25519 ForeignTx domain configured by governance becomes permanently non-functional. Every `verify_foreign_transaction` request targeting that domain enters the pending queue and can never be resolved — the yield promise never resumes. This breaks the request-lifecycle invariant ("all accepted requests can be fulfilled") for Ed25519 ForeignTx domains and permanently locks the associated pending state in the contract.

---

### Likelihood Explanation

**Low-Medium.** Triggering the bug requires an Ed25519 ForeignTx domain to be voted in by governance participants. However, the protocol explicitly supports multiple domain purposes and curves, and the code contains no guard preventing this combination. As the system expands to support more chains (e.g., Solana, which uses Ed25519), the probability of an Ed25519 ForeignTx domain being configured increases. Once configured, every single response attempt fails deterministically — no special attacker action is needed.

---

### Recommendation

Add an Ed25519 match arm to `respond_verify_foreign_tx()` mirroring the one in `respond()`. The derived Ed25519 public key should be computed from the root key and `request.tweak` (as done in `respond`), and `verify_eddsa_signature` should be called against the payload hash. Additionally, consider adding a compile-time or governance-time guard that rejects Ed25519 domains with `DomainPurpose::ForeignTx` until the response handler is fully implemented.

---

### Proof of Concept

1. Governance participants call `vote_add_domains` with a domain config: `{ protocol: Protocol::Frost, purpose: DomainPurpose::ForeignTx, id: <next_id> }`.
2. Once the domain is active, a user calls `verify_foreign_transaction({ domain_id: <ed25519_foreign_tx_domain>, request: SolanaRpcRequest { ... }, derivation_path: "...", payload_version: V1 })`.
3. The contract accepts the request (passes `check_request_preconditions` with `DomainPurpose::ForeignTx`), stores it in `pending_verify_foreign_tx_requests`, and yields.
4. MPC nodes observe the request, verify the Solana transaction, compute `payload_hash`, and sign it with their Ed25519 threshold key.
5. A node calls `respond_verify_foreign_tx(request, VerifyForeignTransactionResponse { payload_hash, signature: SignatureResponse::Ed25519 { signature: ... } })`.
6. The contract executes the match at line 718: `(SignatureResponse::Ed25519 { .. }, PublicKeyExtended::Ed25519 { .. })` — no arm matches → falls to catch-all → returns `Err(RespondError::SignatureSchemeMismatch { .. })`.
7. The response is rejected. All nodes retry and fail identically. The pending request is never resolved. [2](#0-1) [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L526-557)
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

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
    }
```

**File:** crates/contract/src/lib.rs (L586-640)
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

**File:** crates/contract/src/lib.rs (L948-960)
```rust
    pub fn vote_add_domains(&mut self, domains: Vec<DomainConfig>) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!(
            "vote_add_domains: signer={}, domains={:?}",
            env::signer_account_id(),
            domains,
        );

        if let Some(new_state) = self.protocol_state.vote_add_domains(domains)? {
            self.protocol_state = new_state;
        }
        Ok(())
    }
```
