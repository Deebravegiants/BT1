### Title
Missing Contract Account ID in `ForeignTxSignPayload::compute_msg_hash` Enables Cross-Deployment Signature Replay - (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

---

### Summary

`ForeignTxSignPayload::compute_msg_hash()` computes `SHA-256(borsh(ForeignTxSignPayload))` over only `(ForeignChainRpcRequest, Vec<ExtractedValue>)`. It omits any deployment-specific context — specifically the NEAR contract account ID. This is the direct analog of the Biconomy `getHash` missing `chainId`: a `VerifyForeignTransactionResponse` (payload hash + ECDSA signature) produced by the MPC network for one contract deployment is cryptographically identical to a valid response for the same foreign transaction on any other deployment sharing the same MPC key, enabling cross-deployment replay that causes the bridge contract to accept a foreign-chain attestation that the target deployment's MPC nodes never performed.

---

### Finding Description

`ForeignTxSignPayload::compute_msg_hash` is defined as:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:1504-1509
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
}
```

The serialized struct contains only:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:1499-1502
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,  // chain type + tx_id + extractors
    pub values: Vec<ExtractedValue>,      // extracted on-chain values
}
```

No NEAR contract account ID, no network identifier, no domain ID, no nonce. The design document confirms this explicitly:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```

The `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs` (lines 718–734) verifies only that the submitted `response.payload_hash` carries a valid MPC signature — it does not re-derive the hash from the pending request to confirm they match:

```rust
// crates/contract/src/lib.rs:726-734
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
```

The `ForeignChainSignatureVerifier::verify_signature` in the SDK (`crates/near-mpc-sdk/src/foreign_chain.rs`, lines 48–88) reconstructs the expected hash from `(request, expected_extracted_values)` and checks `expected_payload_hash == response.payload_hash`. Because the hash is deployment-agnostic, this check passes identically on any deployment that shares the same MPC key and receives the same `(request, values)` pair.

---

### Impact Explanation

**Cross-deployment replay of foreign-chain attestations.**

Scenario: the NEAR MPC contract is deployed on both mainnet (`v1.signer.near`) and testnet (`v1.signer.testnet`) with the same MPC key (realistic during migration, key resharing, or if the same MPC network serves multiple contracts).

1. Attacker submits `verify_foreign_transaction` for Bitcoin tx X on **testnet**.
2. Testnet MPC nodes verify X and sign `H_X = SHA-256(borsh(V1 { request: Bitcoin(X), values: [BlockHash=H] }))`.
3. Attacker obtains `{payload_hash: H_X, signature: sig(H_X)}`.
4. Attacker submits `verify_foreign_transaction` for the same Bitcoin tx X on **mainnet**.
5. Attacker (as an attested participant on mainnet) calls `respond_verify_foreign_tx(request=X, response={payload_hash: H_X, signature: sig(H_X)})` on mainnet.
6. Mainnet contract: `sig(H_X)` is valid over `H_X` under the shared public key → **accepted**.
7. The mainnet bridge contract's SDK verifier reconstructs `expected_hash_X` from `(Bitcoin(X), [BlockHash=H])` → equals `H_X` → **passes**.
8. The bridge contract releases mainnet funds for a transaction that **mainnet MPC nodes never verified**.

The mainnet MPC nodes are bypassed entirely. The bridge contract cannot distinguish a genuine mainnet attestation from a replayed testnet one.

---

### Likelihood Explanation

The precondition is that the same MPC key is used across two deployments. This occurs during:
- Key migration / resharing where the old key is temporarily active on both environments.
- A single MPC operator network serving multiple NEAR contracts (e.g., a bridge contract and a general-purpose signing contract) with the same domain key.
- Testnet deployments that reuse mainnet key material for integration testing.

The attacker must also be an attested participant on the target deployment (required by `assert_caller_is_attested_participant_and_protocol_active`), which is a single-node capability — strictly below the signing threshold. No threshold collusion is required.

---

### Recommendation

Include the NEAR contract account ID (and optionally the domain ID) in the signed payload hash to make it deployment-specific. The simplest fix is to add a `contract_id` field to `ForeignTxSignPayloadV1`, populated at request time from `env::current_account_id()` in the contract, before the hash is computed:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub contract_id: AccountId,   // <-- add: env::current_account_id()
    pub domain_id: DomainId,      // <-- add: domain_id from the request
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

Alternatively, the contract can compute the hash itself (where `env::current_account_id()` is available) and pass it to the node, rather than having the node compute it from the interface crate. Either way, the Borsh field ordering must be preserved for existing verifiers, so a new `V2` variant should be introduced.

---

### Proof of Concept

Root cause — hash excludes contract identity: [1](#0-0) 

Signed struct fields — no contract account ID, no network ID: [2](#0-1) 

`respond_verify_foreign_tx` verifies signature over caller-supplied `payload_hash` without re-deriving it from the pending request: [3](#0-2) 

SDK verifier reconstructs expected hash from `(request, values)` — passes identically on any deployment with the same key and same inputs: [4](#0-3) 

Design doc confirming the hash formula contains no deployment context: [5](#0-4)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/contract/src/lib.rs (L718-734)
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
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L48-64)
```rust
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
```

**File:** docs/foreign-chain-transactions.md (L182-186)
```markdown
The 32-byte `msg_hash` that nodes sign is computed as:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```
```
