# [?] fix(test): keep temporary test data on panic (#5272)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-07-06
Source: https://github.com/nervosnetwork/ckb/commit/fe5f4962a6f6d2f04f73f653f51cc61e392ef56d
Type: security-commit

## Details
fix(test): keep temporary test data on panic (#5272)

<!--
Thank you for contributing to nervosnetwork/ckb!

If you haven't already, please read
[CONTRIBUTING](https://github.com/nervosnetwork/ckb/blob/develop/CONTRIBUTING.md)
document.

If you're unsure about anything, just ask; somebody should be along to
answer within a day or two.

**Important**: We use Squash Merge to merge PRs, so the PR title will
become the commit message.
Please ensure your PR title follows the [Conventional Commit
Messages](https://www.conventionalcommits.org/) format.

The most important prefixes you should use:

- `fix:`: represents bug fixes, and results in a SemVer patch bump.
- `feat:`: represents a new feature, and results in a SemVer minor bump.
- `<prefix>!:` (e.g. `feat!:`): represents a breaking change (indicated
by the !) and results in a SemVer major bump.

Other conventional prefixes are also acceptable (e.g., `docs:`,
`refactor:`, `test:`, `chore:`, etc.).
-->
### What problem does this PR solve?

Problem Summary:

When running `ckb-test` with `--keep-tmp-data`, temporary node
directories are still deleted when a spec panics or errors. This makes
it hard to inspect logs and state after a failed test run.

### What is changed and how it works?

When `clean_tmp` is false, call `std::mem::forget(path)` to prevent
`TempPathBuf` from removing the directory on drop.

### Related changes

### Check List <!--REMOVE the items that are not applicable-->

Tests
- Manual test (add detailed scripts or steps below)

Side effects
- No code changes to production logic.


### Manual test steps

make it panic (e.g.)
```diff
diff --git a/test/src/specs/alert/alert_propagation.rs b/test/src/specs/alert/alert_propagation.rs
index 3af797ecd..500d1cf93 100644
--- a/test/src/specs/alert/alert_propagation.rs
+++ b/test/src/specs/alert/alert_propagation.rs
@@ -34,6 +34,7 @@ impl Spec for AlertPropagation {
     //    2. cancel previous alert via node0; all nodes should receive the alert;
     //    3. resend the first alert, all nodes should ignore the alert.
     fn run(&self, nodes: &mut Vec<Node>) {
+        panic!("test");
         out_ibd_mode(nodes);
         connect_all(nodes);
```

```bash
> cargo run -p ckb-test -- AlertPropagation
> ls /tmp/ckb-it*
ls: cannot access '/tmp/ckb-it*': No such file or directory

> cargo run -p ckb-test -- --keep-tmp-data AlertPropagation
> # checkout tmp data
> ls /tmp/ckb-it*
/tmp/ckb-it-AlertPropagation-node0-sKWASe:
ckb.toml  data	default.db-options  specs

/tmp/ckb-it-AlertPropagation-node1-JaMyCc:
ckb.toml  data	default.db-options  specs

/tmp/ckb-it-AlertPropagation-node2-xPEPAY:
ckb.toml  data	default.db-options  specs
```

### test/src/lib.rs
```diff
@@ -216,9 +216,7 @@ pub fn main_test() {
                 spec_name,
                 seconds,
                 node_log_paths,
-                // node_paths is ignored here to let TempPathBuf handle
-                // automatic directory cleanup when this scope ends.
-                ..
+                node_paths,
             } => {
                 test_results.push(TestResult {
                     spec_name: spec_name.clone(),
@@ -237,13 +235,18 @@ pub fn main_test() {
                     info!("[{}] Error", spec_name);
                     tail_node_logs(&node_log_paths);
                 }
+                // `--keep-tmp-data` is set: preserve the test directories for post-mortem analysis.
+                if !clean_tmp {
+                    for path in node_paths {
+                        path.leak();
+                    }
+                }
             }
             Notify::Panick {
                 spec_name,
                 seconds,
                 node_log_paths,
-                // same as above
-                ..
+                node_paths,
             } => {
                 test_results.push(TestResult {
                     spec_name: spec_name.clone(),
@@ -262,6 +265,12 @@ pub fn main_test() {
                     info!("[{}] Panic", spec_name);
                     print_panicked_logs(&node_log_paths);
                 }
+                // same as above
+                if !clean_tmp {
+                    for path in node_paths {
+                        path.leak();
+                    }
+                }
             }
             Notify::Done {
                 spec_name,
@@ -285,6 +294,11 @@ pub fn main_test() {
                             warn!("failed to remove directory [{:?}] since {}", path, err);
                         }
                     }
+                } else {
+                    // same as above
+                    for path in node_paths {
+                        path.leak();
+                    }
                 }
             }
             Notify::Stop => {
```

### test/src/utils.rs
```diff
@@ -230,6 +230,13 @@ impl TempPathBuf {
     pub fn path(&self) -> &Path {
         &self.path
     }
+
+    /// Consumes the `TempPathBuf` and returns the underlying path without
+    /// deleting the temporary directory.
+    pub fn leak(self) -> PathBuf {
+        let mut this = std::mem::ManuallyDrop::new(self);
+        std::mem::take(&mut this.path)
+    }
 }
 
 impl Deref for TempPathBuf {
@@ -362,3 +369,23 @@ pub fn message_name(data: &Bytes) -> String {
         panic!("unknown message item");
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use std::fs::remove_dir_all;
+
+    #[test]
+    fn temp_path_buf_leak_keeps_directory() {
+        let temp = TempPathBuf::new("test", "leak");
+        let path = temp.path().to_owned();
+        let returned = temp.leak();
+        assert_eq!(returned, path);
+        assert!(
+            path.exists(),
+            "leak() should keep the temporary directory alive"
+        );
+        // Clean up manually since the test intentionally bypassed automatic cleanup.
+        remove_dir_all(&path).unwrap();
+    }
+}
```
