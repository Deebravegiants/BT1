### Title
Single Attested Participant Can Deliver Attacker-Controlled Key Material via Unverified `respond_ckd` for `AppPublicKey` Requests — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function performs **no cryptographic verification** of the `CKDResponse` when the pending request uses the `AppPublicKey` (legacy, privately-verifiable) variant. A single attested MPC participant — strictly below the signing threshold — can call `respond_ckd` with an entirely fabricated `(big_c, big_y)` pair, substituting the user's confidential key with a scalar the attacker chose. Because the `AppPublicKey` variant provides no on-chain or off-chain means for the user to verify correctness, the substitution is undetectable and the attacker gains full knowledge of the key the user will use.

---

### Finding Description

In `respond_ckd` the contract branches on the request's `app_public_key` variant:

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
```

For `AppPublicKeyPV` the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(app_id,pk), msk·G2)` is verified on-chain, binding the response to the network's master key and the user's ephemeral key pair. For `AppPublicKey` the arm is empty: **any** `CKDResponse` is accepted and immediately delivered to the user via `resolve_yields_for`.

The `AppPublicKey` variant is still accepted by `request_app_private_key` and is described as the "legacy" path in the README and CKD documentation. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

The CKD scheme encrypts the confidential key `S = H(app_id, pk) · msk` under the user's ephemeral public key `A = a·G₁`:

```
big_c = S + A·y,   big_y = y·G₁
```

The user recovers `S = big_c − a·big_y`.

An attacker who controls one attested participant can instead submit:

```
big_y_fake = y'·G₁,   big_c_fake = s_fake·G₁ + A·y'
```

The user then computes `big_c_fake − a·big_y_fake = s_fake·G₁`, which is the attacker's chosen point. The attacker knows `s_fake` and therefore knows the key the user will use for all subsequent operations (encryption, signing, etc.). Because the `AppPublicKey` variant provides no verification path — neither on-chain nor off-chain — the user cannot distinguish a legitimate response from a substituted one.

This is a **threshold bypass**: the security property that no coalition below the signing threshold can influence the CKD output is violated by a single attested participant. [4](#0-3) [5](#0-4) 

---

### Likelihood Explanation

- **Entry path**: Any attested MPC participant can call `respond_ckd` directly; the only gate is `assert_caller_is_attested_participant_and_protocol_active`.
- **Timing**: The attacker observes a `request_app_private_key` receipt on-chain, skips the threshold computation entirely, and submits `respond_ckd` immediately. Honest nodes must index the request, run the BLS threshold protocol, and then submit — giving the attacker a structural timing advantage.
- **Finality**: `resolve_yields_for` drains the entire yield queue on the first successful `respond_ckd` call. Subsequent honest responses receive `RequestNotFound` and are silently discarded.
- **Persistence**: The user can retry with a new ephemeral key, but the attacker can front-run every retry at negligible cost.
- **Legacy usage**: The `AppPublicKey` variant is still accepted and documented; existing integrations that have not migrated to `AppPublicKeyPV` are fully exposed. [6](#0-5) [7](#0-6) 

---

### Recommendation

1. **Deprecate and gate `AppPublicKey`**: Reject `AppPublicKey` requests at the contract level (or behind a governance flag) and require all callers to use `AppPublicKeyPV`, which has an on-chain pairing check.
2. **If `AppPublicKey` must remain**: Add a threshold-of-votes mechanism analogous to `respond` for signatures — require at least `threshold` attested participants to submit matching `(big_c, big_y)` values before the yield is resumed.
3. **Documentation**: At minimum, prominently document that `AppPublicKey` CKD responses carry no on-chain integrity guarantee and that a single malicious participant can substitute the derived key. [8](#0-7) 

---

### Proof of Concept

```rust
// Attacker is one attested MPC participant.
// Step 1: user submits request_app_private_key with AppPublicKey(A), A = a·G1.
// Step 2: attacker observes the pending CKDRequest on-chain.

// Step 3: attacker crafts a substituted response.
let s_fake   = Scalar::random(&mut rng);          // attacker-chosen scalar
let big_s_fake = G1Projective::generator() * s_fake;
let y_fake   = Scalar::random(&mut rng);
let big_y_fake = G1Projective::generator() * y_fake;
let big_c_fake = big_s_fake + app_pk_g1 * y_fake; // app_pk_g1 = A = a·G1

let fabricated = CKDResponse {
    big_y: Bls12381G1PublicKey::from(&big_y_fake),
    big_c: Bls12381G1PublicKey::from(&big_c_fake),
};

// Step 4: attacker calls respond_ckd — accepted with no verification.
contract.respond_ckd(ckd_request, fabricated);
// resolve_yields_for drains the queue; honest nodes' later calls get RequestNotFound.

// Step 5: user decrypts  big_c_fake − a·big_y_fake = big_s_fake = s_fake·G1.
// Attacker knows s_fake and therefore controls the user's confidential key.
```

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates that arbitrary `[1u8;48]` / `[2u8;48]` byte arrays are accepted as a valid `CKDResponse` for an `AppPublicKey` request, confirming the absence of any response check. [9](#0-8)

### Citations

**File:** crates/contract/src/lib.rs (L469-512)
```rust
    pub fn request_app_private_key(&mut self, request: CKDRequestArgs) {
        log!(
            "request_app_private_key: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        let domain_id: DomainId = request.domain_id;
        let (_, predecessor) = self.check_request_preconditions(
            domain_id,
            DomainPurpose::CKD,
            Gas::from_tgas(self.config.ckd_call_gas_attachment_requirement_tera_gas),
            MINIMUM_CKD_REQUEST_DEPOSIT,
        );

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
        }

        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_ck_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_ckd_request(request, id),
        );
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

**File:** crates/contract/src/primitives/ckd.rs (L1-31)
```rust
use blstrs::G1Projective;
use near_account_id::AccountId;
use near_mpc_contract_interface::types as dtos;
use near_mpc_contract_interface::types::kdf::derive_app_id;
use near_mpc_contract_interface::types::{CKDResponse, DomainId};
use near_sdk::{env, near};

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
#[near(serializers=[borsh, json])]
pub struct CKDRequest {
    /// The app ephemeral public key
    pub app_public_key: dtos::CKDAppPublicKey,
    pub app_id: dtos::CkdAppId,
    pub domain_id: DomainId,
}

impl CKDRequest {
    pub fn new(
        app_public_key: dtos::CKDAppPublicKey,
        domain_id: DomainId,
        predecessor_id: &AccountId,
        derivation_path: &str,
    ) -> Self {
        let app_id = derive_app_id(predecessor_id, derivation_path);
        Self {
            app_public_key,
            app_id,
            domain_id,
        }
    }
}
```

**File:** crates/contract/src/primitives/ckd.rs (L56-74)
```rust
/// Check that `e(app_pk1, g2) = e(g1, app_pk2)`.
///
/// Point validation is fully delegated to the host: the decompression
/// functions abort execution on malformed or off-curve encodings, and
/// `bls12381_pairing_check` returns `false` when a point is outside its
/// prime-order subgroup.
pub(crate) fn app_public_key_check(app_public_key: &dtos::CKDAppPublicKeyPV) -> bool {
    let pk1 = env::bls12381_p1_decompress(&app_public_key.pk1);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);

    let pairing_input = [
        pk1.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        G1_GENERATOR_UNCOMPRESSED.as_slice(),
        pk2.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
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

**File:** crates/contract/src/pending_requests.rs (L62-88)
```rust
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
