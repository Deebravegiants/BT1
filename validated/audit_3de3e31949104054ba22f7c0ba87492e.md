### Title
Missing Cryptographic Binding Check for `AppPublicKey` Variant in `respond_ckd` Allows Single Byzantine Participant to Deliver Arbitrary CKD Output — (`crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function enforces the pairing-based cryptographic binding check (`ckd_output_check`) **only** for the `AppPublicKeyPV` variant of `CKDAppPublicKey`. For the `AppPublicKey` variant, the match arm is an empty block — no check is performed. A single attested participant can call `respond_ckd` with any arbitrary `big_c`/`big_y` bytes for a pending `AppPublicKey` request, and the contract will unconditionally resolve the yield and deliver the fabricated output to the waiting caller.

---

### Finding Description

In `respond_ckd`, after verifying the caller is an attested participant and the protocol is running, the contract performs a match on `request.app_public_key`: [1](#0-0) 

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the MPC master key and `app_id`: [2](#0-1) 

For `AppPublicKey`, this entire check is skipped. The function then unconditionally resolves the yield: [3](#0-2) 

The `AppPublicKey` variant carries only a G1 key (no G2 component), which is why the pairing check cannot be applied directly. However, the contract provides no substitute verification — it simply trusts whatever `big_c`/`big_y` the single responding participant supplies.

The `CKDAppPublicKey` enum confirms the two variants: [4](#0-3) 

`respond_ckd` requires only a single attested participant — there is no threshold aggregation before `resolve_yields_for` is called: [5](#0-4) 

---

### Impact Explanation

A single Byzantine attested participant can:
1. Observe any pending `CKDRequest` using the `AppPublicKey` variant.
2. Call `respond_ckd` with a crafted `CKDResponse` containing arbitrary `big_c`/`big_y` bytes (e.g., all-zero, or points of their choosing).
3. The contract accepts the call and resolves the yield, delivering the fabricated output to the original requester.

The requester receives a `CKDResponse` with no cryptographic binding to the MPC master key or `app_id`. This constitutes **unauthorized confidential key derivation output without the required participant authorization** — the output is not a product of the threshold MPC protocol.

---

### Likelihood Explanation

Any single attested participant acting Byzantine can trigger this. The attacker does not need threshold collusion — one participant suffices. The `AppPublicKey` variant is the default/legacy deserialization path (plain G1 key strings deserialize to it), making it the most commonly used variant in practice. [6](#0-5) 

---

### Recommendation

For the `AppPublicKey` variant, the contract cannot perform the full pairing check (no G2 key is available). Two remediation options:

1. **Deprecate `AppPublicKey` in favor of `AppPublicKeyPV`** — require all callers to supply both G1 and G2 keys so the pairing check can always be enforced on-chain.
2. **Require threshold-aggregated proof** — before resolving, require that a threshold of participants have submitted matching responses, so a single Byzantine participant cannot unilaterally resolve the yield.

Option 1 is simpler and eliminates the asymmetry entirely.

---

### Proof of Concept

```rust
// Enqueue a CKDRequest with AppPublicKey variant (single G1 key, no G2)
let request = CKDRequest::new(
    CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey([1u8; 48])),
    DomainId(0),
    &"alice.near".parse().unwrap(),
    "m/0",
);
// contract.request_ckd(request.clone()) — enqueues and yields

// Single attested participant submits all-zero big_c / big_y
let fake_response = CKDResponse {
    big_c: Bls12381G1PublicKey([0u8; 48]),
    big_y: Bls12381G1PublicKey([0u8; 48]),
};
// contract.respond_ckd(request, fake_response) — accepted, yield resolved
// The match arm at lib.rs:676 is `{}` — ckd_output_check is never called.
// resolve_yields_for delivers fake_response to the original caller.
```

The `AppPublicKey` match arm at line 676 is an empty block, so `ckd_output_check` (lines 678–680) is never reached for this variant, confirming the bypass. [1](#0-0) [2](#0-1)

### Citations

**File:** crates/contract/src/lib.rs (L654-688)
```rust
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

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L15-18)
```rust
pub enum CKDAppPublicKey {
    AppPublicKey(Bls12381G1PublicKey),
    AppPublicKeyPV(CKDAppPublicKeyPV),
}
```

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L47-51)
```rust
        match Helper::deserialize(deserializer)? {
            Helper::Tagged(Tagged::AppPublicKey(pk)) => Ok(CKDAppPublicKey::AppPublicKey(pk)),
            Helper::Tagged(Tagged::AppPublicKeyPV(pk)) => Ok(CKDAppPublicKey::AppPublicKeyPV(pk)),
            Helper::Plain(pk) => Ok(CKDAppPublicKey::AppPublicKey(pk)),
        }
```
