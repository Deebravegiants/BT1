# [?] fix: version overflow on total votes

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-18
Source: https://github.com/Conflux-Chain/conflux-rust/commit/9a97bbb182fbca9bfc719e8b8865999960b0b06f
Type: security-commit

## Details
fix: version overflow on total votes

## Patch
### crates/execution/executor/src/internal_contract/impls/params_control.rs
```diff
@@ -220,17 +220,18 @@ pub fn total_votes(
 
     let state = &context.state;
 
-    let votes_entries = if version + 1 == current_voting_version {
-        SETTLED_VOTES_ENTRIES.as_ref()
-    } else if version == current_voting_version {
-        CURRENT_VOTES_ENTRIES.as_ref()
-    } else {
-        internal_bail!(
-            "Unsupport version {} (current {})",
-            version,
-            current_voting_version
-        );
-    };
+    let votes_entries =
+        if version.checked_add(1) == Some(current_voting_version) {
+            SETTLED_VOTES_ENTRIES.as_ref()
+        } else if version == current_voting_version {
+            CURRENT_VOTES_ENTRIES.as_ref()
+        } else {
+            internal_bail!(
+                "Unsupport version {} (current {})",
+                version,
+                current_voting_version
+            );
+        };
 
     let mut answer = vec![];
     for x in 0..params_index_max(context.spec) {
@@ -263,17 +264,18 @@ pub fn pos_stake_for_votes(
         + 1;
 
     let state = &context.state;
-    let pos_stake_entry = if version + 1 == current_voting_version {
-        settled_pos_staking_for_votes()
-    } else if version == current_voting_version {
-        current_pos_staking_for_votes()
-    } else {
-        internal_bail!(
-            "Unsupport version {} (current {})",
-            version,
-            current_voting_version
-        );
-    };
+    let pos_stake_entry =
+        if version.checked_add(1) == Some(current_voting_version) {
+            settled_pos_staking_for_votes()
+        } else if version == current_voting_version {
+            current_pos_staking_for_votes()
+        } else {
+            internal_bail!(
+                "Unsupport version {} (current {})",
+                version,
+                current_voting_version
+            );
+        };
     Ok(state.get_system_storage(&pos_stake_entry)?)
 }
 
```
