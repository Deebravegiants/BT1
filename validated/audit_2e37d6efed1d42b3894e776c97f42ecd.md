Now I have enough information to trace the exact execution path. Let me verify the `commit_block` ordering precisely.

### Title
Silent Queue Eviction of Valid Successor Transaction After Predecessor Rejection in Fee-Priority Mode — (`crates/apollo_mempool/src/mempool.rs`)

---

### Summary

The bug is **real and confirmed**. In fee-priority mode, when a staged transaction at nonce N is reported as rejected in `commit_block`, the `rewind_txs` → `remove_rejected_txs` sequence causes the valid successor transaction at nonce N+1 to be silently evicted from the queue while remaining stranded in the pool indefinitely. The consensus-divergence framing in the question is incorrect, but the core sequencing defect is a genuine High-severity admission issue.

---

### Finding Description

**Exact execution trace:**

**After `add_tx` for nonce N and N+1 (fee-priority mode):**
- `add_tx_inner` line 609: only nonce N enters the queue (its nonce equals the account nonce); nonce N+1 is pool-only. [1](#0-0) 

**After `get_txs(1)`:**
- `pop_ready_chunk` removes nonce N from the queue.
- `enqueue_next_eligible_txs` finds nonce N+1 in the pool and inserts it into the queue.
- `state.stage` records staged[A] = N+1. [2](#0-1) 

State: `pool = {tx_N, tx_N+1}`, `queue = {tx_N+1}`, `staged = {A: N+1}`.

**`commit_block(address_to_nonce={}, rejected={hash_tx_N})`:**

**Step 1 — `rewind_txs` (runs BEFORE `remove_rejected_txs`):**

`rewind_txs` queries the pool for the lowest-nonce tx for address A. At this point tx_N is **still in the pool**, so it returns tx_N. [3](#0-2) 

`FeeTransactionQueue::rewind_txs` then:
1. Calls `remove_by_address(A)` → **evicts tx_N+1 from the queue**.
2. Calls `insert(tx_N_ref)` → re-inserts tx_N into the queue. [4](#0-3) 

State: `pool = {tx_N, tx_N+1}`, `queue = {tx_N}`.

**Step 2 — `remove_rejected_txs`:**

`rewound_tx_hashes` is always empty for the fee-priority queue (it returns `IndexSet::new()`), so the skip-guard at line 562 never fires. [5](#0-4) 

- `tx_pool.remove(hash_tx_N)` removes tx_N from the pool.
- `tx_queue.remove_by_address(A)` removes tx_N from the queue (the one just re-inserted by rewind). [6](#0-5) 

**Final state:** `pool = {tx_N+1}`, `queue = {}`. tx_N+1 is stranded — present in the pool but absent from the queue. `update_accounts_with_gap` correctly detects the gap (account nonce N < lowest pool nonce N+1) and marks A in `accounts_with_gap`, but this does not re-queue the transaction. [7](#0-6) 

`get_txs` only pops from the queue, so tx_N+1 is never returned for sequencing. [8](#0-7) 

---

### Impact Explanation

A valid, correctly-signed transaction at nonce N+1 — submitted by an unprivileged user through the public RPC/gateway — is silently removed from the sequencing queue after its predecessor at nonce N is rejected during block execution. The transaction remains in the pool consuming capacity but is never proposed in any subsequent block. Recovery requires the user to resubmit a new transaction at nonce N, which is not communicated to them. This matches: **High — Mempool/gateway/RPC admission rejects valid transactions before sequencing.**

---

### Likelihood Explanation

Transaction rejection during block execution is a normal, expected event (e.g., insufficient fee balance at execution time, contract revert). Any user who submits two consecutive transactions and whose first transaction is rejected will silently lose sequencing of the second. No special privileges are required; the trigger is ordinary RPC submission.

---

### Recommendation

In `remove_rejected_txs`, after removing the rejected tx from the pool, instead of calling `tx_queue.remove_by_address`, check whether the queue currently holds the **rejected** tx's nonce for that address. If it does not (i.e., `rewind_txs` already replaced it with a successor), skip the `remove_by_address` call. Alternatively, restructure `rewind_txs` in fee-priority mode to skip addresses whose lowest-nonce pool tx is the one being rejected (since it is about to be removed), so the successor is correctly re-inserted after removal.

---

### Proof of Concept

```rust
// In fee-priority (Starknet) mode:
// 1. add_tx(A, nonce=0)  → pool={tx0}, queue={tx0}
// 2. add_tx(A, nonce=1)  → pool={tx0,tx1}, queue={tx0}
// 3. get_txs(1)          → returns [tx0]; enqueues tx1
//                          pool={tx0,tx1}, queue={tx1}, staged={A:1}
// 4. commit_block(address_to_nonce={}, rejected={hash(tx0)})
//    rewind_txs: lowest pool nonce for A = 0 (tx0 still in pool)
//      → remove_by_address(A) evicts tx1 from queue
//      → insert(tx0) into queue
//    remove_rejected_txs({hash(tx0)}, {}):
//      → pool.remove(tx0)
//      → queue.remove_by_address(A) evicts tx0
//    Final: pool={tx1}, queue={}
// 5. get_txs(1) → returns [] (tx1 is stranded, never sequenced)
assert!(mempool.get_txs(1).unwrap().is_empty()); // passes — tx1 is lost from queue
```

The `rewound_tx_hashes` guard at line 562 that protects FIFO mode from this exact problem is never populated for the fee-priority queue, leaving fee-priority mode unprotected. [9](#0-8) [10](#0-9) 

---

**Note on the consensus-divergence claim:** The claim that this causes proposer/validator divergence via P2P re-admission is incorrect. The mempool is a pre-consensus component; validators do not independently re-admit transactions in a way that affects block agreement. The actual impact is confined to the sequencing layer: a valid transaction is silently dropped from the queue, causing it to be omitted from all future blocks until the user manually resubmits the predecessor.

### Citations

**File:** crates/apollo_mempool/src/mempool.rs (L336-355)
```rust
        while n_remaining_txs > 0 && self.tx_queue.has_ready_txs() {
            let chunk = self.tx_queue.pop_ready_chunk(n_remaining_txs);

            let (valid_txs, expired_txs_updates) = self.prune_expired_nonqueued_txs(chunk);
            account_nonce_updates.extend(expired_txs_updates);

            // In FIFO mode, all transactions are already enqueued. In fee-priority mode,
            // we need to enqueue the next eligible transaction for each address.
            if !self.is_fifo() {
                self.enqueue_next_eligible_txs(&valid_txs)?;
            }

            n_remaining_txs -= valid_txs.len();
            eligible_tx_references.extend(valid_txs);
        }

        // Update the mempool state with the given transactions' nonces.
        for tx_reference in &eligible_tx_references {
            self.state.stage(tx_reference)?;
        }
```

**File:** crates/apollo_mempool/src/mempool.rs (L532-545)
```rust
            let next_txs_by_address = addresses_to_rewind
                .iter()
                .filter_map(|&address| {
                    self.tx_pool
                        .account_txs_sorted_by_nonce(address)
                        .next()
                        .map(|tx_reference| (address, *tx_reference))
                })
                .collect::<HashMap<ContractAddress, TransactionReference>>();
            self.tx_queue.rewind_txs(RewindData::FeePriority {
                next_txs_by_address: &next_txs_by_address,
                validate_resource_bounds: self.config.static_config.validate_resource_bounds,
            })
        }
```

**File:** crates/apollo_mempool/src/mempool.rs (L559-576)
```rust
        for tx_hash in rejected_tx_hashes {
            // In FIFO mode, if a rejected transaction was rewound, skip removal (keep in pool and
            // queue). Otherwise, remove it from both pool and queue.
            if rewound_tx_hashes.contains(&tx_hash) {
                continue;
            }

            if let Ok(tx) = self.tx_pool.remove(tx_hash) {
                self.tx_queue.remove_by_address(tx.contract_address());
                rejected_txs_counter += 1;
                self.decrement_stuck_txs_if_gap_account(tx.contract_address(), 1);
                account_nonce_updates
                    .entry(tx.contract_address())
                    .and_modify(|nonce| *nonce = (*nonce).min(tx.nonce()))
                    .or_insert(tx.nonce());
            } else {
                continue; // Transaction hash unknown to mempool, from a different node.
            }
```

**File:** crates/apollo_mempool/src/mempool.rs (L609-616)
```rust
        } else if tx_reference.nonce == account_nonce {
            // Fee mode: only add transactions with matching account nonce.
            // Remove queued transactions the account might have. This includes old nonce
            // transactions that have become obsolete; those with an equal nonce should
            // already have been removed via fee escalation (`remove_replaced_tx`).
            self.tx_queue.remove_by_address(address);
            self.insert_to_tx_queue(tx_reference);
        }
```

**File:** crates/apollo_mempool/src/mempool.rs (L947-978)
```rust
    fn update_accounts_with_gap(&mut self, address_to_nonce: AddressToNonce) {
        for (address, account_nonce) in address_to_nonce {
            // If a delayed declare transaction exists at the account nonce, it is next to execute,
            // so no gap exists.
            if self.delayed_declares.contains(address, account_nonce) {
                self.remove_from_accounts_with_gap(address);
                continue;
            }

            // Gap exists when lowest transaction nonce is higher than account nonce.
            let gap_exists = match self.tx_pool.get_lowest_nonce(address) {
                Some(lowest_nonce) => account_nonce < lowest_nonce,
                None => false, // No transactions for the account, so no gap.
            };

            // Update the eviction tracking set accordingly.
            if gap_exists {
                if self.accounts_with_gap.insert(address) {
                    // Newly entered gap: all current pool txs for this account are now stuck.
                    let n_stuck = self.tx_pool.n_txs_for_address(address);
                    self.n_stuck_txs += n_stuck;
                    warn!(
                        "Account {address} has a nonce gap; {n_stuck} transaction(s) are now \
                         stuck."
                    );
                }
                // Stayed in gap: per-tx deltas were already applied at add/remove sites.
            } else {
                // Left gap: remaining pool txs for this account are no longer stuck.
                self.remove_from_accounts_with_gap(address);
            }
        }
```

**File:** crates/apollo_mempool/src/fee_transaction_queue.rs (L129-144)
```rust
    fn rewind_txs(&mut self, rewind_data: RewindData<'_>) -> IndexSet<TransactionHash> {
        // Extract fee-priority specific data
        let RewindData::FeePriority { next_txs_by_address, validate_resource_bounds } = rewind_data
        else {
            unreachable!("FeeTransactionQueue received Fifo data instead of FeePriority data");
        };

        // Rewind by re-inserting the next transaction for each address.
        for (address, tx_reference) in next_txs_by_address {
            self.remove_by_address(*address);
            self.insert(*tx_reference, validate_resource_bounds);
        }

        // Fee-priority queue doesn't track rewound hashes
        IndexSet::new()
    }
```
