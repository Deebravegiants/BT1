### Title
Intra-batch write/readonly lock check runs against stale state, allowing simultaneous write+read locks on the same key - ([File: accounts-db/src/account_locks.rs])

### Finding Description
`AccountLocks::try_lock_transaction_batch` implements a two-phase "check-then-lock" design instead of the sequential check-and-lock-per-transaction model the invariant requires:

```rust
pub fn try_lock_transaction_batch<'a>(
    &mut self,
    mut validated_batch_keys: Vec<TransactionResult<impl Iterator<Item = (&'a Pubkey, bool)> + Clone>>,
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
``` [1](#0-0) 

Phase 1 iterates over every transaction in the batch and calls `can_lock_accounts` (which uses `can_write_lock`/`can_read_lock`), but `self` (the `write_locks`/`readonly_locks` maps) is **not mutated** during this loop — `lock_accounts` is only invoked afterward in phase 2. Consequently, phase 1 only validates each transaction's keys against locks that existed *before this batch call* (i.e., from previous, still-outstanding batches). It never checks one transaction's requested locks in the batch against another transaction's requested locks in the *same* batch. [2](#0-1) 

Phase 2 then unconditionally applies `lock_accounts` for every entry still marked `Ok`, incrementing `write_locks`/`readonly_locks` counters with no re-validation:
```rust
fn lock_accounts<'a>(&mut self, keys: impl Iterator<Item = (&'a Pubkey, bool)>) {
    for (key, writable) in keys {
        if writable { self.lock_write(key); } else { self.lock_readonly(key); }
    }
}
``` [3](#0-2) 

`can_write_lock`/`can_read_lock` enforce the mutual-exclusion invariant (write lock requires zero readonly and zero write locks; read lock requires zero write locks): [4](#0-3) 

Because phase 1 evaluates all transactions against the same unmutated `self` snapshot, if transaction A declares key `K` writable and transaction B (in the same batch, no pre-existing lock on `K`) declares `K` readonly, both pass phase 1 as `Ok`. Phase 2 then locks both unconditionally, leaving `write_locks[K] == 1` and `readonly_locks[K] == 1` simultaneously — a direct violation of the "only one writer, no writer+reader" invariant that the rest of the runtime (account loading/commit) depends on for safe concurrent/parallel account access.

An unprivileged attacker fully controls this: they only need to submit two (or more) independent, otherwise valid `SanitizedTransaction`s that reference a common account key with conflicting writable flags (one `is_writable == true`, one `false`) close enough together that banking stage batches them into a single `Accounts::lock_accounts` call, which internally calls `try_lock_transaction_batch`.

### Impact Explanation
This breaks the fundamental account-locking invariant that guards concurrent/parallel transaction execution and account loading (`can_write_lock`/`can_read_lock`). Concurrent write+read locks on the same key can allow the readonly transaction to observe account state that is being concurrently mutated by the writable transaction (a data race across execution/loading paths that assume exclusivity), and can cause both transactions to be scheduled/executed as if isolated when they are not. This falls under undeclared/unsynchronized account mutation and can produce nondeterministic results depending on scheduling/thread timing, risking cross-node divergence if different validators' internal execution ordering differs.

### Likelihood Explanation
Fully attacker-reachable with no privileged access: any user can submit two ordinary transactions, one marking an account writable and one marking the same account readonly, timed to land in the same leader batch. No signature bypass, no nonce manipulation, and no special account state is required — only crafting the writable-bit assignment across a batch, which is entirely attacker-controlled via standard transaction construction (message account metas).

### Recommendation
Restore atomic check-and-lock semantics per transaction within a batch: either (a) fold `can_lock_accounts` and `lock_accounts` into a single step evaluated sequentially per transaction (mutating `self` before checking the next transaction in the batch, so a later transaction sees the tentative locks of earlier transactions in the same batch), or (b) pre-detect and reject intra-batch key conflicts (conflicting writable/readonly declarations on the same pubkey across different transactions in the same `validated_batch_keys` vector) before entering the two-phase check/lock split.

### Proof of Concept
```rust
// accounts-db/src/account_locks.rs (tests module)
#[test]
fn test_accounts_locks_intrabatch_write_read_conflict() {
    let key = Pubkey::new_unique();
    let mut account_locks = AccountLocks::default();

    // tx1: writes `key`; tx2: reads `key`. Neither key is locked beforehand.
    let tx1_keys = vec![(&key, true)];
    let tx2_keys = vec![(&key, false)];

    let batch: Vec<TransactionResult<_>> = vec![
        Ok(tx1_keys.into_iter()),
        Ok(tx2_keys.into_iter()),
    ];

    let results = account_locks.try_lock_transaction_batch(batch);

    // Expect only ONE of the two conflicting transactions to succeed.
    let ok_count = results.iter().filter(|r| r.is_ok()).count();
    assert_eq!(
        ok_count, 1,
        "both a writable and a readonly lock were granted concurrently on the same key"
    );

    // Invariant check: write and readonly locks must never coexist on the same key.
    assert!(
        !(account_locks.is_locked_write(&key) && account_locks.is_locked_readonly(&key)),
        "write_locks and readonly_locks both set for key {key:?}"
    );
}
```
Running this test against the current implementation is expected to fail (`ok_count == 2` and both `is_locked_write`/`is_locked_readonly` true for `key`), demonstrating that `try_lock_transaction_batch` grants a writable and a readonly lock on the same key simultaneously within one batch call, in violation of `can_write_lock`/`can_read_lock`'s invariant.

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

**File:** accounts-db/src/account_locks.rs (L93-101)
```rust
    fn can_read_lock(&self, key: &Pubkey) -> bool {
        // If the key is not write-locked, it can be read-locked
        !self.is_locked_write(key)
    }

    fn can_write_lock(&self, key: &Pubkey) -> bool {
        // If the key is not read-locked or write-locked, it can be write-locked
        !self.is_locked_readonly(key) && !self.is_locked_write(key)
    }
```
