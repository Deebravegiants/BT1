### Title
Completed MPC Signature Replay Bypasses Threshold Requirement on Re-Submitted Requests - (File: crates/contract/src/lib.rs, crates/contract/src/pending_requests.rs)

### Summary
The `respond()` function in `MpcContract` verifies that a submitted signature is cryptographically valid for the given `SignatureRequest`, but does not track whether that specific signature value has already been used to satisfy a prior pending request. Because the contract-side `SignatureRequest` key contains no uniqueness component (no nonce, no block height, no timestamp), a single malicious attested MPC participant can replay a previously computed threshold signature to satisfy any new pending request for the same `(domain_id, tweak, payload)` tuple — without performing the threshold computation and without involving any other participant.

### Finding Description

The contract-side `SignatureRequest` struct is defined as:

```rust
pub struct SignatureRequest {
    pub tweak: Tweak,
    pub payload: Payload,
    pub domain_id: DomainId,
}
``` [1](#0-0) 

The `tweak` is deterministically derived from `(predecessor_id, path)` with no randomness or block-specific input:

```rust
pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
    let tweak = crate::kdf::derive_tweak(predecessor_id, path);
    SignatureRequest { domain_id: domain, tweak, payload }
}
``` [2](#0-1) 

The `sign()` function constructs this key and stores it in `pending_signature_requests`: [3](#0-2) 

When `respond()` is called, it verifies the signature is cryptographically valid for the `(tweak, payload, domain_id)` tuple, then calls `resolve_yields_for` which removes the pending entry: [4](#0-3) 

`resolve_yields_for` simply removes the map entry and resumes all queued yields: [5](#0-4) 

There is no record of which signature values have been used. After the map entry is removed, the same `SignatureRequest` key can be re-inserted by a new `sign()` call with identical arguments. At that point, any attested participant can call `respond()` with the previously computed signature `S` — which is still cryptographically valid for the same `(tweak, payload, domain_id)` — and the contract will accept it, resolving the new pending request without any threshold computation having occurred.

### Impact Explanation

A single Byzantine MPC participant (below the signing threshold) can unilaterally satisfy any pending signature request for a payload it has previously observed being signed, bypassing the t-of-n threshold requirement entirely. This breaks the core security guarantee of the MPC network: that no fewer than `t` participants can produce a valid signature. The attacker needs only to cache old `(SignatureRequest, SignatureResponse)` pairs and replay them whenever the same request key reappears in the pending map.

This maps to: **Critical — Bypass of threshold-signature requirements; unauthorized threshold signature issuance without the required participant authorization.**

### Likelihood Explanation

- Retrying the same signing request is a normal operational pattern (network failures, transaction retries, same payload signed for different downstream uses).
- The malicious participant only needs to store `(SignatureRequest, SignatureResponse)` pairs from prior rounds — trivial in-memory or on-disk storage.
- The attacker is a single attested MPC participant, which is the explicitly in-scope "Byzantine participant strictly below the signing threshold."
- No coordination with other participants is required.

### Recommendation

Introduce a uniqueness component into the contract-side `SignatureRequest` key so that each `sign()` invocation produces a distinct key that cannot be satisfied by a previously computed signature. Options include:

1. **Include the NEAR receipt ID** of the `sign()` call in the `SignatureRequest` key. Each `sign()` call produces a unique receipt, making every pending entry unique.
2. **Include a per-caller nonce** incremented on each `sign()` call, stored in contract state per `(predecessor, path, domain)`.
3. **Track used `(SignatureRequest, SignatureResponse)` pairs** in a completed-set mapping (analogous to the Foundation fix: store a mapping of used signatures and reject replays).

Option 1 is the lowest-overhead fix: the NEAR receipt ID is already available via `env::current_account_id()` context and is guaranteed unique per call.

### Proof of Concept

1. User calls `sign({payload: X, path: P, domain: D})` → contract stores `SignatureRequest{tweak=T, payload=X, domain=D}` in `pending_signature_requests`.
2. MPC nodes run threshold protocol; leader calls `respond(SignatureRequest{T,X,D}, S)` → entry removed, user receives signature `S`.
3. User calls `sign({payload: X, path: P, domain: D})` again (retry/reuse) → contract stores the identical `SignatureRequest{tweak=T, payload=X, domain=D}` in `pending_signature_requests`.
4. Malicious attested participant calls `respond(SignatureRequest{T,X,D}, S)` with the cached old signature `S`.
5. `respond()` verifies `S` is a valid ECDSA/EdDSA signature for `(payload=X, derived_key=f(root_key, T))` → **passes**.
6. `resolve_yields_for` removes the entry and resumes the user's yield with `S`.
7. The second request is satisfied with zero threshold participation — one node acted alone. [6](#0-5) [7](#0-6) [1](#0-0)

### Citations

**File:** crates/near-mpc-crypto-types/src/sign.rs (L111-125)
```rust
pub struct SignatureRequest {
    pub tweak: Tweak,
    pub payload: Payload,
    pub domain_id: DomainId,
}

impl SignatureRequest {
    pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
        let tweak = crate::kdf::derive_tweak(predecessor_id, path);
        SignatureRequest {
            domain_id: domain,
            tweak,
            payload,
        }
    }
```

**File:** crates/contract/src/lib.rs (L379-397)
```rust
        let request = SignatureRequest::new(
            request.domain_id,
            request.payload,
            &predecessor,
            &request.path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_SIGNATURE_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_signature_request(request, id),
        );
```

**File:** crates/contract/src/lib.rs (L564-651)
```rust
    pub fn respond(
        &mut self,
        request: SignatureRequest,
        response: dtos::SignatureResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain)?;

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

        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/src/pending_requests.rs (L43-88)
```rust
pub(crate) fn push_pending_yield<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: K,
    data_id: CryptoHash,
) where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
    }
    queue.push(YieldIndex { data_id });
}

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
