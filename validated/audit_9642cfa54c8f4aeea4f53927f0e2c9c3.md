### Title
Zero `BlockConfirmations` Bypasses Bitcoin Finality Check, Enabling Signature Over Unconfirmed Transactions - (`crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

### Summary

The `verify_foreign_transaction` contract entry point accepts a user-supplied `confirmations: BlockConfirmations(0)` in a `BitcoinRpcRequest` without any minimum-value validation. The node-side Bitcoin inspector uses this value directly as the finality threshold. Because `0 <= any_value` is always true, the confirmation check is trivially bypassed, and the MPC network will produce a threshold signature attesting to an unconfirmed (or zero-confirmation) Bitcoin transaction.

### Finding Description

`verify_foreign_transaction` accepts a `VerifyForeignTransactionRequestArgs` whose inner `ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest { confirmations, ... })` is fully caller-controlled. The contract performs no lower-bound validation on `confirmations`. [1](#0-0) 

The contract only checks domain validity, chain support, gas attachment, and deposit — never that `confirmations >= 1`.

On the node side, `execute_foreign_chain_request` passes the caller-supplied value directly to the Bitcoin inspector as `block_confirmations_threshold`: [2](#0-1) 

The Bitcoin inspector then evaluates:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;

if !enough_block_confirmations {
    return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations { ... });
}
``` [3](#0-2) 

When `block_confirmations_threshold = 0`, the inequality `0 <= any_value` is unconditionally true for any transaction the RPC returns — including mempool transactions with zero confirmations. The check is completely bypassed, and the inspector proceeds to extract values and the MPC network proceeds to sign.

### Impact Explanation

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow: a NEAR contract reacts to a foreign-chain event only after the MPC network attests that the transaction finalized. With `confirmations: 0`, an attacker can obtain a valid MPC threshold signature over an unconfirmed Bitcoin transaction. The attacker can then:

1. Submit a Bitcoin transaction to the bridge.
2. Immediately call `verify_foreign_transaction` with `confirmations: 0`.
3. Receive a valid MPC signature before the transaction is confirmed.
4. Redeem bridge funds on NEAR using the signature.
5. Double-spend or RBF-replace the original Bitcoin transaction.

This constitutes **forged foreign-chain verification enabling double-spend / invalid bridge execution**, matching the High impact tier: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass … that causes invalid bridge execution or double-spend conditions."*

### Likelihood Explanation

The entry point is public and payable; any account can call it with only the minimum deposit. No privileged role is required. The attacker only needs to craft a `BitcoinRpcRequest` with `confirmations: 0(u64)` — a trivial parameter change. The Bitcoin RPC will return any transaction (including zero-confirmation ones) for `getrawtransaction`, so the inspector will always succeed. Likelihood is **High**.

### Recommendation

Enforce a minimum confirmation count at the contract boundary inside `verify_foreign_transaction` before the request is enqueued:

```rust
if let ForeignChainRpcRequest::Bitcoin(ref btc_req) = request.request {
    if btc_req.confirmations.0 == 0 {
        env::panic_str("Bitcoin confirmations must be >= 1");
    }
}
```

Alternatively, enforce the minimum inside `BitcoinRpcRequest` deserialization or in a dedicated request-validation helper so the invariant is guaranteed for all callers. A protocol-level minimum (e.g., 1 for testnet, 6 for mainnet) should be enforced on-chain rather than left to the caller.

### Proof of Concept

1. Deploy the contract and register Bitcoin as a supported foreign chain.
2. Call `verify_foreign_transaction` with:
   ```json
   {
     "request": {
       "domain_id": <foreign_tx_domain_id>,
       "payload_version": "V1",
       "request": {
         "Bitcoin": {
           "tx_id": "<mempool_tx_id_32_bytes>",
           "confirmations": 0,
           "extractors": ["BlockHash"]
         }
       }
     }
   }
   ```
3. Observe that MPC nodes query the Bitcoin RPC, the confirmation check `0 <= rpc_confirmations` passes unconditionally, and a threshold signature is returned for the unconfirmed transaction.
4. The attacker now holds a valid MPC-signed attestation for a transaction that has not finalized and can be reorganized or replaced. [3](#0-2) [4](#0-3)

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L117-125)
```rust
    async fn execute_foreign_chain_request(
        &self,
        request: &dtos::ForeignChainRpcRequest,
        payload_version: dtos::ForeignTxPayloadVersion,
    ) -> anyhow::Result<dtos::ForeignTxSignPayload> {
        chain_is_supported(&self.foreign_chain_policy_reader, request).await?;

        let values: Vec<dtos::ExtractedValue> = match request {
            dtos::ForeignChainRpcRequest::Ethereum(_request) => {
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
