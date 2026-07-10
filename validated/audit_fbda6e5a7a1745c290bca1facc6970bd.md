### Title
Missing L2 Sequencer Liveness Check in `EvmInspector::verify_finality_level` Enables Signing Attestations for Reorganizable Transactions - (File: crates/foreign-chain-inspector/src/evm/inspector.rs)

---

### Summary

The shared `EvmInspector` used for Arbitrum, Base, Abstract, HyperEVM, BNB, and Polygon does not verify whether the L2 sequencer is operational before accepting finality data from the RPC. When a sequencer is down, the RPC returns stale block-tag data. The `verify_finality_level` check can pass against this stale head, causing MPC nodes to produce a threshold signature attesting that a foreign transaction reached a finality level it has not actually reached. If the sequencer later restarts and reorganizes those blocks, the signed attestation becomes a forgery that can be replayed on NEAR to trigger invalid bridge execution.

---

### Finding Description

`EvmInspector::verify_finality_level` resolves the chain head by querying `eth_getBlockByNumber` with a `FinalityTag` (`Finalized`, `Safe`, or `Latest`) and then asserts:

```rust
// crates/foreign-chain-inspector/src/evm/inspector.rs  lines 107-123
let finality_tag = match finality {
    EthereumFinality::Finalized => FinalityTag::Finalized,
    EthereumFinality::Safe      => FinalityTag::Safe,
    EthereumFinality::Latest    => FinalityTag::Latest,
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
``` [1](#0-0) 

There is no check that the sequencer is live and actively advancing the chain. On L2 chains with a centralized sequencer (Arbitrum, Base, Abstract, HyperEVM), when the sequencer halts:

- The RPC node continues serving the last known block for each tag.
- A transaction included in block N before the halt will still satisfy `head.number >= N` for `Safe` or `Latest` tags.
- The function returns `Ok(())`, and the full `extract` pipeline proceeds to produce extracted values. [2](#0-1) 

The `ArbitrumInspector` is a direct type alias for `EvmInspector<Client, Arbitrum>` with no additional sequencer check:

```rust
// crates/foreign-chain-inspector/src/arbitrum/inspector.rs  line 14
pub type ArbitrumInspector<Client> = crate::evm::inspector::EvmInspector<Client, Arbitrum>;
``` [3](#0-2) 

The node dispatches to this inspector directly in `sign.rs`:

```rust
// crates/node/src/providers/verify_foreign_tx/sign.rs  lines 218-238
dtos::ForeignChainRpcRequest::Arbitrum(request) => {
    let inspector = self.inspectors.arbitrum.as_ref()
        .context("no inspector configured for Arbitrum")?;
    let finality: EthereumFinality = request.finality.clone().try_into()?;
    let values = inspector
        .extract(transaction_id, finality, extractors)
        .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
        .await??;
    values.into_iter().map(Into::into).collect()
}
``` [4](#0-3) 

The `FanOut` inspector fans the query to multiple RPC providers and requires quorum agreement, but if all providers are backed by the same stale sequencer state, they will all agree on the stale head — the quorum check does not help. [5](#0-4) 

The signed payload commits only to `(request, extracted_values)` — there is no timestamp or block-height freshness bound in the payload itself:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs  lines 1499-1501
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [6](#0-5) 

---

### Impact Explanation

The MPC network's `verify_foreign_transaction` flow is the trust anchor for the Omnibridge inbound path: NEAR contracts react to foreign-chain events **only** because the MPC threshold signature attests that the transaction was verified. If the MPC signs an attestation for a transaction that is subsequently reorganized out of the canonical chain, the resulting signature is a forgery. A bridge contract on NEAR that accepts this signature will release funds for a deposit that no longer exists on the foreign chain — a direct, irreversible loss of funds from the bridge.

This maps to: **High — forged foreign-chain verification / light-client-style verification bypass causing invalid bridge execution.**

---

### Likelihood Explanation

- Arbitrum, Base, and Abstract each have a centralized sequencer. Sequencer outages have occurred historically on Arbitrum (e.g., the December 2021 and January 2023 incidents).
- An attacker who monitors sequencer health can time a `verify_foreign_transaction` submission to land during a downtime window.
- For `EvmFinality::Safe` (batch posted to L1 but not yet L1-finalized), a sequencer restart with a different batch ordering can reorganize the block. For `EvmFinality::Latest`, reorganization is straightforward.
- The `verify_foreign_transaction` endpoint is open to any unprivileged NEAR account with the deposit; no special role is required.
- The `FanOut` quorum across multiple RPC providers does not help if all providers reflect the same stale sequencer state.

---

### Recommendation

Before accepting finality data from an L2 RPC, check that the sequencer is live by verifying the timestamp of the returned head block against a maximum staleness bound (analogous to Chainlink's heartbeat check). For example:

```rust
// After fetching `head`, assert its timestamp is recent:
let head_timestamp = head.timestamp; // seconds since epoch
let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .unwrap()
    .as_secs();
if now.saturating_sub(head_timestamp) > MAX_SEQUENCER_STALENESS_SECS {
    return Err(ForeignChainInspectionError::SequencerDown);
}
```

`MAX_SEQUENCER_STALENESS_SECS` should be set per-chain based on the expected block time (e.g., 60 seconds for Arbitrum's ~0.25 s block time). The new error variant should be classified as **transient** so the request retries once the sequencer recovers, consistent with the existing `NotFinalized` handling. [7](#0-6) 

Additionally, consider restricting `EvmFinality::Latest` for L2 chains with a centralized sequencer, or at minimum documenting that callers bear full reorganization risk when choosing it.

---

### Proof of Concept

1. Attacker deposits 10 000 USDC into the Omnibridge contract on Arbitrum. The transaction lands in Arbitrum block N, which is posted to L1 as a batch (status: `safe`).
2. The Arbitrum sequencer halts. The RPC continues serving block N as the `safe` head.
3. Attacker calls `verify_foreign_transaction` on the NEAR MPC contract with `ForeignChainRpcRequest::Arbitrum { tx_id: <deposit_tx>, finality: EvmFinality::Safe, extractors: [BlockHash] }`.
4. Each MPC node calls `eth_getBlockByNumber("safe")` → receives stale block N. `head.number (N) >= receipt_block_number (N)` → `verify_finality_level` returns `Ok(())`.
5. `verify_block_is_canonical` also passes because the RPC still serves block N as canonical.
6. All nodes extract the block hash and produce signature shares; the threshold signature is assembled and returned on-chain.
7. The sequencer restarts, reorganizes block N (the deposit transaction is dropped), and the Arbitrum chain advances from a different state.
8. Attacker presents the MPC signature to the NEAR bridge contract, which releases 10 000 USDC — for a deposit that no longer exists on Arbitrum. [8](#0-7) [9](#0-8) [4](#0-3)

### Citations

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L50-85)
```rust
    async fn extract(
        &self,
        transaction: Chain::TransactionHash,
        finality: EthereumFinality,
        extractors: Vec<EvmExtractor>,
    ) -> Result<Vec<EvmExtractedValue<Chain>>, ForeignChainInspectionError> {
        let get_transaction_receipt_args = GetTransactionReceiptARgs {
            transaction_hash: H256(transaction.into()),
        };
        let transaction_receipt: GetTransactionReceiptResponse = self
            .client
            .request(
                GET_TRANSACTION_RECEIPT_METHOD,
                &get_transaction_receipt_args,
            )
            .await?;

        self.verify_finality_level(transaction_receipt.block_number, finality)
            .await?;
        self.verify_block_is_canonical(
            transaction_receipt.block_number,
            transaction_receipt.block_hash,
        )
        .await?;

        let transaction_success = transaction_receipt.status == U64::one();

        if !transaction_success {
            return Err(ForeignChainInspectionError::TransactionFailed);
        }

        extractors
            .iter()
            .map(|extractor| extractor.extract_value(&transaction_receipt))
            .collect()
    }
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L100-124)
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
```

**File:** crates/foreign-chain-inspector/src/arbitrum/inspector.rs (L1-16)
```rust
use crate::{
    arbitrum::{ArbitrumBlockHash, ArbitrumTransactionHash},
    evm::inspector::EvmChain,
};

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Arbitrum;

impl EvmChain for Arbitrum {
    type BlockHash = ArbitrumBlockHash;
    type TransactionHash = ArbitrumTransactionHash;
}

pub type ArbitrumInspector<Client> = crate::evm::inspector::EvmInspector<Client, Arbitrum>;
pub type ArbitrumExtractedValue = crate::evm::inspector::EvmExtractedValue<Arbitrum>;
pub type ArbitrumExtractor = crate::evm::inspector::EvmExtractor;
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L218-238)
```rust
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
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L130-141)
```rust
        if let Some(first_values) = successes.first() {
            let all_successes_agree = successes.iter().all(|(_, v)| v == &first_values.1);
            if !all_successes_agree {
                tracing::error!(
                    responses = ?successes,
                    "fan-out: inspectors returned mismatching extracted values",
                );
                return Err(ForeignChainInspectionError::InspectorResponseMismatch);
            }
            let (_, first) = successes.into_iter().next().expect("checked non-empty");

            return Ok(first);
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L265-275)
```rust
impl ForeignChainInspectionError {
    pub fn is_transient(&self) -> bool {
        matches!(
            self,
            Self::ClientError(_)
                | Self::RpcRequestFailed(_)
                | Self::NotFinalized
                | Self::NotEnoughBlockConfirmations { .. }
        )
    }
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```
