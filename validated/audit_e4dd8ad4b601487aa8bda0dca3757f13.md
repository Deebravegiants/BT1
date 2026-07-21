### Title
Hardcoded `Fee(1)` in Consensus L1Handler Conversion Produces Wrong `paid_fee_on_l1` in Receipts and Bypasses Blockifier Fee Check - (`crates/apollo_transaction_converter/src/transaction_converter.rs`)

### Summary

`TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` unconditionally sets `paid_fee_on_l1 = Fee(1)` for every L1Handler transaction arriving through the consensus path. The actual fee paid on L1 is discarded. Because the blockifier's only fee guard for L1Handler transactions is `paid_fee == Fee(0)`, this hardcoded value always passes the check, and every resulting receipt carries the wrong fee value.

### Finding Description

In `crates/apollo_transaction_converter/src/transaction_converter.rs` the consensus-path conversion of L1Handler transactions is:

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
``` [1](#0-0) 

This is called from `convert_consensus_tx_to_internal_consensus_tx` for every `ConsensusTransaction::L1Handler`: [2](#0-1) 

The resulting `L1HandlerTransaction` struct carries `paid_fee_on_l1: Fee(1)` regardless of what was actually paid on L1: [3](#0-2) 

The blockifier's only fee guard for L1Handler execution is:

```rust
if paid_fee == Fee(0) {
    return Err(TransactionExecutionError::TransactionFeeError(...));
}
``` [4](#0-3) 

Since `Fee(1) != Fee(0)`, this check always passes. The `paid_fee_on_l1` field is then embedded in the `TransactionReceipt` produced by `TransactionReceipt::from_l1_handler`, so every L1Handler receipt emitted by the sequencer carries `paid_fee_on_l1 = 1` instead of the actual amount paid on L1.

### Impact Explanation

Every L1Handler transaction executed through the consensus path produces a receipt with `paid_fee_on_l1 = Fee(1)`. This is wrong receipt/event data for every L1→L2 message processed by the sequencer. Applications, bridges, and monitoring tools that read `paid_fee_on_l1` from receipts receive a systematically incorrect value. Additionally, the blockifier's fee guard — intended to reject zero-fee L1Handler transactions — is permanently bypassed for the consensus path, meaning the guard provides no protection regardless of what was actually paid on L1.

This maps to the allowed impact: **"Critical. Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input"** and **"High. Transaction conversion or signature/hash logic binds the wrong signer, hash, type, or executable payload."**

### Likelihood Explanation

Every L1Handler transaction processed through the consensus path (i.e., all L1→L2 messages in normal sequencer operation) is affected. No special attacker action is required; the wrong value is injected unconditionally by the converter. The L1 contract does validate that a non-zero fee is paid on L1, which limits the economic exploitation of the bypassed blockifier check, but the wrong receipt data is produced for every such transaction regardless.

### Recommendation

1. Propagate the actual `paid_fee_on_l1` through the consensus transaction type. The `ConsensusTransaction::L1Handler` variant currently carries only `transaction::L1HandlerTransaction` (which has no fee field); it should be extended to carry the fee, or the fee should be looked up from the L1 event store at conversion time.
2. Until the above is implemented, at minimum add an assertion or metric that fires when `paid_fee_on_l1` is set to the placeholder value, so the issue is visible in production.
3. Resolve the `TODO(Gilad)` comment before the consensus path is used in production for L1Handler transactions.

### Proof of Concept

1. Submit an L1→L2 message on L1 paying a fee of, e.g., `1 ETH`.
2. The L1 event scraper picks up the message and creates an `L1HandlerTransaction` with `paid_fee_on_l1 = 1 ETH`.
3. The transaction enters the mempool and is included in a consensus proposal as `ConsensusTransaction::L1Handler(tx)`.
4. The validator node calls `convert_consensus_tx_to_internal_consensus_tx`, which calls `convert_consensus_l1_handler_to_internal_l1_handler`, setting `paid_fee_on_l1 = Fee(1)`.
5. The blockifier executes the transaction; the check `paid_fee == Fee(0)` passes (since `Fee(1) != Fee(0)`).
6. The resulting receipt contains `paid_fee_on_l1 = 1` (one FRI unit) instead of `1 ETH`.
7. Any RPC call to `starknet_getTransactionReceipt` for this transaction returns the wrong fee value. [1](#0-0) [4](#0-3)

### Citations

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L197-201)
```rust
            ConsensusTransaction::L1Handler(tx) => {
                let internal_tx = self.convert_consensus_l1_handler_to_internal_l1_handler(tx)?;
                Ok((InternalConsensusTransaction::L1Handler(internal_tx), None))
            }
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

**File:** crates/starknet_api/src/executable_transaction.rs (L381-406)
```rust
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

    pub fn payload_size(&self) -> usize {
        // The calldata includes the "from" field, which is not a part of the payload.
        // `saturating_sub` guards the empty-calldata case (which would otherwise underflow to
        // `usize::MAX` in release): `L1HandlerTransaction` derives `Deserialize` and `Calldata`
        // has no non-empty invariant.
        self.tx.calldata.0.len().saturating_sub(1)
    }
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
