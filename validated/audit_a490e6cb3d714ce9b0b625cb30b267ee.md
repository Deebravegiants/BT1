### Title
Unbound `payload_hash` in `respond_verify_foreign_tx` Enables Single-Node Cross-Request Replay of Foreign-Chain Verification Signatures - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` using the MPC root public key, but it never verifies that `response.payload_hash` was actually derived from the `request` parameter supplied in the same call. A single attested MPC participant (below the signing threshold) can replay any previously issued foreign-chain verification signature — produced legitimately by the full threshold for a different transaction — to satisfy an unrelated pending `verify_foreign_transaction` request. The caller's contract receives a `VerifyForeignTransactionResponse` that cryptographically attests to a different foreign-chain transaction than the one it submitted.

---

### Finding Description

**Root cause — missing binding between `request` and `response.payload_hash`**

In `respond_verify_foreign_tx` the contract performs two independent checks and then resolves all queued yields:

```rust
// crates/contract/src/lib.rs  lines 718–753
let signature_is_valid = match (&response.signature, public_key) {
    (Secp256k1(sig), Secp256k1 { near_public_key }) => {
        let secp_pk = ...;
        let payload_hash: [u8; 32] = response.payload_hash.0;
        // Check the signature is correct against the root public key
        near_mpc_signature_verifier::verify_ecdsa_signature(sig, &payload_hash, &secp_pk).is_ok()
    }
    ...
};
if !signature_is_valid { return Err(RespondError::InvalidSignature.into()); }

pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [1](#0-0) 

The contract verifies:
1. `response.signature` is a valid ECDSA signature over `response.payload_hash` using the root key.
2. A pending entry for `request` exists in `pending_verify_foreign_tx_requests`.

It does **not** verify that `response.payload_hash == SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values: ... }))`. The `payload_hash` is accepted as-is from the caller.

**What `payload_hash` should be**

Per the design documentation, the hash the MPC nodes sign is:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload::V1 { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> }))
``` [2](#0-1) 

The `ForeignChainRpcRequest` embedded in `ForeignTxSignPayload` must match the `request.request` field of the pending `VerifyForeignTransactionRequest`. The contract never enforces this.

**`VerifyForeignTransactionRequest` has no caller binding**

Unlike `SignatureRequest` (which embeds a `tweak` derived from `predecessor_id + path`), `VerifyForeignTransactionRequest` contains only `{request, domain_id, payload_version}` — no caller identity, no per-request nonce. [3](#0-2) 

The contract itself acknowledges this is intentional (caller-agnostic fan-out): [4](#0-3) 

**Exploit path (single malicious attested participant, below threshold)**

1. The MPC network legitimately processes `verify_foreign_transaction(bitcoin_tx_id=Y)` and the threshold of nodes cooperate to produce `response_Y = {payload_hash: H_Y, signature: sig_Y}`. This response is broadcast on-chain via `respond_verify_foreign_tx`.

2. Later, a bridge contract submits `verify_foreign_transaction(bitcoin_tx_id=X)` — a different transaction (e.g., a deposit the bridge needs to unlock funds for).

3. A single malicious attested MPC participant calls:
   ```
   respond_verify_foreign_tx(
       request = VerifyForeignTransactionRequest { request: bitcoin_tx_id=X, ... },
       response = { payload_hash: H_Y, signature: sig_Y }   // ← replayed from tx Y
   )
   ```

4. The contract checks: is `sig_Y` a valid ECDSA signature over `H_Y` using the root key? **Yes** — it was legitimately produced by the threshold. The check passes.

5. `resolve_yields_for` drains the queue for `bitcoin_tx_id=X` and delivers `{payload_hash: H_Y, signature: sig_Y}` to every caller waiting on that request.

6. The bridge contract receives a `VerifyForeignTransactionResponse` that carries a valid MPC signature, but the `payload_hash` attests to transaction Y, not X. If the bridge contract trusts the signature without independently recomputing the expected `payload_hash` from the transaction it submitted, it will unlock funds for a transaction that was never verified.

**Why one node is sufficient**

Producing a new threshold signature requires cooperation of ≥ threshold nodes. But *replaying* an existing threshold signature requires only one node: any participant who observed a previous `respond_verify_foreign_tx` call on-chain (all on-chain transactions are public) can extract `{payload_hash, signature}` and reuse it. The contract's only guard is `assert_caller_is_attested_participant_and_protocol_active()`, which is satisfied by any single active participant. [5](#0-4) 

---

### Impact Explanation

A single Byzantine MPC participant (strictly below the signing threshold) can cause the contract to deliver a cryptographically valid but semantically incorrect `VerifyForeignTransactionResponse` to any pending `verify_foreign_transaction` caller. The response carries a real MPC signature, but it attests to a different foreign-chain transaction than the one the caller submitted. Bridge contracts or other on-chain consumers that rely on this attestation to authorize fund releases or state transitions can be deceived into executing against an unverified (or already-processed) foreign transaction. This constitutes **forged foreign-chain verification** and enables **double-spend or invalid bridge execution** conditions.

Severity: **High** — matches the allowed impact "Cross-chain replay, forged foreign-chain verification, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."

---

### Likelihood Explanation

- Any single attested MPC participant can execute this attack; no threshold collusion is required.
- All `respond_verify_foreign_tx` calls are public on-chain; the attacker only needs to observe a previous legitimate response.
- The attack is silent: the contract emits no error, the signature is cryptographically valid, and the caller has no on-chain mechanism to distinguish a replayed response from a fresh one unless it independently recomputes the expected `payload_hash`.
- The `verify_foreign_transaction` use case (Omnibridge inbound flow) is explicitly the primary production use case, making this a realistic attack surface. [6](#0-5) 

---

### Recommendation

In `respond_verify_foreign_tx`, after verifying the signature, recompute the expected `payload_hash` from `request.request` and the extracted values embedded in the response, and assert it equals `response.payload_hash`. Concretely:

1. Include the `ForeignChainRpcRequest` (from `request.request`) in the on-chain hash recomputation, or
2. Require the responder to also supply the `Vec<ExtractedValue>` so the contract can compute `SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values }))` and compare it to `response.payload_hash`.

This binds the `payload_hash` to the specific pending request, closing the replay window. The analog fix in the reference report was adding a `messageInProgressLocker` modifier; here the equivalent is enforcing `payload_hash` ↔ `request` binding before resolving yields.

---

### Proof of Concept

```
// State before attack:
// - MPC network previously processed verify_foreign_transaction(bitcoin_tx_id=Y)
// - On-chain: respond_verify_foreign_tx was called with
//     request = { request: Bitcoin(tx_id=Y), domain_id=D, payload_version=V1 }
//     response = { payload_hash: H_Y, signature: sig_Y }
//   where H_Y = SHA-256(borsh(ForeignTxSignPayload::V1 { request: Bitcoin(tx_id=Y), values: [...] }))
//   and sig_Y = valid threshold ECDSA signature over H_Y using root key

