### Title
Missing CKD Response Verification for `AppPublicKey` Variant Allows Single Participant to Deliver Unauthorized Confidential Key Derivation Output — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd()` function in the MPC contract skips all output verification for `CKDAppPublicKey::AppPublicKey` requests. Any single attested participant can race the legitimate threshold computation and deliver a fabricated `CKDResponse` to the user, bypassing the threshold requirement for confidential key derivation.

---

### Finding Description

In `respond_ckd()`, the contract conditionally verifies the CKD output only for the `AppPublicKeyPV` variant: [1](#0-0) 

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no verification at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKey` requests the arm is a no-op. The function then unconditionally calls `resolve_yields_for()`: [2](#0-1) 

`resolve_yields_for()` atomically removes the pending request from the map and resumes every queued yield with the supplied bytes: [3](#0-2) 

Once the first `respond_ckd()` call succeeds, the entry is gone. Any subsequent call — including the legitimate threshold-computed response — returns `RequestNotFound` and is silently discarded.

The `AppPublicKeyPV` variant carries a `{pk1, pk2}` pair that makes the output publicly verifiable on-chain via `ckd_output_check`. The legacy `AppPublicKey` variant carries only a single G1 point, which does not support on-chain verification. The contract README acknowledges this distinction: [4](#0-3) 

However, the absence of on-chain verification is not merely a UX limitation — it removes the only contract-level enforcement of the threshold requirement for this request type.

---

### Impact Explanation

A single malicious attested participant (strictly below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request in the contract's `pending_ckd_requests` map.
2. Immediately call `respond_ckd()` with an arbitrary fabricated `CKDResponse` — no cryptographic proof is required.
3. The contract accepts the response without any check and delivers it to the user via `resolve_yields_for()`.
4. The user's yield-resume callback fires with the fake encrypted key material.
5. The legitimate threshold computation eventually completes, but its `respond_ckd()` call fails with `RequestNotFound` — the request has already been consumed.

The user receives a confidential key that was never computed by the threshold of participants. Because the fake `big_y` / `big_c` values are attacker-controlled, the user's application private key is effectively lost: it is encrypted under a key the attacker chose, not the MPC-derived key.

This satisfies the Critical impact criterion: **unauthorized confidential key derivation output without the required participant authorization**.

---

### Likelihood Explanation

- The attacker must be an attested participant — a legitimate network role, not an external account.
- A single participant suffices; no collusion is required.
- The MPC threshold computation requires multiple protocol rounds (triple generation, presigning, signing). The attacker can submit a fake response in a single NEAR transaction immediately after the request appears on-chain, well before the honest nodes finish.
- The `AppPublicKey` variant is explicitly supported and documented as the "legacy" path, so real users will continue to use it.

Likelihood is **Medium-High**: the attack is straightforward for any participant who turns adversarial, and the timing window is wide.

---

### Recommendation

1. **Preferred**: Deprecate `AppPublicKey` and require all callers to migrate to `AppPublicKeyPV`, which supports on-chain verification via `ckd_output_check`. Gate `respond_ckd()` to reject `AppPublicKey` requests entirely.
2. **Alternative**: If `AppPublicKey` must be retained for backwards compatibility, add a protocol-level commitment (e.g., a hash of the expected output committed at request time) so the contract can verify the response without a full public-verifiability proof.
3. At minimum, document prominently that `AppPublicKey` CKD requests provide **no protection against a malicious participant** and that users should prefer `AppPublicKeyPV`.

---

### Proof of Concept

```
1. User calls request_app_private_key({ app_public_key: AppPublicKey(G1_point), ... })
   → contract stores entry in pending_ckd_requests, parks user's call via yield-resume

2. Malicious participant P (one of n, below threshold t) observes the pending request.

3. P immediately calls respond_ckd(request, CKDResponse { big_y: fake_G1, big_c: fake_G1 })
   → respond_ckd() reaches the match arm for AppPublicKey → no-op (no verification)
   → resolve_yields_for() removes the entry and resumes the user's yield with fake bytes

4. User's yield-resume callback fires → user receives fake { big_y, big_c }

5. Honest nodes finish threshold computation and call respond_ckd() with the real response
   → resolve_yields_for() finds no entry → returns RequestNotFound → response discarded

Result: user holds a confidential key encrypted under attacker-chosen material,
        not the MPC-derived key. Threshold requirement bypassed by a single participant.
``` [5](#0-4) [6](#0-5)

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

**File:** crates/contract/README.md (L280-282)
```markdown
- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
