### Title
Single unprivileged account can monopolize the entire per-shard transaction pool, denying mempool admission to all other accounts sharing that shard - ([File: chain/pool/src/lib.rs])

### Summary
The Zebra advisory describes a shared, bounded resource (25 inbound mempool download slots) with no per-peer accounting, allowing one entity to exhaust it and deny admission to everyone else. `nearcore`'s `TransactionPool` has the structurally identical gap: the only admission-control check is a single, shard-wide byte-size budget (`transaction_pool_size_limit`, default 100 MB), with **no per-account or per-key quota**. A single unprivileged account, submitting only ordinary signed transactions through the public RPC (`broadcast_tx_async`/`broadcast_tx_commit`), can fill an entire shard's pool and cause `InsertTransactionResult::NoSpaceLeft` for every other account whose account ID maps to that shard.

### Finding Description
`TransactionPool::insert_transaction` groups transactions by `(account_id, public_key, nonce_index)` and enforces admission solely via a global `total_transaction_size_limit` check, with no cap on how much of that budget a single signer/group can occupy: [1](#0-0) 

This pool is created per shard (`ShardedTransactionPool::pool_for_shard`), so the size limit is shared across every account whose transactions route to that shard: [2](#0-1) 

The default limit is 100 MB per shard, configurable but with no secondary per-account ceiling anywhere in the config surface: [3](#0-2) 

Critically, admission checks in `rpc_handler.rs` validate each incoming transaction against the current committed chain state root, and in the default (non-`spice`) code path the `PendingConstraints` used for balance/nonce accounting is always `PendingConstraints::default()` (i.e., zero) — meaning the balance and nonce impact of the sender's *other already-queued but not-yet-executed* transactions in the pool is not considered when validating a new one: [4](#0-3) 

The actual balance check in `verify_and_charge_tx_ephemeral` only subtracts `pending.paid_from_balance`, which is zero outside the `spice` pending-transaction-queue feature, so many transactions from the same account, each individually affordable against the unchanged on-chain balance, all pass verification independently: [5](#0-4) 

Once verified, the transaction is unconditionally inserted into the shared per-shard pool if the node is a chunk producer for that shard, with the only gate being the shard-wide byte budget: [6](#0-5) 

There is no mechanism analogous to per-peer slot capping (as recommended in the Zebra fix) that limits how many bytes/transactions of the shared pool budget a single `(account_id, public_key)` group can occupy. The only per-account throttling mechanism found in the codebase — `PendingTxSession`/`P_MAX` in `pending_transaction_queue.rs` — is gated behind the `protocol_feature_spice` feature and only applies to contract-deploying accounts under the Spice pending-transaction-queue design, not to the default transaction pool used by all networks today: [7](#0-6) 

### Impact Explanation
An unprivileged account with a modest balance can submit a large volume of small, individually-valid transactions (e.g., minimal transfers with strictly increasing nonces) via ordinary RPC calls. Because each is checked against the unmodified chain state (no cumulative balance/nonce reservation across pending pool entries outside the Spice feature), all of them can be admitted until the shard's `transaction_pool_size_limit` (100 MB by default) is exhausted. From that point, `InsertTransactionResult::NoSpaceLeft` is returned for every other transaction targeting the same shard — including transactions from unrelated, legitimate accounts and even RPC nodes' own forwarded traffic — causing denial of mempool admission for that shard until the attacker's transactions are drained (executed, expired, or evicted). This can degrade or stall normal transaction processing for every account whose address hashes into the targeted shard, without the attacker needing any special privilege, validator role, or network-layer position.

### Likelihood Explanation
High. The attack requires only a funded account and use of the standard, publicly exposed transaction-submission RPC — no validator status, no P2P-layer positioning, and no protocol version tricks. The only cost to the attacker is the cumulative gas/fee cost of the flood of transactions themselves (bounded by the pool size limit / tx size, not by nonce-sequencing constraints since nonces need only be increasing, not contiguous, in default nonce mode), and pool occupancy persists until the transactions are included, time out, or are evicted, giving a sustained window to keep the shard's pool full.

### Recommendation
Introduce per-account (or per `(account_id, public_key)` group) accounting in `TransactionPool`/`ShardedTransactionPool`, analogous to the Zebra fix's per-peer slot cap: reject or evict a signer's transactions once they exceed a fraction of the shard's total `transaction_pool_size_limit` (e.g., a configurable per-account byte/count cap), and surface `NoSpaceLeft` due to single-account saturation distinctly from generic overload so operators can identify and potentially deprioritize a flooding account. Consider also incorporating already-pooled (unexecuted) transactions from an account into RPC-time balance/nonce validation outside of the `spice` feature, closing the gap where multiple transactions can be independently "affordable" against the same static state root.

### Proof of Concept
1. Fund a single test account `attacker.near` with enough balance to cover many minimal `Transfer` transactions.
2. Submit N transactions via `broadcast_tx_async`, each with a fresh strictly-increasing nonce and destination `self`/`black_hole.near`, sized to approach `transaction_pool_size_limit` (100 MB default) for the shard `attacker.near` maps to — e.g., pad transaction payload where allowed, or simply submit enough small transactions to reach the byte budget.
3. Observe via logs/metrics (`transaction_pool_size_metric`) that the shard's pool fills to the configured limit.
4. From a second, unrelated funded account `victim.near` mapped to the same shard, submit a normal transfer transaction via RPC.
5. Observe the RPC handler logs `"transaction pool is full, dropping/trying to forward the transaction"` and the victim's transaction returns `InsertTransactionResult::NoSpaceLeft`, confirming denial of mempool admission for a legitimate user via [8](#0-7)  caused solely by a single unprivileged account's flood, matching the "single-peer inbound queue saturation" bug class from the Zebra advisory but reached entirely through normal transaction submission rather than the P2P layer.

### Citations

**File:** chain/pool/src/lib.rs (L87-107)
```rust
    /// Inserts a signed transaction that passed validation into the pool.
    pub fn insert_transaction(
        &mut self,
        validated_tx: ValidatedTransaction,
    ) -> InsertTransactionResult {
        let tx_hash = validated_tx.get_hash();
        if self.unique_transactions.contains(&tx_hash) {
            return InsertTransactionResult::Duplicate;
        }
        // We never expect the total size to go over `u64` during real operation as that would
        // be more than 10^9 GiB of RAM consumed for transaction pool, so panicking here is intended
        // to catch a logic error in estimation of transaction size.
        let new_total_transaction_size = self
            .total_transaction_size
            .checked_add(validated_tx.wire_size())
            .expect("Total transaction size is too large");
        if let Some(limit) = self.total_transaction_size_limit {
            if new_total_transaction_size > limit {
                return InsertTransactionResult::NoSpaceLeft;
            }
        }
```

**File:** chain/chunks/src/client.rs (L91-99)
```rust
    fn pool_for_shard(&mut self, shard_uid: ShardUId) -> &mut TransactionPool {
        self.tx_pools.entry(shard_uid).or_insert_with(|| {
            TransactionPool::new(
                Self::random_seed(&self.rng_seed, shard_uid.shard_id()),
                self.pool_size_limit,
                &shard_uid.to_string(),
            )
        })
    }
```

**File:** core/chain-configs/src/client_config.rs (L579-581)
```rust
pub fn default_transaction_pool_size_limit() -> Option<u64> {
    Some(100_000_000) // 100 MB.
}
```

**File:** chain/client/src/rpc_handler.rs (L248-275)
```rust
            } else {
                let chunk_store = self.chain_store.chunk_store();
                let root = match chunk_store.get_chunk_extra(&head.last_block_hash, &shard_uid) {
                    Ok(chunk_extra) => *chunk_extra.state_root(),
                    Err(_) => {
                        if is_forwarded {
                            return Err(near_client_primitives::types::Error::Other(
                                "Node has not caught up yet".to_string(),
                            ));
                        } else {
                            self.forward_tx(&epoch_id, signed_tx)?;
                            return Ok(ProcessTxResponse::RequestRouted);
                        }
                    }
                };
                (root, PendingConstraints::default())
            };
            if let Err(err) = self.runtime.can_verify_and_charge_tx(
                &shard_layout,
                gas_price,
                state_root,
                &validated_tx,
                protocol_version,
                &constraints,
            ) {
                tracing::debug!(target: "client", ?err, "invalid tx");
                return Ok(ProcessTxResponse::InvalidTx(err));
            }
```

**File:** chain/client/src/rpc_handler.rs (L279-298)
```rust
            // Transactions only need to be recorded if this node is a chunk producer for the transaction's shard.
            if self.is_chunk_producer_for_transaction(&head, signed_tx.transaction.signer_id())? {
                let mut pool = self.tx_pool.lock();
                match pool.insert_transaction(shard_uid, validated_tx) {
                    InsertTransactionResult::Success => {
                        tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "recorded a transaction");
                    }
                    InsertTransactionResult::Duplicate => {
                        tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "duplicate transaction, not forwarding it");
                        return Ok(ProcessTxResponse::ValidTx);
                    }
                    InsertTransactionResult::NoSpaceLeft => {
                        if is_forwarded {
                            tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "transaction pool is full, dropping the transaction");
                        } else {
                            tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "transaction pool is full, trying to forward the transaction");
                        }
                    }
                }
            }
```

**File:** runtime/runtime/src/verifier.rs (L300-317)
```rust
    let account_id = tx.signer_id();
    let tx_nonce = tx.nonce().nonce();
    let effective_nonce = std::cmp::max(access_key.nonce, pending.max_nonce);
    if let Err(e) = verify_nonce(tx_nonce, effective_nonce, block_height, tx.nonce_mode()) {
        return TxVerdict::Failed(e);
    }

    // saturating_sub is fine here: on the consensus path pending constraints
    // are always default (zero), so the subtraction is exact. On the RPC /
    // chunk-production path it is best-effort and does not affect consensus.
    let available_balance = account.amount().saturating_sub(pending.paid_from_balance);
    if available_balance < total_cost {
        return TxVerdict::Failed(InvalidTxError::NotEnoughBalance {
            signer_id: account_id.clone(),
            balance: available_balance,
            cost: total_cost,
        });
    }
```

**File:** chain/client/src/pending_transaction_queue.rs (L826-847)
```rust
    #[test]
    fn test_session_accumulates_across_calls() {
        let sharded = make_sharded_ptq();
        let signer = test_signer();
        let mut session = make_session(&sharded);

        // Admit P_MAX access key txs from a contract account within a single session.
        for i in 1..=P_MAX {
            let tx = make_transfer_tx(&signer, "bob.near", i as Nonce, TEST_DEPOSIT);
            assert!(
                matches!(
                    session.check_pending(&tx, HasContract::Yes),
                    PendingTxCheckResult::Admit(_)
                ),
                "tx {} should be admitted",
                i
            );
        }
        // The (P_MAX + 1)th should be skipped.
        let tx = make_transfer_tx(&signer, "bob.near", (P_MAX + 1) as Nonce, TEST_DEPOSIT);
        assert_eq!(session.check_pending(&tx, HasContract::Yes), PendingTxCheckResult::Skip);
    }
```
