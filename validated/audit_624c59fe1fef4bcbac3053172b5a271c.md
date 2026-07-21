### Title
Duplicate Transaction Hashes in Consensus Proposal Bypass Validation, Causing Node Panic After Block Commitment — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`handle_proposal_part` in the proposal validation path accepts `ProposalPart::Transactions` batches without checking for duplicate transaction hashes. A malicious proposer can craft a proposal containing the same transaction hash twice. All validators accept the proposal, the batcher executes it (the second copy fails with `InvalidNonce` but the proposal is not rejected), consensus decides, and then `finalize_decision` panics on the duplicate hash after the block has already been committed to storage — leaving every validator node in an inconsistent state.

### Finding Description

**Root cause — missing duplicate check in `handle_proposal_part`:**

When a validator receives a `ProposalPart::Transactions` batch, `handle_proposal_part` converts each transaction and appends the entire batch to `content` without any uniqueness check on transaction hashes: [1](#0-0) 

The `content` accumulator is a plain `Vec<Vec<InternalConsensusTransaction>>`. Nothing prevents the same `TransactionHash` from appearing in two different batches or twice within the same batch.

**Contrast with the individual-add path:**

The mempool's `TransactionPool::insert` explicitly rejects duplicate hashes: [2](#0-1) 

The gateway's `validate_incoming_tx` also rejects duplicates: [3](#0-2) 

The proposal-validation path — the only path through which a validator node processes externally-supplied transactions during consensus — has no equivalent guard.

**Fin count check does not close the gap:**

The only guard in the Fin handler is: [4](#0-3) 

This checks `executed_txs_count > n_received_txs`. If the proposer sends `[Tx_A, Tx_A, Tx_B]` and claims `executed_transaction_count = 3`, the check passes (`3 ≤ 3`). The content is then truncated to 3 entries — retaining both copies of `Tx_A`: [5](#0-4) 

**Batcher executes without rejecting the proposal:**

`send_txs_for_proposal` forwards transactions to the tx-provider channel without a duplicate check: [6](#0-5) 

The blockifier executes `Tx_A` successfully (nonce N → N+1), then fails the second `Tx_A` with `InvalidNonce`. This is a per-transaction failure; the proposal itself is not marked `InvalidProposal`. The batcher returns `FinishProposalStatus::Finished` with a commitment computed over the successfully executed transactions.

**Panic in `finalize_decision` after block commitment:**

After consensus decides, `finalize_decision` is called with the stored `content` (which still contains both copies of `Tx_A`). It builds a `HashMap` keyed by `tx_hash`: [7](#0-6) 

The `TODO(Dafna): Handle this error gracefully` comment confirms this panic path is known but unguarded. The panic fires **after** `decision_reached` has already committed the block to storage: [8](#0-7) 

The node crashes before completing `update_state_sync_with_new_block` and `prepare_blob_for_next_height`, leaving the committed block without a corresponding state-sync update or cende blob.

### Impact Explanation

Every honest validator independently validates the same proposal, executes it deterministically through the blockifier, and computes the same `batcher_block_commitment`. All validators vote for this commitment; consensus decides. All validators then call `finalize_decision` with content containing the duplicate hash and all panic simultaneously. The block is committed to storage on every node, but finalization is incomplete. The network halts.

This matches: **Critical. Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input** — the committed block's state-sync view and cende blob are never written, producing an inconsistent on-chain state.

### Likelihood Explanation

Any validator is the designated proposer for some round. A single Byzantine validator can trigger this attack in any round where it holds the proposer role. No special privilege beyond being a committee member is required. The attack requires crafting a proposal with one repeated transaction hash — trivially achievable by any proposer.

### Recommendation

Add a duplicate-hash check inside `handle_proposal_part` when processing `ProposalPart::Transactions`. Maintain a `HashSet<TransactionHash>` across all batches received for a single proposal and return `HandledProposalPart::Failed` (or `HandledProposalPart::Invalid`) if any hash is seen more than once:

```rust
// In validate_proposal, alongside `content` and `verify_and_store_proof_tasks`:
let mut seen_tx_hashes: HashSet<TransactionHash> = HashSet::new();

// In the Transactions arm of handle_proposal_part:
for tx in &txs {
    if !seen_tx_hashes.insert(tx.tx_hash()) {
        return HandledProposalPart::Failed(format!(
            "Duplicate transaction hash in proposal: {:?}", tx.tx_hash()
        ));
    }
}
```

This mirrors the invariant already enforced by `TransactionPool::insert` and `validate_incoming_tx` in the mempool/gateway path, closing the gap in the consensus validation path.

### Proof of Concept

1. A malicious validator waits for its proposer turn at height H.
2. It constructs a proposal containing `[Tx_A, Tx_A, Tx_B]` where `Tx_A` is a valid invoke transaction, and sets `executed_transaction_count = 3` in `ProposalFin`.
3. All honest validators receive the proposal. `handle_proposal_part` processes the three transactions without a duplicate check, appending `[Tx_A, Tx_A, Tx_B]` to `content`.
4. The Fin check passes: `3 ≤ 3`. `truncate_to_executed_txs` retains all three entries.
5. `send_txs_for_proposal` forwards all three to the batcher. The blockifier executes `Tx_A` (success), `Tx_A` (fail — `InvalidNonce`), `Tx_B` (success). The proposal is not rejected.
6. `finish_proposal` returns `FinishProposalStatus::Finished` with a commitment over `{Tx_A, Tx_B}`. All validators compute the same commitment and vote for it.
7. Consensus decides. Each validator calls `decision_reached` → batcher commits the block to storage → `finalize_decision` is called with `transactions = [[Tx_A, Tx_A, Tx_B]]`.
8. The loop at line 523 inserts `Tx_A`'s hash, then on the second `Tx_A` finds `is_some() == true` and panics. Every validator node crashes after the block is committed but before state sync or cende blob are updated.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L519-528)
```rust
            // `executed_transaction_count` comes straight off the wire, so a dishonest or
            // spoofed `Fin` can claim more transactions than were actually streamed. Reject
            // that here instead of trusting the count downstream.
            let n_received_txs = content.iter().map(Vec::len).sum::<usize>();
            if executed_txs_count > n_received_txs {
                return HandledProposalPart::Failed(format!(
                    "Fin claims {executed_txs_count} executed transactions but only \
                     {n_received_txs} were received in the proposal."
                ));
            }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L530-530)
```rust
            *content = truncate_to_executed_txs(content, executed_txs_count);
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L598-634)
```rust
        Some(ProposalPart::Transactions(TransactionBatch { transactions: txs })) => {
            // TODO(guyn): check that the length of txs and the number of batches we receive is not
            // so big it would fill up the memory (in case of a malicious proposal)
            debug!("Received transaction batch with {} txs", txs.len());
            let conversion_results =
                futures::future::join_all(txs.into_iter().map(|tx| {
                    transaction_converter.convert_consensus_tx_to_internal_consensus_tx(tx)
                }))
                .await
                .into_iter()
                .collect::<Result<Vec<_>, _>>();
            let conversion_results = match conversion_results {
                Ok(results) => results,
                Err(e) => {
                    return HandledProposalPart::Failed(format!(
                        "Failed to convert transactions. Stopping the build of the current \
                         proposal. {e:?}"
                    ));
                }
            };

            // Separate internal transactions from verification and store proof tasks. Each task
            // verifies the proof and stores it in the proof manager. Tasks are collected
            // and awaited later in the fin case.
            let (txs, tasks): (
                Vec<InternalConsensusTransaction>,
                Vec<Option<VerifyAndStoreProofTask>>,
            ) = conversion_results.into_iter().unzip();
            verify_and_store_proof_tasks.extend(tasks.into_iter().flatten());

            debug!(
                "Converted transactions to internal representation. hashes={:?}",
                txs.iter().map(|tx| tx.tx_hash()).collect::<Vec<TransactionHash>>()
            );

            content.push(txs.clone());
            let input = SendTxsForProposalInput { proposal_id, txs };
```

**File:** crates/apollo_mempool/src/transaction_pool.rs (L60-70)
```rust
    pub fn insert(&mut self, tx: InternalRpcTransaction) -> MempoolResult<()> {
        let tx_reference = TransactionReference::new(&tx);
        let tx_hash = tx_reference.tx_hash;
        let tx_size = tx.total_bytes();

        // Insert to pool.
        if let hash_map::Entry::Vacant(entry) = self.tx_pool.entry(tx_hash) {
            entry.insert(tx);
        } else {
            return Err(MempoolError::DuplicateTransaction { tx_hash });
        }
```

**File:** crates/apollo_mempool/src/mempool.rs (L702-710)
```rust
    fn validate_incoming_tx(
        &self,
        tx_reference: TransactionReference,
        incoming_account_nonce: Nonce,
    ) -> MempoolResult<()> {
        if self.tx_pool.get_by_tx_hash(tx_reference.tx_hash).is_ok() {
            return Err(MempoolError::DuplicateTransaction { tx_hash: tx_reference.tx_hash });
        }
        self.state.validate_incoming_tx(tx_reference, incoming_account_nonce)
```

**File:** crates/apollo_batcher/src/batcher.rs (L580-599)
```rust
    pub async fn send_txs_for_proposal(
        &mut self,
        send_txs_for_proposal_input: SendTxsForProposalInput,
    ) -> BatcherResult<SendTxsForProposalStatus> {
        let SendTxsForProposalInput { proposal_id, txs: new_txs } = send_txs_for_proposal_input;
        self.ensure_validate_proposal_exists(proposal_id)?;

        if self.is_active(proposal_id).await {
            // The proposal is active. Send transactions through the tx provider.
            let tx_provider_sender = &self
                .validate_tx_streams
                .get(&proposal_id)
                .expect("Expecting tx_provider_sender to exist during batching.");
            for tx in new_txs {
                tx_provider_sender.send(tx).await.map_err(|err| {
                    error!("Failed to send transaction to the tx provider: {}", err);
                    BatcherError::InternalError
                })?;
            }
            return Ok(SendTxsForProposalStatus::Processing);
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L522-528)
```rust
        let mut transactions_hash_map = HashMap::new();
        for tx in transactions.into_iter().flatten() {
            let key = tx.tx_hash();
            if transactions_hash_map.insert(key, tx).is_some() {
                // TODO(Dafna): Handle this error gracefully.
                panic!("Duplicate transactions found with the same tx_hash: {key:?}");
            }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L551-556)
```rust
        // The conversion should never fail, if we already managed to get a decision.
        let cende_block_info = convert_to_sn_api_block_info(init).expect(
            "Failed to convert block info to SN API block info (required for state sync and \
             preparing the cende blob). IMPORTANT: The block was committed; a revert might be \
             required for the node to be able to proceed.",
        );
```
