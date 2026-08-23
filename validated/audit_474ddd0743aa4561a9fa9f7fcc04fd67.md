### Title
Unbounded recursion in transaction status resolution can crash a node via a long receipt chain - ([File: chain/chain/src/chain.rs])

### Summary
The Aptos report fixes a compiler bug where recursive type-default resolution could recurse into a cycle with no visited-set/depth guard, causing a stack overflow. The closest reachable analog in nearcore is `Chain::get_recursive_transaction_results`, which walks the receipt-outcome graph of a transaction purely via native Rust recursion, with no depth limit and no cycle/visited-set guard, to answer transaction-status RPC queries.

### Finding Description
`get_recursive_transaction_results` recursively follows every `receipt_ids` entry of each execution outcome, one recursive call per receipt, with no bound on recursion depth: [1](#0-0) 

This is invoked by `get_final_transaction_result`, which is the routine used to compute `FinalExecutionOutcomeView` for the `tx` / `broadcast_tx_commit` RPC methods (transaction-status polling): [2](#0-1) 

Unlike the analogous `receipt_to_tx` traversal (`GetReceiptToTxError::DepthExceeded`, tested with an explicit `MAX_DEPTH=1000` guard), this transaction-result traversal has no equivalent depth cap: [3](#0-2) 

A single `FunctionCall` transaction can legitimately spawn a chain of thousands of sequential cross-contract-call receipts (each one issuing one more receipt, gated only by remaining gas), as demonstrated by the near-test-contracts self-recursion helper: [4](#0-3) 

Because gas accounting allows a transaction to fan out many hundreds/thousands of sequential (not parallel) receipts before running out of prepaid gas, an attacker-submitted transaction can produce a receipt-outcome chain long enough that `get_recursive_transaction_results`'s native call-stack recursion exceeds the RPC/view-client thread's stack, aborting the process (Rust stack overflow is not a catchable panic – it's an abort).

### Impact Explanation
If the recursion depth is attacker-controllable and sufficiently deep, calling the `tx` / `broadcast_tx_commit` RPC on such a transaction hash would abort the serving process's thread with a stack overflow, resulting in a node crash/DoS on any RPC/view node that answers transaction-status queries for the malicious transaction. This matches the "node panic or unbounded resource use" acceptance criterion.

### Likelihood Explanation
Likelihood is moderate-to-uncertain: an attacker needs to submit (and get executed) a transaction producing a sufficiently long chain of sequential receipts, then query its status via `tx`/`broadcast_tx_commit`. This requires gas to fund the chain, and the actual required recursion depth to overflow a thread stack was not empirically confirmed here (Rust default stack sizes and the size of each stack frame in this function are unknown without running the code). Whether an existing runtime limit (e.g., total receipts per transaction, gas-based limiting of chain length) already bounds this depth to a safe value was not fully verified from the code alone.

### Recommendation
Convert `get_recursive_transaction_results` to an iterative (worklist/stack-based) traversal instead of native recursion, and/or add an explicit depth or outcome-count limit (mirroring the `receipt_to_tx` `MAX_DEPTH` pattern) that returns a graceful error instead of recursing unboundedly.

### Proof of Concept
Not independently reproduced. Conceptually: submit a `FunctionCall` transaction to a contract that issues a long chain of sequential self cross-contract calls (e.g., `max_self_recursion_delay` in `near-test-contracts`) with maximum prepaid gas, wait for execution, then query `tx`/`broadcast_tx_commit` for that transaction hash on an RPC node; if the resulting outcome chain exceeds the thread's stack capacity, `get_recursive_transaction_results` will recurse until stack overflow. Confirming the exact depth needed to overflow the stack requires running the code, which was not performed in this analysis.

### Citations

**File:** chain/chain/src/chain.rs (L3190-3207)
```rust
    fn get_recursive_transaction_results(
        &self,
        outcomes: &mut Vec<ExecutionOutcomeWithIdView>,
        id: &CryptoHash,
        require_all_outcomes: bool,
    ) -> Result<(), Error> {
        let outcome = match self.get_execution_outcome(id) {
            Ok(outcome) => outcome,
            Err(err) => return if require_all_outcomes { Err(err) } else { Ok(()) },
        };
        outcomes.push(ExecutionOutcomeWithIdView::from(outcome));
        let outcome_idx = outcomes.len() - 1;
        for idx in 0..outcomes[outcome_idx].outcome.receipt_ids.len() {
            let id = outcomes[outcome_idx].outcome.receipt_ids[idx];
            self.get_recursive_transaction_results(outcomes, &id, require_all_outcomes)?;
        }
        Ok(())
    }
```

**File:** chain/chain/src/chain.rs (L3209-3225)
```rust
    /// Returns FinalExecutionOutcomeView for the given transaction.
    /// Waits for the end of the execution of all corresponding receipts
    pub fn get_final_transaction_result(
        &self,
        transaction_hash: &CryptoHash,
    ) -> Result<FinalExecutionOutcomeView, Error> {
        let mut outcomes = Vec::new();
        self.get_recursive_transaction_results(&mut outcomes, transaction_hash, true)?;
        let status = self.get_execution_status(&outcomes, transaction_hash);
        let receipts_outcome = outcomes.split_off(1);
        let transaction = self.chain_store.get_transaction(transaction_hash).ok_or_else(|| {
            Error::DBNotFoundErr(format!("Transaction {} is not found", transaction_hash))
        })?;
        let transaction = SignedTransactionView::from(Arc::unwrap_or_clone(transaction));
        let transaction_outcome = outcomes.pop().unwrap();
        Ok(FinalExecutionOutcomeView { status, transaction, transaction_outcome, receipts_outcome })
    }
```

**File:** test-loop-tests/src/tests/receipt_to_tx/errors.rs (L157-219)
```rust
/// Handler-level: write synthetic ReceiptToTx rows forming chain of 1001
/// FromReceipt entries (exceeds MAX_DEPTH=1000). Verify DepthExceeded
/// returned with originally queried receipt_id.
#[test]
fn test_receipt_to_tx_depth_exceeded() {
    init_test_logger();

    let mut env = TestLoopBuilder::new().epoch_length(EPOCH_LENGTH).track_all_shards().build();

    let store = env.validator().store();
    let mut store_update = store.store_update();

    // Chain of 1002 receipt IDs: receipt_0 → receipt_1 → ... → receipt_1001.
    // receipt_0..receipt_1000 are FromReceipt → next. receipt_1001 is
    // FromTransaction (terminal — never reached).
    let chain_len = 1002usize;
    let receipt_ids: Vec<CryptoHash> =
        (0..chain_len).map(|i| CryptoHash::hash_bytes(&(i as u32).to_le_bytes())).collect();

    // Terminal node: receipt_1001 → tx.
    store_update.insert_ser(
        DBCol::ReceiptToTx,
        receipt_ids[chain_len - 1].as_ref(),
        &ReceiptToTxInfo::V1(ReceiptToTxInfoV1 {
            origin: ReceiptOrigin::FromTransaction(ReceiptOriginTransaction {
                tx_hash: CryptoHash::hash_bytes(b"tx"),
                sender_account_id: "sender".parse().unwrap(),
            }),
            receiver_account_id: "receiver".parse().unwrap(),
            shard_id: ShardId::new(0),
        }),
    );

    // Intermediates: receipt_i → receipt_{i+1}.
    for i in 0..chain_len - 1 {
        store_update.insert_ser(
            DBCol::ReceiptToTx,
            receipt_ids[i].as_ref(),
            &ReceiptToTxInfo::V1(ReceiptToTxInfoV1 {
                origin: ReceiptOrigin::FromReceipt(ReceiptOriginReceipt {
                    parent_receipt_id: receipt_ids[i + 1],
                    parent_predecessor_id: "system".parse().unwrap(),
                }),
                receiver_account_id: "receiver".parse().unwrap(),
                shard_id: ShardId::new(0),
            }),
        );
    }

    store_update.commit();

    // Query receipt_0 — needs 1001 hops, exceeds MAX_DEPTH=1000.
    let handle = env.node_datas[0].view_client_sender.actor_handle();
    let view_client: &mut near_client::ViewClientActor = env.test_loop.data.get_mut(&handle);
    let result = view_client.handle(receipt_to_tx_req(receipt_ids[0]));

    match result {
        Err(GetReceiptToTxError::DepthExceeded { receipt_id, limit }) => {
            assert_eq!(receipt_id, receipt_ids[0], "error reports originally queried receipt");
            assert_eq!(limit, 1000, "limit == MAX_DEPTH=1000");
        }
        other => panic!("expected DepthExceeded error, got: {other:?}"),
    }
```

**File:** runtime/near-test-contracts/test-contract-rs/src/lib.rs (L847-881)
```rust
/// Delay completion of the receipt for as long as possible through self cross-contract calls.
///
/// This contract keeps the recursion depth and returns it when less than 5Tgas remains, which is
/// most likely is no longer sufficient for another cross-contract call.
///
/// This is a stable alternative to yield/resume proposal at the time of writing.
#[unsafe(no_mangle)]
pub unsafe fn max_self_recursion_delay() {
    input(0);
    let mut bytes = [0u8; 4];
    read_register(0, bytes.as_mut_ptr());
    let recursion = u32::from_be_bytes(bytes);
    let available_gas = prepaid_gas() - used_gas();
    if available_gas < 5_000_000_000_000 {
        return value_return(4, bytes.as_ptr() as u64);
    }
    current_account_id(1);
    let method_name = "max_self_recursion_delay";
    let promise_idx = promise_batch_create(u64::MAX, 1);
    let amount = 1u128;
    let gas_fixed = 0;
    let gas_weight = 1;
    let argument_bytes = recursion.saturating_add(1).to_be_bytes();
    promise_batch_action_function_call_weight(
        promise_idx,
        method_name.len() as u64,
        method_name.as_ptr() as u64,
        argument_bytes.len() as u64,
        argument_bytes.as_ptr() as u64,
        &amount as *const u128 as u64,
        gas_fixed,
        gas_weight,
    );
    promise_return(promise_idx);
}
```
