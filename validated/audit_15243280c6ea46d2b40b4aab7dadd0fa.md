### Title
Receipt Size Limit Bypass via Post-Validation `output_data_receivers` Mutation After `promise_return` - (File: runtime/runtime/src/lib.rs)

### Summary

An unprivileged user can deploy a contract that crafts a receipt sized exactly at `max_receipt_size` (4 MB), passes the `NewReceipt` size validation, and then has additional `output_data_receivers` appended to it after validation via the `promise_return` mechanism. The resulting receipt exceeds `max_receipt_size` and is injected into the protocol state without being rejected, violating the invariant that all receipts must be below 4 MB.

### Finding Description

The NEAR runtime validates newly created receipts with `ValidateReceiptMode::NewReceipt` inside the per-action loop in `apply_action_receipt`. However, after this validation, the runtime performs a post-validation mutation: when a contract uses `promise_return(C)` and the parent receipt has `output_data_receivers` (i.e., a callback is waiting), the runtime appends those `output_data_receivers` to receipt C's `output_data_receivers` field.

The validation occurs at: [1](#0-0) 

The post-validation mutation occurs after the action loop completes: [2](#0-1) 

The size check in `validate_receipt` only runs in `NewReceipt` mode: [3](#0-2) 

When the oversized receipt arrives at the destination shard, it is validated with `ExistingReceipt` mode, which explicitly skips the size check: [4](#0-3) 

The codebase explicitly acknowledges this as a known bug (issue #12606) and has added workarounds in congestion control to avoid receipts getting stuck: [5](#0-4) 

And in bandwidth scheduling: [6](#0-5) 

The `max_receipt_size` limit exists specifically to bound `ChunkStateWitness` size. The bug is confirmed by an integration test that asserts an oversized receipt is produced and processed: [7](#0-6) 

### Impact Explanation

The `max_receipt_size` invariant (4 MB) is violated. Receipts above this limit are injected into the protocol state and processed by the runtime. The limit exists to keep `ChunkStateWitness` size bounded (documented target: under 17 MiB total). An oversized receipt directly inflates the witness beyond its expected bounds. The codebase has had to add multiple workarounds (in `try_forward` and `generate_bandwidth_request`) to prevent the oversized receipt from causing the bandwidth scheduler and congestion control to malfunction, confirming the protocol-level impact.

The corrupted protocol value is: the `max_receipt_size` invariant on receipts stored in and routed through the protocol state, and by extension the `ChunkStateWitness` size bound.

### Likelihood Explanation

Medium. An attacker must deploy a contract and craft a specific promise DAG: create promise A with a callback B, have A execute and create promise C with args sized to bring C exactly to `max_receipt_size`, then call `promise_return(C)`. This is a reproducible, deterministic exploit path demonstrated by the existing integration test. No validator or operator privileges are required — only the ability to deploy a contract and submit transactions.

### Recommendation

Perform the receipt size check **after** all post-execution mutations (including `output_data_receivers` propagation) rather than before. Specifically, the size validation of newly created receipts should occur after the `output_data_receivers` from the parent receipt are appended to the returned receipt, not inside the per-action loop before the merge. Similarly, the `DataReceipt` created from a large `value_return` should be size-checked after it is constructed.

### Proof of Concept

1. Deploy a contract with two methods: `method1` and `method2`.
2. `method1` creates promise A (`method2`) with callback B (`mark_test_completed`): `A -then-> B`.
3. `method2` creates promise C (`noop`) with args sized as `max_receipt_size - base_receipt_size` (so C is exactly at the 4 MB limit), then calls `promise_return(C)`.
4. The runtime validates C at creation time (passes, C == 4 MB), then appends B's `output_data_receivers` to C (C > 4 MB), and routes the oversized C to the destination shard.
5. The destination shard processes C with `ExistingReceipt` mode (no size check), and B's callback executes successfully.
6. An oversized receipt (above `max_receipt_size`) is confirmed in the chain's incoming receipts.

This exact scenario is demonstrated in: [8](#0-7)

### Citations

**File:** runtime/runtime/src/lib.rs (L855-866)
```rust
            if new_result.result.is_ok() {
                if let Err(e) = new_result.new_receipts.iter().try_for_each(|receipt| {
                    validate_receipt(
                        &apply_state.config.wasm_config.limit_config,
                        receipt,
                        apply_state.current_protocol_version,
                        ValidateReceiptMode::NewReceipt,
                    )
                }) {
                    new_result.result = Err(ActionErrorKind::NewReceiptValidationError(e).into());
                }
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

**File:** runtime/runtime/src/congestion_control.rs (L556-562)
```rust
        // There's a bug which allows to create receipts above `max_receipt_size` (https://github.com/near/nearcore/issues/12606).
        // This could cause problems with bandwidth scheduler which would generate requests for size above max size, and these
        // requests would never be fulfilled. For bandwidth requests let's pretend that all sizes are below `max_receipt_size`.
        // The same pretending logic is also present in `try_forward` which compares receipt size with outgoing limit.
        // This logic should also make it possible to do protocol upgrades that lower `max_receipt_size` without too much trouble.
        let sizes_iter = receipt_sizes_iter
            .map_ok(|group_size| std::cmp::min(group_size, params.max_receipt_size));
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-208)
```rust
// A function call will generate a new receipt. Size of this receipt will be equal to
// `max_receipt_size`, it'll pass validation, but then `output_data_receivers` will be modified and
// the receipt's size will go above max_receipt_size. The receipt should be rejected, but currently
// isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
// Runtime shouldn't die when it encounters a receipt with size above `max_receipt_size`.
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
