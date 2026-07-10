Looking at the vulnerability class — **unprotected attacker-controlled parameter on a publicly callable function** — I need to find an analog in the NEAR MPC codebase where an unprivileged caller can supply a malicious parameter value that bypasses a security invariant.

The key findings from my investigation:

1. `verify_foreign_transaction()` is open to any caller (no access control, only a small deposit required)
2. `BitcoinRpcRequest.confirmations` is fully attacker-controlled
3. The contract performs zero validation on the `confirmations` value
4. The MPC nodes use the attacker-supplied value directly as the `block_confirmations_threshold`

---

### Title
Unprotected `confirmations` Parameter in `verify_foreign_transaction()` Allows Any Caller to Obtain MPC Signatures for Insufficiently Confirmed Bitcoin Transactions - (File: crates/contract/src/lib.rs)

### Summary
Any unprivileged caller can invoke `verify_foreign_transaction()` with `confirmations: 1` (or `confirmations: 0`) for a Bitcoin request. Neither the contract nor the MPC nodes enforce a minimum confirmation threshold. The MPC network will produce a valid threshold signature attesting to a transaction that may be reorganized, enabling double-spend conditions.

### Finding Description
`verify_foreign_transaction()` in `crates/contract/src/lib.rs` accepts a `VerifyForeignTransactionRequestArgs` containing a `BitcoinRpcRequest` with a caller-supplied `confirmations` field. The contract validates only three things before enqueuing the request:

1. Domain purpose is `ForeignTx`
2. The chain is in the supported-chains list
3. The attached deposit meets `MINIMUM_SIGN_REQUEST_DEPOSIT`

No minimum `confirmations` value is enforced at the contract level.

The MPC node's `VerifyForeignTxProvider` in `crates/node/src/providers/verify_foreign_tx/sign.rs` then reads the request from the store and passes the caller-supplied value directly to `BitcoinInspector::extract()` as `block_confirmations_threshold`:

```rust
let block_confirmations = request.confirmations.0.into();
let extracted_values = inspector
    .extract(transaction_id, block_confirmations, extractors)
    ...
```

Inside `BitcoinInspector::extract()` in `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`, the only check is:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
if !enough_block_confirmations {
    return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations { ... });
}
```

With `block_confirmations_threshold = 1`, any transaction that has appeared in a single block passes this check. The MPC nodes then sign the `ForeignTxSignPayload` (which includes the full request, including `confirmations: 1`) and call `respond_verify_foreign_tx()` on the contract, which resolves the yield and delivers the signature to the original caller.

There is no floor on `confirmations` anywhere in the contract, node configuration, or `ForeignChainsMetadata`.

### Impact Explanation
Bitcoin transactions with 1 confirmation are routinely reorganized. An attacker who obtains an MPC threshold signature over a payload attesting to a 1-confirmation Bitcoin transaction can present that signature to a downstream NEAR contract (or bridge) that trusts the MPC network as the authoritative foreign-chain verifier. If the downstream consumer does not independently re-check the `confirmations` field in the signed payload — a reasonable assumption given that the MPC network is positioned as a trusted oracle — the attacker can claim NEAR-side assets for a Bitcoin transaction that is subsequently reorganized, constituting a double-spend.

This matches the **High** allowed impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

### Likelihood Explanation
High. The entry point is a public, payable function requiring only a 1-yoctoNEAR deposit. No special role, key, or participant status is needed. The attacker simply submits a well-formed `BitcoinRpcRequest` with `confirmations: 1`. The attack is deterministic and requires no timing luck beyond the normal Bitcoin block time.

### Recommendation
Enforce a protocol-level minimum confirmation threshold. Two complementary approaches:

1. **Contract-level**: Add a `min_confirmations` field to `ForeignChainsConfig` (voted in by participants via `register_foreign_chain_config`) and reject any `verify_foreign_transaction()` call whose `confirmations` value falls below the configured minimum for that chain.
2. **Node-level**: Have each MPC node compare the request's `confirmations` against a locally configured floor before proceeding with inspection; refuse to sign if the threshold is below the minimum.

For Bitcoin, a minimum of 6 confirmations is the industry standard for finality.

### Proof of Concept

1. Attacker calls `verify_foreign_transaction()` with:
   ```json
   {
     "domain_id": <valid_foreign_tx_domain>,
     "payload_version": "V1",
     "request": {
       "Bitcoin": {
         "tx_id": "<target_bitcoin_tx_id>",
         "confirmations": 1,
         "extractors": ["BlockHash"]
       }
     }
   }
   ```
   attaching `1 yoctoNEAR`.

2. The contract enqueues the request — no `confirmations` validation occurs. [1](#0-0) 

3. MPC nodes observe the pending request and call `BitcoinInspector::extract()` with `block_confirmations_threshold = 1`. [2](#0-1) 

4. The inspector accepts the transaction (it has ≥ 1 confirmation) and returns extracted values. [3](#0-2) 

5. MPC nodes sign the `ForeignTxSignPayload` (which embeds `confirmations: 1`) and call `respond_verify_foreign_tx()`, delivering the threshold signature to the attacker. [4](#0-3) 

6. The Bitcoin transaction is reorganized. The attacker presents the MPC signature to a downstream bridge contract, which trusts the MPC network as the authoritative verifier and releases NEAR-side assets — a double-spend.

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L137-149)
```rust
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
```

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L50-59)
```rust
        let transaction_block_confirmation = rpc_response.confirmations.into();
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }
```
