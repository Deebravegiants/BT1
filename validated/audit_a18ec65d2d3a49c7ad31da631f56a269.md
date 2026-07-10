### Title
`respond_verify_foreign_tx` Accepts Attacker-Controlled `payload_hash` Without Binding It to the Pending Request - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_verify_foreign_tx` function verifies that `response.signature` is valid over `response.payload_hash` using the root public key, but never verifies that `response.payload_hash` is the canonical hash of the `ForeignTxSignPayload` derived from the submitted `request`. A single Byzantine attested participant can reuse a valid `(payload_hash, signature)` pair obtained from one foreign-tx verification to resolve a completely different pending request, delivering a forged attestation to the victim caller.

### Finding Description

In `crates/contract/src/lib.rs`, the `respond_verify_foreign_tx` function accepts a `VerifyForeignTransactionResponse` containing two attacker-controlled fields: `payload_hash` and `signature`. The contract performs only one cryptographic check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The contract verifies that `signature` is valid over `payload_hash` using the root public key, but it does **not** verify that `payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload{ request, values }))` for the specific `request` being resolved.

The `ForeignTxSignPayload` is constructed by MPC nodes from the `request` and the extracted `values` (obtained by querying the foreign chain RPC):

```rust
let payload = match payload_version {
    dtos::ForeignTxPayloadVersion::V1 => {
        dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
            request: request.clone(),
            values,
        })
    }
    ...
};
``` [2](#0-1) 

The `payload_hash` is then computed as `SHA-256(borsh(ForeignTxSignPayload))`: [3](#0-2) 

And the signing uses a zero tweak (root key): [4](#0-3) 

Because the contract cannot independently recompute the `payload_hash`

### Citations

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L39-47)
```rust
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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L337-346)
```rust
        let payload = match payload_version {
            dtos::ForeignTxPayloadVersion::V1 => {
                dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
                    request: request.clone(),
                    values,
                })
            }
            _ => bail!("unsupported payload_version"),
        };
        Ok(payload)
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1510)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
}
```
