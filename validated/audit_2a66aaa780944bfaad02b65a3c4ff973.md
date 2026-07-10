### Title
Missing On-Chain Cryptographic Verification of CKD Response for `AppPublicKey` Variant Allows Single Byzantine Participant to Deliver Fabricated Confidential Key — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in the MPC contract performs on-chain cryptographic verification of the CKD response **only** for the `AppPublicKeyPV` (publicly verifiable) variant. For the `AppPublicKey` (privately verifiable, legacy) variant — which is the default and most widely used path — the contract performs **zero verification** of the submitted `CKDResponse`. A single Byzantine attested participant can call `respond_ckd` with the correct pending request key and any fabricated `big_y`/`big_c` values; the contract will accept the response, drain the pending request queue, and deliver the fabricated confidential key to every waiting caller.

---

### Finding Description

In `respond_ckd` at `crates/contract/src/lib.rs` lines 675–682:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO VERIFICATION
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The `AppPublicKeyPV` arm calls `ckd_output_check`, which verifies the response against the master BLS12-381 public key on-chain. The `AppPublicKey` arm is an empty no-op. After this match, the function unconditionally calls `resolve_yields_for`, which removes the request from `pending_ckd_requests` and fans the raw `response` bytes out to every queued yield: [2](#0-1) 

The only guards before this point are:
1. `assert_caller_is_signer()` — caller must be a direct NEAR account, not a contract.
2. `assert_caller_is_attested_participant_and_protocol_active()` — caller must be an attested participant. [3](#0-2) 

Neither guard verifies that the submitted `CKDResponse` (`big_y`, `big_c`) was actually produced by the threshold protocol. The pending request map is public on-chain state; any attested participant can read the `CKDRequest` key (including `app_id` and `domain_id`) and race to call `respond_ckd` with arbitrary values before the legitimate leader does.

The `CKDRequest` struct stores the `app_id` (derived from predecessor and derivation path) and `app_public_key` — all observable on-chain: [4](#0-3) 

The `AppPublicKey` variant is the legacy default, accepted by the contract's `request_app_private_key` entry point without any additional restriction: [5](#0-4) 

The asymmetry is explicit: `AppPublicKeyPV` has both a submission-time pairing check (`app_public_key_check`) and a response-time output check (`ckd_output_check`); `AppPublicKey` has neither at the response stage.

---

### Impact Explanation

**Critical — confidential key derivation output delivered without required threshold-protocol authorization.**

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request on-chain.
2. Call `respond_ckd` with the correct `CKDRequest` key and fabricated `CKDResponse{big_y: [attacker_chosen], big_c: [attacker_chosen]}`.
3. The contract accepts the call, removes the request from `pending_ckd_requests`, and fans the fabricated bytes to every queued yield.
4. Every caller waiting on that request (potentially multiple, due to the fan-out queue) receives the fabricated confidential key.

The requesting TEE application receives a wrong `(big_y, big_c)` pair. If the app does not independently verify the response before use, it will derive a wrong secret — one controlled by the attacker. Even if the app detects the failure, the legitimate pending request has been consumed; the user must pay and resubmit, and the attacker can repeat the attack indefinitely as long as they remain an attested participant.

---

### Likelihood Explanation

- The `AppPublicKey` variant is the legacy default and is the path exercised by the existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists`, which passes an arbitrary `CKDResponse{big_y: [1u8;48], big_c: [2u8;48]}` — demonstrating that the contract accepts any bytes. [6](#0-5) 

- The attacker needs only to be an attested participant — a condition that any node operator who has submitted a valid TEE attestation satisfies, regardless of whether they are in the current signing set.
- The attack is a simple on-chain transaction race; no cryptographic capability is required.
- The fan-out queue means a single fabricated `respond_ckd` call corrupts all duplicate submissions of the same request simultaneously.

---

### Recommendation

Apply the same `ckd_output_check` verification to the `AppPublicKey` arm, or reject `AppPublicKey` requests at the `respond_ckd` level and require migration to `AppPublicKeyPV`. If "privately verifiable" semantics must be preserved (i.e., the contract cannot verify the encryption), introduce a commit-reveal or threshold-vote mechanism so that at least `t` participants must agree on the response before it is delivered, preventing a single Byzantine leader from unilaterally substituting a fabricated value.

---

### Proof of Concept

The existing unit test already demonstrates the absence of verification:

```rust
// crates/contract/src/lib.rs ~line 3424
let response = CKDResponse {
    big_y: dtos::Bls12381G1PublicKey([1u8; 48]),  // arbitrary garbage
    big_c: dtos::Bls12381G1PublicKey([2u8; 48]),  // arbitrary garbage
};
// respond_ckd succeeds with no error
contract.respond_ckd(ckd_request.clone(), response.clone())
    .expect("respond_ckd should not fail");
``` [7](#0-6) 

**Exploit steps on a live network:**

1. Attacker is an attested participant (one node, below threshold).
2. User submits `request_app_private_key` with `AppPublicKey` variant; the `CKDRequest` key appears in `pending_ckd_requests`.
3. Attacker reads the `CKDRequest` from chain state.
4. Attacker calls `respond_ckd(request, CKDResponse{big_y: attacker_point, big_c: attacker_point})` before the legitimate leader.
5. Contract passes all checks (attested participant ✓, request exists ✓, `AppPublicKey` arm → no-op ✓).
6. `resolve_yields_for` drains the queue and delivers the fabricated response to the user.
7. User's TEE application receives a confidential key derived from attacker-chosen values. [8](#0-7)

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

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L77-97)
```rust
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
