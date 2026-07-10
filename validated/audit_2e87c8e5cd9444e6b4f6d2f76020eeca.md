### Title
CKD Output Validity Check Bypassed for `AppPublicKey` Variant in `respond_ckd` - (File: crates/contract/src/lib.rs)

### Summary

`respond_ckd` enforces a cryptographic pairing check (`ckd_output_check`) only for `AppPublicKeyPV` requests. For `AppPublicKey` requests the branch is an explicit no-op, so any attested participant can submit an arbitrary `CKDResponse` and the contract will accept and deliver it to the waiting user.

### Finding Description

In `respond_ckd`, after verifying the caller is an attested participant, the contract branches on the request variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(app_id), mpc_pk)`, which cryptographically proves the response was produced using the MPC network's master secret. For `AppPublicKey`, the empty arm accepts any `big_y` and `big_c` values unconditionally.

This is structurally identical to the M-18 pattern: a second branch of a match/if-else that handles a specific request state (`CANCEL_CLOSE_PENDING` / `AppPublicKey`) silently omits the invariant check that the other branches enforce.

The `AppPublicKey` variant is the "privately verifiable" CKD mode — the user can verify correctness off-chain using the MPC public key and their own private scalar. However, the contract imposes no on-chain enforcement, so a single Byzantine participant can forge the response before the user ever has a chance to verify.

The existing unit test at line 3403 confirms this: it passes `[1u8; 48]` / `[2u8; 48]` as `big_y` / `big_c` (cryptographically invalid garbage) and asserts the call succeeds. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation

The CKD protocol computes `big_c = msk·H(app_id) + a·big_y` so the user can recover `msk·H(app_id)` by computing `big_c − a·big_y`. A malicious responder who knows the user's public key `A = a·G1` (available in the pending request map) can choose arbitrary `r` and set:

- `big_y = r·G1`
- `big_c = r·A + X` for any `X` they choose

The user then decrypts: `big_c − a·big_y = r·A + X − a·r·G1 = r·a·G1 + X − a·r·G1 = X`

The user's derived confidential key is `X`, a value the attacker chose and knows. Any data the user encrypts under this key is immediately readable by the attacker. This is unauthorized confidential key derivation output produced by a single participant below the signing threshold, bypassing the threshold requirement entirely. [4](#0-3) [5](#0-4) 

### Likelihood Explanation

The attacker must be a single attested participant in the running protocol — a realistic Byzantine-below-threshold adversary. The `assert_caller_is_attested_participant_and_protocol_active` check is the only gate; once past it, the `AppPublicKey` branch imposes no further constraint. The pending request map is public contract state, so the attacker can read the user's `A` and craft the forged response before any honest node responds. [6](#0-5) [7](#0-6) 

### Recommendation

Apply the same `ckd_output_check` guard to the `AppPublicKey` branch. Because `AppPublicKey` provides only a G1 component, the existing pairing check (which requires a G2 component from `AppPublicKeyPV`) cannot be applied directly. The analogous check for the privately-verifiable variant is:

```
e(big_c, G2) = e(H(app_id), mpc_pk) · e(big_y, a·G2)
```

However, `a·G2` is not available from the request. The practical fix is to require callers who need on-chain output integrity to use `AppPublicKeyPV`, and to document clearly that `AppPublicKey` responses carry no on-chain validity guarantee and **must** be verified off-chain by the recipient before use. Alternatively, deprecate `AppPublicKey` in favour of `AppPublicKeyPV` for all production use cases where the response integrity matters. [8](#0-7) 

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey(A)` where `A = a·G1`.
2. Attacker (attested participant) reads the pending `CKDRequest` from contract state to obtain `A` and `app_id`.
3. Attacker picks scalar `r`, computes `big_y = r·G1`, `big_c = r·A + X` for chosen `X`.
4. Attacker calls `respond_ckd(request, CKDResponse { big_y, big_c })`.
5. Contract executes the `AppPublicKey(_) => {}` arm — no check — and calls `resolve_yields_for`, delivering the forged response to the user.
6. User computes `big_c − a·big_y = X`; their confidential key is `X`, known to the attacker.

