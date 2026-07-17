### Title
Receipt `max_receipt_size` Limit Bypassed via `promise_return` and `value_return` Code Paths, Allowing Oversized Receipts to Propagate - (`File: runtime/runtime/src/lib.rs`, `runtime/near-vm-runner/src/logic/logic.rs`)

### Summary

The NEAR runtime enforces a `max_receipt_size` limit on newly created receipts via `validate_receipt()` with `ValidateReceiptMode::NewReceipt`. However, two alternative code paths — `promise_return` (which appends `output_data_receivers` to an already-validated receipt after the size check) and `value_return` (which checks only the raw value length, not the total data receipt size) — allow an unprivileged contract to produce receipts that exceed `max_receipt_size`. This is an acknowledged bug (nearcore issue #12606) with a workaround in the congestion control layer, but the root cause remains unpatched.

### Finding Description

**Path 1 — `promise_return` bypass:**

When a contract executes `promise_return(C)` inside a promise chain `[A -then-> B]`, the runtime in `runtime/runtime/src/lib.rs` at lines 1019–1037 modifies receipt C's `output_data_receivers` by appending the parent receipt's receivers to it **after** receipt C has already passed the `NewReceipt` size check. A contract can craft receipt C to be exactly at `max_receipt_size` (4,194,304 bytes), pass validation, and then have its size pushed above the limit when `output_data_receivers` are appended.

**Path 2 — `value_return` bypass:**

In `runtime/near-vm-runner/src/logic/logic.rs` at lines 3877–3918, `value_return` checks the raw value length against `max_length_returned_data` (also 4,194,304 bytes). However, the resulting `DataReceipt` wraps the value in a struct with additional metadata (data_id, predecessor_id, receiver_id, etc.), making the total serialized receipt size exceed `max_receipt_size`. This oversized data receipt is never re-validated against the receipt size limit.

**The size check is only applied in `NewReceipt` mode:**

In `runtime/runtime/src/verifier.rs` at lines 533–542, the `max_receipt_size` check is gated on `mode == ValidateReceiptMode::NewReceipt`. The `ExistingReceipt` mode explicitly skips this check, with a comment acknowledging the bug.

**Congestion control workaround:**

In `runtime/runtime/src/congestion_control.rs` at lines 413–427, the `try_forward` function clamps oversized receipt sizes to `max_receipt_size` to prevent them from getting stuck in the outgoing buffer. Without this workaround, the oversized receipt would never satisfy the outgoing size limit check and would be permanently stuck in the buffer, bricking the promise chain.

### Impact Explanation

An unprivileged user can deploy a contract that produces receipts exceeding `max_receipt_size`. The concrete corrupted protocol value is the `max_receipt_size` invariant in the runtime state. Before the congestion control workaround was added, these receipts would get permanently stuck in the outgoing receipt buffer (because their actual size exceeded the outgoing size limit), bricking the promise chain for the affected account — analogous to the external report's "safe permanently bricked" outcome. The workaround mitigates the stuck-receipt consequence but does not fix the root cause: oversized receipts still enter the state and are propagated across shards, violating the protocol's size invariant.

### Likelihood Explanation

Any unprivileged user who can deploy a contract can trigger this. The attack requires crafting a contract that:
1. Creates a near-maximum-size receipt and calls `promise_return` on it inside a chained promise, or
2. Returns a value of size equal to `max_length_returned_data` in a promise chain.

Both paths are reachable via standard public RPC transactions. The test files `test_max_receipt_size_promise_return` and `test_max_receipt_size_value_return` confirm the bug is reproducible.

### Recommendation

1. After appending `output_data_receivers` to a receipt in the `promise_return` path, re-validate the receipt's total serialized size against `max_receipt_size` and fail the action if exceeded.
2. In `value_return`, check the total serialized size of the resulting `DataReceipt` (value + metadata) against `max_receipt_size`, not just the raw value length against `max_length_returned_data`.
3. Remove the size-clamping workaround in `try_forward` once the root cause is fixed.

### Proof of Concept

**Path 1 (`promise_return`):**

1. Deploy a contract with a method `method1` that:
   - Creates a promise chain `[A -then-> B]`
   - In promise A's execution, creates receipt C with `args_size = max_receipt_size - base_receipt_size` bytes (exactly at the limit)
   - Calls `promise_return(C)` — this causes the runtime to append B's `output_data_receivers` to C, pushing C above `max_receipt_size`
2. Submit a transaction calling `method1`.
3. Observe that receipt C is propagated with size > `max_receipt_size`.

This is exactly what `test_max_receipt_size_promise_return` in `test-loop-tests/src/tests/max_receipt_size.rs` demonstrates.

**Path 2 (`value_return`):**

1. Deploy a contract with a method that returns a value of exactly `max_receipt_size` bytes in a promise chain `[A -then-> B]`.
2. The resulting `DataReceipt` (value + `data_id` + predecessor/receiver IDs) exceeds `max_receipt_size`.
3. This is demonstrated by `test_max_receipt_size_value_return`.

**Key code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** runtime/near-vm-runner/src/logic/logic.rs (L3877-3888)
```rust
    pub fn value_return(&mut self, value_len: u64, value_ptr: u64) -> Result<()> {
        self.result_state.gas_counter.pay_base(base)?;
        let return_val = get_memory_or_register!(self, value_ptr, value_len)?;
        let mut burn_cost = ParameterCost::ZERO;
        let num_bytes = return_val.len() as u64;
        if num_bytes > self.config.limit_config.max_length_returned_data {
            return Err(HostError::ReturnedValueLengthExceeded {
                length: num_bytes,
                limit: self.config.limit_config.max_length_returned_data,
            }
            .into());
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

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-128)
```rust
// A function call will generate a new receipt. Size of this receipt will be equal to
// `max_receipt_size`, it'll pass validation, but then `output_data_receivers` will be modified and
// the receipt's size will go above max_receipt_size. The receipt should be rejected, but currently
// isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
// Runtime shouldn't die when it encounters a receipt with size above `max_receipt_size`.
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L210-213)
```rust
/// Return a value that is as large as max_receipt_size. The value will be wrapped in a data receipt
/// and the data receipt will be bigger than max_receipt_size. The receipt should be rejected, but
/// currently isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
/// Creates the following promise DAG:
```
