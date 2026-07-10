### Title
`ForeignTxSignPayload::compute_msg_hash()` Omits Contract Address and Chain ID, Enabling Cross-Contract Replay of Foreign-Chain Verification Signatures — (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

---

### Summary

`ForeignTxSignPayload::compute_msg_hash()` computes `SHA-256(borsh({request, values}))` without binding the hash to the NEAR contract address, NEAR chain ID, or domain ID. A threshold signature produced for a foreign-chain transaction verification on one MPC contract deployment is therefore cryptographically valid on any other deployment that shares the same key material. A single Byzantine MPC node (below the signing threshold) can replay a previously observed valid `VerifyForeignTransactionResponse` against a different contract instance, causing the new contract to accept a forged foreign-chain verification without the MPC network ever inspecting the transaction on the new contract's behalf.

---

### Finding Description

`ForeignTxSignPayload::compute_msg_hash()` is defined as:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
}
```

The signed hash is `SHA-256(borsh(ForeignTxSignPayload))`. The payload contains only the foreign-chain RPC request and the extracted values. It does **not** include:

- The NEAR contract account ID (`current_account_id`)
- The NEAR chain ID (mainnet vs. testnet)
- The `domain_id` under which the request was submitted [1](#0-0) 

The node-side `build_signature_request()` confirms that the tweak is hardcoded to all-zeros for foreign-tx flows, meaning the root key (not a derived key) signs the hash:

```rust
// crates/node/src/providers/verify_foreign_tx/sign.rs
Ok(SignatureRequest {
    ...
    tweak: Tweak::new([0u8; 32]),   // zero tweak — root key signs
    ...
})
``` [2](#0-1) 

On the contract side, `respond_verify_foreign_tx()` verifies only that the supplied `payload_hash` is signed by the domain's public key. It does **not** recompute the expected hash from the pending request and compare it, nor does it bind the hash to the contract's own identity:

```rust
// crates/contract/src/lib.rs
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,   // taken verbatim from the caller-supplied response
    &secp_pk,
).is_ok()
``` [3](#0-2) 

Because the hash is context-free, any valid `VerifyForeignTransactionResponse` produced for foreign-chain transaction X on contract A is also a valid response for the same transaction X on contract B, provided both contracts share the same domain key.

---

### Impact Explanation

During a contract migration (e.g., from `v1.signer` to `v2.signer`) where key material is preserved and migrated, the following attack is possible:

1. The MPC network legitimately produces a `VerifyForeignTransactionResponse` for Bitcoin tx X on contract A (`v1.signer`). The response is publicly observable on-chain.
2. A Byzantine MPC node (a single node, below the signing threshold) submits `verify_foreign_transaction(bitcoin_tx_X)` to contract B (`v2.signer`) as a regular user, creating a pending request.
3. The same Byzantine node calls `respond_verify_foreign_tx` on contract B with the old response from contract A.
4. The signature verifies: the hash is identical (no contract address in it), and the key is the same (migrated).
5. Contract B resolves the pending request and delivers the `VerifyForeignTransactionResponse` to the caller as if the MPC network had freshly verified the transaction.

A bridge contract consuming this response would accept it as a genuine MPC attestation of Bitcoin tx X on the new contract, enabling double-spend or invalid bridge execution without any fresh foreign-chain inspection.

This matches the **High** allowed impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

The preconditions are:

1. **Same key material across two contract deployments** — This is a realistic scenario during contract migration. The codebase contains explicit migration infrastructure (`crates/contract/src/node_migrations.rs`, `crates/contract/src/v3_12_0_state.rs`), and key shares are designed to be migrated between node instances. A contract account migration that preserves the domain key satisfies this condition.
2. **A Byzantine MPC node below the signing threshold** — The attacker only needs to be an attested participant on the new contract (which any migrated node would be) and to have observed a prior valid response. No threshold collusion is required; a single node can replay an already-produced threshold signature.

The `respond_verify_foreign_tx` entry point is restricted to attested participants, but a single Byzantine node among the participant set satisfies that check.

---

### Recommendation

Include the NEAR contract address (`env::current_account_id()`) and the NEAR chain ID in the signed payload. The `domain_id` should also be bound into the hash to prevent cross-domain replay within the same contract. A `V2` payload variant can be introduced without breaking existing `V1` verifiers:

```rust
pub struct ForeignTxSignPayloadV2 {
    pub contract_id: AccountId,   // env::current_account_id()
    pub chain_id: String,         // "mainnet" | "testnet"
    pub domain_id: DomainId,
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

The `ForeignTxPayloadVersion` enum already supports versioning for exactly this purpose. [4](#0-3) 

---

### Proof of Concept

```
// Setup: two MPC contracts sharing the same Secp256k1 domain key
// (realistic after a contract account migration)
//
// Contract A: v1.signer (old)
// Contract B: v2.signer (new, same key material)

// Step 1 (honest): User submits verify_foreign_transaction(bitcoin_tx_X) to Contract A.
//   MPC network inspects Bitcoin, produces:
//     payload = ForeignTxSignPayload::V1 { request: BitcoinRpcRequest{tx_id: X, ...}, values: [BlockHash(H)] }
//     msg_hash = SHA-256(borsh(payload))   // no contract address!
//     sig = ECDSA_sign(root_key, msg_hash)
//     response_A = VerifyForeignTransactionResponse { payload_hash: msg_hash, signature: sig }
//   response_A is emitted on-chain and is publicly observable.

// Step 2 (attacker — single Byzantine node):
//   Attacker calls verify_foreign_transaction(bitcoin_tx_X) on Contract B as a user.
//   This creates a pending request on Contract B.

// Step 3 (attacker — same Byzantine node, now acting as MPC participant on Contract B):
//   Attacker calls respond_verify_foreign_tx(request_B, response_A) on Contract B.
//
//   Contract B checks:
//     assert_caller_is_attested_participant_and_protocol_active() -> OK (node is migrated)
//     verify_ecdsa_signature(sig, msg_hash, root_key_B) -> OK (same key, same hash)
//     resolve_yields_for(pending_verify_foreign_tx_requests, request_B, response_A) -> OK
//
//   Contract B delivers response_A to the user as a fresh MPC attestation.
//   Bridge contract accepts it and executes the bridge operation — double spend achieved.
``` [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1478-1480)
```rust
pub enum ForeignTxSignPayload {
    V1(ForeignTxSignPayloadV1),
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-47)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
```

**File:** crates/contract/src/lib.rs (L718-753)
```rust
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
```
