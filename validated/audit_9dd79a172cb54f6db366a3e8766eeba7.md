### Title
Validator hardcodes `paid_fee_on_l1 = Fee(1)` for L1 handler transactions, bypassing fee validation — (`crates/apollo_transaction_converter/src/transaction_converter.rs`)

### Summary

When a validator node receives an L1 handler transaction via the consensus protocol, `TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` hardcodes `paid_fee_on_l1 = Fee(1)` instead of the actual fee paid on L1. The consensus protobuf message `L1HandlerV0` carries no `paid_fee_on_l1` field, so the actual fee is silently dropped at the proposer's serialization boundary and replaced with a placeholder on the validator side. This is the direct Sequencer analog of the CrosschainDistributor bug: a fee value that must be forwarded through a cross-component call is not forwarded, and a hardcoded substitute is used instead.

### Finding Description

**Proposer serialization strips `paid_fee_on_l1`.**

When the proposer converts an `InternalConsensusTransaction::L1Handler` (which carries the real `paid_fee_on_l1` from the L1 scraper) to a `ConsensusTransaction::L1Handler` for streaming, it discards the fee:

```rust
// transaction_converter.rs line 178-180
InternalConsensusTransaction::L1Handler(tx) => {
    Ok(ConsensusTransaction::L1Handler(tx.tx))  // tx.tx is raw L1HandlerTransaction, no paid_fee_on_l1
}
```

The protobuf `L1HandlerV0` message confirms the field is absent from the wire format — it only carries `nonce`, `address`, `entry_point_selector`, and `calldata`:

```rust
// protoc_output.rs line 240-249
pub struct L1HandlerV0 {
    pub nonce: Option<Felt252>,
    pub address: Option<Address>,
    pub entry_point_selector: Option<Felt252>,
    pub calldata: Vec<Felt252>,
    // NO paid_fee_on_l1
}
```

**Validator reconstruction hardcodes `Fee(1)`.**

When the validator receives the consensus transaction and calls `convert_consensus_tx_to_internal_consensus_tx`, it reaches:

```rust
// transaction_converter.rs line 473-483
fn convert_consensus_l1_handler_to_internal_l1_handler(
    &self,
    tx: transaction::L1HandlerTransaction,
) -> TransactionConverterResult<executable_transaction::L1HandlerTransaction> {
    Ok(executable_transaction::L1HandlerTransaction::create(
        tx,
        &self.chain_id,
        // TODO(Gilad): Change this once we put real value in paid_fee_on_l1.
        Fee(1),
    )?)
}
```

The TODO comment explicitly acknowledges this is a placeholder with no real value.

**Blockifier fee check.**

The blockifier's only guard in `l1_handler_transaction.rs` (line 106) is:

```rust
if paid_fee == Fee(0) {
    return Err(TransactionExecutionError::TransactionFeeError(...));
}
```

`Fee(1)` satisfies `!= Fee(0)`, so the check passes unconditionally on the validator side regardless of what was actually paid on L1.

### Impact Explanation

The validator executes every L1 handler transaction with `paid_fee_on_l1 = Fee(1)`, never the actual value. This breaks the invariant that the executable transaction presented to the blockifier must faithfully represent the on-chain payment.

**Current impact (High — transaction conversion binds wrong executable payload):** The `paid_fee_on_l1` field of the `executable_transaction::L1HandlerTransaction` handed to the blockifier on the validator is always `Fee(1)`, not the value scraped from L1. This is a wrong value bound into the executable payload by the conversion path. If the blockifier check is tightened to `paid_fee >= actual_fee` (as the TODO implies), validators will accept L1 handler transactions that the proposer rejects, causing a consensus split: the proposer's block commitment will differ from the validator's because the validator will include transactions the proposer excluded.

**Edge-case divergence today:** If any L1 handler transaction reaches the proposer with `paid_fee_on_l1 = Fee(0)` (e.g., due to a scraper bug or a future protocol change), the proposer rejects it while the validator accepts it with the hardcoded `Fee(1)`, producing an immediate consensus divergence.

### Likelihood Explanation

Every L1 handler transaction processed by a validator node goes through this path. The trigger is unprivileged: any user sending a message from L1 to L2 causes an L1 handler transaction to be included in a block proposal. The hardcoded `Fee(1)` is always substituted. The current lenient check (`!= Fee(0)`) masks the divergence in the normal case, but the acknowledged TODO makes the tightened check a planned production change.

### Recommendation

