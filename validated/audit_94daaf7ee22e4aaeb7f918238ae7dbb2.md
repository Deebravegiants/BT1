### Title
Attacker-Controlled Finality Parameter Enables MPC Attestation of Unfinalized Foreign-Chain Transactions — (`crates/foreign-chain-inspector/src/bitcoin/inspector.rs`, `crates/node/src/providers/verify_foreign_tx/sign.rs`)

### Summary

The `verify_foreign_transaction` flow accepts a fully attacker-controlled finality parameter (`BlockConfirmations` for Bitcoin, `EvmFinality::Latest` for EVM chains) with no protocol-enforced minimum. An unprivileged caller can submit a `BitcoinRpcRequest` with `confirmations: 0`, causing the MPC network to produce a threshold-signed attestation over a transaction that has not reached any meaningful finality threshold. A downstream bridge contract that trusts the MPC signature without re-checking the `confirmations` field in the signed payload will accept this attestation, enabling a double-spend.

### Finding Description

**Root cause — no minimum `BlockConfirmations` enforced anywhere in the stack.**

`BlockConfirmations` is defined as a plain `u64` wrapper with `minimum: 0.0` in the JSON schema: [1](#0-0) 

The contract's `verify_foreign_transaction` entry point performs no validation on the `confirmations` field: [2](#0-1) 

The node's `execute_foreign_chain_request` passes the caller-supplied value directly to the inspector: [3](#0-2) 

Inside `BitcoinInspector::extract`, the only guard is:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
``` [4](#0-3) 

When `block_confirmations_threshold = 0`, the condition `0 <= actual_confirmations` is trivially true for any confirmed transaction (even one with a single confirmation). The inspector proceeds to sign.

The signed payload is `ForeignTxSignPayloadV1 { request, values }`, where `request` includes the attacker-supplied `confirmations: 0`: [5](#0-4) 

The `msg_hash` the MPC nodes sign is `SHA-256(borsh(ForeignTxSignPayload))`, so the `confirmations: 0` field is baked into the signed attestation.

**EVM analog — `EvmFinality::Latest` is accepted without restriction.**

For all EVM-family chains (Base, BNB, Arbitrum, Polygon, HyperEVM, Abstract), the caller can supply `finality: Latest`. The `EvmFinality` enum exposes `Latest` as a valid variant: [6](#0-5) 

The node converts and passes it through without any minimum-finality guard: [7](#0-6) 

`EthereumFinality::Latest` maps to `eth_getBlockByNumber("latest")`, which is the chain tip — easily reorged. [8](#0-7) 

### Impact Explanation

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow: a user locks funds on a foreign chain and the MPC attestation unlocks equivalent funds on NEAR. If the MPC signs an attestation for a transaction with `confirmations: 0` (Bitcoin) or `finality: Latest` (EVM), an attacker can:

1. Submit a Bitcoin transaction locking funds.
2. Wait for 1 confirmation (or none for EVM `Latest`).
3. Call `verify_foreign_transaction` with `confirmations: 0`.
4. Receive a valid MPC threshold signature over `(tx_id, confirmations: 0, block_hash)`.
5. Submit the attestation to the NEAR bridge contract to claim the bridged funds.
6. Simultaneously attempt to double-spend / reorg the foreign-chain transaction (trivial for 1-confirmation Bitcoin; feasible for EVM `Latest`).

The MPC signature is cryptographically valid — it was produced by a threshold of honest nodes — but it attests to a state that was never final. The bridge is deceived into releasing funds for a transaction that is subsequently reversed. This is a **forged foreign-chain verification enabling double-spend**, matching the High impact category.

### Likelihood Explanation

The attack requires no privileged access. Any NEAR account can call `verify_foreign_transaction` with a deposit of 1 yoctoNEAR. The attacker controls the `confirmations` field entirely. For Bitcoin, a 1-confirmation reorg requires significant hashrate but is economically rational for large bridge amounts. For EVM `Latest`, a single-block reorg is achievable by a miner/validator or via MEV infrastructure. The attack is directly analogous to the flash-loan spot-price manipulation in the reference report: both exploit an attacker-controlled parameter that the protocol uses without enforcing a safe minimum.

### Recommendation

1. **Enforce a protocol-level minimum `BlockConfirmations`** in the on-chain contract or in the node's `execute_foreign_chain_request`. For Bitcoin, a minimum of 6 is the industry standard. Reject requests with `confirmations < MIN_BITCOIN_CONFIRMATIONS` before enqueuing.
2. **Reject `EvmFinality::Latest`** (and optionally `Safe`) for bridge-critical use cases. Only `Finalized` should be accepted for `verify_foreign_transaction` requests that unlock bridge funds.
3. **Encode the minimum in the on-chain `ChainEntry` whitelist** (alongside the RPC quorum) so the threshold is governance-controlled and auditable, not hardcoded in node software.

### Proof of Concept

```
// Attacker submits to verify_foreign_transaction:
{
  "request": {
    "Bitcoin": {
      "tx_id": "<attacker_btc_tx_with_1_confirmation>",
      "confirmations": 0,   // <-- attacker sets this to 0
      "extractors": ["BlockHash"]
    }
  },
  "domain_id": <foreign_tx_domain>,
  "payload_version": 1
}

// Node executes:
// block_confirmations_threshold = BlockConfirmations(0)
// rpc_response.confirmations = 1  (actual on-chain confirmations)
// check: 0 <= 1  → true → proceeds to sign

// MPC produces threshold signature over:
// SHA-256(borsh(ForeignTxSignPayloadV1 {
//   request: Bitcoin { tx_id, confirmations: 0, extractors: [BlockHash] },
//   values: [BlockHash(<block_hash>)]
// }))

// Attacker submits this valid MPC signature to the NEAR bridge contract.
// Bridge releases funds.
// Attacker double-spends the Bitcoin transaction (reorg the 1-confirmation block).
```

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L768-772)
```rust
pub enum EvmFinality {
    Latest,
    Safe,
    Finalized,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
pub struct BlockConfirmations(pub u64);
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L131-150)
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
                extracted_values.into_iter().map(Into::into).collect()
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L196-216)
```rust
            dtos::ForeignChainRpcRequest::Base(request) => {
                let inspector = self
                    .inspectors
                    .base
                    .as_ref()
                    .context("no inspector configured for Base")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<BaseExtractor> = request
                    .extractors
                    .iter()
                    .cloned()
                    .map(TryInto::try_into)
                    .collect::<Result<_, _>>()?;
                let values = inspector
                    .extract(transaction_id, finality, extractors)
                    .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
                    .await
                    .context("timed out during execution of foreign chain request")??;
                values.into_iter().map(Into::into).collect()
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

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L107-124)
```rust
        let finality_tag = match finality {
            EthereumFinality::Finalized => FinalityTag::Finalized,
            EthereumFinality::Safe => FinalityTag::Safe,
            EthereumFinality::Latest => FinalityTag::Latest,
        };
        let args = GetBlockByNumberArgs::new(
            BlockNumberOrTag::Tag(finality_tag),
            ReturnFullTransactionObjects::from(false),
        );
        let head: GetBlockByNumberResponse = self
            .client
            .request(GET_BLOCK_BY_NUMBER_METHOD, &args)
            .await?;

        if head.number < receipt_block_number {
            return Err(ForeignChainInspectionError::NotFinalized);
        }
        Ok(())
```
