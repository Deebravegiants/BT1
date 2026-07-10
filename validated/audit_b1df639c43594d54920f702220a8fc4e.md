Based on my investigation of the relevant source files, here is my assessment:

---

### Title
Unverified CKD Output for `AppPublicKey` Variant Allows Byzantine Leader to Submit Fraudulent Response — (`crates/contract/src/primitives/ckd.rs`)

### Summary

The contract's `ckd_output_check` function is structurally typed to only accept `CKDAppPublicKeyPV` and cannot be applied to the `AppPublicKey` variant. No equivalent on-chain verification exists for `AppPublicKey` CKD outputs. A single Byzantine node elected as leader can submit an arbitrary `(big_y, big_c)` pair for an `AppPublicKey` CKD request, and the contract will accept it without cryptographic verification.

### Finding Description

`ckd_output_check` in `crates/contract/src/primitives/ckd.rs` performs the pairing check:

> `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` [1](#0-0) 

This check requires `app_pk2` (a G2 element), which is only present in `CKDAppPublicKeyPV`. The `AppPublicKey` variant carries only a G1 point and has no G2 component, making the pairing equation structurally inapplicable to it. [2](#0-1) 

In `CKDComputation`, both variants run distinct MPC protocols — `ckd()` for `AppPublicKey` and `ckd_pv()` for `AppPublicKeyPV` — and the leader collects the result and submits it via `respond_ckd`. [3](#0-2) 

Because no on-chain check exists for the `AppPublicKey` variant, a Byzantine leader can skip `CKDComputation` entirely and call `respond_ckd` with an arbitrary `(big_y, big_c)` pair. The contract has no mechanism to reject it.

### Impact Explanation

The caller receives a CKD output `(big_y, big_c)` that does not correspond to the MPC network's shared secret. This is a confidential key derivation output produced without the required participant authorization — matching the Critical impact category: *unauthorized confidential key derivation output without required participant authorization*.

### Likelihood Explanation

A single attested participant node can be elected leader for a CKD request (leader selection is random among active participants). This requires only one Byzantine node below the signing threshold — no collusion is needed. The `AppPublicKey` variant is a production code path, not a test or devnet-only path. [4](#0-3) 

### Recommendation

Implement an on-chain output check for the `AppPublicKey` variant. Since `AppPublicKey` only provides a G1 point (`pk1`), the pairing-based check cannot be applied directly. Options:

1. **Require callers to always use `AppPublicKeyPV`** — deprecate `AppPublicKey` for CKD requests, since it is structurally unverifiable on-chain.
2. **Add a G2 component to `AppPublicKey`** — effectively making it equivalent to `AppPublicKeyPV`, enabling the same pairing check.
3. **Require threshold-of-participants to co-sign the response** — so the contract verifies a threshold signature over `(big_y, big_c, app_id, app_public_key)` rather than relying solely on the leader's submission.

### Proof of Concept

A contract unit test that:
1. Submits a CKD request with `AppPublicKey` variant.
2. Calls `respond_ckd` with a randomly generated `(big_y, big_c)` pair (not produced by the CKD protocol).
3. Asserts the contract **accepts** the response — demonstrating the missing verification.

The structural proof is in `ckd_output_check`'s signature: it takes `&dtos::CKDAppPublicKeyPV`, making it impossible to call for an `AppPublicKey` request without a G2 component. [1](#0-0)

### Citations

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

**File:** crates/node/src/providers/ckd/sign.rs (L43-52)
```rust
            .client
            .select_random_active_participants_including_me(
                threshold.value(),
                &running_participants,
            )
            .context("Could not choose active participants for a ckd")?;

        let channel = self
            .client
            .new_channel_for_task(CKDTaskId::Ckd { id }, participants)?;
```

**File:** crates/node/src/providers/ckd/sign.rs (L151-178)
```rust
        let result = match self.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(pk) => {
                let protocol = ckd(
                    cs_participants.as_slice(),
                    leader,
                    my_id,
                    self.keygen_output,
                    app_id,
                    ElementG1::try_from(&pk)?,
                    OsRng,
                )?;
                run_protocol("ckd", channel, protocol).await?
            }
            dtos::CKDAppPublicKey::AppPublicKeyPV(pv) => {
                let pk1 = ElementG1::try_from(&pv.pk1)?;
                let pk2 = ElementG2::try_from(&pv.pk2)?;
                let protocol = ckd_pv(
                    cs_participants.as_slice(),
                    leader,
                    my_id,
                    self.keygen_output,
                    app_id,
                    PublicVerificationKey::new(pk1, pk2),
                    OsRng,
                )?;
                run_protocol("ckd_pv", channel, protocol).await?
            }
        };
```
