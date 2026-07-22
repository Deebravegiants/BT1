### Title
Hardcoded `paid_fee_on_l1 = Fee(1)` in `TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` Produces Wrong Fee Value in Cende Blob and Execution Path — (`File: crates/apollo_transaction_converter/src/transaction_converter.rs`)

---

### Summary

`TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` unconditionally substitutes `Fee(1)` for the actual L1-paid fee when a validator converts a consensus-received `L1HandlerTransaction` into its executable form. This is the direct sequencer analog of M-08: a conversion function returns a fixed partial value instead of the real one, causing every downstream consumer — the blockifier fee guard, the cende blob, and the centralized recorder — to operate on a fabricated fee rather than the value attested on L1.

---

### Finding Description

When the validator's `TransactionConverter` receives an `L1HandlerTransaction` from the proposer over the consensus wire, it calls:

```rust
// crates/apollo_transaction_converter/src/transaction_converter.rs  lines 473-483
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

The `paid_fee_on_l1` field is hardcoded to `Fee(1)` for every L1 handler transaction that arrives through consensus, regardless of what was actually paid on L1.

The resulting `executable_transaction::L1HandlerTransaction` (with `paid_fee_on_l1 = Fee(1)`) is then:

1. **Executed by the blockifier**, which checks:
   ```rust
   // crates/blockifier/src/transaction/l1_handler_transaction.rs  lines 103-113
   let paid_fee = self.paid_fee_on_l1;
   if paid_fee == Fee(0) {
       return Err(TransactionExecutionError::TransactionFeeError(...));
   }
   ```
   Because `Fee(1) ≠ Fee(0)`, the guard always passes — even for transactions whose real `paid_fee_on_l1` was zero.

2. **Serialized into the cende blob** via `CentralL1HandlerTransaction`:
   ```rust
   // crates/apollo_consensus_orchestrator/src/cende/central_objects.rs  lines 383-393
   impl From<L1HandlerTransaction> for CentralL1HandlerTransaction {
       fn from(tx: L1HandlerTransaction) -> CentralL1HandlerTransaction {
           CentralL1HandlerTransaction {
               ...
               paid_fee_on_l1: tx.paid_fee_on_l1,   // always Fee(1) on the validator
               ...
           }
       }
   }
   ```
   The centralized recorder therefore receives `paid_fee_on_l1 = Fee(1)` for every L1 handler transaction committed by a validator node.

The proposer path is unaffected: it obtains L1 handler transactions from the L1 provider with the real `paid_fee_on_l1`. The divergence is exclusive to the **validator conversion path** (`convert_consensus_tx_to_internal_consensus_tx` → `convert_consensus_l1_handler_to_internal_l1_handler`).

---

### Impact Explanation

**High — Transaction conversion binds the wrong executable payload; authoritative-looking wrong value propagates to the cende blob and RPC.**

- The blockifier's only fee guard for L1 handlers (`paid_fee == Fee(0)`) is bypassed for any L1 handler transaction that actually had `paid_fee_on_l1 = Fee(0)` on L1, because the validator substitutes `Fee(1)` before execution. A transaction that should be rejected as having paid zero fee is instead accepted and committed.
- The cende blob written to Aerospike carries `paid_fee_on_l1 = Fee(1)` for all L1 handler transactions on validator nodes. The centralized recorder reconstructs block data from this blob; the `paid_fee_on_l1` field it stores is systematically wrong.
- Any RPC view or trace that surfaces `paid_fee_on_l1` for an L1 handler transaction will return `1` (the minimum non-zero `u128`) rather than the actual amount attested on L1, constituting an authoritative-looking wrong value.

---

### Likelihood Explanation

This is a **systematic, always-triggered** defect on every validator node for every L1 handler transaction included in any block. No special attacker input is required; normal block production with L1 handler transactions is sufficient. The TODO comment confirms the developers know the value is a placeholder, but the code is in production scope and the guard it bypasses (`paid_fee == Fee(0)`) is the only fee enforcement point for L1 handlers in the blockifier.

---

### Recommendation

Transmit `paid_fee_on_l1` in the consensus wire format. The `ConsensusTransaction::L1Handler` variant currently carries only the raw `transaction::L1HandlerTransaction` (which has no `paid_fee_on_l1` field). Add `paid_fee_on_l1: Fee` to the consensus protobuf `L1HandlerTransaction` message and propagate it through `convert_consensus_l1_handler_to_internal_l1_handler` instead of hardcoding `Fee(1)`. Until then, the validator cannot enforce the L1 fee invariant and will produce incorrect cende blobs.

---

### Proof of Concept

1. An L1 handler transaction is submitted on L1 with `paid_fee_on_l1 = Fee(0)` (or