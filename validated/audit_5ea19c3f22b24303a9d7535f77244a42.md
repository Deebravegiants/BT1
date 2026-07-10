### Title
Missing Zero-Value Validation for `BlockConfirmations` Bypasses Bitcoin Finality Check - (File: `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

### Summary

The `verify_foreign_transaction` contract entry point accepts a caller-supplied `BlockConfirmations(0)` for Bitcoin requests without any minimum-value enforcement. Because the inspector's finality check is `block_confirmations_threshold <= transaction_block_confirmation`, a threshold of `0` is always satisfied — including for unconfirmed mempool transactions that return `confirmations: 0` from `getrawtransaction`. The MPC network will therefore sign a foreign-tx payload attesting to a Bitcoin transaction that has never been included in a block, enabling a bridge double-spend.

### Finding Description

`BlockConfirmations` is defined as a plain `u64` newtype with no minimum constraint: [1](#0-0) 

The contract's `verify_foreign_transaction` entry point performs no validation on the `confirmations` field — it only checks that the chain is whitelisted and that gas/deposit preconditions are met: [2](#0-1) 

The node-side inspector then evaluates finality with a simple `<=` comparison: [3](#0-2) 

When `block_confirmations_threshold = 0`, the expression `0 <= transaction_block_confirmation` is unconditionally `true` for any `u64` value returned by the RPC, including `0` (the value Bitcoin's `getrawtransaction` returns for mempool-only, unconfirmed transactions). The canonical-chain check that follows (`verify_block_is_canonical`) is also skipped for unconfirmed transactions because they have no `blockhash` to verify against. [4](#0-3) 

The signed payload is then submitted to the contract via `respond_verify_foreign_tx`, which verifies only the ECDSA signature against the MPC root key — it does not re-examine the `confirmations` value embedded in the request: [5](#0-4) 

### Impact Explanation

An attacker who controls a bridge or omnibridge inbound flow can:

1. Broadcast a Bitcoin transaction to the mempool (no mining required).
2. Submit `verify_foreign_transaction` with `confirmations: 0` and that transaction ID.
3. MPC nodes call `getrawtransaction`; the mempool transaction is found with `confirmations: 0`; the check `0 <= 0` passes.
4. The MPC network signs and returns a `VerifyForeignTransactionResponse` attesting the transaction is "verified."
5. The attacker redeems the NEAR-side bridge payout using the valid MPC signature.
6. The attacker then double-spends or simply never confirms the Bitcoin transaction.

This is a **High** impact finding: forged foreign-chain verification that causes invalid bridge execution and double-spend conditions, matching the allowed impact scope.

### Likelihood Explanation

The entry point is fully permissionless — any account can call `verify_foreign_transaction` with a deposit of 1 yoctoNEAR. No privileged role, threshold collusion, or TEE compromise is required. The only prerequisite is a Bitcoin transaction visible in any node's mempool, which costs only a standard Bitcoin transaction fee and can be double-spent immediately after the NEAR-side payout is received.

### Recommendation

1. **Enforce a minimum of 1 confirmation at the contract level.** Reject any `BitcoinRpcRequest` where `confirmations.0 == 0` inside `verify_foreign_transaction` before the request is queued.
2. **Enforce a protocol-level minimum in the inspector.** Add a guard at the top of `BitcoinInspector::extract` that returns `Err(ForeignChainInspectionError::NotEnoughBlockConfirmations)` immediately when `block_confirmations_threshold.0 == 0`.
3. **Consider a governance-enforced minimum per chain.** Store a per-chain minimum confirmation count in the on-chain `ForeignChainRpcWhitelist` so operators cannot accidentally configure zero.

### Proof of Concept

```rust
// Attacker broadcasts a Bitcoin tx to the mempool, then calls:
let request_args = VerifyForeignTransactionRequestArgs {
    domain_id: foreign_tx_domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: BitcoinTxId(attacker_mempool_tx_hash),
        confirmations: BlockConfirmations(0), // zero — bypasses finality check
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
};
// Contract accepts the request (no confirmations validation).
// MPC nodes call getrawtransaction; mempool tx returns confirmations=0.
// Inspector check: 0 <= 0 → true → finality "passed".
// MPC signs the payload; attacker redeems on NEAR; double-spends Bitcoin.
```

The inspector comparison at `crates/foreign-chain-inspector/src/bitcoin/inspector.rs` line 52 (`block_confirmations_threshold <= transaction_block_confirmation`) is the necessary vulnerable step: with a caller-supplied threshold of `0`, it can never reject any transaction, confirmed or not. [6](#0-5)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
pub struct BlockConfirmations(pub u64);
```

**File:** crates/contract/src/lib.rs (L519-556)
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

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L33-70)
```rust
    async fn extract(
        &self,
        transaction: BitcoinTransactionHash,
        block_confirmations_threshold: BlockConfirmations,
        extractors: Vec<BitcoinExtractor>,
    ) -> Result<Vec<BitcoinExtractedValue>, ForeignChainInspectionError> {
        let request_parameters = GetRawTransactionArgs {
            transaction_hash: TransportBitcoinTransactionHash::from(*transaction),
            verbose: VERBOSE_RESPONSE,
        };

        // TODO(#1978): add retry mechanism if the error from the request is transient
        let rpc_response: GetRawTransactionVerboseResponse = self
            .client
            .request(GET_RAW_TRANSACTION_METHOD, &request_parameters)
            .await?;

        let transaction_block_confirmation = rpc_response.confirmations.into();
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }

        self.verify_block_is_canonical(rpc_response.blockhash)
            .await?;

        let extracted_values = extractors
            .iter()
            .map(|extractor| extractor.extract_value(&rpc_response))
            .collect();

        Ok(extracted_values)
    }
```