// Attack:
// 1. Bridge contract submits:
contract.verify_foreign_transaction({
    request: Bitcoin(tx_id=X),   // ← different transaction
    domain_id: D,
    payload_version: V1,
})
// → pending entry created for key K_X = { request: Bitcoin(tx_id=X), domain_id: D, payload_version: V1 }

// 2. Single malicious attested participant calls:
contract.respond_verify_foreign_tx(
    request = { request: Bitcoin(tx_id=X), domain_id: D, payload_version: V1 },  // ← K_X
    response = { payload_hash: H_Y, signature: sig_Y }  // ← replayed from tx Y
)

// 3. Contract checks:
//    verify_ecdsa_signature(sig_Y, H_Y, root_pk) → OK  (legitimate threshold sig)
//    pending_verify_foreign_tx_requests.remove(K_X) → resolves bridge contract's yield

// 4. Bridge contract receives { payload_hash: H_Y, signature: sig_Y }
//    If bridge checks only "is signature valid over payload_hash?" → YES → unlocks funds for X
//    But the attestation is for Y, not X.
``` [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L692-754)
```rust
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
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

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/src/lib.rs (L3255-3263)
```rust
        // Then: both yields are queued under the single (caller-agnostic) request key.
        assert_eq!(
            contract
                .pending_verify_foreign_tx_requests
                .get(&request)
                .map(|q| q.len()),
            Some(2),
            "duplicate foreign-tx requests from different callers should fan out",
        );
```

**File:** docs/foreign-chain-transactions.md (L7-10)
```markdown
This feature lets the MPC network sign payloads only after verifying a specific foreign-chain transaction, so NEAR contracts can react to external chain events without a trusted relayer. Primary use cases:

* Omnibridge inbound flow (foreign chain -> NEAR) where Chain Signatures are required to attest that a foreign transaction finalized successfully.
* Broader chain abstraction: a single MPC network verifies foreign chain state and returns small, typed observations that contracts can interpret.
```

**File:** docs/foreign-chain-transactions.md (L182-189)
```markdown
The 32-byte `msg_hash` that nodes sign is computed as:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```

Callers select the payload version via `VerifyForeignTransactionRequestArgs::payload_version`.
Borsh field ordering is stability-critical — fields and enum variants must never be reordered.
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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
