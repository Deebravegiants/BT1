### Title
Unverified CKD Output for `AppPublicKey` Variant Enables Single Byzantine Participant to Deliver Arbitrary Key Material — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function applies a cryptographic pairing check to validate the CKD output **only** when the request uses the `AppPublicKeyPV` variant. For the `AppPublicKey` variant, no output verification is performed. A single Byzantine attested participant can call `respond_ckd` with arbitrary `big_y` and `big_c` values, delivering incorrect key material to the requesting user without any on-chain detection. This is structurally analogous to the Seaport finding: one code path enforces an explicit resolver/verifier check while the other silently skips it, allowing a malicious party to substitute the output the caller receives.

---

### Finding Description

In `respond_ckd`, the contract branches on the `app_public_key` variant stored in the `CKDRequest`:

```rust
// crates/contract/src/lib.rs:675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(pk ‖ app_id), msk_pk)`, which can only be satisfied by output produced by the threshold MPC protocol:

```rust
// crates/contract/src/primitives/ckd.rs:80-101
pub(crate) fn ckd_output_check(...) -> bool {
    ...
    env::bls12381_pairing_check(&pairing_input)
}
``` [2](#0-1) 

For `AppPublicKey`, the arm is an empty block. Any `CKDResponse` — with any `big_y` and `big_c` — is accepted as long as the caller passes `assert_caller_is_attested_participant_and_protocol_active()`. [3](#0-2) 

The `CKDResponse` type carries two raw BLS12-381 G1 compressed points with no further constraints:

```rust
pub struct CKDResponse {
    pub big_y: Bls12381G1PublicKey,
    pub big_c: Bls12381G1PublicKey,
}
``` [4](#0-3) 

The user's `request_app_private_key` call is resolved via `pending_requests::resolve_yields_for`, which delivers whatever `CKDResponse` the first responding attested participant submits: [5](#0-4) 

---

### Impact Explanation

The CKD protocol is designed so that the user holds a secret scalar `a` and submits `pk1 = G1 * a`. The honest MPC output satisfies `big_c − a · big_y = msk · H(pk ‖ app_id)`, giving the user a deterministic derived key. Because the contract performs no check for `AppPublicKey`, a Byzantine attested participant can instead submit:

- `big_y = G1 * 0` (the G1 identity)
- `big_c = G1 * s` for an attacker-chosen scalar `s`

The user then computes `G1 * s − a · identity = G1 * s`. The attacker knows `s` and therefore controls the derived key. Any funds or credentials bound to that derived key are immediately accessible to the attacker.

This satisfies the allowed critical impact: **confidential key derivation output produced without the required threshold participant authorization** — a single Byzantine node below the signing threshold suffices.

---

### Likelihood Explanation

The attack requires only **one** Byzantine attested participant, not a threshold quorum. The attacker must:

1. Be an active, TEE-attested participant in the MPC network.
2. Race to call `respond_ckd` before honest nodes do, for a pending `AppPublicKey` request.

A compromised TEE image, a malicious operator of a single node, or an insider threat satisfies condition 1. Condition 2 is a standard front-running race on the NEAR chain, which is realistic given that the attacker is an active network participant with direct chain access. The `AppPublicKey` variant is a production feature exercised in e2e tests, so real users will submit such requests.

---

### Recommendation

1. **Short-term**: Require callers to use `AppPublicKeyPV` for all CKD requests, removing `AppPublicKey` from the production API, or prominently document that `AppPublicKey` provides **no on-chain output integrity guarantee** and that a single Byzantine participant can substitute arbitrary key material.

2. **Long-term**: Extend the protocol so that `AppPublicKey` responses include a zero-knowledge proof of correct computation (e.g., a Schnorr proof that `big_c − a · big_y` lies on the correct coset), or mandate `AppPublicKeyPV` for all security-critical derivations.

The inconsistency is directly analogous to the Seaport finding: `AppPublicKeyPV` acts like a regular criteria order (the fulfiller can verify what they receive), while `AppPublicKey` acts like a contract order (the fulfiller cannot verify, and a malicious party can substitute the output).

---

### Proof of Concept

```
1. Alice calls request_app_private_key({ AppPublicKey(pk1 = G1*a), domain_id, path })
   → contract stores CKDRequest in pending_ckd_requests

2. Byzantine attested participant Eve calls respond_ckd(request, CKDResponse {
       big_y: G1 * 0,   // identity element — Eve knows this is 0
       big_c: G1 * s,   // Eve chooses scalar s
   })
   → contract hits the AppPublicKey arm: empty block, no check
   → resolve_yields_for delivers the response to Alice's yield

3. Alice receives big_y = identity, big_c = G1*s
   Alice computes: derived_key = big_c − a * big_y
                               = G1*s − a * identity
                               = G1*s

4. Eve knows s, so Eve knows derived_key = G1*s.
   Eve can sign on behalf of Alice's derived key and steal any funds
   or credentials bound to it.
```

The root cause is at `crates/contract/src/lib.rs:676` — the empty `AppPublicKey(_) => {}` arm — contrasted with the enforced `ckd_output_check` at line 678. [1](#0-0)

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

**File:** crates/contract/src/primitives/ckd.rs (L80-101)
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
```

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L76-97)
```rust
/// CKD request with derived app_id.
#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct CKDRequest {
    pub app_public_key: CKDAppPublicKey,
    pub app_id: CkdAppId,
    pub domain_id: DomainId,
}

impl CKDRequest {
    pub fn new(
        app_public_key: CKDAppPublicKey,
        domain_id: DomainId,
        predecessor_id: &AccountId,
        derivation_path: &str,
    ) -> Self {
        let app_id = crate::kdf::derive_app_id(predecessor_id, derivation_path);
        Self {
            app_public_key,
            app_id,
            domain_id,
        }
    }
```
