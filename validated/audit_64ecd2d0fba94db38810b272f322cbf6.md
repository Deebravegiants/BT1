### Title
L1 Handler Fee Validation Accepts Any Positive `paid_fee_on_l1` Regardless of Actual Execution Cost — (`crates/blockifier/src/transaction/l1_handler_transaction.rs`)

### Summary

The `execute_raw` implementation for `L1HandlerTransaction` checks only that `paid_fee_on_l1 != 0` before accepting the transaction. Any positive fee — even `Fee(1)` — passes the check regardless of the actual execution cost computed in `receipt.fee`. This is the direct sequencer analog of the external `mintWithEth()` bug: both use a loose `>=` / `!= 0` guard instead of enforcing that the supplied payment actually covers the required amount.

### Finding Description

After a successful L1 handler execution, the fee adequacy check in `execute_raw` is:

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
``` [1](#0-0) 

The guard fires only when `paid_fee == Fee(0)`. Any value `>= 1` passes unconditionally. The `InsufficientFee` error variant is explicitly typed as `{ paid_fee: Fee, actual_fee: Fee }` and its message reads *"Actual fee ({}) exceeded paid fee on L1 ({})"*, confirming the intended invariant is `paid_fee >= actual_fee` — but the code never enforces it. [2](#0-1) 

The test suite explicitly documents this gap:

```rust
// Today, we check that the paid_fee is positive, no matter what was the actual fee.
let tx_no_fee = l1handler_tx(Fee(0), contract_address);
let error = tx_no_fee.execute(state, block_context).unwrap_err();
``` [3](#0-2) 

### Impact Explanation

An L1 handler transaction with `paid_fee_on_l1 = Fee(1)` (1 wei) is accepted and fully executed on L2 even when the actual L2 execution cost (`receipt.fee`) is orders of magnitude larger. The sequencer absorbs the difference. This is an **incorrect fee accounting with economic impact** — the exact impact class listed as Critical in the scope.

The `l1_handler_tx_execution_info` helper always zeroes out the on-chain fee field, so no STRK is charged on L2; the only intended compensation is the ETH paid on L1. When that ETH amount is far below the actual L2 cost, the protocol is economically exploited. [4](#0-3) 

### Likelihood Explanation

Any user can send an L1→L2 message to the Starknet core contract with an arbitrarily small ETH value. The sequencer's own comment acknowledges the check is intentionally weak ("covered by the starknet core contract"), but the L1 contract enforces only that *some* ETH is attached — it does not know the L2 execution cost in advance. The gap between L1 enforcement and L2 actual cost is the attack surface. The root cause is entirely within this repository.

### Recommendation

Replace the zero-only guard with a proper sufficiency check:

```rust
// Before:
if paid_fee == Fee(0) { ... }

// After:
if paid_fee < receipt.fee {
    return Err(TransactionExecutionError::TransactionFeeError(Box::new(
        TransactionFeeError::InsufficientFee {
            paid_fee,
            actual_fee: receipt.fee,
        },
    )));
}
```

This matches the semantics already encoded in the `InsufficientFee` error variant and the existing test infrastructure.

### Proof of Concept

1. Construct an `L1HandlerTransaction` with `paid_fee_on_l1 = Fee(1)`.
2. Execute it against a block context where the handler writes storage (non-trivial L2 cost).
3. Observe that `execute_raw` returns `Ok(...)` — the transaction is committed and state changes are applied — despite `paid_fee (1) << receipt.fee (actual cost)`.
4. The existing test `l1handler_tx(Fee(0), ...)` confirms `Fee(0)` is rejected; substituting `Fee(1)` for the same workload will succeed, demonstrating the gap. [5](#0-4)

### Citations

**File:** crates/blockifier/src/transaction/l1_handler_transaction.rs (L97-115)
```rust
                match fee_check_report {
                    Ok(()) => {
                        // Post-execution check passed, commit the execution.
                        execution_state.commit();
                        // TODO(Arni): Consider removing this check. It is covered by the starknet
                        // core contract.
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

                        Ok(l1_handler_tx_execution_info(execute_call_info, receipt, None))
```

**File:** crates/blockifier/src/transaction/l1_handler_transaction.rs (L146-158)
```rust
fn l1_handler_tx_execution_info(
    execute_call_info: Option<CallInfo>,
    mut receipt: TransactionReceipt,
    revert_error: Option<RevertError>,
) -> TransactionExecutionInfo {
    receipt.fee = Fee(0);
    TransactionExecutionInfo {
        validate_call_info: None,
        execute_call_info,
        fee_transfer_call_info: None,
        receipt,
        revert_error,
    }
```

**File:** crates/blockifier/src/transaction/errors.rs (L49-50)
```rust
    #[error("Actual fee ({}) exceeded paid fee on L1 ({}).", actual_fee.0, paid_fee.0)]
    InsufficientFee { paid_fee: Fee, actual_fee: Fee },
```

**File:** crates/blockifier/src/transaction/transactions_test.rs (L2946-2948)
```rust
    let tx_no_fee = l1handler_tx(Fee(0), contract_address);
    let error = tx_no_fee.execute(state, block_context).unwrap_err(); // Do not charge fee as L1Handler's resource bounds (/max fee) is 0.
    // Today, we check that the paid_fee is positive, no matter what was the actual fee.
```
