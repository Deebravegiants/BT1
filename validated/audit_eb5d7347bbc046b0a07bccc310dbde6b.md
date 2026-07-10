### Title
`respond_ckd` Accepts Unverified CKD Output for `AppPublicKey` Variant, Enabling Byzantine Leader to Corrupt Key Derivation — (File: `crates/contract/src/lib.rs`)

---

### Summary

`MpcContract::respond_ckd` performs a cryptographic pairing check on the CKD response only when the request carries the `AppPublicKeyPV` variant. When the request carries the plain `AppPublicKey` variant — the default, non-publicly-verifiable form — the function performs **zero verification** of the returned `{big_c, big_y}` points and immediately resolves the pending yield with whatever the responding node supplied. A single Byzantine leader node can therefore submit an arbitrary `CKDResponse` for any `AppPublicKey` request and the contract will accept it unconditionally.

---

### Finding Description

`respond_ckd` branches on the request's `app_public_key` field:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(pk‖app_id), msk_pk)`, binding the response to the master public key and the app identity. [2](#0-1) 

For `AppPublicKey`, the arm is an empty block. The contract resolves the yield immediately with the unverified response: [3](#0-2) 

The node-side `CKDComputation` runs the threshold protocol and the leader aggregates participant shares before calling `respond_ckd`. Because the leader is the sole submitter of the final on-chain response, a Byzantine leader can substitute any `{big_c, big_y}` pair without needing cooperation from other participants. [4](#0-3) 

---

### Impact Explanation

The CKD output `{big_c, big_y}` is the only material the requester receives to reconstruct their derived private key: `sk = big_c − app_sk · big_y`. A crafted response produces an attacker-chosen derived key. If the requester subsequently uses that key to receive funds on a foreign chain (the primary use-case for CKD), those funds are permanently inaccessible because the correct key is never derivable from the corrupted output. The contract's acceptance of the response constitutes an on-chain endorsement; callers that rely on the contract having validated the output are misled.

This maps to: **Medium — request-lifecycle and contract execution-flow manipulation that breaks the production safety invariant that a resolved CKD yield carries a cryptographically correct derivation output.**

---

### Likelihood Explanation

`AppPublicKey` is the default, non-publicly-verifiable variant documented in the CLI and used in all non-PV tests. Any registered participant that is elected leader for a CKD request can exploit this without colluding with any other participant. Leader election is per-request and rotates across participants, so a Byzantine participant will be leader for a predictable fraction of requests.

---

### Recommendation

Add an equivalent on-chain binding check for the `AppPublicKey` path. Because `app_sk` is secret, a direct pairing check is not possible; however, the contract can at minimum verify that `big_c` and `big_y` are valid, non-identity points on the BLS12-381 G1 curve (subgroup membership) before accepting the response. More robustly, require callers to use `AppPublicKeyPV` for any request where on-chain integrity guarantees are needed, and document clearly that `AppPublicKey` responses carry no on-chain verification.

---

### Proof of Concept

The existing unit test already demonstrates the issue — it passes completely invalid byte strings as curve points and the contract accepts them without error:

```rust
let response = CKDResponse {
    big_y: dtos::Bls12381G1PublicKey([1u8; 48]),  // not a valid G1 point
    big_c: dtos::Bls12381G1PublicKey([2u8; 48]),  // not a valid G1 point
};
// ...
match contract.respond_ckd(ckd_request.clone(), response.clone()) {
    Ok(_) => { /* succeeds */ }
    Err(_) => panic!("respond_ckd should not fail"),
}
``` [5](#0-4) 

A Byzantine leader reproduces this on mainnet by:
1. Participating honestly in the threshold CKD round to avoid detection by peers.
2. Discarding the correct aggregated output.
3. Calling `respond_ckd` with arbitrary `big_c`/`big_y` values that encode an attacker-chosen scalar as the victim's derived key.
4. The contract resolves the yield and returns the forged response to the requester.

### Citations

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

**File:** crates/node/src/providers/ckd/sign.rs (L151-181)
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

        Ok(result.map(|f| (f.big_y(), f.big_c())))
    }
```
