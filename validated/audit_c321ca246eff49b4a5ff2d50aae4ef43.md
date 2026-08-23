### Title
Receipt size cap (`max_receipt_size`) is not actually enforced because validation runs before `output_data_receivers` are appended, allowing oversized receipts into the system - (File: `runtime/runtime/src/lib.rs`, `runtime/runtime/src/verifier.rs`, `runtime/runtime/src/congestion_control.rs`)

### Summary
This is the same bug class as the OmoVault report: a hard cap is declared (`supplyCap` there, `max_receipt_size`/`LimitConfig::max_receipt_size` here) but is not enforced on the code path that actually matters, letting the guarded quantity exceed the configured maximum. In nearcore, `validate_receipt` checks a new receipt's serialized size against `limit_config.max_receipt_size` at receipt-creation time, but the receipt is subsequently mutated (its `output_data_receivers` are extended) *after* that check, so the final receipt committed to state/forwarded across shards can be larger than the enforced cap.

### Finding Description
`validate_receipt` performs the size check only `if mode == ValidateReceiptMode::NewReceipt`, comparing the borsh-serialized size of the receipt to `limit_config.max_receipt_size` and returning `ReceiptValidationError::ReceiptSizeExceeded` if it is exceeded: [1](#0-0) 

However, in `Runtime::process_action_receipt` (`lib.rs`), after the receipt executes, if the *executing* action receipt has `output_data_receivers`, the runtime extends the `output_data_receivers` of an already-created new receipt (found via `ReturnData::ReceiptIndex`) with additional entries — this mutation happens after the new receipt has already been produced and can push its size above `max_receipt_size`: [2](#0-1) 

The comment attached to `ValidateReceiptMode::ExistingReceipt` explicitly documents that this is a known unresolved bug (tracked as near/nearcore#12606): "There is a bug which allows to create receipts that are above the size limit. Runtime has to handle them gracefully until the receipt size limit bug is fixed." [3](#0-2) 

Downstream, `ReceiptSinkV2::try_forward` (congestion control) has to work around this by clamping the receipt's counted size to `max_receipt_size` for limit-accounting purposes, while still forwarding the oversized receipt itself: [4](#0-3) 

This exactly mirrors the OmoVault pattern: a cap variable/config exists and is checked in one function, but a later mutation in the same logical flow (deposit/mint in OmoVault; `output_data_receivers` extension in nearcore) is not re-validated against the cap, so the cap is silently bypassed for the "real" quantity that matters (final receipt bytes on-chain vs. final vault assets).

### Impact Explanation
Impact is Low, matching the original report's low/high severity split, because:
- The oversized receipt is still gracefully handled by the runtime (it does not crash), and forwarding logic clamps the *counted* size to `max_receipt_size` so congestion/bandwidth accounting does not literally overflow its own limits — this is an explicit mitigation already in place.
- However, the actual on-wire/on-disk receipt bytes still exceed the protocol's configured `max_receipt_size`, meaning a size invariant that other subsystems (chunk witness size limits, state sync, per-receipt storage proof limits) may rely on is violated. This creates a latent risk of larger-than-expected state witnesses or storage/trie entries whenever this path is exercised, and is exactly the kind of "free or underpriced… storage" / limit-bypass class the validation rules ask to accept.

### Likelihood Explanation
Likelihood is High and unprivileged: this is reachable by any account submitting a function-call transaction that creates a promise chain returning a `ReceiptIndex` (`promise_return`) or a large return value routed to `output_data_receivers`, both of which are ordinary, permissionless contract-execution patterns. The nearcore test suite itself demonstrates the trigger is trivially exercisable via a deployed test contract and two follow-up transactions: [5](#0-4) [6](#0-5) 

### Recommendation
Re-validate (or re-size-check) the receipt against `limit_config.max_receipt_size` *after* `output_data_receivers` are appended in `Runtime::process_action_receipt`, before the receipt is emitted as a new/outgoing receipt, instead of only checking size at initial creation time in `validate_receipt`. Alternatively, account for the maximum possible `output_data_receivers` growth before the initial size check so the check is conservative. This closes the gap referenced by nearcore issue #12606 rather than continuing to paper over it with size-clamping in the congestion-control forwarding path.

### Proof of Concept
The existing nearcore test-loop tests are themselves a proof of concept for this bug, explicitly noting in comments that the receipt "should be rejected, but currently isn't because of a bug": [7](#0-6) [8](#0-7) 

Both tests: (1) deploy a test contract, (2) construct a receipt whose base size is exactly at `max_receipt_size` (4,194,304 bytes) so it passes the initial `validate_receipt` check, (3) trigger a `promise_return`/large value-return which causes `output_data_receivers` to be appended post-validation, and (4) assert (`assert_oversized_receipt_occurred`) that an oversized receipt occurred rather than the transaction being rejected — confirming the cap is not enforced end-to-end.

**Note on confidence:** I was unable to fully trace every call site of `validate_receipt` (a regex search failed and could not be re-run due to iteration limits), so I cannot state with certainty whether `ValidateReceiptMode::NewReceipt` is invoked anywhere *after* the `output_data_receivers` extension in `lib.rs`. Based on the explicit code comments and the dedicated regression tests referencing GitHub issue #12606, however, the codebase itself confirms this cap-bypass is real and currently only mitigated (not fixed) downstream in congestion control.

### Citations

**File:** runtime/runtime/src/verifier.rs (L526-542)
```rust
/// Validates a given receipt. Checks validity of the Action or Data receipt.
pub(crate) fn validate_receipt(
    limit_config: &LimitConfig,
    receipt: &Receipt,
    current_protocol_version: ProtocolVersion,
    mode: ValidateReceiptMode,
) -> Result<(), ReceiptValidationError> {
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

**File:** runtime/runtime/src/lib.rs (L1092-1116)
```rust
        // Generating outgoing data
        // A {
        // B().then(C())}  B--data receipt->C

        // A {
        // B(); 42}
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

**File:** runtime/runtime/src/congestion_control.rs (L403-427)
```rust
    fn try_forward(
        receipt: Receipt,
        gas: Gas,
        mut size: u64,
        shard: ShardId,
        outgoing_limit: &mut HashMap<ShardId, OutgoingLimit>,
        outgoing_receipts: &mut Vec<Receipt>,
        apply_state: &ApplyState,
        stats: &mut ReceiptSinkStats,
    ) -> Result<ReceiptForwarding, RuntimeError> {
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

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L210-267)
```rust
/// Return a value that is as large as max_receipt_size. The value will be wrapped in a data receipt
/// and the data receipt will be bigger than max_receipt_size. The receipt should be rejected, but
/// currently isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
/// Creates the following promise DAG:
/// A[self.return_large_value()] -then-> B[self.mark_test_completed()]
#[test]
fn test_max_receipt_size_value_return() {
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

    let max_receipt_size = 4_194_304;

    // Call the contract
    let large_receipt_tx = SignedTransaction::call(
        102,
        account.clone(),
        account.clone(),
        &account_signer,
        Balance::ZERO,
        "max_receipt_size_value_return_method".into(),
        format!("{{\"value_size\": {}}}", max_receipt_size).into(),
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
