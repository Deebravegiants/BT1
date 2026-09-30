# [?] Resolve race condition in wait_for_idle (#7583)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-08-19
Source: https://github.com/anza-xyz/agave/commit/702a02840bf748fa1aac583dee851f39665e8017
Type: security-commit

## Details
Resolve race condition in wait_for_idle (#7583)

## Patch
### accounts-db/src/bucket_map_holder.rs
```diff
@@ -140,13 +140,13 @@ impl<T: IndexValue, U: DiskIndexValue + From<T> + Into<T>> BucketMapHolder<T, U>
             return;
         }
 
-        // when age has incremented twice, we know that we have made it through scanning all bins since we started waiting,
-        //  so we are then 'idle'
-        let end_age = self.current_age().wrapping_add(2);
+        let start_age = self.current_age();
         loop {
             self.wait_dirty_or_aged
                 .wait_timeout(Duration::from_millis(self.age_interval_ms()));
-            if end_age == self.current_age() {
+            // when age has incremented twice or more from the starting age, we know that we have
+            // made it through scanning all bins since we started waiting, so we are then 'idle'
+            if self.current_age().wrapping_sub(start_age) > 1 {
                 break;
             }
         }
```
