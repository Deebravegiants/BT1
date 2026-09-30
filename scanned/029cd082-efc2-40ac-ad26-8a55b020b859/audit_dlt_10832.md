# [?] Merge pull request #7372 from benjamin-stacks/fix/get-bandwidth-underflow

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-07-01
Source: https://github.com/stacks-network/stacks-core/commit/baac5e5f4894896f7b4bf7343f45f4872ef65c3c
Type: security-commit

## Details
Merge pull request #7372 from benjamin-stacks/fix/get-bandwidth-underflow

fix: prevent subtraction underflow in `NeighborStats::get_bandwidth`

## Patch
### changelog.d/7372-get-bandwidth-underflow.fixed
```diff
@@ -0,0 +1 @@
+Gracefully handle clock skew when computing P2P bandwidth stats.
\ No newline at end of file
```

### stackslib/src/net/chat.rs
```diff
@@ -272,7 +272,8 @@ impl NeighborStats {
             }
         }
 
-        if elapsed_time_start == elapsed_time_end {
+        // "greater than" is possible if the system clock was adjusted between recordings
+        if elapsed_time_start >= elapsed_time_end {
             total_bytes as f64
         } else {
             (total_bytes as f64) / ((elapsed_time_end - elapsed_time_start) as f64)
@@ -7421,4 +7422,37 @@ mod test {
             .is_some());
         assert_eq!(convo_1.stats.msgs_err, err_before);
     }
+
+    #[test]
+    fn test_get_bandwidth() {
+        let recently = get_epoch_time_secs() - 1;
+        let longer_ago = recently - 6;
+
+        let mut counts = VecDeque::<(u64, u64)>::new();
+        counts.push_back((recently, 54));
+        counts.push_back((longer_ago, 18));
+        assert_eq!(
+            NeighborStats::get_bandwidth(&counts, 1000),
+            72f64,
+            "non-monotonous timestamps should be treated like 1 second apart"
+        );
+
+        let mut counts = VecDeque::<(u64, u64)>::new();
+        counts.push_back((recently, 54));
+        counts.push_back((recently, 18));
+        assert_eq!(
+            NeighborStats::get_bandwidth(&counts, 1000),
+            72f64,
+            "identical timestamps should be treated like 1 second apart"
+        );
+
+        let mut counts = VecDeque::<(u64, u64)>::new();
+        counts.push_back((longer_ago, 54));
+        counts.push_back((recently, 18));
+        assert_eq!(
+            NeighborStats::get_bandwidth(&counts, 1000),
+            12f64, // 72 divided by 6
+            "properly ordered timestamps should be handled correctly"
+        );
+    }
 }
```
