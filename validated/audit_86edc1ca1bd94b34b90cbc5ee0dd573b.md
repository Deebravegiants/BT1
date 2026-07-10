### Title
`verify_foreign_transaction` Accepts Empty Extractor List, Producing Signatures With No Content Attestation - (`crates/contract/src/lib.rs`, `crates/node/src/providers/verify_foreign_tx/sign.rs`)

### Summary

The `verify_foreign_transaction` endpoint accepts requests with an empty `extractors` array. When no extractors are specified, the MPC network performs finality/confirmation checks but signs a payload containing zero extracted values — attesting only that a transaction ID exists on-chain, not what the transaction actually did. This is the direct analog of AuraSpell's `minAmountsOut = []`: just as that empty array means "accept any output amount," an empty `extractors` list means "attest to nothing about transaction content."

### Finding Description

The `verify_foreign_transaction` method in `crates/contract/src/lib.rs` performs no validation on the `extractors` field of the incoming request:

```rust
pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
    self.check_request_preconditions(
        request.domain_id,
        DomainPurpose::ForeignTx,
        Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
        MINIMUM_SIGN_REQUEST_DEPOSIT,
    );
    let requested_chain = request.request.chain();
    let supported_chains = self.get_supported_foreign_chains();
    if !supported_chains.contains(&requested_chain) { ... }
    // No check: request.request.extractors().is_empty()
    ...
}
``` [1](#0-0) 

The MPC nodes' `execute_foreign_chain_request` in `crates/node/src/providers/verify_foreign_tx/sign.rs` faithfully processes whatever extractor list is given — including an empty one — and builds a `ForeignTxSignPayloadV1` with `values: vec![]`:

```rust
let values: Vec<dtos::ExtractedValue> = match request {
    dtos::ForeignChainRpcRequest::Bitcoin(request) => {
        let extractors: Vec<BitcoinExtractor> = request.extractors.iter()...collect()?;
        inspector.extract(transaction_id, block_confirmations, extractors).await??
        // If extractors is [], extracted_values is []
    }
    ...
};
let payload = dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
    request: request.clone(),
    values,  // empty vec when extractors was empty
});
``` [2](#0-1) 

The inspector tests explicitly confirm that empty extractors succeed and return empty values: [3](#0-2) [4](#0-3) 

The SDK's `ForeignChainRequestBuilder` also explicitly supports building requests with no extractors, and tests assert this is valid: [5](#0-4) 

The signed payload hash is `SHA-256(borsh(ForeignTxSignPayload { request: { tx_id, extractors: [] }, values: [] }))`. This signature is cryptographically valid but attests to nothing about the transaction's content. [6](#0-5) 

### Impact Explanation

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow: a bridge contract on NEAR calls this to get the MPC network to attest that a specific foreign-chain deposit occurred with specific values (amount, recipient, token). With empty extractors, an attacker can submit any transaction ID on a supported chain and receive a valid MPC threshold signature over a payload with no extracted values. A bridge contract that does not independently enforce that the returned `values` list is non-empty and matches expected content (amount, recipient) would accept this signature as proof of a deposit — enabling the attacker to mint bridged tokens without having made the corresponding foreign-chain deposit. This breaks the core safety invariant of the `verify_foreign_transaction` feature: that the MPC signature constitutes a meaningful attestation of foreign-chain transaction content.

**Impact class:** Medium — balance/accounting invariant broken; bridge fund theft is possible if downstream contracts do not independently validate extracted values.

### Likelihood Explanation

The attack path is fully unprivileged: any NEAR account can call `verify_foreign_transaction` with `extractors: []` for any transaction ID on a supported chain. The contract accepts the request, the nodes process it, and a valid threshold signature is returned. No collusion, no privileged access, and no network-level attack is required. The only external factor is whether the downstream bridge contract independently validates the extracted values — but the MPC contract provides no protocol-level guarantee that it will not sign empty-extractor payloads, so bridge contracts cannot rely on the MPC layer for this protection.

### Recommendation

Enforce a minimum extractor count of 1 in `verify_foreign_transaction` before enqueueing the request:

```rust
pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
    // Reject requests with no extractors — a signature over empty values
    // provides no meaningful attestation about transaction content.
    if request.request.extractors_is_empty() {
        env::panic_str("at least one extractor is required");
    }
    ...
}
```

Alternatively, use the existing `BoundedVec` infrastructure with a lower bound of 1 on the `extractors` field in each `*RpcRequest` struct, so the type system enforces non-emptiness at deserialization time. [7](#0-6) 

### Proof of Concept

1. A supported chain (e.g., Bitcoin) is available via `get_supported_foreign_chains()`.
2. Attacker calls `verify_foreign_transaction` with:
   ```json
   {
     "request": {
       "Bitcoin": {
         "tx_id": "<any_valid_bitcoin_txid>",
         "confirmations": 1,
         "extractors": []
       }
     },
     "domain_id": <foreign_tx_domain_id>,
     "payload_version": 1
   }
   ```
3. The contract accepts the request (no extractor count check at lines 526–556 of `lib.rs`).
4. MPC nodes call `execute_foreign_chain_request` with `extractors: []`, which returns `values: []` (confirmed by the `extract_returns_empty_when_no_extractors_provided` test).
5. Nodes sign `SHA-256(borsh({ request: { tx_id, extractors: [] }, values: [] }))` and call `respond_verify_foreign_tx`.
6. The contract returns a valid threshold signature to the caller.
7. Attacker presents this signature to an Omnibridge NEAR contract as "proof" that a deposit occurred. If the bridge contract does not validate that `values` is non-empty and contains the expected amount/recipient, it mints bridged tokens for the attacker with no corresponding foreign-chain deposit. [1](#0-0) [8](#0-7)

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L124-347)
```rust
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
            }
            dtos::ForeignChainRpcRequest::Abstract(request) => {
                let inspector = self
                    .inspectors
                    .abstract_chain
                    .as_ref()
                    .context("no inspector configured for abstract")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<AbstractExtractor> = request
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
            }
            dtos::ForeignChainRpcRequest::Bnb(request) => {
                let inspector = self
                    .inspectors
                    .bnb
                    .as_ref()
                    .context("no inspector configured for BNB")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<BnbExtractor> = request
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
            }
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
            }
            dtos::ForeignChainRpcRequest::Arbitrum(request) => {
                let inspector = self
                    .inspectors
                    .arbitrum
                    .as_ref()
                    .context("no inspector configured for Arbitrum")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<ArbitrumExtractor> = request
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
            }
            dtos::ForeignChainRpcRequest::HyperEvm(request) => {
                let inspector = self
                    .inspectors
                    .hyper_evm
                    .as_ref()
                    .context("no inspector configured for HyperEVM")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<HyperEvmExtractor> = request
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
            }
            dtos::ForeignChainRpcRequest::Polygon(request) => {
                let inspector = self
                    .inspectors
                    .polygon
                    .as_ref()
                    .context("no inspector configured for Polygon")?;

                let transaction_id = request.tx_id.0.into();
                let finality: EthereumFinality = request.finality.clone().try_into()?;
                let extractors: Vec<PolygonExtractor> = request
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
            }
            dtos::ForeignChainRpcRequest::Starknet(request) => {
                let inspector = self
                    .inspectors
                    .starknet
                    .as_ref()
                    .context("no inspector configured for Starknet")?;

                let transaction_id = request.tx_id.0.0.into();
                let finality: StarknetFinality = request.finality.clone().try_into()?;
                let extractors: Vec<StarknetExtractor> = request
                    .extractors
                    .iter()
                    .cloned()
                    .map(TryInto::try_into)
                    .collect::<Result<_, _>>()?;

                let extracted_values = inspector
                    .extract(transaction_id, finality, extractors)
                    .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
                    .await
                    .context("timed out during execution of foreign chain request")??;

                extracted_values.into_iter().map(Into::into).collect()
            }
            dtos::ForeignChainRpcRequest::Ton(_request) => {
                bail!("ForeignChainRpcRequest::Ton is unsupported")
            }
            dtos::ForeignChainRpcRequest::Aptos(request) => {
                let inspector = self
                    .inspectors
                    .aptos
                    .as_ref()
                    .context("no inspector configured for Aptos")?;

                let tx_id = request.tx_id.0.into();
                let finality: AptosFinality = request.finality.clone().try_into()?;
                let extractors: Vec<AptosExtractor> = request
                    .extractors
                    .iter()
                    .cloned()
                    .map(TryInto::try_into)
                    .collect::<Result<_, _>>()?;

                let extracted_values = inspector
                    .extract(tx_id, finality, extractors)
                    .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
                    .await
                    .context("timed out during execution of foreign chain request")??;

                extracted_values.into_iter().map(Into::into).collect()
            }
            _ => bail!("unsupported foreign chain request"),
        };
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
    }
```

**File:** crates/foreign-chain-inspector/tests/bitcoin_inspector.rs (L105-139)
```rust
#[tokio::test]
async fn extract_returns_empty_when_no_extractors_provided() {
    // given
    let tx_id = BitcoinTransactionHash::from([11; 32]);
    let expected_block_hash = BitcoinBlockHash::from([12; 32]);

    let confirmations = BlockConfirmations::from(9u64);
    let threshold = BlockConfirmations::from(6u64);
    let transport_block_hash = TransportBitcoinBlockHash::from(*expected_block_hash);

    let tx_response = GetRawTransactionVerboseResponse {
        blockhash: transport_block_hash,
        confirmations: *confirmations,
    };
    let block_response = GetBlockHeaderVerboseResponse {
        hash: transport_block_hash,
        height: TEST_BLOCK_HEIGHT,
    };

    let mock_client = SequentialResponseMockClientBuilder::new()
        .with_response(tx_response)
        .with_response(block_response)
        .with_response(transport_block_hash)
        .build();
    let inspector = BitcoinInspector::new(mock_client);

    // when
    let extracted_values = inspector
        .extract(tx_id, threshold, Vec::new())
        .await
        .expect("extract should succeed");

    // then
    let expected_extractions: Vec<BitcoinExtractedValue> = vec![];
    assert_eq!(expected_extractions, extracted_values);
```

**File:** crates/foreign-chain-inspector/tests/evm_inspector.rs (L235-271)
```rust
            #[tokio::test]
            async fn extract_returns_empty_when_no_extractors_provided() {
                // given
                let tx_id = TxHash::from([11; 32]);

                let finality_block_response = GetBlockByNumberResponse {
                    number: U64::from(100),
                    hash: H256::from([0xaa; 32]),
                };
                let tx_response = GetTransactionReceiptResponse {
                    block_hash: H256::from([12; 32]),
                    block_number: U64::from(90),
                    status: U64::one(),
                    logs: vec![test_log()],
                };
                let canonical_block_response = GetBlockByNumberResponse {
                    number: tx_response.block_number,
                    hash: tx_response.block_hash,
                };

                let mock_client = SequentialResponseMockClientBuilder::new()
                    .with_response(&tx_response)
                    .with_response(&finality_block_response)
                    .with_response(&canonical_block_response)
                    .build();
                let inspector = Inspector::new(mock_client);

                // when
                let extracted_values = inspector
                    .extract(tx_id, EthereumFinality::Finalized, Vec::new())
                    .await
                    .unwrap();

                // then
                let expected_extractions: Vec<ExtractedValue> = vec![];
                assert_eq!(expected_extractions, extracted_values);
            }
```

**File:** crates/near-mpc-sdk/tests/bitcoin.rs (L7-26)
```rust
#[test]
fn no_extractor_added() {
    // given
    let domain_id = DomainId::from(2);
    let tx_id = BitcoinTxId::from([123; 32]);

    // when
    let (_verifier, built_sign_request_args) = ForeignChainRequestBuilder::new_bitcoin()
        .with_tx_id(tx_id)
        .with_block_confirmations(10)
        .with_domain_id(domain_id)
        .build();

    // then
    let no_extractors = vec![];

    assert_matches!(built_sign_request_args.request, ForeignChainRpcRequest::Bitcoin(bitcoin_rpc_request) => {
        assert_eq!(bitcoin_rpc_request.extractors, no_extractors);
    });
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1510)
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
```

**File:** crates/near-mpc-bounded-collections/src/bounded_vec.rs (L32-51)
```rust
/// BoundedVec errors
#[derive(Error, PartialEq, Eq, Debug, Clone)]
pub enum BoundedVecOutOfBounds {
    /// Items quantity is less than L (lower bound)
    #[error("Lower bound violation: got {got} (expected >= {lower_bound})")]
    LowerBoundError {
        /// L (lower bound)
        lower_bound: usize,
        /// provided value
        got: usize,
    },
    /// Items quantity is more than U (upper bound)
    #[error("Upper bound violation: got {got} (expected <= {upper_bound})")]
    UpperBoundError {
        /// U (upper bound)
        upper_bound: usize,
        /// provided value
        got: usize,
    },
}
```
