### Title
Oversized-receipt clamp in `ReceiptSinkV2::try_forward` lets an unprivileged contract call desynchronize bandwidth-limit accounting from actual receipt size - (File: `runtime/runtime/src/congestion_control.rs`)

### Summary
An unprivileged account can trigger a contract execution path (already demonstrated by in-repo tests) that produces a receipt whose real borsh size exceeds `wasm_config.limit_config.max_receipt_size` because the size check is performed before `output_data_receivers`/return-value data are attached, not after. When such an oversized receipt reaches `ReceiptSinkV2::try_forward`, its size is clamped down to `max_receipt_size` purely for admission/limit-decrement purposes, so the per-link `OutgoingLimit.size` (driven by the bandwidth scheduler grant) is decremented by less than the receipt's true byte size.

### Finding Description
The size-limit bypass at receipt-creation time is a pre-existing, code-acknowledged bug (linked to `https://github.com/near/nearcore/issues/12606`) and is exercised by the repo's own tests: `test_max_receipt_size_promise_return` and `test_max_receipt_size_value_return` in `test-loop-tests/src/tests/max_receipt_size.rs` build a promise DAG where a receipt passes the size check at exactly `max_receipt_size`, but is later grown by `output_data_receivers`/a large returned value beyond the configured limit — all reachable purely via ordinary `FunctionCall` actions through public RPC [1](#0-0) .

Once such a receipt is buffered and later drained via `forward_from_buffer_to_shard`, or admitted directly via `forward_or_buffer_receipt`, it is passed into `ReceiptSinkV2::try_forward`, where the comment explicitly states this is a "bug workaround for oversized receipts": if `size > max_receipt_size`, the local `size` used for the admission comparison and for decrementing `forward_limit.size` is clamped to `max_receipt_size` [2](#0-1) . The forward decision and limit decrement then use this clamped value: `forward_limit.size -= size;` [3](#0-2) .

Because `forward_limit.size` derives from `bandwidth_scheduler_output.granted_bandwidth.get_granted_bandwidth(...)` set up per chunk in `ReceiptSink::new` [4](#0-3) , an oversized receipt consumes less of the granted per-link byte budget than its actual wire size, letting the sender push more real bytes across a link than the bandwidth scheduler intended to grant for that height. Meanwhile, `own_congestion_info` byte accounting during buffering/removal (`add_receipt_bytes`/`remove_receipt_bytes` in `buffer_receipt` and `forward_from_buffer_to_shard`) still uses the true, unclamped size computed by `compute_receipt_size` [5](#0-4) [6](#0-5) , so congestion-gas/memory accounting stays correct — only the *bandwidth-grant* consumption for that specific link/height is under-charged.

### Impact Explanation
This is a real, already-acknowledged accounting gap (tracked upstream as issue #12606) rather than a novel authorization bypass: an oversized receipt can consume its granted per-link byte budget by less than its true size, allowing a shard to transmit more bytes on a scheduled link than the bandwidth scheduler granted for that height. Repeated abuse (chaining promise-return/value-return oversized receipts as shown in the existing tests) could increase actual chunk/receipt payload sizes beyond what the bandwidth scheduler accounted for, straining downstream shard processing bandwidth assumptions. This maps to a "congestion/receipt accounting failure" impact class, bounded to the specific link's bandwidth-grant bookkeeping — it does not appear to corrupt `own_congestion_info` gas/memory tracking (which remains size-accurate), nor does it directly cause fund loss.

### Likelihood Explanation
The precondition (an ordinary account deploying/calling a standard contract to create a promise chain whose late-bound `output_data_receivers`/return value pushes the receipt above `max_receipt_size`) is fully unprivileged and already demonstrated as reachable and reproducible by the repository's own integration tests (`test_max_receipt_size_promise_return`, `test_max_receipt_size_value_return`). The clamp itself is deliberately implemented as a workaround to avoid receipts getting permanently stuck, so triggering it requires no special privilege — just crafting a promise chain near the size boundary, which is straightforward and repeatable.

### Recommendation
Fix the root cause instead of relying on the admission-time clamp: enforce `max_receipt_size` validation *after* all late-bound fields (`output_data_receivers`, returned data payload) are finalized, so oversized receipts cannot be created at all (closing issue #12606 properly). If the clamp must remain as a stop-gap for backward compatibility, decrement the bandwidth-grant limit and generate bandwidth requests (`generate_bandwidth_requests`, referenced around `congestion_control.rs:561` for request sizing) using the *true* receipt size rather than the clamped value, while only using the clamp for the pass/fail admission comparison — this prevents grant under-charging even when a legacy oversized receipt is being drained.

### Proof of Concept
Extend the existing `test_max_receipt_size_promise_return`/`test_max_receipt_size_value_return` tests in `test-loop-tests/src/tests/max_receipt_size.rs`:
1. Construct a cross-shard scenario (receiver on a different shard) so the oversized receipt goes through `ReceiptSinkV2::try_forward`/buffering with a real bandwidth grant limit.
2. Instrument or assert on `ReceiptSinkStats`/`OutgoingLimit.size` before and after forwarding the oversized receipt.
3. Assert that `real_receipt_size (borsh::object_length) > max_receipt_size` while `forward_limit.size` was decremented by only `max_receipt_size`, demonstrating the discrepancy between real bytes sent and bandwidth budget charged.
4. Repeat across N chunks/receipts near the boundary and show cumulative drift between bytes actually transmitted on the link and the bandwidth scheduler's granted allowance for that link.

### Citations

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-177)
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
```

**File:** runtime/runtime/src/congestion_control.rs (L113-117)
```rust
                let size_limit = bandwidth_scheduler_output
                    .granted_bandwidth
                    .get_granted_bandwidth(apply_state.shard_id, shard_id);

                (shard_id, OutgoingLimit { gas: gas_limit, size: size_limit })
```

**File:** runtime/runtime/src/congestion_control.rs (L349-368)
```rust
        {
            let receipt = receipt_result?;
            let gas = receipt_congestion_gas(&receipt, &apply_state.config)?;
            let size = receipt_size(&receipt)?;
            let should_update_outgoing_metadatas = receipt.should_update_outgoing_metadatas();
            let receipt = receipt.into_receipt();
            let target_shard_id = receipt.receiver_shard_id(&shard_layout)?;

            match Self::try_forward(
                receipt,
                gas,
                size,
                target_shard_id,
                &mut self.outgoing_limit,
                &mut self.outgoing_receipts,
                apply_state,
                &mut self.stats,
            )? {
                ReceiptForwarding::Forwarded => {
                    self.own_congestion_info.remove_receipt_bytes(size)?;
```

**File:** runtime/runtime/src/congestion_control.rs (L412-427)
```rust
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

**File:** runtime/runtime/src/congestion_control.rs (L451-456)
```rust
        if forward_limit.gas >= admission_gas && forward_limit.size >= size {
            tracing::trace!(target: "runtime", ?shard, receipt_id=?receipt.receipt_id(), "forwarding buffered receipt");
            outgoing_receipts.push(receipt);
            forward_limit.gas = forward_limit.gas.saturating_sub(gas);
            forward_limit.size -= size;
            stats.forwarded_receipts.entry(shard).or_default().add_receipt(size, gas);
```

**File:** runtime/runtime/src/congestion_control.rs (L486-487)
```rust
        self.own_congestion_info.add_receipt_bytes(size)?;
        self.own_congestion_info.add_buffered_receipt_gas(gas)?;
```
