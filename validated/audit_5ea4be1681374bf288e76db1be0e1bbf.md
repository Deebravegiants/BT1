### Title
Missing Minimum Confirmation Validation in Bitcoin Foreign-Chain Verification Allows Signing of Unconfirmed Transactions - (File: `crates/foreign-chain-inspector/src/bitcoin/inspector.rs` / `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` flow accepts a caller-supplied `BlockConfirmations` value of `0` for Bitcoin requests. Neither the on-chain contract nor the node-side inspector enforces a minimum confirmation threshold. Because the confirmation check is `threshold <= rpc_confirmations`, a threshold of `0` is trivially satisfied by any transaction the RPC knows about, including unconfirmed mempool transactions. The MPC network then signs a payload attesting to a transaction that has not achieved any block finality, enabling a double-spend attack against bridge contracts that rely on the MPC signature as a finality proof.

---

### Finding Description

**Contract layer — no validation of `confirmations`:**

`verify_foreign_transaction` in `crates/contract/src/lib.rs` accepts the full `VerifyForeignTransactionRequestArgs` and only checks domain purpose, gas, deposit, and chain support. It does not inspect the `confirmations` field of a `BitcoinRpcRequest` at all. [1](#0-0) 

The `BlockConfirmations` type is defined as a plain `u64` wrapper with a JSON schema `minimum: 0.0`, explicitly permitting zero. [2](#0-1) 

**Node layer — confirmation check is trivially bypassed at threshold 0:**

`BitcoinInspector::extract` performs:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
if !enough_block_confirmations {
    return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations { ... });
}
``` [3](#0-2) 

When `block_confirmations_threshold = 0`, the condition `0 <= rpc_confirmations` is always `true` for any `u64` value, so the check is a no-op. The inspector proceeds to `verify_block_is_canonical` and then signs the payload. [4](#0-3) 

**Signed payload embeds the caller-controlled `confirmations` field:**

The signed payload is `SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))`, where `request` is the full `BitcoinRpcRequest` including `confirmations: 0`. The MPC signature therefore attests to "this transaction exists with a required confirmation threshold of 0" — which is semantically equivalent to no finality guarantee at all. [5](#0-4) 

---

### Impact Explanation

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow: a bridge contract on NEAR releases funds only after the MPC network attests that a foreign-chain transaction finalized. If an attacker submits `confirmations: 0`, the MPC network signs a payload for a Bitcoin transaction that has not been included in any block (or has only 1 confirmation, which is trivially reorganizable). The attacker can then:

1. Broadcast a Bitcoin transaction sending funds to the bridge.
2. Immediately call `verify_foreign_transaction` with `confirmations: 0`.
3. Receive a valid MPC signature attesting to the transaction.
4. Submit the signature to the NEAR bridge contract to claim funds.
5. Double-spend the Bitcoin transaction (replace-by-fee or via a reorg).

The bridge contract receives a cryptographically valid MPC signature but for a transaction that never achieved finality. This constitutes **forged foreign-chain verification that causes invalid bridge execution and double-spend conditions**, matching the High impact tier.

---

### Likelihood Explanation

Any unprivileged NEAR account can call `verify_foreign_transaction` with `confirmations: 0` by paying the minimum deposit (`MINIMUM_SIGN_REQUEST_DEPOSIT`). No special role, key, or collusion is required. The attacker only needs a Bitcoin transaction visible to the RPC (even a mempool transaction, if the RPC's `getrawtransaction` returns it with `confirmations` field present) and a bridge contract that trusts the MPC signature without independently re-checking the embedded confirmation count.

---

### Recommendation

1. **Contract-level enforcement**: In `verify_foreign_transaction`, reject `BitcoinRpcRequest` with `confirmations == 0`. A minimum of 1 should be required; the network operators or governance should define a per-chain minimum (e.g., 6 for Bitcoin mainnet) and enforce it on-chain.

2. **Node-level enforcement**: In `BitcoinInspector::extract`, add an explicit guard:
   ```rust
   if block_confirmations_threshold == BlockConfirmations::from(0) {
       return Err(ForeignChainInspectionError::InvalidConfirmationThreshold);
   }
   ```

3. **EVM analog**: Similarly, consider whether `EvmFinality::Latest` should be accepted for bridge-critical flows, since `Latest` blocks can be reorganized. Restricting to `Safe` or `Finalized` for production bridge use cases would close the analogous staleness gap. [6](#0-5) 

---

### Proof of Concept

```
1. Attacker broadcasts Bitcoin tx T (e.g., sending 1 BTC to bridge deposit address).
2. Attacker calls on NEAR:
     verify_foreign_transaction({
       domain_id: <foreign_tx_domain>,
       payload_version: V1,
       request: Bitcoin({
         tx_id: T,
         confirmations: 0,   // ← bypass
         extractors: [BlockHash],
       })
     })
   with the minimum 1 yoctoNEAR deposit.
3. Contract accepts the request (no confirmations validation).
4. MPC nodes call getrawtransaction(T, verbose=true).
   - If T is in mempool: RPC may return it with confirmations=0.
   - If T has 1 confirmation: 0 <= 1 is true, check passes.
5. Nodes sign SHA-256(borsh({ request: {tx_id:T, confirmations:0, ...}, values:[block_hash] })).
6. respond_verify_foreign_tx delivers the signature on-chain.
7. Attacker submits the MPC signature to the NEAR bridge contract → bridge releases funds.
8. Attacker issues a conflicting Bitcoin tx T' (RBF or miner collusion) → T is evicted/reorganized.
9. Bridge has released NEAR-side funds for a Bitcoin tx that never finalized.
``` [7](#0-6) [8](#0-7)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L972-996)
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
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
#[non_exhaustive]
pub enum ExtractedValue {
    BitcoinExtractedValue(BitcoinExtractedValue),
    EvmExtractedValue(EvmExtractedValue),
    StarknetExtractedValue(StarknetExtractedValue),
    TonExtractedValue(TonExtractedValue),
    AptosExtractedValue(AptosExtractedValue),
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
pub struct BlockConfirmations(pub u64);
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

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L100-125)
```rust
    /// Checks that the receipt's block has reached the requested finality level — i.e. that the
    /// head of the chain at `finality` is at or past `receipt_block_number`.
    async fn verify_finality_level(
        &self,
        receipt_block_number: U64,
        finality: EthereumFinality,
    ) -> Result<(), ForeignChainInspectionError> {
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
    }
```
