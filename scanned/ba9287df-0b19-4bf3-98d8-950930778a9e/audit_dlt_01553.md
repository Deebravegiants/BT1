# [?] fix: re-enable test_scheduler_drop_idle by resolving race condition (#9042)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-11-19
Source: https://github.com/anza-xyz/agave/commit/35f53334b125ad61a527ae58d9bd46a1aa91d1f1
Type: security-commit

## Details
fix: re-enable test_scheduler_drop_idle by resolving race condition (#9042)

* fix: re-enable test_scheduler_drop_idle by resolving race condition

  Remove #[ignore] attribute and fix timing to eliminate race condition
  in test_scheduler_drop_idle, which was disabled in PR #8278.

  The test verifies the scheduler pool's cleaner thread correctly removes
  idle schedulers while preserving recently-pooled ones.

  Root cause:
  The original test used a 100ms idle threshold with 1000ms sleep, but
  timing was still unreliable due to system variations. The race occurred
  when old_scheduler and new_scheduler had unclear age differences.

  Fix:
  - Use explicit 300ms idle threshold for this test (instead of 100ms)
  - Sleep 350ms before returning new_scheduler (provides 50ms+ safety margin)
  - This guarantees old_scheduler is idle while new_scheduler is not

  Result:
  - old_scheduler: 350ms old (> 300ms threshold) → definitely idle → removed
  - new_scheduler: ~0ms old (< 300ms threshold) → definitely not idle → kept
  - Test is now deterministic and matches expected checkpoint sequence

  Fixes #8279

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

* Address all reviewer feedback on test_scheduler_drop_idle

   - Move SHORTENED_MAX_POOLING_DURATION constant to test_scheduler_drop_stale where it's used
   - Convert test_max_pooling_duration from let to const TEST_MAX_POOLING_DURATION following conventions
   - Create TEST_WAIT_FOR_IDLE constant (500ms) with explicit safety margin tied to TEST_MAX_POOLING_DURATION
   - Increase safety margin from 50ms to 200ms for CI reliability
   - Add detailed comments explaining 300ms pooling duration tradeoff (speed vs race condition window)
   - Update assertion comment with explicit timing guarantees: old_scheduler ~500ms old (exceeds 300ms threshold),
   new_scheduler ~50ms old (below threshold)

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

* refactor: tie test duration constants together and improve comment accuracy

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

* fix: cargo fmt

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

---------

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

### unified-scheduler-pool/src/lib.rs
```diff
@@ -2869,10 +2869,8 @@ mod tests {
     }
 
     const SHORTENED_POOL_CLEANER_INTERVAL: Duration = Duration::from_millis(1);
-    const SHORTENED_MAX_POOLING_DURATION: Duration = Duration::from_millis(100);
 
     #[test]
-    #[ignore]
     fn test_scheduler_drop_idle() {
         agave_logger::setup();
 
@@ -2883,6 +2881,15 @@ mod tests {
             &TestCheckPoint::AfterIdleSchedulerCleaned,
         ]);
 
+        // Use 300ms pooling duration as a balance between:
+        // - Keeping the test fast (as small as possible)
+        // - Providing a large enough window to avoid the race condition where the second
+        //   scheduler could also be freed before we can assert only one remains
+        const TEST_MAX_POOLING_DURATION_MS: u64 = 300;
+        const TEST_MAX_POOLING_DURATION: Duration =
+            Duration::from_millis(TEST_MAX_POOLING_DURATION_MS);
+        const TEST_WAIT_FOR_IDLE_MS: u64 = TEST_MAX_POOLING_DURATION_MS + 200;
+        const TEST_WAIT_FOR_IDLE: Duration = Duration::from_millis(TEST_WAIT_FOR_IDLE_MS);
         let ignored_prioritization_fee_cache = Arc::new(PrioritizationFeeCache::new(0u64));
         let pool_raw = DefaultSchedulerPool::do_new(
             None,
@@ -2891,7 +2898,7 @@ mod tests {
             None,
             ignored_prioritization_fee_cache,
             SHORTENED_POOL_CLEANER_INTERVAL,
-            SHORTENED_MAX_POOLING_DURATION,
+            TEST_MAX_POOLING_DURATION,
             DEFAULT_MAX_USAGE_QUEUE_COUNT,
             DEFAULT_TIMEOUT_DURATION,
         );
@@ -2905,8 +2912,9 @@ mod tests {
         let new_scheduler_id = new_scheduler.id();
         Box::new(old_scheduler.into_inner().1).return_to_pool();
 
-        // sleepless_testing can't be used; wait a bit here to see real progress of wall time...
-        sleep(SHORTENED_MAX_POOLING_DURATION * 10);
+        // Wait for old_scheduler to be considered idle by the cleaner.
+        sleep(TEST_WAIT_FOR_IDLE);
+
         Box::new(new_scheduler.into_inner().1).return_to_pool();
 
         // Block solScCleaner until we see returned schedlers...
@@ -2916,12 +2924,8 @@ mod tests {
         // See the old (= idle) scheduler gone only after solScCleaner did its job...
         sleepless_testing::at(&TestCheckPoint::AfterIdleSchedulerCleaned);
 
-        // The following assertion is racy.
-        //
-        // We need to make sure new_scheduler isn't treated as idle up to now since being returned
-        // to the pool after sleep(SHORTENED_MAX_POOLING_DURATION * 10).
-        // Removing only old_scheduler is the expected behavior. So, make
-        // SHORTENED_MAX_POOLING_DURATION rather long...
+        // Only new_scheduler should remain. old_scheduler exceeds the
+        // TEST_MAX_POOLING_DURATION idle threshold, while new_scheduler does not.
         assert_eq!(pool_raw.scheduler_inners.lock().unwrap().len(), 1);
         assert_eq!(
             pool_raw
@@ -3012,6 +3016,7 @@ mod tests {
 
     #[test]
     fn test_scheduler_drop_stale() {
+        const SHORTENED_MAX_POOLING_DURATION: Duration = Duration::from_millis(100);
         agave_logger::setup();
 
         let _progress = sleepless_testing::setup(&[
```
