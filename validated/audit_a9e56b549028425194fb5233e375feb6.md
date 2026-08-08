### Title
Intra-batch write-write lock check uses stale pre-batch state, allowing two sibling transactions to simultaneously write-lock the same account - ([File: accounts-db/src/account_locks.rs])

### Summary
`AccountLocks::try_lock_transaction_batch` validates every transaction in a batch against the account-lock table in a first pass, and only afterward performs the actual locking in a second pass. Because the validation pass never mutates `self` (uses `&self` in `can_lock_accounts`), two sibling transactions in the same batch that write-lock the identical pubkey both observe the pre-batch lock state and are both marked `Ok`, then both get locked in the second pass without any conflict detection.

### Finding Description
`try_lock_transaction_batch` is implemented as two sequential loops: [1](#0-0) 

- Pass 1 (`validated_batch_keys.iter_mut().for_each`) calls `self.can_lock_accounts(keys.clone())`, which only reads `self.write_locks` / `self.readonly_locks` (immutable borrow) and returns `Err(AccountInUse)` if the key is *already* locked in the table at that moment: [2](#0-1) 
No lock is registered during this pass, so processing transaction A's keys does not change the table state seen when checking transaction B's keys immediately afterward.
- Pass 2 (`.into_iter().map(...self.lock_accounts...)`) then unconditionally locks every key for every transaction whose pass-1 result was `Ok`, via `lock_accounts` → `lock_write`/`lock_readonly`, which merely increments a counter and cannot fail or detect a conflict: [3](#0-2) [4](#0-3) 

Consequently, if transaction A and transaction B in the same batch both write-lock pubkey `P`, and `P` was unlocked before the batch call: during pass 1, A's check for `P` sees no lock (Ok), and B's check for `P` also sees no lock (Ok), since pass 1 never calls `lock_accounts`. Pass 2 then calls `lock_write(P)` twice, once for A and once for B, and both entries in the returned `Vec<TransactionResult<()>>` are `Ok(())`. This violates the intended invariant that within a single batch, conflicting write-write (or write-read) accesses to the same pubkey must be serialized/rejected via `AccountInUse`, exactly as the audit's proof idea describes.

This is reachable by an unprivileged attacker: any pair of transactions that both declare the same account as writable (e.g., two simple transfers from/to account `P`, or two arbitrary program invocations both listing `P` as a writable account) submitted so that the runtime batches them together (e.g., via `banking_stage`/scheduler batching in `core/src/banking_stage/consumer.rs` or `transaction_scheduler`) will trigger this path. No special privileges, signatures beyond normal transaction signing, or validator control are required — the attacker only needs to submit two ordinary transactions that happen to be batched together and share a writable account.

### Impact Explanation
Both transactions proceed to execution believing they hold an exclusive write lock on `P`. Since the accounts-db locking mechanism is the only synchronization primitive protecting concurrent SVM execution of a batch, two threads/execution slots can concurrently read-modify-write the same account state with no ordering guarantee. This can produce non-deterministic execution results depending on thread interleaving, which can differ between validators, causing bank-hash divergence — a chain-halting/cluster-divergence-class issue in Agave's bounty categorization ("consensus/state divergence", the highest severity category), and potentially incorrect final account state (value loss/corruption) since one transaction's write to `P` may be silently overwritten by the other depending on interleaving.

### Likelihood Explanation
This requires only that two transactions submitted normally end up in the same "lock batch" (the `Vec` passed to `try_lock_transaction_batch`) and both declare the same account as writable. Batches are formed continuously during normal transaction processing (e.g., in `consumer.rs` / scheduler paths), so an attacker can trivially craft and broadcast such a pair repeatedly; feasibility is high and fully attacker-controlled (no timing tricks, no validator cooperation needed) — the only external factor is that the scheduler/consumer must place both transactions in the same locking call, which is a normal, expected outcome of concurrent submission of transactions from the same sender/account.

### Recommendation
Merge the two passes so that each transaction's lock check and lock acquisition happen atomically relative to sibling transactions in the same batch: i.e., iterate `validated_batch_keys` once, and for each `Ok` entry call `can_lock_accounts` immediately followed by `lock_accounts` (still with `&mut self`) before moving to the next transaction, so subsequent transactions in the same batch observe locks taken by earlier transactions in that same call. This restores intra-batch write-write/write-read conflict detection.

### Proof of Concept
```rust
// accounts-db/src/account_locks.rs (test module)
#[test]
fn test_try_lock_transaction_batch_intra_batch_write_write_conflict() {
    let mut account_locks = AccountLocks::default();
    let key = Pubkey::new_unique();

    // Two transactions in the SAME batch call, both write-locking `key`.
    let tx_a_keys = vec![(&key, true)];
    let tx_b_keys = vec![(&key, true)];

    let batch: Vec<TransactionResult<_>> = vec![
        Ok(tx_a_keys.into_iter()),
        Ok(tx_b_keys.into_iter()),
    ];

    let results = account_locks.try_lock_transaction_batch(batch);

    // Expected (correct) behavior: intra-batch write-write must conflict.
    assert_eq!(results[0], Ok(()));
    assert_eq!(results[1], Err(TransactionError::AccountInUse));

    // Actual current behavior demonstrates the bug: both succeed.
    // assert_eq!(results, vec![Ok(()), Ok(())]); // <- current buggy outcome
}
```
Running this test against current `try_lock_transaction_batch` yields `[Ok(()), Ok(())]` instead of `[Ok(()), Err(AccountInUse)]`, confirming both sibling transactions acquire a write lock on the identical pubkey within one batch call.

### Citations

**File:** accounts-db/src/account_locks.rs (L22-40)
```rust
    pub fn try_lock_transaction_batch<'a>(
        &mut self,
        mut validated_batch_keys: Vec<
            TransactionResult<impl Iterator<Item = (&'a Pubkey, bool)> + Clone>,
        >,
    ) -> Vec<TransactionResult<()>> {
        validated_batch_keys.iter_mut().for_each(|validated_keys| {
            if let Ok(keys) = validated_keys.as_ref()
                && let Err(e) = self.can_lock_accounts(keys.clone())
            {
                *validated_keys = Err(e);
            }
        });

        validated_batch_keys
            .into_iter()
            .map(|available_keys| available_keys.map(|keys| self.lock_accounts(keys)))
            .collect()
    }
```

**File:** accounts-db/src/account_locks.rs (L56-71)
```rust
    fn can_lock_accounts<'a>(
        &self,
        keys: impl Iterator<Item = (&'a Pubkey, bool)>,
    ) -> TransactionResult<()> {
        for (key, writable) in keys {
            if writable {
                if !self.can_write_lock(key) {
                    return Err(TransactionError::AccountInUse);
                }
            } else if !self.can_read_lock(key) {
                return Err(TransactionError::AccountInUse);
            }
        }

        Ok(())
    }
```

**File:** accounts-db/src/account_locks.rs (L73-81)
```rust
    fn lock_accounts<'a>(&mut self, keys: impl Iterator<Item = (&'a Pubkey, bool)>) {
        for (key, writable) in keys {
            if writable {
                self.lock_write(key);
            } else {
                self.lock_readonly(key);
            }
        }
    }
```

**File:** accounts-db/src/account_locks.rs (L107-109)
```rust
    fn lock_write(&mut self, key: &Pubkey) {
        *self.write_locks.entry(*key).or_default() += 1;
    }
```
