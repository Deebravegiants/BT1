### Title
Hardcoded `paid_fee_on_l1 = Fee(1)` in Consensus L1 Handler Conversion Produces Wrong Execution Result — (`crates/apollo_transaction_converter/src/transaction_converter.rs`)

### Summary

`TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` unconditionally injects `paid_fee_on_l1 = Fee(1)` for every L1 handler transaction arriving through the consensus (validator) path. The blockifier's `L1HandlerTransaction::execute_raw` enforces `paid_fee != Fee(0)`. Because `Fee(1)` always satisfies that guard, the validator silently accepts any L1 handler regardless of the actual fee paid on L1, and the wrong value propagates into the cende blob sent to the centralized pipeline.

### Finding Description

When a validator node receives a `ConsensusTransaction::L1Handler` over P2P, `convert_consensus_tx_to_internal_consensus_tx` dispatches to:

```rust
// crates/apollo_transaction_converter/src/transaction_converter.rs:473-483
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

The blockifier's execution path then checks:

```rust
// crates/blockifier/src/transaction/l1_handler_transaction.rs:103-113
let paid_fee = self.paid_fee_on_l1;
if paid_fee == Fee(0) {
    return Err(TransactionExecutionError::TransactionFeeError(Box::new(
        TransactionFeeError::InsufficientFee {
            paid_fee,
            actual_fee: receipt.fee,
        },
    )));
}
``` [2](#0-1) 

Because `Fee(1) != Fee(0)`, the guard is always bypassed on the validator side. The proposer, by contrast, obtains the real `paid_fee_on_l1` from the L1 provider and uses it verbatim. If the real value is `Fee(0)` (theoretically possible if the L1 contract enforcement is absent or bypassed), the proposer rejects the transaction while the validator accepts it — a divergent execution result.

Even when the real fee is non-zero, the wrong value `Fee(1)` is serialised into `CentralL1HandlerTransaction.paid_fee_on_l1` inside the cende blob:

```rust
// crates/apollo_consensus_orchestrator/src/cende/central_objects.rs:383-393
impl From<L1HandlerTransaction> for CentralL1HandlerTransaction {
    fn from(tx: L1HandlerTransaction) -> CentralL1HandlerTransaction {
        CentralL1HandlerTransaction {
            ...
            paid_fee_on_l1: tx.paid_fee_on_l1

### Citations

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
