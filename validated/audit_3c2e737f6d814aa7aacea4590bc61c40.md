### Title
Single Malicious Participant Can Forge CKD Output for `AppPublicKey` Requests — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in the MPC contract skips all cryptographic output verification when the user's request uses the `AppPublicKey` variant of `CKDAppPublicKey`. A single Byzantine attested participant (strictly below the signing threshold) can race honest nodes, submit an arbitrary `CKDResponse`, and cause the contract to resolve the user's yield with a forged key-derivation output that the attacker fully controls.

---

### Finding Description

`respond_ckd` (lines 653–689 of `crates/contract/src/lib.rs`) contains the following branch:

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

For the `AppPublicKeyPV` variant the contract calls `ckd_output_check`, which performs a BLS12-381 pairing check:

```
e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)
```

This is a zero-knowledge proof that `big_c` and `big_y` were produced by the threshold CKD protocol using the network's master secret key. [2](#0-1) 

For the `AppPublicKey` variant **no analogous check exists**. The contract unconditionally accepts whatever `CKDResponse { big_c, big_y }` the caller supplies and immediately resolves every queued yield for that request:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [3](#0-2) 

`resolve_yields_for` drains the **entire** fan-out queue in one call, so the first `respond_ckd` that arrives wins and all subsequent honest-node responses are rejected with `RequestNotFound`. [4](#0-3) 

The only gate in front of `respond_ckd` is `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to be a single attested participant — not a threshold quorum. [5](#0-4) 

---

### Impact Explanation

The CKD output `(big_c, big_y)` is used by the requester to derive their application private key. Concretely, the user computes:

```
derived_key_point = big_c − big_y · app_scalar
                  = hash_point · msk   (honest case)
```

An attacker who controls `(big_c, big_y)` can substitute any scalar `msk_fake` they know:

```
big_y_fake = g1 · r          (r chosen by attacker)
big_c_fake = hash_point · msk_fake + app_pk1 · r
```

The user then derives `hash_point · msk_fake`, a point the attacker already knows. The attacker therefore learns the user's derived key material without threshold cooperation. This constitutes **unauthorized confidential key derivation output** — the attacker obtains the same secret the user believes only the threshold network can produce.

Impact maps to: **Critical — confidential key derivation output without the required participant authorization.**

---

### Likelihood Explanation

- The attacker needs only to be **one** attested participant (strictly below threshold).
- The `request_app_private_key` call and its arguments are public on-chain; the attacker can reconstruct the exact `CKDRequest` key deterministically from the emitted transaction.
- The attacker simply submits `respond_ckd` with crafted `big_c`/`big_y` before honest nodes respond. No special timing or network access beyond normal NEAR RPC is required.
- The `AppPublicKey` variant is a documented, production-facing API path (it is accepted by `request_app_private_key` and exercised in contract tests).

---

### Recommendation

Require a threshold-quorum commitment before resolving `AppPublicKey` CKD yields. Two concrete options:

1. **Require `AppPublicKeyPV` for all CKD requests** — remove the `AppPublicKey` variant from the public API so every request carries the pairing-verifiable key pair and `ckd_output_check` is always enforced.
2. **Accumulate votes** — store `respond_ckd` submissions in a per-request vote map (keyed by `(request, response_hash)`) and resolve the yield only when a threshold number of distinct attested participants have submitted the identical response, mirroring the `vote_pk` / `vote_reshared` pattern used elsewhere in the contract.

---

### Proof of Concept

1. Honest user calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(g1 * app_scalar)` on domain `D`.
2. The contract stores the yield index under the deterministic `CKDRequest` key and emits the transaction on-chain.
3. Malicious attested participant `M` reads the transaction, reconstructs the identical `CKDRequest` struct, and picks arbitrary `r` and `msk_fake`.
4. `M` calls `respond_ckd(request, CKDResponse { big_y: g1*r, big_c: hash_point*msk_fake + app_pk1*r })`.
5. The contract's `AppPublicKey` branch executes the empty arm — no check — and calls `resolve_yields_for`, draining the queue and resuming the user's yield with the forged response.
6. Honest nodes' subsequent `respond_ckd` calls return `RequestNotFound` and are silently discarded.
7. The user receives `(big_c_fake, big_y_fake)` and derives `hash_point · msk_fake` — a key the attacker already knows — believing it to be their legitimate MPC-derived application key. [6](#0-5)

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
