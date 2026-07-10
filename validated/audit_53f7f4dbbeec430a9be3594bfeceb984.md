The code is clear enough to render a definitive verdict. Let me verify the exact guard (or lack thereof) in `respond_ckd` and the `unmask` path.

### Title
Missing CKD Output Validation for `AppPublicKey` Variant Allows Single Byzantine Node to Deliver Attacker-Controlled Secret to TEE App — (`crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` enforces a cryptographic pairing check (`ckd_output_check`) only for the `AppPublicKeyPV` variant. For the `AppPublicKey` (privately-verifiable / legacy) variant the match arm is an explicit no-op. Any single attested MPC participant can therefore call `respond_ckd` with arbitrary `big_y` / `big_c` bytes — including the G1 identity point — and the contract will accept and store the response. The TEE app subsequently calls `unmask(a) = big_c − big_y·a`, receiving a fully attacker-controlled value as its derived secret.

---

### Finding Description

**Root cause — empty validation branch:**

In `crates/contract/src/lib.rs` the `respond_ckd` handler branches on the request variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no validation
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The `AppPublicKeyPV` arm calls `ckd_output_check`, which verifies `e(big_c, g2) = e(big_y, app_pk2) · e(H, pk)` via a host pairing check. The `AppPublicKey` arm does nothing. After the match, the response bytes are serialised and stored unconditionally:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

**Identity point is a valid compressed encoding:**

`TryFrom<&Bls12381G1PublicKey> for blstrs::G1Projective` delegates to `blstrs::G1Projective::from_compressed`, which accepts the identity (point-at-infinity) because it carries a well-formed infinity flag in the BLS12-381 compressed encoding:

```rust
fn try_from(dto: &Bls12381G1PublicKey) -> Result<Self, Self::Error> {
    blstrs::G1Projective::from_compressed(dto)
        .into_option()
        .ok_or(CryptoConversionError::InvalidPoint)
}
``` [3](#0-2) 

The codebase itself documents this: the test `app_public_key_check__should_accept_identity_key_pair` explicitly asserts that the identity pair passes the pairing check. [4](#0-3) 

**`unmask` propagates the attacker-chosen value directly:**

```rust
pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
    self.big_c - self.big_y * secret_scalar
}
``` [5](#0-4) 

If the attacker sets `big_c = big_y = G1::identity()`, then `unmask(a) = identity − identity·a = identity` for any `a`. If the attacker sets `big_c = identity` and `big_y = P` (any chosen point), then `unmask(a) = −P·a`, which is fully determined by the attacker's choice of `P` and the app's known public key `A = a·G1`.

---

### Impact Explanation

The TEE app's derived secret is replaced by an attacker-chosen G1 element. Because the privately-verifiable variant provides no mechanism for the TEE app to verify the output against the MPC network's public key (that check requires knowing `msk`, which the app does not have), the app cannot detect the substitution. Any cryptographic material the app derives from this secret — encryption keys, signing keys, authentication tokens — is known to or controlled by the attacker. This constitutes **unauthorized confidential key derivation output** delivered to the TEE app without the required honest-majority participant authorization.

---

### Likelihood Explanation

The attack requires exactly one Byzantine attested MPC participant. The contract's only caller check is `assert_caller_is_attested_participant_and_protocol_active()`; there is no check that the caller is the designated coordinator for the request. [6](#0-5) 

Any attested participant can race to call `respond_ckd` before the honest coordinator. The first call that matches a pending request resolves the yield; subsequent calls fail. A single Byzantine node is strictly below the signing threshold.

---

### Recommendation

Apply the same pairing-based output check to the `AppPublicKey` variant. Because the app's public key `A` is a G1 point and the network public key `pk` is a G2 point, the relation `e(big_c, g2) = e(big_y, g2)^? · e(H(app_id, pk), pk)` cannot be checked without a G2 counterpart for `A`. The simplest fix is one of:

1. **Deprecate `AppPublicKey` entirely** and require all new requests to use `AppPublicKeyPV`, which already has a validated output check.
2. **Add a non-degeneracy check** at minimum: reject `big_y = identity` and `big_c = identity` in the `AppPublicKey` branch. This does not provide full binding but eliminates the trivially-predictable-secret attack.
3. **Require `AppPublicKeyPV` for all new requests** and add a migration path for existing `AppPublicKey` requests.

---

### Proof of Concept

```rust
// Byzantine attested participant calls respond_ckd with identity points
let identity_bytes = blstrs::G1Projective::identity().to_compressed();
let manipulated_response = CKDResponse {
    big_y: dtos::Bls12381G1PublicKey(identity_bytes),
    big_c: dtos::Bls12381G1PublicKey(identity_bytes),
};

// Contract accepts — AppPublicKey branch has no validation
contract.respond_ckd(ckd_request, manipulated_response).unwrap();

// TEE app side: TryFrom succeeds for identity
let big_y = blstrs::G1Projective::try_from(&response.big_y).unwrap(); // identity
let big_c = blstrs::G1Projective::try_from(&response.big_c).unwrap(); // identity

// unmask returns identity regardless of the app's secret scalar `a`
let secret = big_c - big_y * app_secret_scalar; // identity - identity*a = identity
assert_eq!(secret, blstrs::G1Projective::identity()); // attacker knows this value
```

### Citations

**File:** crates/contract/src/lib.rs (L655-666)
```rust
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

**File:** crates/contract/src/lib.rs (L684-688)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-crypto-types/src/conversions/blstrs.rs (L10-17)
```rust
impl TryFrom<&Bls12381G1PublicKey> for blstrs::G1Projective {
    type Error = CryptoConversionError;
    fn try_from(dto: &Bls12381G1PublicKey) -> Result<Self, Self::Error> {
        blstrs::G1Projective::from_compressed(dto)
            .into_option()
            .ok_or(CryptoConversionError::InvalidPoint)
    }
}
```

**File:** crates/contract/src/primitives/ckd.rs (L479-495)
```rust
    /// Documents the pre-existing behavior that identity key pairs satisfy
    /// the pairing equation and are accepted.
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

**File:** crates/threshold-signatures/src/confidential_key_derivation.rs (L53-55)
```rust
    pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
        self.big_c - self.big_y * secret_scalar
    }
```
