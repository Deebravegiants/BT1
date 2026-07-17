### Title
`prepare_transactions_extra` checks only current-chunk transaction size against `combined_transactions_size_limit`, ignoring previous chunk's contribution — (`chain/chain/src/runtime/mod.rs`)

### Summary

`combined_transactions_size_limit` is documented and enforced as a hard limit on the **combined** size of transactions from both the previous chunk and the current chunk inside a `ChunkStateWitness`. However, the chunk producer's `prepare_transactions_extra` function initialises its running size counter at zero and only accumulates the size of transactions it is adding in the **current** session. It never subtracts the space already consumed by the previous chunk's transactions. This is the exact same class of bug as the SuperPool report: a local/partial capacity value is used instead of the actual total capacity, so the producer can overshoot the real limit.

### Finding Description

`WitnessConfig::combined_transactions_size_limit` is explicitly documented as:

> "A witness contains transactions from both the previous chunk and the current one. This parameter limits the sum of sizes of transactions from both of those chunks." [1](#0-0) 

In `prepare_transactions_extra` (the SPICE chunk-production path), the size budget is initialised to the full `combined_transactions_size_limit` with no deduction for the previous chunk's transactions:

```rust
let mut total_size = 0u64;
// ...
let size_limit = runtime_config.witness_config.combined_transactions_size_limit as u64;
``` [2](#0-1) 

The loop then stops only when `total_size >= size_limit` or when a single transaction would push `total_size` over `size_limit`: [3](#0-2) 

Because `total_size` starts at zero and never accounts for the previous chunk's transactions, the producer can include up to `combined_transactions_size_limit` bytes of **new** transactions even when the previous chunk already consumed a large portion of that budget. The resulting witness carries `prev_chunk_tx_size + current_chunk_tx_size` bytes of transactions, which can substantially exceed `combined_transactions_size_limit` (4 MiB in production).

### Impact Explanation

The documentation is explicit that chunk validators re-enforce every limit:

> "Chunk validators have to verify that chunk producer respected all of the limits while producing the chunk. If it turns out that some limits weren't respected, the validators will generate a different result of chunk application and they won't endorse the chunk." [4](#0-3) 

When the combined transaction size exceeds the hard limit, validators compute a different chunk application result and withhold endorsements. The corrupted protocol value is the **chunk validity decision**: a chunk the producer believed was valid is rejected by validators, causing a missing chunk on that shard.

### Likelihood Explanation

`max_transaction_size` is 1.5 MiB and `combined_transactions_size_limit` is 4 MiB. A previous chunk can legitimately contain two 1.5 MiB transactions (3 MiB total, within the limit). The next chunk producer then believes it has the full 4 MiB budget and packs up to 4 MiB of new transactions. The combined witness size reaches 7 MiB — nearly double the 4 MiB hard limit. Any unprivileged user can trigger this by submitting several near-maximum-size transactions in rapid succession; no validator collusion is required.

### Recommendation

Before the transaction-packing loop begins, query the size of the previous chunk's transactions and subtract it from `size_limit`:

```rust
let prev_chunk_tx_size = /* sum of size_for_limits() for transactions in the previous chunk */;
let size_limit = (runtime_config.witness_config.combined_transactions_size_limit as u64)
    .saturating_sub(prev_chunk_tx_size);
```

This mirrors the SuperPool fix: take the minimum of the local cap and the actual remaining capacity before attempting to fill it.

### Proof of Concept

1. User submits two transactions of ~1.5 MiB each (e.g., large `DeployContract` actions). Both fit within `combined_transactions_size_limit` = 4 MiB, so the chunk producer includes them in chunk N. Previous-chunk transaction size = ~3 MiB.
2. User submits two more ~1.5 MiB transactions. The chunk producer for chunk N+1 initialises `total_size = 0` and `size_limit = 4 MiB`. It packs both new transactions (total_size = ~3 MiB < 4 MiB).
3. The `ChunkStateWitness` for chunk N+1 now contains ~3 MiB (from chunk N) + ~3 MiB (from chunk N+1) = ~6 MiB of transactions, exceeding the 4 MiB hard limit.
4. Chunk validators enforce the combined limit, compute a divergent result, and withhold endorsements. Chunk N+1 is treated as missing.

**Note:** This bug is in the `prepare_transactions_extra` code path, which is gated on `ProtocolFeature::Spice`. Whether SPICE is active in the current production deployment determines whether this path is reachable. Additionally, I was unable to locate the exact validator-side enforcement code for `combined_transactions_size_limit` within the available search results; the impact claim rests on the documentation's explicit guarantee that validators enforce all listed hard limits. [5](#0-4) [6](#0-5)

### Citations

**File:** core/parameters/src/config.rs (L260-272)
```rust
#[derive(Debug, Copy, Clone, PartialEq)]
pub struct WitnessConfig {
    /// Size limit for storage proof generated while executing receipts in a chunk.
    /// After this limit is reached we defer execution of any new receipts.
    pub main_storage_proof_size_soft_limit: u64,
    /// Maximum size of transactions contained inside ChunkStateWitness.
    ///
    /// A witness contains transactions from both the previous chunk and the current one.
    /// This parameter limits the sum of sizes of transactions from both of those chunks.
    pub combined_transactions_size_limit: usize,
    /// Size limit of storage proof used to validate new transactions in ChunkStateWitness.
    pub new_transactions_validation_state_size_soft_limit: u64,
}
```

**File:** chain/chain/src/runtime/mod.rs (L893-979)
```rust
    fn prepare_transactions_extra(
        &self,
        storage: TrieUpdate,
        shard_id: ShardId,
        prev_block: PrepareTransactionsBlockContext,
        transaction_groups: &mut dyn TransactionGroupIterator,
        chain_validate: &dyn Fn(&SignedTransaction) -> bool,
        validate_tx_ttl: &dyn Fn(&SignedTransaction) -> bool,
        skip_tx_hashes: HashSet<CryptoHash>,
        check_pending: &mut dyn FnMut(&SignedTransaction, HasContract) -> PendingTxCheckResult,
        time_limit: Option<Duration>,
        cancel: Option<Arc<AtomicBool>>,
    ) -> Result<(PreparedTransactions, SkippedTransactions), Error> {
        let span = tracing::Span::current();
        let start_time = std::time::Instant::now();

        let epoch_id = prev_block.next_epoch_id;
        let protocol_version = self.epoch_manager.get_epoch_protocol_version(&epoch_id)?;
        let runtime_config = self.runtime_config_store.get_config(protocol_version);

        // While the height of the next block that includes the chunk might not be prev_height + 1,
        // using it will result in a more conservative check and will not accidentally allow
        // invalid transactions to be included.
        let next_block_height = prev_block.height + 1;

        // Interim updates for accounts and nonces are written to signer_overlay,
        // not back to the state_update.
        let state_update = TrieUpdateWitnessSizeWrapper::new(storage);
        let mut signer_overlay = SignerOverlay::new();

        // Total amount of gas burnt for converting transactions towards receipts.
        let mut total_gas_burnt = Gas::ZERO;
        let mut total_size = 0u64;

        let transactions_gas_limit = chunk_tx_gas_limit(runtime_config, &prev_block, shard_id);

        let mut prepared_transactions = PreparedTransactions::new();
        let mut skipped_transactions = Vec::new();
        let mut num_checked_transactions = 0;

        let size_limit = runtime_config.witness_config.combined_transactions_size_limit as u64;
        // for metrics only
        let mut rejected_due_to_congestion = 0;
        let mut rejected_invalid_tx = 0;
        let mut rejected_invalid_for_chain = 0;

        // Add new transactions to the result until some limit is hit or the transactions run out.
        'add_txs_loop: while let Some(transaction_group_iter) = transaction_groups.next() {
            if total_gas_burnt >= transactions_gas_limit {
                prepared_transactions.limited_by = PrepareTransactionsLimit::Gas;
                break;
            }
            if total_size >= size_limit {
                prepared_transactions.limited_by = PrepareTransactionsLimit::Size;
                break;
            }

            if let Some(time_limit) = &time_limit {
                if start_time.elapsed() >= *time_limit {
                    prepared_transactions.limited_by = PrepareTransactionsLimit::Time;
                    break;
                }
            }

            if state_update.recorded_storage_size() as u64
                > runtime_config.witness_config.new_transactions_validation_state_size_soft_limit
            {
                prepared_transactions.limited_by = PrepareTransactionsLimit::StorageProofSize;
                break;
            }

            if let Some(cancel) = &cancel {
                if cancel.load(Ordering::Relaxed) {
                    prepared_transactions.limited_by = PrepareTransactionsLimit::Cancelled;
                    break;
                }
            }

            // Take a single transaction from this transaction group
            while let Some(tx_peek) = transaction_group_iter.peek_next() {
                // Stop adding transactions if the size limit would be exceeded
                if total_size.saturating_add(tx_peek.size_for_limits(protocol_version))
                    > size_limit as u64
                {
                    prepared_transactions.limited_by = PrepareTransactionsLimit::Size;
                    break 'add_txs_loop;
                }
```

**File:** docs/misc/state_witness_size_limits.md (L38-41)
```markdown
### Validating the limits

Chunk validators have to verify that chunk producer respected all of the limits while producing the chunk. This means that validators also have to keep track of recorded storage proof by recording all trie accesses and they have to enforce the limits.
If it turns out that some limits weren't respected, the validators will generate a different result of chunk application and they won't endorse the chunk.
```
