# [?] Resolve panic in read_retry during remove_unrooted_slots (#10841)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-03-09
Source: https://github.com/anza-xyz/agave/commit/17f8be73521c0c4c105cb7fb97c32f501e69e0b3
Type: security-commit

## Details
Resolve panic in read_retry during remove_unrooted_slots (#10841)

Loosening panic in retry_to_get_account_accessor as panic is firing invalidly

## Patch
### accounts-db/src/accounts_db.rs
```diff
@@ -3696,6 +3696,42 @@ impl AccountsDb {
         // Remarks for purger: So, for any reading operations, it's a race condition
         // where P2 happens between R1 and R2. In that case, retrying from R1 is safu.
         // In that case, we may bail at index read retry when P3 hasn't been run
+        //
+        // Remover                                | Accessed data source for cached
+        // ---------------------------------------+----------------------------------
+        // M1 purge_slots_from_cache_and_store()  | index
+        //        (via remove_unrooted_slots())   | (removes old entries for slot)
+        //          |                             |
+        //          V                             |
+        // M2 purge_slots_from_cache_and_store()  | map of caches
+        //        (via remove_unrooted_slots())   | (removes old slot cache)
+        //          |                             |
+        //          V                             |
+        // M3 store_accounts_cached()             | map of caches (creates new Cached entry)
+        //          |                             |
+        //          V                             |
+        // M4 update index                        | index (writes fresh Cached entry)
+        //                                        V
+        //
+        // Remarks for remover: This scenario arises when remove_unrooted_slots()
+        // purges a cached slot (e.g. duplicate-block detection abandoning a fork)
+        // and the same slot is subsequently re-stored (e.g. re-processed by banking
+        // stage on a fresh fork).
+        //
+        // M1 removes the index entries before M2 removes the cache (see
+        // purge_slots_from_cache_and_store). M3 writes the fresh cache entry
+        // before M4 writes the fresh index entry, so any reader who observes M4's
+        // index entry is guaranteed to find M3's cache entry too.
+        //
+        // The observable race is M2 happening between R1 and R2, with M3+M4
+        // completing before the subsequent index re-read:
+        //   R1  → (slot, Cached)   [old index entry, before M1]
+        //   M1/M2 remove old index and cache entries
+        //   M3/M4 write fresh cache and index entries
+        //   get_account_accessor() → Cached(None)  [old entry removed by M2]
+        //   re-read index         → (slot, Cached) [fresh M4 entry, same store_id]
+        // In that case, retrying from R1 is safe: the next get_account_accessor()
+        // on the fresh (slot, Cached) entry is guaranteed to return Cached(Some(_)).
 
         #[cfg(test)]
         {
@@ -3719,14 +3755,27 @@ impl AccountsDb {
                     // storage *before* it is removed from the cache
                     match load_hint {
                         LoadHint::FixedMaxRoot => {
-                            // it's impossible for this to fail for transaction loads from
-                            // replaying/banking more than once.
-                            // This is because:
-                            // 1) For a slot `X` that's being replayed, there is only one
-                            // latest ancestor containing the latest update for the account, and this
-                            // ancestor can only be flushed once.
-                            // 2) The root cannot move while replaying, so the index cannot continually
-                            // find more up to date entries than the current `slot`
+                            // Under FixedMaxRoot, Cached(None) can occur at most once per load.
+                            // There are two ways the initial cache miss can happen:
+                            //
+                            // 1) The write-cache entry for the located slot was being concurrently
+                            //    flushed to storage.  After re-reading the index the entry will
+                            //    have moved to Stored, so the next get_account_accessor() call
+                            //    succeeds via Stored(Some(_)).  With a fixed root the index
+                            //    references a single ancestor slot for a given account; that
+                            //    slot is flushed exactly once, so this race cannot repeat.
+                            //
+                            // 2) A parent slot was removed by remove_unrooted_slots() and
+                            //    concurrently re-stored (the M1-M4 "Remover" sequence above).
+                            //    We read the stale index entry (R1, before M1 ran), found the
+                            //    old cache entry already removed (M2), and got Cached(None).
+                            //    After re-reading the index we see the fresh M4 entry, and the
+                            //    next get_account_accessor() call is guaranteed to find M3's
+                            //    cache entry.  For a second Cached(None) to occur here the
+                            //    same parent slot would have to complete the full
+                            //    remove-replay-confirm-duplicate cycle a second time between
+                            //    consecutive loop iterations — a far stricter requirement than
+                            //    the first miss, which only needed a single remove + re-store.
                             assert!(num_acceptable_failed_iterations <= 1);
                         }
                         LoadHint::Unspecified => {
@@ -3808,42 +3857,50 @@ impl AccountsDb {
             // Notice the subtle `?` at previous line, we bail out pretty early if missing.
 
             if new_slot == slot && new_storage_location.is_store_id_equal(&storage_location) {
-                self.accounts_index
-                    .get_and_then(pubkey, |entry| -> (_, ()) {
-                        let message = format!(
-                            "Bad index entry detected ({pubkey}, {slot}, {storage_location:?}, \
-                             {load_hint:?}, {new_storage_location:?}, {entry:?})"
-                        );
-                        // Considering that we've failed to get accessor above and further that
-                        // the index still returned the same (slot, store_id) tuple, offset must be same
-                        // too.
-                        assert!(
-                            new_storage_location.is_offset_equal(&storage_location),
-                            "{message}"
-                        );
+                if !new_storage_location.is_cached() {
+                    self.accounts_index
+                        .get_and_then(pubkey, |entry| -> (_, ()) {
+                            let message = format!(
+                                "Bad index entry detected ({pubkey}, {slot}, \
+                                 {storage_location:?}, {load_hint:?}, {new_storage_location:?}, \
+                                 {entry:?})"
+                            );
+                            // Considering that we've failed to get accessor above and further that
+                            // the index still returned the same (slot, store_id) tuple, offset must be same
+                            // too.
+                            assert!(
+                                new_storage_location.is_offset_equal(&storage_location),
+                                "{message}"
+                            );
 
-                        // If the entry was missing from the cache, that means it must have been flushed,
-                        // and the accounts index is always updated before cache flush, so store_id must
-                        // not indicate being cached at this point.
-                        assert!(!new_storage_location.is_cached(), "{message}");
-
-                        // If this is not a cache entry, then this was a minor fork slot
-                        // that had its storage entries cleaned up by purge_slots() but hasn't been
-                        // cleaned yet. That means this must be rpc access and not replay/banking at the
-                        // very least. Note that purge shouldn't occur even for RPC as caller must hold all
-                        // of ancestor slots..
-                        assert_eq!(load_hint, LoadHint::Unspecified, "{message}");
-
-                        // Everything being assert!()-ed, let's panic!() here as it's an error condition
-                        // after all....
-                        // That reasoning is based on the fact all of code-path reaching this fn
-                        // retry_to_get_account_accessor() must outlive the Arc<Bank> (and its all
-                        // ancestors) over this fn invocation, guaranteeing the prevention of being purged,
-                        // first of all.
-                        // For details, see the comment in AccountIndex::do_checked_scan_accounts(),
-                        // which is referring back here.
-                        panic!("{message}");
-                    });
+                            // If this is not a cache entry, then this was a minor fork slot
+                            // that had its storage entries cleaned up by purge_slots() but hasn't been
+                            // cleaned yet. That means this must be rpc access and not replay/banking at the
+                            // very least. Note that purge shouldn't occur even for RPC as caller must hold all
+                            // of ancestor slots..
+                            assert_eq!(load_hint, LoadHint::Unspecified, "{message}");
+
+                            // Everything being assert!()-ed, let's panic!() here as it's an error condition
+                            // after all....
+                            // That reasoning is based on the fact all of code-path reaching this fn
+                            // retry_to_get_account_accessor() must outlive the Arc<Bank> (and its all
+                            // ancestors) over this fn invocation, guaranteeing the prevention of being purged,
+                            // first of all.
+                            // For details, see the comment in AccountIndex::do_checked_scan_accounts(),
+                            // which is referring back here.
+                            panic!("{message}");
+                        });
+                } else {
+                    // For the Cached variant: remove_unrooted_slots() removes the index entry and
+                    // the cache entry, then a subsequent re-store writes a fresh Cached entry for
+                    // the same slot.  This produces the observable sequence:
+                    //   get_account_accessor()              -> Cached(None)   [old entry gone]
+                    //   read_index_for_accessor_or_load_slow() -> (slot, Cached) [new entry]
+                    // That is not an index corruption -- the next get_account_accessor() call on
+                    // the fresh (slot, Cached) will succeed.  Fall through to retry.
+                    //
+                    // Also no code in this arm!
+                }
             } else if fallback_to_slow_path {
                 // the above bad-index-entry check must had been checked first to retain the same
                 // behavior
```

### accounts-db/tests/accounts_db.rs
```diff
@@ -0,0 +1,101 @@
+use {
+    solana_account::{AccountSharedData, ReadableAccount},
+    solana_accounts_db::{
+        accounts_db::{AccountsDb, LoadHint, PopulateReadCache},
+        ancestors::Ancestors,
+    },
+    solana_pubkey::Pubkey,
+    std::{
+        sync::{
+            Arc,
+            atomic::{AtomicBool, Ordering},
+        },
+        thread::sleep,
+        time::Duration,
+    },
+};
+
+/// Regression test for the race scenario where `retry_to_get_account_accessor` would
+/// incorrectly panic when the following sequence of events occurs:
+///
+/// 1. A load thread calls `read_index_for_accessor_or_load_slow` and gets
+///    `(slot, Cached)` from the accounts index.
+/// 2. A duplicate bank is detected; `remove_unrooted_slots` purges the slot (removing
+///    both the accounts-index entry and the cache entry).
+/// 3. The load thread's `get_account_accessor` returns `Cached(None)` because the
+///    cache is now empty.
+/// 4. `store_accounts_unfrozen` re-populates the slot: it writes to the cache and
+///    then updates the accounts index, both with `(slot, Cached)`.
+/// 5. The load thread retries `read_index_for_accessor_or_load_slow`, finds
+///    `(slot, Cached)` again, and `new_slot == slot && is_store_id_equal` is true.
+///
+/// The fix: guard the bad-index-entry panic with `!new_storage_location.is_cached()`.
+/// For the Cached variant, the sequence above is not a corruption -- the next
+/// `get_account_accessor` call on the fresh `(slot, Cached)` entry will succeed.
+#[test]
+fn test_load_after_remove_unrooted_and_restore_to_same_slot() {
+    let slot = 402240429;
+    let bank_id = 1;
+    let pubkey = Pubkey::new_unique();
+    let account = AccountSharedData::new(42, 0, AccountSharedData::default().owner());
+
+    let db = Arc::new(AccountsDb::new_single_for_tests());
+    let ancestors = Ancestors::from(vec![(slot, 0)]);
+
+    let exit = Arc::new(AtomicBool::new(false));
+
+    // Control thread – performs the sequential remove-then-store cycle that mirrors
+    // what happens in production when a duplicate bank is purged and the slot is
+    // subsequently re-processed by the banking stage.
+    let t_store = {
+        let db = db.clone();
+        let account = account.clone();
+        let exit = exit.clone();
+        std::thread::Builder::new()
+            .name("control".to_string())
+            .spawn(move || {
+                loop {
+                    if exit.load(Ordering::Relaxed) {
+                        return;
+                    }
+                    // Step A: purge the slot (simulate remove_unrooted_slots).
+                    if db.accounts_cache.slot_cache(slot).is_some() {
+                        db.remove_unrooted_slots(&[(slot, bank_id)]);
+                    }
+                    // Step B: re-store the account (simulate store_accounts_unfrozen).
+                    db.store_for_tests((slot, &[(&pubkey, &account)][..]));
+                }
+            })
+            .unwrap()
+    };
+
+    // Load thread – continuously attempts to load the account.
+    let t_do_load = {
+        let db = db.clone();
+        let exit = exit.clone();
+        std::thread::Builder::new()
+            .name("load".to_string())
+            .spawn(move || {
+                loop {
+                    if exit.load(Ordering::Relaxed) {
+                        return;
+                    }
+                    let _ = db.load(
+                        &ancestors,
+                        &pubkey,
+                        LoadHint::FixedMaxRoot,
+                        PopulateReadCache::False,
+                    );
+                }
+            })
+            .unwrap()
+    };
+
+    // Prior to the fix, it failed with a panic in 'retry_to_get_account_accessor' after ~1 second,
+    // run long enough to catch the failure reliably.
+    sleep(Duration::from_secs(5));
+    exit.store(true, Ordering::Relaxed);
+    t_store.join().unwrap();
+    // Propagate any panic from the load thread in retry_to_get_account_accessor).
+    t_do_load.join().map_err(std::panic::resume_unwind).unwrap();
+}
```
