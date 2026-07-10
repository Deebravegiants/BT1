### Title
Missing Cryptographic Output Validation in `respond_ckd` for `AppPublicKey` Variant Allows Single Malicious Participant to Forge Confidential Key Derivation Output - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract validates the CKD response cryptographically only for the `AppPublicKeyPV` (publicly verifiable) variant. For the `AppPublicKey` (privately verifiable / legacy) variant, the match arm is a no-op — any arbitrary `CKDResponse` is accepted and delivered to the user without any pairing check. A single malicious attested participant can call `respond_ckd` with a crafted `(big_y, big_c)` pair it controls, causing the contract to resolve the pending yield with forged key material. The user receives a "derived key" whose discrete-log the attacker knows, enabling full impersonation.

---

### Finding Description

`respond_ckd` fetches the BLS12-381 public key and then branches on the request's `app_public_key` variant:

```rust
// crates/contract/src/lib.rs  lines 675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, G2) = e(big_y, app_pk2) · e(H(pk, app_id), pk)`, which cryptographically binds the response to the threshold master secret key and the user's public key: [2](#0-1) 

For `AppPublicKey`, **no equivalent check exists**. The contract immediately calls `resolve_yields_for`, serialising whatever `big_y` and `big_c` the caller supplied and resuming every queued yield promise with that payload: [3](#0-2) 

Compare with `respond` (ECDSA/EdDSA), which always verifies the signature against the derived public key before resolving: [4](#0-3) 

The CKD protocol requires threshold cooperation to produce a correct `(big_y, big_c)` pair. The coordinator aggregates Lagrange-weighted shares `(λ_i · Y_i, λ_i · C_i)` from at least `t` nodes to reconstruct `C = msk · H(pk, app_id) + a · Y`. No single node knows `msk`. The contract is supposed to enforce this by verifying the output, but for `AppPublicKey` it does not. [5](#0-4) 

The `AppPublicKey` variant is the legacy, still-supported, still-actively-used mode: [6](#0-5) 

The access guard `assert_caller_is_attested_participant_and_protocol_active` only requires the caller to be a single attested participant in the current epoch — well below the signing threshold: [7](#0-6) 

---

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without the required participant authorization.**

A single malicious attested participant constructs a forged response:

- Choose attacker scalar `y_a` and target scalar `z` (both known to attacker).
- Set `big_y = G1 * y_a`, `big_c = G1 * z + app_pk * y_a`.

The user decrypts:

```
sig = big_c − a · big_y
    = G1·z + app_pk·y_a − G1·a·y_a
    = G1·z + G1·a·y_a − G1·a·y_a
    = G1·z
```

The attacker knows `z`, so it knows the user's derived key `G1·z`. The user's downstream system (e.g., a TEE app) uses this as its deterministic secret. The attacker can impersonate the user on any system relying on that derived key, or simply deliver garbage (`z = 0`) to permanently deny the user their key.

Because `resolve_yields_for` drains the entire fan-out queue in one call, every duplicate submission of the same request is simultaneously poisoned. [8](#0-7) 

---

### Likelihood Explanation

- The `AppPublicKey` (legacy) variant is the default plain-G1-point format accepted by the contract and is actively used in production and tests.
- The attacker needs only to be one attested participant — a Byzantine node strictly below the signing threshold, which is the canonical threat model for a `t-of-n` system.
- The attack requires no coordination, no key leakage, and no network-level capability: the attacker simply calls `respond_ckd` on-chain with crafted arguments before the honest coordinator does.
- Because NEAR transactions are ordered by the block producer, a malicious participant can race the honest `respond_ckd` submission. If the honest response lands first, the attacker's call returns `RequestNotFound` (harmless). If the attacker's lands first, the honest call also returns `RequestNotFound` — the forged response is already delivered.

---

### Recommendation

Apply the same pairing-based output check to the `AppPublicKey` variant. Because `AppPublicKey` only provides `pk1` (a G1 point), the check must use the G1 point directly in place of `app_pk2`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(app_pk) => {
        // Verify e(big_c, G2) = e(big_y, G2·a) · e(H(pk,app_id), pk)
        // where G2·a is reconstructed from app_pk (G1·a) via the discrete-log
        // relationship — or alternatively require AppPublicKeyPV for all new requests
        // and deprecate AppPublicKey entirely.
        if !ckd_output_check_legacy(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

Note: because `AppPublicKey` does not supply a G2 component, a direct pairing check equivalent to `AppPublicKeyPV` is not possible without a protocol change. The preferred mitigation is to **deprecate `AppPublicKey` and require all callers to use `AppPublicKeyPV`**, which already has a sound on-chain check. Until migration is complete, `respond_ckd` for `AppPublicKey` requests should at minimum verify that `big_y` and `big_c` are valid, non-identity BLS12-381 G1 points, and consider requiring threshold-many identical responses before resolving.

---

### Proof of Concept

```rust
// Attacker is an attested participant (account: "malicious_node.near")
// User submitted: request_app_private_key({ app_public_key: AppPublicKey(app_pk), ... })

// Attacker chooses known scalars
let y_a: Scalar = Scalar::from(42u64);
let z:   Scalar = Scalar::from(99u64);  // attacker will know the user's derived key = G1*z

let big_y = G1Projective::generator() * y_a;
let big_c = G1Projective::generator() * z + app_pk_point * y_a;

let forged_response = CKDResponse {
    big_y: Bls12381G1PublicKey::from(&big_y),
    big_c: Bls12381G1PublicKey::from(&big_c),
};

// Attacker calls respond_ckd — no on-chain check rejects this
contract.respond_ckd(ckd_request, forged_response).unwrap();
// → pending yield resolved; user receives (big_y, big_c) controlled by attacker
// → user decrypts: sig = big_c - a*big_y = G1*z  (attacker knows z)
```

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates that `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` — completely arbitrary bytes — is accepted without error for an `AppPublicKey` request: [9](#0-8)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L76-102)
```rust
/// Check that `e(big_c, g2) = e(big_y, app_pk2) . e(hash_point, public_key)`.
///
/// Point validation is fully delegated to the host, as in
/// [`app_public_key_check`].
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

**File:** crates/threshold-signatures/docs/confidential_key_derivation/confidential-key-derivation.md (L167-188)
```markdown
  - Node $`i\in \{1, \ldots n\}`$
    - receives $`(\texttt{app\_id}, A)`$
    > **Publicly verifiable variant:** Verifies that $A$ is a valid
    > public key, i.e. $`e(A_1, G_2) = e(G_1, A_2)`$
    - computes:
      - $`y_i  \gets^{\$} \mathbb{Z}_q`$
      - $`Y_i \gets y_i \cdot G_1`$
      - $`S_i = x_i \cdot H(\texttt{\texttt{pk}, app\_id})`$
      - $`C_i =  S_i + y_i \cdot A_1`$
    - sends $`(λ_i \cdot Y_i, λ_i \cdot C_i)`$ to the *MPC network* coordinator
  - The coordinator
    - adds the received pairs together:
      - $`Y \gets λ_1 \cdot Y_1 + \ldots + λ_n \cdot Y_n`$
      - $`C \gets λ_1 \cdot C_1 + \ldots + λ_n \cdot C_n = λ_1 \cdot S_1 + \ldots +
      λ_n \cdot S_n + ({y_1 \cdot λ_1 + \ldots + y_n \cdot λ_n }) \cdot A_1 =
      \texttt{msk} \cdot H(\texttt{pk},\, \texttt{app\_id}) + a \cdot Y`$
      - $`\texttt{es} \gets (Y, C) `$
    > **Publicly verifiable variant:** Verifies that $es$ is a valid
    > encryption of a signature with respect to the MPC network public key
    > $`\texttt{pk}`$, i.e.
    > $`e(C, G_2) = e\bigl(H(\texttt{pk},\, \texttt{app\_id}),\; \texttt{pk}\bigr) \cdot e(Y, A_2)`$
    - sends $`\texttt{es}`$ to *app* on-chain
```

**File:** crates/contract/README.md (L118-121)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
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