1. Add `paid_fee_on_l1` to the `L1HandlerV0` protobuf message so it is transmitted through the consensus protocol.
2. Update `convert_consensus_l1_handler_to_internal_l1_handler` to use the received value instead of `Fee(1)`.
3. Update `convert_internal_consensus_tx_to_consensus_tx` to include `paid_fee_on_l1` when serializing `InternalConsensusTransaction::L1Handler`.

### Proof of Concept

1. User sends a message from L1 to L2 with `paid_fee_on_l1 = X` (any non-zero value).
2. L1 scraper stores the transaction with `paid_fee_on_l1 = X`.
3. Proposer fetches it from the L1 provider and executes it with `paid_fee_on_l1 = X`.
4. Proposer serializes it to `ConsensusTransaction::L1Handler` → `L1HandlerV0` protobuf (no `paid_fee_on_l1` field).
5. Validator receives `ConsensusTransaction::L1Handler` and calls `convert_consensus_l1_handler_to_internal_l1_handler`.
6. Validator constructs `executable_transaction::L1HandlerTransaction` with `paid_fee_on_l1 = Fee(1)`.
7. Blockifier check: `Fee(1) != Fee(0)` → passes.
8. Validator's executable transaction has `paid_fee_on_l1 = Fee(1)` ≠ proposer's `paid_fee_on_l1 = X`.

The corrupted field is `executable_transaction::L1HandlerTransaction::paid_fee_on_l1`, set to `Fee(1)` instead of the actual L1-paid fee, on every validator node for every L1 handler transaction. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L178-180)
```rust
            InternalConsensusTransaction::L1Handler(tx) => {
                Ok(ConsensusTransaction::L1Handler(tx.tx))
            }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L473-483)
```rust
    fn convert_consensus_l1_handler_to_internal_l1_handler(
        &self,
        tx: transaction::L1HandlerTransaction,
    ) -> TransactionConverterResult<executable_transaction::L1HandlerTransaction> {
        Ok(executable_transaction::L1HandlerTransaction::create(
            tx,
            &self.chain_id,
            // TODO(Gilad): Change this once we put real value in paid_fee_on_l1.
            Fee(1),
        )?)
    }
```

**File:** crates/apollo_protobuf/src/protobuf/protoc_output.rs (L240-249)
```rust
pub struct L1HandlerV0 {
    #[prost(message, optional, tag = "1")]
    pub nonce: ::core::option::Option<Felt252>,
    #[prost(message, optional, tag = "2")]
    pub address: ::core::option::Option<Address>,
    #[prost(message, optional, tag = "3")]
    pub entry_point_selector: ::core::option::Option<Felt252>,
    #[prost(message, repeated, tag = "4")]
    pub calldata: ::prost::alloc::vec::Vec<Felt252>,
}
```

**File:** crates/blockifier/src/transaction/l1_handler_transaction.rs (L103-113)
```rust
                        let paid_fee = self.paid_fee_on_l1;
                        // For now, assert only that any amount of fee was paid.
                        // The error message still indicates the required fee.
                        if paid_fee == Fee(0) {
                            return Err(TransactionExecutionError::TransactionFeeError(Box::new(
                                TransactionFeeError::InsufficientFee {
                                    paid_fee,
                                    actual_fee: receipt.fee,
                                },
                            )));
                        }
```

**File:** crates/starknet_api/src/executable_transaction.rs (L380-397)
```rust
#[derive(Clone, Debug, Default, Deserialize, Eq, PartialEq, Serialize, Hash)]
pub struct L1HandlerTransaction {
    pub tx: crate::transaction::L1HandlerTransaction,
    pub tx_hash: TransactionHash,
    pub paid_fee_on_l1: Fee,
}

impl L1HandlerTransaction {
    pub const L1_HANDLER_TYPE_NAME: &str = "L1_HANDLER";

    pub fn create(
        raw_tx: crate::transaction::L1HandlerTransaction,
        chain_id: &ChainId,
        paid_fee_on_l1: Fee,
    ) -> Result<L1HandlerTransaction, StarknetApiError> {
        let tx_hash = raw_tx.calculate_transaction_hash(chain_id, &raw_tx.version)?;
        Ok(Self { tx: raw_tx, tx_hash, paid_fee_on_l1 })
    }
```

**File:** crates/apollo_protobuf/src/converters/transaction.rs (L987-995)
```rust
impl From<L1HandlerTransaction> for protobuf::L1HandlerV0 {
    fn from(value: L1HandlerTransaction) -> Self {
        Self {
            nonce: Some(value.nonce.0.into()),
            address: Some(value.contract_address.into()),
            entry_point_selector: Some(value.entry_point_selector.0.into()),
            calldata: value.calldata.0.iter().map(|calldata| (*calldata).into()).collect(),
        }
    }
```
