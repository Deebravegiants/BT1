# [?] add guard check to avoid underflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-03
Source: https://github.com/Conflux-Chain/conflux-rust/commit/daa77ffba840d0c844241eed93705c563dc202de
Type: security-commit

## Details
add guard check to avoid underflow

## Patch
### crates/pos/types/types/src/term_state.rs
```diff
@@ -445,11 +445,13 @@ impl TermList {
     fn serving_votes(
         &self, target_term_offset: usize, author: &AccountAddress,
     ) -> u64 {
-        assert!(target_term_offset < TERM_LIST_LEN + 2);
+        assert!(
+            target_term_offset >= TERM_LIST_LEN - 1
+                && target_term_offset < TERM_LIST_LEN + 2
+        );
         // TODO(lpl): Optimize by adding hash set to each term or adding another
         // field to node_map.
-        let start_term_offset =
-            target_term_offset as usize - (TERM_LIST_LEN - 1);
+        let start_term_offset = target_term_offset - (TERM_LIST_LEN - 1);
 
         // The checking of `target_view` ensures that this is in range of
         // `term_list`.
@@ -458,7 +460,7 @@ impl TermList {
         // `target_term`.
         let mut serving_votes = Vec::with_capacity(TERM_LIST_LEN);
         for i in start_term_offset..target_term_offset {
-            let term = &self.term_list[i as usize];
+            let term = &self.term_list[i];
             serving_votes.push(term.node_list.serving_votes(author));
         }
         return serving_votes.iter().sum();
```
