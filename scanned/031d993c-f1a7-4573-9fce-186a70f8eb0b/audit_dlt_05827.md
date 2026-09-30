# [?] fix: test-loop: panic less on failed tests. (#14290)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-22
Source: https://github.com/near/nearcore/commit/86d5f7b29306618fe0b8c6ada602e513a13791c3
Type: security-commit

## Details
fix: test-loop: panic less on failed tests. (#14290)

When tests fail it results in panic and it's expected that in that case
test loop wouldn't be shutdown properly. Extra panic creates noise and
makes it harder to see the actual test failure so this PR avoids panic
on testloop drop when we are already panicking which makes failed test
output much easier to read.

## Patch
### core/async/src/test_loop/mod.rs
```diff
@@ -73,6 +73,7 @@ use serde::Serialize;
 use std::collections::{BinaryHeap, HashSet};
 use std::sync::Arc;
 use std::sync::atomic::{AtomicBool, Ordering};
+use std::thread::panicking;
 use time::ext::InstantExt;
 
 /// Main struct for the Test Loop framework.
@@ -444,11 +445,13 @@ impl Drop for TestLoopV2 {
             // Drop any references that may be held by the event callbacks. This can help
             // with destruction of the data.
             self.events.clear();
-            panic!(
-                "Event scheduled at {} is not handled at the end of the test: {}.
+            if !panicking() {
+                panic!(
+                    "Event scheduled at {} is not handled at the end of the test: {}.
                      Consider calling `test.shutdown_and_drain_remaining_events(...)`.",
-                event.due, event.event.description
-            );
+                    event.due, event.event.description
+                );
+            }
         }
         // Needed for the log visualizer to know when the test loop ends.
         tracing::info!(target: "test_loop", "TEST_LOOP_SHUTDOWN");
```
