### Title
Receipt Size Cap Bypassed via `promise_return` + `output_data_receivers` Append After Validation - (File: `runtime/runtime/src/lib.rs`)

### Summary
The `max_receipt_size` limit is checked on a newly-created receipt **before** the runtime appends `output_data_receivers` to it during `promise_return` processing. This is the exact same bug class as the external report: a cap check is performed on the pre-update value, and the final mutation that pushes the value over the cap is never re-validated. An unprivileged user can deploy a contract that produces receipts exceeding `max_receipt_size`, corrupting the `receipt_bytes` field in `CongestionInfo` and violating the protocol's receipt-size invariant. The nearcore codebase explicitly acknowledges this as a known bug (GitHub issue #12606).

### Finding Description

In `runtime/runtime/src/verifier.rs`, `validate_receipt` with `ValidateReceiptMode::NewReceipt` checks the serialized size of a receipt against `limit_config.max_receipt_size`: [1](#0-0) 

This check is called during receipt creation inside the VM execution loop. However, in `runtime/runtime/src/lib.rs`, after the VM finishes executing an action receipt, the runtime checks whether the result is `ReturnData::ReceiptIndex` (i.e., the contract called `promise_return`). If the **parent** receipt had `output_data_receivers` (because it was part of a `.then()` chain), the runtime appends those receivers directly to the returned receipt: [2](#0-1) 

No re-validation of the receipt's size is performed after this `extend_from_slice`. The receipt that passed the size check at creation time now has additional `output_data_receivers` appended, making its serialized size exceed `max_receipt_size`. The codebase itself documents this as a bug: [3](#0-2) 

The same pattern applies to data receipts: when a contract returns a value of size exactly `max_receipt_size`, the resulting data receipt wraps that value and exceeds the limit without being rejected: [4](#0-3) 

The `ValidateReceiptMode::ExistingReceipt` mode was introduced specifically to tolerate these already-oversized receipts in the state: [5](#0-4) 

### Impact Explanation

The corrupted protocol value is the `receipt_bytes` field in `CongestionInfo`. The congestion control system tracks receipt sizes using `compute_receipt_size` at the time the receipt is stored, but for oversized receipts produced via `promise_return`, the tracked size is the pre-modification (under-limit) size, not the actual serialized size. This means:

1. **`CongestionInfo.receipt_bytes` is understated** for oversized receipts, causing the congestion control system to underestimate memory pressure on the receiving shard.
2. **The `max_receipt_size` invariant is violated**: receipts larger than `max_receipt_size` are forwarded to the network and must be processed by all validators.
3. The `try_forward` workaround in `congestion_control.rs` clamps the size to `max_receipt_size` to prevent receipts from getting stuck, but the receipt still exists and is processed: [6](#0-5) 

### Likelihood Explanation

Any unprivileged user can deploy a contract that:
1. Creates a promise chain `A.then(B)` so that receipt A has `output_data_receivers` pointing to B.
2. Inside A's execution, creates a new receipt C with args sized to exactly `max_receipt_size - base_receipt_size` bytes, then calls `promise_return(C)`.
3. The runtime appends A's `output_data_receivers` to C, making C exceed `max_receipt_size`.

This is demonstrated by the existing test contract method `max_receipt_size_promise_return_method1` and the integration test `test_max_receipt_size_promise_return`, which confirms the oversized receipt is produced and forwarded on-chain.

### Recommendation

After appending `output_data_receivers` to the returned receipt in `apply_action_receipt`, re-validate the receipt size. If the new size exceeds `max_receipt_size`, treat the execution as a failure (similar to how `ReceiptSizeExceeded` is returned for directly oversized receipts). This mirrors the fix described in the external report: check the cap **after** the final mutation, not before.

### Proof of Concept

The existing integration test `test_max_receipt_size_promise_return` in `test-loop-tests/src/tests/max_receipt_size.rs` is a complete proof of concept: [7](#0-6) 

The test deploys a contract, calls `max_receipt_size_promise_return_method1` with args sized to fill the receipt to exactly `max_receipt_size`, and then asserts via `assert_oversized_receipt_occurred` that an incoming receipt with size above `max_receipt_size` was observed on-chain — confirming the cap bypass is reachable by an unprivileged user through a normal signed transaction.

### Citations

**File:** runtime/runtime/src/verifier.rs (L533-541)
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

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-128)
```rust
// A function call will generate a new receipt. Size of this receipt will be equal to
// `max_receipt_size`, it'll pass validation, but then `output_data_receivers` will be modified and
// the receipt's size will go above max_receipt_size. The receipt should be rejected, but currently
// isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
// Runtime shouldn't die when it encounters a receipt with size above `max_receipt_size`.
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L129-208)
```rust
#[test]
fn test_max_receipt_size_promise_return() {
    init_test_logger();

    let account = create_account_id("account0");
    let account_signer = create_user_test_signer(&account);
    let mut env = TestLoopBuilder::new()
        .enable_rpc()
        .add_user_account(&account, Balance::from_near(10_000))
        .build();

    // Deploy the test contract
    let deploy_contract_tx = SignedTransaction::deploy_contract(
        101,
        &account,
        near_test_contracts::rs_contract().into(),
        &account_signer,
        env.rpc_node().head().last_block_hash,
    );
    env.rpc_runner().run_tx(deploy_contract_tx, Duration::seconds(5));

    // User calls a contract method
    // Contract method creates a DAG with two promises: [A -then-> B]
    // When promise A is executed, it creates a third promise - `C` and does a `promise_return`.
    // The DAG changes to: [C ->then-> B]
    // The receipt for promise C is a maximum size receipt.
    // Adding the `output_data_receivers` to C's receipt makes it go over the size limit.
    let base_receipt_template = Receipt::V0(ReceiptV0 {
        predecessor_id: account.clone(),
        receiver_id: account.clone(),
        receipt_id: CryptoHash::default(),
        receipt: ReceiptEnum::Action(ActionReceipt {
            signer_id: account.clone(),
            signer_public_key: account_signer.public_key().into(),
            gas_price: Balance::ZERO,
            output_data_receivers: vec![],
            input_data_ids: vec![],
            actions: vec![Action::FunctionCall(Box::new(FunctionCallAction {
                method_name: "noop".into(),
                args: vec![],
                gas: Gas::ZERO,
                deposit: Balance::ZERO,
            }))],
        }),
    });
    let base_receipt_template = action_receipt_v1_to_latest(&base_receipt_template);
    let base_receipt_size = borsh::object_length(&base_receipt_template).unwrap();
    let max_receipt_size = 4_194_304;
    let args_size = max_receipt_size - base_receipt_size;

    // Call the contract
    let large_receipt_tx = SignedTransaction::call(
        102,
        account.clone(),
        account.clone(),
        &account_signer,
        Balance::ZERO,
        "max_receipt_size_promise_return_method1".into(),
        format!("{{\"args_size\": {}}}", args_size).into(),
        Gas::from_teragas(300),
        env.rpc_node().head().last_block_hash,
    );
    env.rpc_runner().run_tx(large_receipt_tx, Duration::seconds(5));

    // Make sure that the last promise in the DAG was called
    let assert_test_completed = SignedTransaction::call(
        103,
        account.clone(),
        account,
        &account_signer,
        Balance::ZERO,
        "assert_test_completed".into(),
        "".into(),
        Gas::from_teragas(300),
        env.rpc_node().head().last_block_hash,
    );
    env.rpc_runner().run_tx(assert_test_completed, Duration::seconds(5));

    assert_oversized_receipt_occurred(&env.validator());
}
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L210-215)
```rust
/// Return a value that is as large as max_receipt_size. The value will be wrapped in a data receipt
/// and the data receipt will be bigger than max_receipt_size. The receipt should be rejected, but
/// currently isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
/// Creates the following promise DAG:
/// A[self.return_large_value()] -then-> B[self.mark_test_completed()]
#[test]
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
