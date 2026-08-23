### Title
Unprivileged local-receipt storage-proof flooding can indefinitely starve the delayed receipt queue - ([File: runtime/runtime/src/lib.rs])

### Finding Description
`process_receipts` executes local receipts, then delayed receipts, then incoming receipts, all gated by the *same* shared per-chunk proof-size budget check `trie.check_proof_size_limit_exceed()` [1](#0-0) .

`process_local_receipts` is executed **first**, and for each local receipt it checks `compute >= compute_limit || check_proof_size_limit_exceed()` before deciding to execute it inline or push it to the delayed queue [2](#0-1) .

`process_delayed_receipts` runs next and pops from the FIFO `DelayedReceiptQueueWrapper` only while the same proof-size/compute check is false; the very first check happens *before* popping even one receipt [3](#0-2) [4](#0-3) .

Congestion control (`CongestionInfo`/`DelayedReceiptQueueWrapper`) only tracks **gas** and **byte size** of delayed/buffered receipts, and only throttles new-transaction admission (`process_tx_limit`/`max_tx_gas`/`min_tx_gas`) based on that gas-based incoming congestion level [5](#0-4) [6](#0-5) . There is no equivalent fairness/reservation mechanism for the `main_storage_proof_size_soft_limit` (3-4 MB per chunk, shared across local + delayed + incoming execution) [7](#0-6) , and the transaction-admission-time proof budget (`new_transactions_validation_state_size_soft_limit`, 500 KiB) is a completely separate, smaller budget that only limits producer-side *validation* proof, not execution proof [8](#0-7) .

An unprivileged account can therefore repeatedly submit signer==receiver ("local") transactions that call a deployed contract method reading large chunks of previously-written state (e.g. `read_n_megabytes`), each generating close to the per-receipt hard proof limit (`per_receipt_storage_proof_size_limit`, 4 MB) but staying under it so the receipt itself succeeds [9](#0-8) . Because such local receipts are admitted based only on gas-based congestion (which measures the attacker's own shard's delayed-receipt gas backlog, not storage-proof consumption), and because `process_local_receipts` always runs before `process_delayed_receipts` against the *same shared* soft proof budget, the attacker can, chunk after chunk, exhaust the entire per-chunk `main_storage_proof_size_soft_limit` purely with local receipts before a single delayed receipt is popped. The `test_main_storage_proof_size_soft_limit` and `test_storage_proof_size_limit` tests confirm this soft-limit gating behavior for local/incoming receipts but do not test the local-vs-delayed fairness gap [10](#0-9) .

### Impact Explanation
This is a liveness/availability issue: victim receipts already queued in the delayed-receipt FIFO on the targeted shard can be perpetually blocked from execution as long as the attacker keeps submitting maximal-proof local transactions each chunk, since the local-receipt path is processed first against a shared, non-partitioned proof-size budget. This matches the "chain stall / unbounded resource starvation" bounty class rather than direct fund loss, since no balance/gas accounting is violated — the attacker legitimately pays gas for their transactions, but low-cost griefing against the shared per-chunk proof budget can indefinitely delay unrelated users' receipts (denial of service / progress-preservation violation for delayed receipts).

### Likelihood Explanation
Feasibility requires only: (1) deploying a contract with several MB of stored state, (2) continuously submitting local (signer==receiver) transactions each chunk that read close to the 4 MB per-receipt limit, paying ordinary gas fees. No validator/node privilege, protocol version bypass, or race condition is required — every check involved (`check_proof_size_limit_exceed`, gas-based congestion `shard_accepts_transactions`) explicitly allows this pattern since none of them account for storage-proof consumption when throttling local-receipt admission. The main cost to the attacker is the gas fee for repeated large reads, which is bounded and can be sustained indefinitely by a determined attacker with modest ongoing funding.

### Recommendation
Reserve a portion of `main_storage_proof_size_soft_limit` specifically for delayed-receipt processing (analogous to `min_tx_gas` reservation in gas-based congestion control), or process delayed receipts before/interleaved with local receipts against the shared proof budget so that local-receipt processing cannot unilaterally exhaust the whole per-chunk proof allowance. Alternatively, extend `CongestionInfo`/`shard_accepts_transactions` to also factor in per-chunk proof-size pressure so that local transaction admission is throttled when the shard is likely to hit the proof-size soft limit while a delayed backlog exists.

### Proof of Concept
Integration test plan (extending `integration-tests/src/tests/features/storage_proof_size_limit.rs`):
1. Deploy a contract with a large stored state and a "victim" delayed receipt (e.g., submit a transaction that is guaranteed to be delayed once, e.g. by first filling the chunk with cheap receipts to push a marked receipt into the delayed queue).
2. In every subsequent block, have the attacker account submit local (signer==receiver) transactions calling a read-heavy method that generates proof close to `per_receipt_storage_proof_size_limit` but under `main_storage_proof_size_soft_limit`.
3. Track, over N blocks, whether/when the marked victim delayed receipt is executed (via `prev_outgoing_receipts`/execution outcome).
4. Assert failure of an upper bound: if the victim receipt is still unexecuted after a reasonable number of blocks (e.g. 20-50), this demonstrates unmitigated starvation caused purely by local-receipt proof-size flooding, distinguishing it from the expected bounded delay under `test_main_storage_proof_size_soft_limit`/`test_storage_proof_size_limit`.

### Citations

**File:** runtime/runtime/src/lib.rs (L2328-2337)
```rust
        for receipt in &local_receipts {
            if processing_state.total.compute >= compute_limit
                || processing_state.state_update.trie.check_proof_size_limit_exceed()
            {
                processing_state.delayed_receipts.push(
                    &mut processing_state.state_update,
                    &receipt,
                    &processing_state.apply_state,
                )?;
            } else {
```

**File:** runtime/runtime/src/lib.rs (L2406-2421)
```rust
        loop {
            if processing_state.total.compute >= compute_limit
                || processing_state.state_update.trie.check_proof_size_limit_exceed()
            {
                break;
            }

            let receipt = if let Some(receipt) = processing_state
                .delayed_receipts
                .pop(&mut processing_state.state_update, &processing_state.apply_state.config)?
            {
                receipt.into_receipt()
            } else {
                // Break loop if there are no more receipts to be processed.
                break;
            };
```

**File:** runtime/runtime/src/lib.rs (L2602-2636)
```rust
    fn process_receipts(
        &self,
        processing_state: &mut ApplyProcessingReceiptState,
        receipt_sink: &mut ReceiptSink,
    ) -> Result<ProcessReceiptsResult, RuntimeError> {
        let mut validator_proposals = vec![];
        let apply_state = &processing_state.apply_state;

        // TODO(#8859): Introduce a dedicated `compute_limit` for the chunk.
        // For now compute limit always matches the gas limit.
        let compute_limit = apply_state.gas_limit.map(|g| g.as_gas()).unwrap_or(u64::MAX);

        // We first process local receipts. They contain staking, local contract calls, etc.
        self.process_local_receipts(
            processing_state,
            receipt_sink,
            compute_limit,
            &mut validator_proposals,
        )?;

        // Then we process the delayed receipts. It's a backlog of receipts from the past blocks.
        self.process_delayed_receipts(
            processing_state,
            receipt_sink,
            compute_limit,
            &mut validator_proposals,
        )?;

        // And then we process the new incoming receipts. These are receipts from other shards.
        self.process_incoming_receipts(
            processing_state,
            receipt_sink,
            compute_limit,
            &mut validator_proposals,
        )?;
```

**File:** runtime/runtime/src/congestion_control.rs (L880-894)
```rust
    pub(crate) fn pop(
        &mut self,
        trie_update: &mut TrieUpdate,
        config: &RuntimeConfig,
    ) -> Result<Option<ReceiptOrStateStoredReceipt<'_>>, RuntimeError> {
        // While processing receipts, we need to keep track of the gas and bytes
        // even for receipts that may be filtered out due to a resharding event
        loop {
            // Check proof size limit before each receipt is popped.
            if trie_update.trie.check_proof_size_limit_exceed() {
                break;
            }
            let Some(receipt) = self.queue.pop_front(trie_update)? else {
                break;
            };
```

**File:** runtime/runtime/src/congestion_control.rs (L931-940)
```rust
    pub(crate) fn apply_congestion_changes(
        self,
        congestion: &mut CongestionInfo,
    ) -> Result<(), RuntimeError> {
        congestion.add_delayed_receipt_gas(self.new_delayed_gas)?;
        congestion.remove_delayed_receipt_gas(self.removed_delayed_gas)?;
        congestion.add_receipt_bytes(self.new_delayed_bytes)?;
        congestion.remove_receipt_bytes(self.removed_delayed_bytes)?;
        Ok(())
    }
```

**File:** core/primitives/src/congestion_info.rs (L123-151)
```rust
    pub fn shard_accepts_transactions(&self) -> ShardAcceptsTransactions {
        let incoming_congestion = self.incoming_congestion();
        let outgoing_congestion = self.outgoing_congestion();
        let memory_congestion = self.memory_congestion();
        let missed_chunks_congestion = self.missed_chunks_congestion();

        let congestion_level = incoming_congestion
            .max(outgoing_congestion)
            .max(memory_congestion)
            .max(missed_chunks_congestion);

        // Convert to NotNan here, if not possible, the max above is already meaningless.
        let congestion_level =
            NotNan::new(congestion_level).unwrap_or_else(|_| NotNan::new(1.0).unwrap());
        if *congestion_level < self.config.reject_tx_congestion_threshold {
            return ShardAcceptsTransactions::Yes;
        }

        let reason = if missed_chunks_congestion >= *congestion_level {
            RejectTransactionReason::MissedChunks { missed_chunks: self.missed_chunks_count }
        } else if incoming_congestion >= *congestion_level {
            RejectTransactionReason::IncomingCongestion { congestion_level }
        } else if outgoing_congestion >= *congestion_level {
            RejectTransactionReason::OutgoingCongestion { congestion_level }
        } else {
            RejectTransactionReason::MemoryCongestion { congestion_level }
        };
        ShardAcceptsTransactions::No(reason)
    }
```

**File:** core/parameters/res/runtime_configs/69.yaml (L5-6)
```yaml
per_receipt_storage_proof_size_limit: {old: 4_294_967_295, new: 4_000_000}
main_storage_proof_size_soft_limit: {old: 4_294_967_295, new: 3_000_000}
```

**File:** docs/misc/state_witness_size_limits.md (L21-28)
```markdown
* `new_transactions_validation_state_size_soft_limit - 500 KiB`
  * Validating new transactions generates storage proof (recorded trie nodes), which has to be limited. Once transaction validation generates more storage proof than this limit, the chunk producer stops adding new transactions to the chunk.
* `per_receipt_storage_proof_size_limit - 4 MB`
  * Executing a receipt generates storage proof. A single receipt is allowed to generate at most 4MB of storage proof. This is a hard limit, receipts which generate more than that will fail.
* `main_storage_proof_size_soft_limit - 4 MB`
  * This is a limit on the total size of storage proof generated by receipts in one chunk. Once receipts generate more storage proof than this limit, the chunk producer stops processing receipts and moves the rest to the delayed queue.
  * It's a soft limit, which means that the total size of storage proof could reach 8 MB (3.99MB + one receipt which generates 4MB of storage proof)
  * Due to implementation details it's hard to find the exact amount of storage proof generated by a receipt, so an upper bound estimation is used instead. This upper bound assumes that every removal generates additional 2000 bytes of storage proof, so receipts which perform a lot of trie removals might be limited more than theoretically applicable.
```

**File:** integration-tests/src/tests/features/storage_proof_size_limit.rs (L102-126)
```rust
    // Test the hard per-receipt limit
    // First perform a 3MB read (keys 0..3), which should succeed.
    let read3_tx = make_read_transaction(0, 3);
    let res = env.execute_tx(read3_tx).unwrap();
    assert_matches!(res.status, FinalExecutionStatus::SuccessValue(_));

    // Now perform a 20MB read (keys 0..20), which should fail due to the hard per-receipt storage proof size limit.
    let read20_tx = make_read_transaction(0, 20);
    let res = env.execute_tx(read20_tx).unwrap();
    assert_matches!(res.status, FinalExecutionStatus::Failure(_));
    let error_string = match res.status {
        FinalExecutionStatus::Failure(TxExecutionError::ActionError(action_error)) => {
            match action_error.kind {
                ActionErrorKind::FunctionCallError(FunctionCallError::ExecutionError(
                    error_string,
                )) => error_string,
                other => panic!("Bad ActionErrorKind: {:?}", other),
            }
        }
        other => panic!("Bad FinalExecutionStatus: {:?}", other),
    };
    assert!(
        error_string
            .contains("Size of the recorded trie storage proof has exceeded the allowed limit")
    );
```

**File:** runtime/runtime/src/tests/apply.rs (L1440-1466)
```rust
#[test]
fn test_main_storage_proof_size_soft_limit() {
    let (runtime, tries, root, mut apply_state, signers, epoch_info_provider) = setup_runtime(
        vec![alice_account(), bob_account()],
        Balance::from_near(1_000_000),
        Balance::from_near(500_000),
        Gas::from_teragas(1000),
    );

    apply_state.config = Arc::new(RuntimeConfig::free());

    let contract_code = ContractCode::new(near_test_contracts::rs_contract().to_vec(), None);
    let create_acc_fn = |account_id: AccountId, signer: Arc<Signer>| {
        create_receipt_with_actions(
            account_id,
            signer,
            vec![Action::DeployContract(DeployContractAction {
                code: contract_code.code().to_vec(),
            })],
        )
    };

    let trie = tries
        .get_trie_for_shard(ShardUId::single_shard(), root)
        .recording_reads_with_proof_size_limit(
            apply_state.config.witness_config.main_storage_proof_size_soft_limit,
        );
```
