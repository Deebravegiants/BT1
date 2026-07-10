### Title
Forged Foreign-Chain Verification via Compromised RPC Provider — (File: `crates/node/src/providers/verify_foreign_tx/sign.rs`)

### Summary

The `verify_foreign_transaction` flow signs a payload that includes `ExtractedValue`s fetched from external RPC providers after the user's on-chain confirmation, with no cross-node consensus and no on-chain validation of the extracted values. A compromised RPC provider — deterministically selected and shared by all MPC nodes — can cause the entire MPC network to produce a valid threshold signature over attacker-controlled foreign-chain state, enabling invalid bridge execution.

### Finding Description

The `verify_foreign_transaction` flow is a direct analog to the Uniswap wallet's `populateTransaction` vulnerability: a user submits a request (the "confirmation"), external data is then fetched from a remote server and used to populate the signed payload, and the user has no mechanism to re-validate the externally-sourced data before the signature is produced.

**Step 1 — User confirmation.** A caller submits `verify_foreign_transaction(request)` to the contract, specifying `tx_id`, `extractors`, `finality`, and `domain_id`. This is the user's only confirmation step. [1](#0-0) 

**Step 2 — External data populates the signed payload.** Each MPC node independently calls `execute_foreign_chain_request`, which queries an external RPC provider and returns `ExtractedValue`s. These values are then hashed together with the original request to form the `msg_hash` that is actually signed. [2](#0-1) [3](#0-2) 

The signed payload is `SHA-256(borsh(ForeignTxSignPayload{request, values}))` where `values` comes entirely from the external RPC: [4](#0-3) 

**Step 3 — Contract accepts any valid signature over any `payload_hash`.** The `respond_verify_foreign_tx` function verifies only that the ECDSA signature is valid against `response.payload_hash`. It does **not** verify that `response.payload_hash` is the hash of a `ForeignTxSignPayload` whose `request` field matches the pending `VerifyForeignTransactionRequest`, and it has no knowledge of what `ExtractedValue`s were signed. [5](#0-4) 

**Step 4 — All nodes use the same deterministically-selected RPC provider.** The design explicitly states that nodes do not choose their own RPC URL; they deterministically select from the on-chain foreign-chain configuration. This means a single compromised provider affects all nodes identically. [6](#0-5) 

**Step 5 — No cross-node consensus on extracted values.** Both the leader and follower paths independently call `execute_foreign_chain_request` and compute their own `msg_hash` from the RPC response. There is no protocol step where nodes broadcast and agree on the extracted values before signing. [7](#0-6) 

### Impact Explanation

A compromised RPC provider can serve attacker-controlled `ExtractedValue`s to all MPC nodes. Because all nodes deterministically select the same provider, they all compute the same attacker-controlled `msg_hash` and cooperate to produce a valid threshold signature over it. The contract's `respond_verify_foreign_tx` accepts the response because the signature is cryptographically valid. The caller (e.g., an Omnibridge contract) receives a `VerifyForeignTransactionResponse` containing a valid MPC signature over false foreign-chain state — for example, attesting that a deposit occurred when it did not, or attesting a fraudulent block hash. This enables invalid bridge execution and potential theft of bridged funds.

This maps to the allowed impact: **High — forged foreign-chain verification that causes invalid bridge execution.**

### Likelihood Explanation

RPC providers are a well-known attack surface. The on-chain foreign-chain configuration lists a bounded set of allowed providers; compromising or bribing a single listed provider is sufficient. The attack requires no threshold collusion among MPC nodes — all nodes are honest but all query the same compromised provider. The attacker-controlled entry path is the RPC JSON-RPC response, which is entirely external input to the MPC node's `execute_foreign_chain_request` function.

### Recommendation

**Short term:** In `respond_verify_foreign_tx`, require the responding node to submit the full `ForeignTxSignPayload` (or at minimum a commitment to the `request` field), and verify on-chain that the `request` field of the submitted payload matches the pending `VerifyForeignTransactionRequest`. This prevents signing a payload for a completely different request. For the `values` portion, add a cross-node consensus round: before signing, the leader broadcasts its extracted values to all participants, and followers verify their locally-extracted values match before contributing their signature share.

**Long term:** Require multiple independent RPC providers per chain in the on-chain configuration and mandate that nodes query at least a quorum of them, refusing to sign if results diverge. This is the direct analog to the external report's recommendation to hard-code baseline data and warn users if remote data deviates significantly.

### Proof of Concept

1. Attacker controls or compromises the RPC provider listed in the on-chain foreign-chain configuration for Bitcoin.
2. A bridge contract calls `verify_foreign_transaction` with `BitcoinRpcRequest{tx_id: <real_tx>, confirmations: 6, extractors: [BlockHash]}`.
3. All MPC nodes call `execute_foreign_chain_request` → `inspector.extract(...)` → the compromised RPC returns `BlockHash([0xff; 32])` (attacker-chosen value) instead of the real block hash.
4. All nodes compute `msg_hash = SHA-256(borsh(ForeignTxSignPayloadV1{request: <real_request>, values: [BlockHash([0xff; 32])]}))` and cooperate to produce a valid threshold signature.
5. The leader calls `respond_verify_foreign_tx(request, VerifyForeignTransactionResponse{payload_hash: <attacker_hash>, signature: <valid_sig>})`.
6. The contract verifies the signature is valid against `payload_hash` — it is — and resolves the yield, returning the response to the bridge contract.
7. The bridge contract receives a valid MPC-signed attestation of false foreign-chain state and processes a fraudulent cross-chain transfer. [8](#0-7) [9](#0-8)

### Citations

**File:** crates/contract/src/lib.rs (L519-557)
```rust
    pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
        log!(
            "verify_foreign_transaction: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
    }
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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
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
}
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L73-86)
```rust
        let response_payload = self
            .execute_foreign_chain_request(
                &foreign_tx_request.request,
                foreign_tx_request.payload_version,
            )
            .await?;

        let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

        let response = self
            .ecdsa_signature_provider
            .make_signature_leader_given_parameters(sign_request, presignature, channel)
            .await?;
        Ok(((response_payload, response.0), response.1))
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L103-114)
```rust
        let response_payload = self
            .execute_foreign_chain_request(
                &foreign_tx_request.request,
                foreign_tx_request.payload_version,
            )
            .await?;

        let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

        self.ecdsa_signature_provider
            .make_signature_follower_given_request(channel, presignature_id, sign_request)
            .await
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L117-150)
```rust
    async fn execute_foreign_chain_request(
        &self,
        request: &dtos::ForeignChainRpcRequest,
        payload_version: dtos::ForeignTxPayloadVersion,
    ) -> anyhow::Result<dtos::ForeignTxSignPayload> {
        chain_is_supported(&self.foreign_chain_policy_reader, request).await?;

        let values: Vec<dtos::ExtractedValue> = match request {
            dtos::ForeignChainRpcRequest::Ethereum(_request) => {
                bail!("ForeignChainRpcRequest::Ethereum is unsupported")
            }
            dtos::ForeignChainRpcRequest::Solana(_request) => {
                bail!("ForeignChainRpcRequest::Solana is unsupported")
            }
            dtos::ForeignChainRpcRequest::Bitcoin(request) => {
                let inspector = self
                    .inspectors
                    .bitcoin
                    .as_ref()
                    .context("no inspector configured for bitcoin")?;
                let transaction_id = request.tx_id.0.into();
                let block_confirmations = request.confirmations.0.into();
                let extractors: Vec<BitcoinExtractor> = request
                    .extractors
                    .iter()
                    .cloned()
                    .map(TryInto::try_into)
                    .collect::<Result<_, _>>()?;
                let extracted_values = inspector
                    .extract(transaction_id, block_confirmations, extractors)
                    .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
                    .await
                    .context("timed out during execution of foreign chain request")??;
                extracted_values.into_iter().map(Into::into).collect()
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

**File:** docs/foreign-chain-transactions.md (L36-36)
```markdown
* **Provider selection**: The request does **not** specify an RPC URL. Nodes deterministically select an allowed provider from the on-chain foreign-chain configurations.
```
