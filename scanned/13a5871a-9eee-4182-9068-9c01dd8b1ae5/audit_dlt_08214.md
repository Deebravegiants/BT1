# [?] Avoid overflow in ThreadSet::any() and nits (#31098)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-04-07
Source: https://github.com/solana-labs/solana/commit/f0432ec50f3c0ebc3efa947891e8f98a0c784b03
Type: security-commit

## Details
Avoid overflow in ThreadSet::any() and nits (#31098)

Avoid overflow in ThreadSet::any and etc

## Patch
### core/src/banking_stage/thread_aware_account_locks.rs
```diff
@@ -25,7 +25,7 @@ pub(crate) struct ThreadSet(u64);
 pub(crate) struct ThreadAwareAccountLocks {
     /// Number of threads.
     num_threads: usize, // 0..MAX_THREADS
-    /// Write locks - only on thread can hold a write lock at a time.
+    /// Write locks - only one thread can hold a write lock at a time.
     /// Contains how many write locks are held by the thread.
     write_locks: HashMap<Pubkey, (ThreadId, LockCount)>,
     /// Read locks - multiple threads can hold a read lock at a time.
@@ -124,9 +124,7 @@ impl ThreadAwareAccountLocks {
         self.schedulable_threads::<true>(account)
     }
 
-    /// Returns `ThreadSet` of schedulable threads, given the read-only lock handler.
-    /// Helper function, since the only difference between read and write schedulable threads
-    ///   is in how the case where only read locks are held is handled.
+    /// Returns `ThreadSet` of schedulable threads.
     /// If there are no locks, then all threads are schedulable.
     /// If only write-locked, then only the thread holding the write lock is schedulable.
     /// If a mix of locks, then only the write thread is schedulable.
@@ -148,8 +146,8 @@ impl ThreadAwareAccountLocks {
             }
             (Some((thread_id, _)), None) => ThreadSet::only(*thread_id),
             (Some((thread_id, _)), Some((thread_set, _))) => {
-                assert_eq!(Some(*thread_id), thread_set.only_one_contained());
-                ThreadSet::only(*thread_id)
+                assert_eq!(thread_set.only_one_contained(), Some(*thread_id));
+                *thread_set
             }
         }
     }
@@ -310,12 +308,16 @@ impl Debug for ThreadSet {
 impl ThreadSet {
     #[inline(always)]
     pub(crate) const fn none() -> Self {
-        Self(0)
+        Self(0b0)
     }
 
     #[inline(always)]
     pub(crate) const fn any(num_threads: usize) -> Self {
-        Self(Self::as_flag(num_threads) - 1)
+        if num_threads == MAX_THREADS {
+            Self(u64::MAX)
+        } else {
+            Self(Self::as_flag(num_threads) - 1)
+        }
     }
 
     #[inline(always)]
@@ -340,7 +342,7 @@ impl ThreadSet {
 
     #[inline(always)]
     pub(crate) fn contains(&self, thread_id: ThreadId) -> bool {
-        self.0 & (Self::as_flag(thread_id)) != 0
+        self.0 & Self::as_flag(thread_id) != 0
     }
 
     #[inline(always)]
@@ -360,7 +362,7 @@ impl ThreadSet {
 
     #[inline(always)]
     const fn as_flag(thread_id: ThreadId) -> u64 {
-        1 << thread_id
+        0b1 << thread_id
     }
 }
 
@@ -661,4 +663,16 @@ mod tests {
             assert_eq!(thread_set.contains(idx), idx == 2);
         }
     }
+
+    #[test]
+    fn test_thread_set_any_zero() {
+        let any_threads = ThreadSet::any(0);
+        assert_eq!(any_threads.num_threads(), 0);
+    }
+
+    #[test]
+    fn test_thread_set_any_max() {
+        let any_threads = ThreadSet::any(MAX_THREADS);
+        assert_eq!(any_threads.num_threads(), MAX_THREADS as u32);
+    }
 }
```
