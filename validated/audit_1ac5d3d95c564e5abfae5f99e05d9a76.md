### Title
Receipt Size Limit Bypass via Post-Validation `output_data_receivers` Mutation - (File: `runtime/runtime/src/lib.rs`)

### Summary
The external report describes a **validate-then-use mismatch**: data is checked in one form (raw JSON string shown to user) but processed in a different form after transformation (JSON parser removes duplicate keys). The analog in nearcore is a **validate-then-mutate** pattern: a new receipt is size-validated before `output_data_receivers` are appended to it, allowing an unprivileged contract to produce receipts that exceed `max_receipt_size` and enter the protocol state.

### Finding Description
In `runtime/runtime/src/lib.rs`, after a new receipt is created by a function call and passes `validate_receipt()` with `ValidateReceiptMode::NewReceipt` (which enforces the `max_receipt_size = 4 MiB` hard limit), the runtime appends `output_data_receivers` from the parent receipt to the new receipt:

```rust
// runtime/runtime/src/lib.rs lines 1019-1037
if !action_receipt.output_data_receivers().is_empty() {
    if let Ok(ReturnData::ReceiptIndex(receipt_index)) = result.result {
        match result.new_receipts.get_mut(receipt_index as usize)...
            ReceiptEnum::Action(new_action_receipt) | ... => new_action_receipt
                .output_data_receivers
                .extend_from_slice(&action_receipt.output_data_receivers()),
```

This mutation happens **after** `validate_receipt()` has already passed the size check. A contract can craft a receipt at exactly `max_receipt_size` (passing validation), then use `promise_return` to trigger the `output_data_receivers` append, pushing the receipt over the limit.

The size check in `validate_receipt()` is only applied in `NewReceipt` mode:

```rust
// runtime/runtime/src/verifier.rs lines 533-541
if mode == ValidateReceiptMode::NewReceipt {
    let receipt_size: u64 = borsh::object_length(receipt)...;
    if receipt_size > limit_config.max_receipt_size {
        return Err(ReceiptValidationError::ReceiptSizeExceeded { ... });
    }
}
```

When the oversized receipt is later received by the target shard, it is validated with `ValidateReceiptMode::ExistingReceipt`, which **skips the size check entirely**:

```rust
// runtime/runtime/src/lib.rs lines 2512-2518
validate_receipt(
    &processing_state.apply_state.config.wasm_config.limit_config,
    receipt,
    protocol_version,
    ValidateReceiptMode::ExistingReceipt,  // size check skipped
)
```