The existing test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates step 4–5 with `[1u8; 48]` / `[2u8; 48]` as the forged values and asserts success. [9](#0-8) [10](#0-9)

### Citations

**File:** crates/contract/src/lib.rs (L653-689)
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

        let PublicKeyExtended::Bls12381 {
            public_key: dtos::PublicKey::Bls12381(public_key),
        } = self.public_key_extended(request.domain_id)?
        else {
            env::panic_str("Domain is not compatible with CKD (expected Bls12381 curve)");
        };

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
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

**File:** crates/contract/src/lib.rs (L3403-3441)
```rust
    #[test]
    fn respond_ckd__should_succeed_when_response_is_valid_and_request_exists() {
        let (context, mut contract, _secret_key) = basic_setup(Curve::Bls12381, &mut OsRng);
        let app_public_key: dtos::Bls12381G1PublicKey =
            "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6"
                .parse()
                .unwrap();
        let request = CKDRequestArgs {
            derivation_path: "".to_string(),
            app_public_key: CKDAppPublicKey::AppPublicKey(app_public_key.clone()),
            domain_id: dtos::DomainId::default(),
        };
        let ckd_request = CKDRequest::new(
            CKDAppPublicKey::AppPublicKey(app_public_key),
            request.domain_id,
            &context.predecessor_account_id,
            &request.derivation_path,
        );
        contract.request_app_private_key(request);
        contract.get_pending_ckd_request(&ckd_request).unwrap();

        let response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        with_active_participant_and_attested_context(&contract);

        match contract.respond_ckd(ckd_request.clone(), response.clone()) {
            Ok(_) => {
                contract
                    .return_ck_and_clean_state_on_success(ckd_request.clone(), Ok(response))
                    .detach();

                assert!(contract.get_pending_ckd_request(&ckd_request).is_none(),);
            }
            Err(_) => panic!("respond_ckd should not fail"),
        }
    }
```

**File:** crates/contract/src/primitives/ckd.rs (L80-102)
```rust
pub(crate) fn ckd_output_check(
    app_id: &dtos::CkdAppId,
    output: &CKDResponse,
    app_public_key: &dtos::CKDAppPublicKeyPV,
    public_key: &dtos::Bls12381G2PublicKey,
) -> bool {
    let big_c = env::bls12381_p1_decompress(&output.big_c);
    let big_y = env::bls12381_p1_decompress(&output.big_y);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);
    let pk = env::bls12381_p2_decompress(public_key);
    let hash_point = hash_app_id_with_pk(public_key.as_slice(), app_id.as_ref());

    let pairing_input = [
        big_c.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        big_y.as_slice(),
        pk2.as_slice(),
        hash_point.as_slice(),
        pk.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```

**File:** crates/threshold-signatures/docs/confidential_key_derivation/confidential-key-derivation.md (L39-45)
```markdown
Two variants of the protocol are supported:

- **Privately verifiable**: Verification is performed by the app after decryption.
- **Publicly verifiable**: Extends the previous variant by allowing any observer
  to verify correctness of the encrypted signature with respect to the MPC
  network public key, without knowing the app's secret key $a$.

```

**File:** crates/threshold-signatures/src/confidential_key_derivation.rs (L51-55)
```rust
    /// Takes a secret scalar and returns
    /// s <- C − a ⋅ Y = msk ⋅ H ( `app_id` )
    pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
        self.big_c - self.big_y * secret_scalar
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L469-498)
```rust
    pub(crate) fn is_caller_an_attested_participant(
        &self,
        participants: &Participants,
    ) -> Result<(), AttestationCheckError> {
        let signer_account_pk = env::signer_account_pk();
        let signer_id = env::signer_account_id();

        let info = participants
            .info(&signer_id)
            .ok_or(AttestationCheckError::CallerNotParticipant)?;

        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;

        if attestation.node_id.account_id != signer_id {
            return Err(AttestationCheckError::AttestationOwnerMismatch);
        }

        // Stored account keys are Ed25519 by construction; a non-Ed25519
        // signer necessarily mismatches.
        let signer_ed25519 = Ed25519PublicKey::try_from(&signer_account_pk)
            .map_err(|_| AttestationCheckError::AttestationKeyMismatch)?;
        if attestation.node_id.account_public_key != signer_ed25519 {
            return Err(AttestationCheckError::AttestationKeyMismatch);
        }

        Ok(())
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
