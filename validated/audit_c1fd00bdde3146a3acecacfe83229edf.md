### Title
Missing Minimum `BlockConfirmations` Validation Enables Signing of Unconfirmed Bitcoin Transactions - (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`, `crates/contract/src/lib.rs`, `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

---

### Summary

The `verify_foreign_transaction` contract method accepts a fully user-controlled `BlockConfirmations` value with no minimum bound enforced anywhere in the contract or node pipeline. An unprivileged caller can set `confirmations: 0`, causing MPC nodes to sign a payload attesting to an unconfirmed (zero-confirmation) Bitcoin transaction. Any bridge contract on NEAR that relies on `verify_foreign_transaction` responses to release funds is exposed to a double-spend attack.

---

### Finding Description

`BlockConfirmations` is defined as a plain `u64` newtype with no minimum validation:

```rust
pub struct BlockConfirmations(pub u64);
``` [1](#0-0) 

The `verify_foreign_transaction` contract entry point performs no validation on the `confirmations` field of a `BitcoinRpcRequest`:

```rust
pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
    self.check_request_preconditions(...);
    let requested_chain = request.request.chain();
    let supported_chains = self.get_supported_foreign_chains();
    if !supported_chains.contains(&requested_chain) { ... }
    // No check on request.request.confirmations
    ...
}
``` [2](#0-1) 

On the node side, the user-supplied value is passed directly as the finality threshold to `BitcoinInspector::extract`:

```rust
let block_confirmations = request.confirmations.0.into();
let extracted_values = inspector
    .extract(transaction_id, block_confirmations, extractors)
    ...
``` [3](#0-2) 

The inspector's only check is:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
``` [4](#0-3) 

With `block_confirmations_threshold = 0`, this condition is satisfied by **any** transaction, including mempool-only (unconfirmed) transactions where `confirmations = 0`. The MPC network then signs a `ForeignTxSignPayload` that includes the original `BitcoinRpcRequest` (with `confirmations: 0`) and the extracted block hash, and submits it via `respond_verify_foreign_tx`. The contract validates only the cryptographic signature, not the semantic validity of the confirmation threshold: [5](#0-4) 

The signed payload is then returned to the caller as a valid MPC attestation of the Bitcoin transaction.

This is structurally identical to the Chainlink circuit-breaker issue: just as Chainlink clamps prices to `minAnswer`/`maxAnswer` without the consuming code checking those bounds, here the user supplies a `confirmations` value that the protocol never bounds from below, causing the MPC network to attest to a weaker finality guarantee than the bridge contract assumes.

---

### Impact Explanation

A bridge contract on NEAR that calls `verify_foreign_transaction` and uses the returned MPC signature to release bridged assets assumes the MPC network enforced a meaningful finality threshold. With `confirmations: 0`, the attacker receives a valid MPC signature over an unconfirmed Bitcoin transaction. The attacker can then:

1. Use the signature to claim bridged NEAR assets immediately.
2. Double-spend the Bitcoin transaction (via RBF or by simply not broadcasting it to miners), keeping both the Bitcoin and the bridged NEAR assets.

This constitutes **forged foreign-chain verification enabling double-spend conditions**, matching the allowed High impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

The attack requires no special privileges. Any account can call `verify_foreign_transaction` with a deposit of `MINIMUM_SIGN_REQUEST_DEPOSIT` (1 yoctoNEAR). The attacker only needs a valid Bitcoin transaction ID visible in the mempool. The attack is fully deterministic and requires no collusion with MPC participants.

---

### Recommendation

Enforce a minimum `BlockConfirmations` value at the contract level inside `verify_foreign_transaction`, before the request is enqueued:

```rust
// In verify_foreign_transaction, after chain support check:
if let ForeignChainRpcRequest::Bitcoin(ref btc_req) = request.request {
    const MIN_BITCOIN_CONFIRMATIONS: u64 = 1; // or a protocol-defined constant
    if btc_req.confirmations.0 < MIN_BITCOIN_CONFIRMATIONS {
        env::panic_str("Bitcoin confirmations must be at least 1");
    }
}
``` [6](#0-5) 

Alternatively, make `BlockConfirmations` a validated newtype that rejects zero at construction time, or add a per-chain minimum confirmation policy to the on-chain foreign chain configuration so governance can set and update the floor.

---

### Proof of Concept

1. Attacker broadcasts Bitcoin transaction `tx_id = X` to the mempool (0 confirmations).
2. Attacker calls `verify_foreign_transaction` with:
   ```json
   { "Bitcoin": { "tx_id": "X", "confirmations": 0, "extractors": ["BlockHash"] } }
   ```
3. Contract accepts the request — no minimum check on `confirmations`.
4. MPC nodes call `BitcoinInspector::extract(X, BlockConfirmations(0), [BlockHash])`.
5. `getrawtransaction` returns the mempool transaction with `confirmations: 0`.
6. Check `0 <= 0` passes; canonical-block check is skipped (unconfirmed tx has no block).
7. MPC signs `ForeignTxSignPayload::V1 { request: { tx_id: X, confirmations: 0, ... }, values: [...] }`.
8. `respond_verify_foreign_tx` is called; contract validates the ECDSA signature and resolves the yield.
9. Attacker receives a valid `VerifyForeignTransactionResponse` with a threshold-signed attestation.
10. Attacker submits this to a NEAR bridge contract to claim bridged funds.
11. Attacker RBF-replaces or abandons the Bitcoin transaction, double-spending it.

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1262-1282)
```rust
#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
    derive_more::Into,
    derive_more::From,
    derive_more::AsRef,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct BlockConfirmations(pub u64);
```

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L137-150)
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
                extracted_values.into_iter().map(Into::into).collect()
```

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L51-59)
```rust
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }
```
