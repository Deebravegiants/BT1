### Title
Missing Minimum Confirmation Bound on Bitcoin Foreign-Chain Verification Allows Finality Bypass - (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

### Summary

The `verify_foreign_transaction` endpoint accepts a caller-supplied `confirmations: 0` in a `BitcoinRpcRequest` with no on-chain minimum enforcement. MPC nodes use this value directly as the finality threshold, so a zero-confirmation request trivially passes the confirmation check for any transaction — including unconfirmed mempool transactions. The MPC network then issues a threshold signature attesting to a "verified" Bitcoin transaction that has not achieved any finality, enabling double-spend conditions in downstream bridge contracts.

### Finding Description

`BlockConfirmations` is a plain `u64` newtype with no minimum constraint: [1](#0-0) 

`BitcoinRpcRequest` embeds it without any validation: [2](#0-1) 

`verify_foreign_transaction` in the contract accepts the request and queues it without checking the `confirmations` value: [3](#0-2) 

On the node side, `execute_foreign_chain_request` passes the caller-supplied value directly to the inspector as the threshold: [4](#0-3) 

Inside `BitcoinInspector::extract`, the check is:

```rust
let enough_block_confirmations = block_confirmations_threshold <= transaction_block_confirmation;
``` [5](#0-4) 

When `block_confirmations_threshold = 0`, the inequality `0 <= any_u64` is always true. The confirmation check is unconditionally bypassed for every transaction, including those with zero confirmations (mempool-only).

The signed payload commits to the full `ForeignTxSignPayload{request, values}`, which includes the `confirmations: 0` field. However, the MPC contract's `respond_verify_foreign_tx` only verifies that the signature is valid over the supplied `payload_hash` — it does not re-derive or validate the hash against a minimum-confirmation policy: [6](#0-5) 

The contract issues no rejection and resolves the yield, delivering a valid threshold signature to the caller.

### Impact Explanation

The primary use case for `verify_foreign_transaction` is the Omnibridge inbound flow (Bitcoin → NEAR), where the MPC signature is the sole proof of Bitcoin finality accepted by the bridge contract. A caller who submits `confirmations: 0` receives a valid MPC threshold signature over an unconfirmed Bitcoin transaction. If the bridge contract does not independently re-check the `confirmations` field embedded in the payload (a common omission when the MPC network is treated as the trusted verifier), it will release NEAR-side assets for a Bitcoin transaction that is subsequently reorged or double-spent. This is a **forged foreign-chain verification / verification bypass causing invalid bridge execution or double-spend conditions** — matching the High allowed impact.

### Likelihood Explanation

The entry path is fully unprivileged: any NEAR account can call `verify_foreign_transaction` with `confirmations: 0` and a valid 1-yoctoNEAR deposit. No special role, key, or collusion is required. The MPC nodes process the request normally. The only prerequisite is that the target Bitcoin chain is whitelisted and available, which is the normal operating state of the network.

### Recommendation

Enforce a protocol-level minimum on `BlockConfirmations` at the contract boundary. Two complementary fixes:

1. **On-chain validation in `verify_foreign_transaction`**: Reject any `BitcoinRpcRequest` whose `confirmations` is below a governance-configured minimum (e.g., 1 for testnet, 6 for mainnet). This mirrors the `amountOutMinimum` fix in the referenced report — the protective parameter must have a non-zero floor enforced by the protocol, not left to the caller.

2. **Type-level enforcement**: Replace `BlockConfirmations(pub u64)` with a validated newtype whose constructor rejects zero, or add a `ChainEntry`-level minimum that the contract checks before queuing the request.

### Proof of Concept

```json
{
  "request": {
    "request": {
      "Bitcoin": {
        "tx_id": "<txid of a 0-confirmation mempool tx>",
        "confirmations": 0,
        "extractors": ["BlockHash"]
      }
    },
    "domain_id": 3,
    "payload_version": 1
  }
}
```

1. Attacker broadcasts a Bitcoin transaction but does not wait for confirmation.
2. Attacker calls `verify_foreign_transaction` with `confirmations: 0` and the above payload.
3. MPC nodes query the Bitcoin RPC; `getrawtransaction` returns the mempool tx with `confirmations: 0`. The check `0 <= 0` passes.
4. Nodes sign `SHA-256(borsh(ForeignTxSignPayload{request, [BlockHash]}))` and call `respond_verify_foreign_tx`.
5. Contract verifies the threshold signature and resolves the yield, returning a valid `VerifyForeignTransactionResponse` to the caller.
6. Caller presents the signature to the bridge contract to claim NEAR-side assets.
7. Attacker double-spends the Bitcoin transaction; the bridge has already released funds based on an unconfirmed attestation.

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L267-271)
```rust
pub struct BitcoinRpcRequest {
    pub tx_id: BitcoinTxId,
    pub confirmations: BlockConfirmations,
    pub extractors: Vec<BitcoinExtractor>,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
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

**File:** crates/contract/src/lib.rs (L718-747)
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
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L131-149)
```rust
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
