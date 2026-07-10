### Title
Missing NEAR Contract Account ID in `ForeignTxSignPayload` Message Digest Enables Cross-Deployment Replay — (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

### Summary

`ForeignTxSignPayload::compute_msg_hash()` computes `SHA-256(borsh(ForeignTxSignPayload))` over only `{request, values}`. It omits the NEAR contract account ID, NEAR network ID, and domain ID. A `VerifyForeignTransactionResponse` (threshold signature + payload hash) produced for one contract deployment is cryptographically identical to one that would be accepted by any other deployment sharing the same MPC root key, enabling cross-deployment replay.

### Finding Description

The signed message digest is computed in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`:

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
}
``` [1](#0-0) 

The hash covers only the foreign chain request and extracted values. It does **not** include:
- The NEAR contract account ID (`env::current_account_id()`)
- The NEAR network ID (mainnet vs. testnet)
- The `domain_id` from `VerifyForeignTransactionRequest`

The node-side signing path in `build_signature_request` directly feeds this hash as the payload to the threshold ECDSA signing protocol:

```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    // ...
    Ok(SignatureRequest { payload: Payload::Ecdsa(payload_bytes), ... })
}
``` [2](#0-1) 

On the contract side, `respond_verify_foreign_tx` verifies the signature only against the domain's root public key and the `payload_hash` from the response — with no binding to the contract's own account ID:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
).is_ok()
``` [3](#0-2) 

### Impact Explanation

**High.** During a contract migration where the same MPC key material is temporarily shared across two NEAR account IDs (e.g., `v1.signer` → `v2.signer`), or if the same key is deployed on both testnet and mainnet for testing, a `VerifyForeignTransactionResponse` produced for contract A is byte-for-byte valid on contract B. A Byzantine MPC participant (below threshold) who is an attested participant on both deployments can:

1. Observe a valid on-chain `VerifyForeignTransactionResponse` from contract A (the signature is public).
2. Submit the same `verify_foreign_transaction` request on contract B for the same foreign chain transaction.
3. Call `respond_verify_foreign_tx` on contract B with the replayed response.
4. Contract B accepts it — the signature verifies against the same root key, and the pending request exists.

The downstream consumer (e.g., an Omnibridge contract) receives a `VerifyForeignTransactionResponse` attesting to a foreign chain event that was never independently verified by contract B's MPC nodes, enabling double-spend or invalid bridge execution.

### Likelihood Explanation

**Medium.** The attack requires the same MPC root key to be active on two contract deployments simultaneously. This is a realistic condition during key-preserving contract migrations (e.g., redeployment to a new account ID while the old key is still live), or if testnet and mainnet deployments share key material for integration testing. The attacker only needs to be an attested participant on the target contract — no threshold collusion is required, as the signature is already public on-chain.

### Recommendation

Bind the signed payload to the specific contract instance and network by including the NEAR contract account ID and network ID in `ForeignTxSignPayloadV1`:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub contract_id: String,       // env::current_account_id()
    pub near_network_id: String,   // e.g. "mainnet" or "testnet"
    pub domain_id: u64,
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

The `contract_id` and `near_network_id` must be injected at request-creation time (on the contract side) and included in the Borsh-serialized payload before hashing. This is the direct analog of EIP-712's `chainId` + `verifyingContract` fields.

### Proof of Concept

1. Deploy the MPC contract at `v1.signer.near` (mainnet) and `v2.signer.near` (migration target), both initialized with the same MPC root key.
2. Call `verify_foreign_transaction` on `v1.signer.near` for Bitcoin tx `T` with extractor `BlockHash`.
3. MPC nodes verify `T`, compute `hash = SHA-256(borsh(ForeignTxSignPayload::V1{request: Bitcoin(T), values: [BlockHash(B)]}))`, and submit `respond_verify_foreign_tx` to `v1.signer.near`. The response `(payload_hash, signature)` is now public on-chain.
4. Call `verify_foreign_transaction` on `v2.signer.near` for the same Bitcoin tx `T` — this creates a pending yield.
5. As an attested participant on `v2.signer.near`, call `respond_verify_foreign_tx(request=T, response=(payload_hash, signature))` with the replayed values from step 3.
6. `v2.signer.near` computes `verify_ecdsa_signature(signature, payload_hash, root_pk)` — this passes because `payload_hash` is identical (no contract binding) and `root_pk` is the same key. The yield resolves, returning a valid `VerifyForeignTransactionResponse` to the caller on `v2.signer.near` without any actual foreign chain verification having occurred on that deployment. [4](#0-3) [5](#0-4)

### Citations

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

**File:** crates/contract/src/lib.rs (L692-753)
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
```
