# [?] fix: prevent subtraction underflow in `NeighborStats::get_bandwidth`

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-07-01
Source: https://github.com/stacks-network/stacks-core/commit/b2b586f83148f800cd519aa4e04a423dc090aed8
Type: security-commit

## Details
fix: prevent subtraction underflow in `NeighborStats::get_bandwidth`

My mock-miner crashed overnight because the subtraction in the `else`
branch underflowed. While this won't crash a release build (and is
unlikely on a true 24/7 node, which won't go into energy saving like
apparently my laptop did), we should still handle it.

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
