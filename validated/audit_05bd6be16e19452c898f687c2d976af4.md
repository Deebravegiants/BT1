### Title
CKD Output Verification Unconditionally Skipped for `AppPublicKey` Variant, Allowing a Single Byzantine Coordinator to Forge Confidential Key Derivation Output — (File: `crates/contract/src/lib.rs`)

### Summary

In `respond_ckd`, the on-chain cryptographic output check (`ckd_output_check`) is only executed when the request carries an `AppPublicKeyPV` key. When the request carries the plain `AppPublicKey` variant, the match arm is empty and the `CKDResponse` (`big_y`, `big_c`) is accepted without any verification. A single malicious attested participant acting as coordinator can submit an arbitrary forged `(big_y, big_c)` pair, causing the user to derive a key that the attacker already knows, completely breaking the confidentiality guarantee of the CKD protocol.

### Finding Description

In `respond_ckd` at `crates/contract/src/lib.rs` lines 675–682:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

The `AppPublicKey` arm is a no-op. The `ckd_output_check` function (defined in `crates/contract/src/primitives/ckd.rs` lines 80–102) verifies the pairing equation `e(big_c, G2) = e(big_y, app_pk2) · e(H(pk, app_id), mpc_pk)`. This check is the only on-chain guard that the MPC nodes actually computed the correct output. For `AppPublicKey` requests, no equivalent check exists.

The `respond_ckd` function only requires the caller to be an attested participant (`assert_caller_is_attested_participant_and_protocol_active`). Any single attested participant can therefore call `respond_ckd` with a crafted `CKDResponse` for any pending `AppPublicKey` request and the contract will accept it, resolving the yield and delivering the forged output to the user.

**Attack path:**

1. User calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(pk1)` where `pk1 = a·G1`.
2. Malicious attested participant monitors the chain for the pending CKD request.
3. Before the honest coordinator responds, the attacker calls `respond_ckd` with `big_y = G1_identity` (the identity point, which is accepted by the host) and `big_c = X` for any attacker-chosen point `X`.
4. The contract passes the empty match arm, calls `resolve_yields_for`, and delivers `(big_y=0, big_c=X)` to the user.
5. User computes `sig = big_c − a·big_y = X − a·0 = X`.
6. User derives key `HKDF(X)`. The attacker chose `X`, so the attacker knows the derived key.

The identity point is explicitly accepted by the NEAR BLS12-381 host functions, as confirmed by the test `app_public_key_check__should_accept_identity_key_pair` in `crates/contract/src/primitives/ckd.rs` lines 481–495.

### Impact Explanation

The CKD protocol's confidentiality guarantee is that only the user (who holds the ephemeral private key `a`) can recover the derived secret `msk·H(pk, app_id)`. By forging `(big_y, big_c)` with `big_y = 0`, the attacker eliminates the user's private key from the computation entirely, making the derived key equal to a value the attacker chose. The attacker learns the user's derived private key without ever learning `a` or the MPC master secret key. This is a **critical** confidential key derivation output compromise by a single Byzantine participant, matching the allowed impact: *"confidential key derivation output without the required participant authorization."*

### Likelihood Explanation

Any single attested MPC participant can execute this attack. The attacker does not need threshold collusion, a leaked key, or privileged operator access — only a valid TEE attestation, which is the normal entry requirement for any MPC node. The attack is a simple race to call `respond_ckd` before the honest coordinator. On a live network with a known block time, this race is reliably winnable by a participant who monitors the mempool or chain state.

### Recommendation

Apply the same output verification to the `AppPublicKey` variant. Because `AppPublicKey` provides only `pk1` (a G1 point) and not `pk2` (a G2 point), the full pairing check used in `ckd_output_check` cannot be applied directly. The recommended fix is to require callers to use `AppPublicKeyPV` for all new requests (deprecating `AppPublicKey`), or to add an alternative on-chain check for the `AppPublicKey` variant — for example, verifying that `big_c − big_y·a_pub = msk·H(pk, app_id)` using a commitment scheme, or requiring the user to supply `pk2` in all cases. At minimum, document that `AppPublicKey` requests provide no on-chain integrity guarantee and that a single malicious coordinator can forge the output.

### Proof of Concept

```
1. Deploy contract in Running state with ≥1 attested participant (the attacker).
2. User calls request_app_private_key({
       app_public_key: AppPublicKey(pk1),   // pk1 = a·G1, a is user's secret
       derivation_path: "test",
       domain_id: 0
   })
3. Attacker (attested participant) calls respond_ckd(
       request = <the pending CKDRequest>,
       response = CKDResponse {
           big_y: G1_identity_compressed,   // 0·G1
           big_c: attacker_chosen_point_X,  // any G1 point
       }
   )
4. Contract executes the AppPublicKey arm (empty), skips ckd_output_check,
   calls resolve_yields_for → user receives (big_y=0, big_c=X).
5. User computes sig = X − a·0 = X.
6. User derives key = HKDF(X).
   Attacker knows X → attacker knows the user's derived key.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L484-491)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
        }
```

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

**File:** crates/contract/src/primitives/ckd.rs (L481-495)
```rust
    #[test]
    #[expect(non_snake_case)]
    fn app_public_key_check__should_accept_identity_key_pair() {
        // Given
        let app_pk = dtos::CKDAppPublicKeyPV {
            pk1: dtos::Bls12381G1PublicKey(G1Projective::identity().to_compressed()),
            pk2: dtos::Bls12381G2PublicKey(G2Projective::identity().to_compressed()),
        };

        // When
        let accepted = app_public_key_check(&app_pk);

        // Then
        assert!(accepted);
    }
```
