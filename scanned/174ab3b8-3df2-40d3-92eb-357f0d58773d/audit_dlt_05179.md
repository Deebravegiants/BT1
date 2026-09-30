# [?] Merge pull request #3565 from peilun-conflux/fix/consensus-blame-underflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-06
Source: https://github.com/Conflux-Chain/conflux-rust/commit/ff99ebe3e65ff93f8169542f2bb2570a22c6d3d4
Type: security-commit

## Details
Merge pull request #3565 from peilun-conflux/fix/consensus-blame-underflow

consensus: harden header blame arithmetic against underflow panics (#3565)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### crates/cfxcore/core/src/consensus/consensus_inner/mod.rs
```diff
@@ -1065,6 +1065,30 @@ impl ConsensusGraphInner {
         self.get_blame(arena_index)
     }
 
+    /// `blame` is an unbounded, attacker-controlled header field (no
+    /// acceptance check), so `trusted_index - blame - 1` can underflow. Honest
+    /// headers have `blame < trusted_index`, so `None` only replaces a panic on
+    /// malformed input; the honest walk is unchanged.
+    fn prev_trusted_pivot_index(
+        trusted_index: usize, blame: u32, from: usize,
+    ) -> Option<usize> {
+        match trusted_index
+            .checked_sub(blame as usize)
+            .and_then(|v| v.checked_sub(1))
+        {
+            Some(prev) if prev >= from => Some(prev),
+            _ => None,
+        }
+    }
+
+    /// Height just below the range of ancestors a header with the given
+    /// `blame` vouches for. `blame` is attacker-controlled and unbounded, so
+    /// `height - blame - 1` can underflow; `None` means the header blames past
+    /// genesis (impossible for an honest header) and its vote is invalid.
+    fn blame_covered_start_height(height: u64, blame: u32) -> Option<u64> {
+        height.checked_sub(blame as u64 + 1)
+    }
+
     pub fn find_first_index_with_correct_state_of(
         &self, pivot_index: usize, blame_bound: Option<u32>,
         min_vote_count: usize,
@@ -1093,13 +1117,10 @@ impl ConsensusGraphInner {
         // or equal to `from`
         while trusted_index != from {
             let blame = self.get_blame_with_pivot_index(trusted_index);
-            let prev_trusted = trusted_index - blame as usize - 1;
-
-            if prev_trusted < from {
-                break;
+            match Self::prev_trusted_pivot_index(trusted_index, blame, from) {
+                Some(prev_trusted) => trusted_index = prev_trusted,
+                None => break,
             }
-
-            trusted_index = prev_trusted;
         }
 
         Some(trusted_index)
@@ -2820,31 +2841,34 @@ impl ConsensusGraphInner {
                         // We need to make sure the ancestor at height
                         // self.arena[index].height - blame - 1 is state valid,
                         // and the remainings are not
-                        let start_height =
-                            self.arena[index].height - blame as u64 - 1;
-                        let mut cur_height = lca_height;
-                        let mut cur = lca;
-                        let mut vote_valid = true;
-                        while cur_height > start_height {
-                            if self.arena[cur].data.state_valid
-                                .expect("state_valid for me has been computed in \
-                                wait_and_compute_state_valid_locked by the caller, \
-                                so the precedents should have state_valid") {
-                                vote_valid = false;
-                                break;
+                        let vote_valid = match Self::blame_covered_start_height(
+                            self.arena[index].height,
+                            blame,
+                        ) {
+                            Some(start_height) => {
+                                let mut cur_height = lca_height;
+                                let mut cur = lca;
+                                let mut vote_valid = true;
+                                while cur_height > start_height {
+                                    if self.arena[cur].data.state_valid
+                                        .expect("state_valid for me has been computed in \
+                                        wait_and_compute_state_valid_locked by the caller, \
+                                        so the precedents should have state_valid") {
+                                        vote_valid = false;
+                                        break;
+                                    }
+                                    cur_height -= 1;
+                                    cur = self.arena[cur].parent;
+                                }
+                                vote_valid
+                                    && self.arena[cur].data.state_valid.expect(
+                                        "state_valid for me has been computed in \
+                                    wait_and_compute_state_valid_locked by the caller, \
+                                    so the precedents should have state_valid",
+                                    )
                             }
-                            cur_height -= 1;
-                            cur = self.arena[cur].parent;
-                        }
-                        if vote_valid
-                            && !self.arena[cur].data.state_valid.expect(
-                                "state_valid for me has been computed in \
-                            wait_and_compute_state_valid_locked by the caller, \
-                            so the precedents should have state_valid",
-                            )
-                        {
-                            vote_valid = false;
-                        }
+                            None => false,
+                        };
                         self.arena[index].data.vote_valid_lca_height =
                             lca_height;
                         self.arena[index].data.vote_valid = vote_valid;
@@ -3563,7 +3587,12 @@ impl ConsensusGraphInner {
                     .block_header_by_hash(&self.arena[cur].hash)
                     .unwrap()
                     .blame();
-                for i in 0..blame + 1 {
+                // `0..=blame` avoids overflowing the u32 counter at the
+                // attacker-controlled `blame == u32::MAX` (equivalent to the
+                // former `0..blame + 1`). The loop breaks at `cur == NULL`, so
+                // the walk is bounded by the parent chain and a large `blame`
+                // never iterates past genesis.
+                for i in 0..=blame {
                     self.arena[cur].data.state_valid = Some(i == 0);
                     trace!(
                         "recover_state_valid: index={} hash={} state_valid={}",
@@ -4163,3 +4192,89 @@ impl StateMaintenanceTrait for ConsensusGraphInner {
             .get_epoch_execution_commitment_with_db(block_hash)
     }
 }
+
+#[cfg(test)]
+mod blame_underflow_tests {
+    use super::ConsensusGraphInner;
+
+    // Reference "honest" arithmetic these helpers must reproduce exactly when
+    // the raw subtraction does not underflow.
+    fn naive_prev(
+        trusted_index: usize, blame: u32, from: usize,
+    ) -> Option<usize> {
+        let prev = trusted_index - blame as usize - 1;
+        if prev >= from {
+            Some(prev)
+        } else {
+            None
+        }
+    }
+
+    #[test]
+    fn blame_prev_trusted_pivot_index_matches_naive_on_honest_inputs() {
+        for &(trusted_index, blame, from) in &[
+            (100usize, 0u32, 10usize),
+            (100, 3, 10),
+            (100, 89, 10), // prev == from
+            (100, 90, 10), // prev < from -> None
+        ] {
+            assert_eq!(
+                ConsensusGraphInner::prev_trusted_pivot_index(
+                    trusted_index,
+                    blame,
+                    from
+                ),
+                naive_prev(trusted_index, blame, from),
+                "trusted_index={trusted_index} blame={blame} from={from}",
+            );
+        }
+    }
+
+    #[test]
+    fn blame_prev_trusted_pivot_index_no_panic_on_malicious_blame() {
+        // blame >= trusted_index underflows the old `trusted_index - blame -
+        // 1`.
+        assert_eq!(
+            ConsensusGraphInner::prev_trusted_pivot_index(5, 5, 0),
+            None
+        );
+        assert_eq!(
+            ConsensusGraphInner::prev_trusted_pivot_index(5, 10, 0),
+            None
+        );
+        assert_eq!(
+            ConsensusGraphInner::prev_trusted_pivot_index(0, u32::MAX, 0),
+            None
+        );
+        assert_eq!(
+            ConsensusGraphInner::prev_trusted_pivot_index(3, u32::MAX, 0),
+            None
+        );
+    }
+
+    #[test]
+    fn blame_covered_start_height_matches_naive_on_honest_inputs() {
+        for &(height, blame) in &[(100u64, 0u32), (100, 3), (100, 94)] {
+            assert_eq!(
+                ConsensusGraphInner::blame_covered_start_height(height, blame),
+                Some(height - blame as u64 - 1),
+                "height={height} blame={blame}",
+            );
+        }
+    }
+
+    #[test]
+    fn blame_covered_start_height_no_panic_on_malicious_blame() {
+        // blame >= height underflows the old `height - blame - 1`.
+        assert_eq!(ConsensusGraphInner::blame_covered_start_height(5, 5), None);
+        assert_eq!(
+            ConsensusGraphInner::blame_covered_start_height(5, 10),
+            None
+        );
+        assert_eq!(ConsensusGraphInner::blame_covered_start_height(0, 0), None);
+        assert_eq!(
+            ConsensusGraphInner::blame_covered_start_height(3, u32::MAX),
+            None
+        );
+    }
+}
```