The codebase explicitly acknowledges this bug (referenced as issue #12606) and added the `ExistingReceipt` mode and a `try_forward` size-capping workaround specifically to prevent the oversized receipt from getting stuck:

```rust
// runtime/runtime/src/congestion_control.rs lines 413-427
// There is a bug which allows to create receipts that are above the size limit.
// Let's pretend that all receipts are at most `max_receipt_size` to avoid receipts getting stuck.
// See https://github.com/near/nearcore/issues/12606
if size > max_receipt_size {
    size = max_receipt_size;
}
```

### Impact Explanation
An unprivileged user who deploys a contract can produce outgoing receipts that exceed `max_receipt_size` and are accepted into the protocol state. The receipt size limit exists to keep `ChunkStateWitness` sizes manageable (target: under 17 MiB). Oversized receipts are included in `source_receipt_proofs` within the state witness. In the worst case, a receipt just over 4 MiB combined with other witness data could push the total witness over the size limit, causing chunk validators to compute a different result than the chunk producer, breaking chunk endorsement and stalling finality for that shard. The concrete corrupted protocol value is the **outgoing receipts root** and **state witness size**, which can diverge from what the protocol's size invariant guarantees.

### Likelihood Explanation
Medium. The attacker must deploy a contract, call it with a crafted promise DAG (`promise_then` + `promise_return`), and size the inner receipt's args to exactly fill `max_receipt_size` minus the base receipt overhead. This is straightforward for any contract developer. The test `test_max_receipt_size_promise_return` in `test-loop-tests/src/tests/max_receipt_size.rs` demonstrates the exact exploit path and confirms the oversized receipt enters the protocol.

### Recommendation
Move the receipt size validation to occur **after** `output_data_receivers` have been appended, not before. Alternatively, validate the final receipt size at the point where new receipts are pushed into `result.new_receipts`, after all mutations are complete. The `ValidateReceiptMode::ExistingReceipt` bypass should remain for backward compatibility with pre-existing receipts, but new receipts generated in the current chunk must be validated against their final, post-mutation size.

### Proof of Concept
The exploit path is:
1. Deploy a contract with a method that calls `promise_then(A, self, "mark_test_completed")` and inside A calls `promise_return(C)` where C has args sized to exactly `max_receipt_size - base_receipt_overhead`.
2. When A executes, the runtime creates receipt C at exactly `max_receipt_size` — passes `NewReceipt` size validation.
3. The runtime then appends `output_data_receivers` (from the `then` chain) to C's receipt, pushing it over `max_receipt_size`.
4. The oversized receipt is forwarded cross-shard and processed with `ExistingReceipt` mode (no size check).

This is confirmed by the existing test at: [1](#0-0) 

The validate-then-mutate root cause: [2](#0-1) 

The size check that is bypassed: [3](#0-2) 

The `ExistingReceipt` mode that skips the size check on the receiving shard: [4](#0-3) 

The `ExistingReceipt` mode used when processing incoming receipts: [5](#0-4) 

The congestion control workaround acknowledging the bug: [6](#0-5)

### Citations

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-128)
```rust
// A function call will generate a new receipt. Size of this receipt will be equal to
// `max_receipt_size`, it'll pass validation, but then `output_data_receivers` will be modified and
// the receipt's size will go above max_receipt_size. The receipt should be rejected, but currently
// isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
// Runtime shouldn't die when it encounters a receipt with size above `max_receipt_size`.
```

**File:** runtime/runtime/src/lib.rs (L1019-1037)
```rust
        if !action_receipt.output_data_receivers().is_empty() {
            if let Ok(ReturnData::ReceiptIndex(receipt_index)) = result.result {
                // Modifying a new receipt instead of sending data
                match result
                    .new_receipts
                    .get_mut(receipt_index as usize)
                    .expect("the receipt for the given receipt index should exist")
                    .receipt_mut()
                {
                    ReceiptEnum::Action(new_action_receipt)
                    | ReceiptEnum::PromiseYield(new_action_receipt) => new_action_receipt
                        .output_data_receivers
                        .extend_from_slice(&action_receipt.output_data_receivers()),
                    ReceiptEnum::ActionV2(new_action_receipt)
                    | ReceiptEnum::PromiseYieldV2(new_action_receipt) => new_action_receipt
                        .output_data_receivers
                        .extend_from_slice(&action_receipt.output_data_receivers()),
                    _ => unreachable!("the receipt should be an action receipt"),
                }
```

**File:** runtime/runtime/src/lib.rs (L2512-2518)
```rust
            validate_receipt(
                &processing_state.apply_state.config.wasm_config.limit_config,
                receipt,
                protocol_version,
                ValidateReceiptMode::ExistingReceipt,
            )
            .map_err(RuntimeError::ReceiptValidationError)?;
```

**File:** runtime/runtime/src/verifier.rs (L533-542)
```rust
    if mode == ValidateReceiptMode::NewReceipt {
        let receipt_size: u64 =
            borsh::object_length(receipt).unwrap().try_into().expect("Can't convert usize to u64");
        if receipt_size > limit_config.max_receipt_size {
            return Err(ReceiptValidationError::ReceiptSizeExceeded {
                size: receipt_size,
                limit: limit_config.max_receipt_size,
            });
        }
    }
```

**File:** runtime/runtime/src/verifier.rs (L573-586)
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ValidateReceiptMode {
    /// Used for validating new receipts that were just created.
    /// More strict than `OldReceipt` mode, which has to handle older receipts.
    NewReceipt,
    /// Used for validating older receipts that were saved in the state/received. Less strict than
    /// NewReceipt validation. Tolerates some receipts that wouldn't pass new validation. It has to
    /// be less strict because:
    /// 1) Older receipts might have been created before new validation rules.
    /// 2) There is a bug which allows to create receipts that are above the size limit. Runtime has
    ///    to handle them gracefully until the receipt size limit bug is fixed.
    ///    See https://github.com/near/nearcore/issues/12606 for details.
    ExistingReceipt,
}
```

**File:** runtime/runtime/src/congestion_control.rs (L413-427)
```rust
        // There is a bug which allows to create receipts that are above the size limit. Receipts
        // above the size limit might not fit under the maximum outgoing size limit. Let's pretend
        // that all receipts are at most `max_receipt_size` to avoid receipts getting stuck.
        // See https://github.com/near/nearcore/issues/12606
        let max_receipt_size = apply_state.config.wasm_config.limit_config.max_receipt_size;
        if size > max_receipt_size {
            tracing::debug!(
                target: "runtime",
                receipt_id=?receipt.receipt_id(),
                size,
                max_receipt_size,
                "try_forward observed a receipt with size exceeding the size limit",
            );
            size = max_receipt_size;
        }
```
