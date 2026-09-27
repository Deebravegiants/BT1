# [?] fix: overflow in new `next_attempt_after` calculation (#5487)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2025-02-17
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/8fc28501ff0c2f0351b17707e2252102ed9d7c35
Type: security-commit

## Details
fix: overflow in new `next_attempt_after` calculation (#5487)

### Description

Due to our lack of unit testing coverage, an overflow bug caused by
https://github.com/hyperlane-xyz/hyperlane-monorepo/pull/5455 wasn't
caught. This bug happened on 7 chains on RC and took down their
submitters.

I've noticed it now on RC due to the rising prep queues
([source](https://abacusworks.grafana.net/goto/kbQcXdcNR?orgId=1)), and
also confirmed using these logs:
https://cloudlogging.app.goo.gl/zJKqhTCTPAxETTg79.

I'm not sure why but for crashed submitters, the prep queue keeps
increasing although the only logic pushing to it lives in the submitter.
Maybe's there's a future cancellation issue with `receive_task` and as a
result it's still alive
([source](https://github.com/hyperlane-xyz/hyperlane-monorepo/blob/ab2917a424534cb034400ad85836b9f833832aaf/rust/main/agents/relayer/src/msg/op_submitter.rs#L222)).
[Logs](https://cloudlogging.app.goo.gl/qEjQq5AaFPWpvrv58) show that
messages are successfully sent over [this
channel](https://github.com/hyperlane-xyz/hyperlane-monorepo/blob/ab2917a424534cb034400ad85836b9f833832aaf/rust/main/agents/relayer/src/msg/processor.rs#L306)
to the submitter (to `base` in the logs linked), and this operation
would fail if no receiving end existed.

This PR adds a unit test that would've caught the overflow, and lowers
the max backoff period from `u32::MAX` to 10 weeks into the future.

### Drive-by changes

- Refactors the logic that calculates `next_attempt` after so it can be
tested
- adds `chrono` as a relayer dependency to easily calcualte how many
seconds are in 10 weeks

### Backward compatibility

Yes

### Testing

Adds a unit test that would have caught the overflow

### rust/main/agents/relayer/Cargo.toml
```diff
@@ -11,6 +11,7 @@ version.workspace = true
 [dependencies]
 async-trait.workspace = true
 axum.workspace = true
+chrono.workspace = true
 config.workspace = true
 console-subscriber.workspace = true
 convert_case.workspace = true
@@ -55,7 +56,6 @@ hyperlane-ethereum = { path = "../../chains/hyperlane-ethereum" }
 
 [dev-dependencies]
 axum = { workspace = true, features = ["macros"] }
-chrono.workspace = true
 once_cell.workspace = true
 mockall.workspace = true
 tokio-test.workspace = true
```

### rust/main/agents/relayer/src/msg/pending_message.rs
```diff
@@ -531,15 +531,18 @@ impl PendingMessage {
         let message_status = Self::get_message_status(ctx.origin_db.clone(), &message);
         let mut pending_message = Self::new(message, ctx, message_status, app_context, max_retries);
         if num_retries > 0 {
-            let next_attempt_after =
-                PendingMessage::calculate_msg_backoff(num_retries, max_retries, None)
-                    .map(|dur| Instant::now() + dur);
+            let next_attempt_after = Self::next_attempt_after(num_retries, max_retries);
             pending_message.num_retries = num_retries;
             pending_message.next_attempt_after = next_attempt_after;
         }
         Some(pending_message)
     }
 
+    fn next_attempt_after(num_retries: u32, max_retries: u32) -> Option<Instant> {
+        PendingMessage::calculate_msg_backoff(num_retries, max_retries, None)
+            .map(|dur| Instant::now() + dur)
+    }
+
     fn get_retries_or_skip(
         origin_db: Arc<dyn HyperlaneDb>,
         message: &HyperlaneMessage,
@@ -716,7 +719,7 @@ impl PendingMessage {
                         "Message has been retried too many times, skipping",
                     );
                 }
-                u64::MAX
+                chrono::Duration::weeks(10).num_seconds() as u64
             }
         }))
     }
@@ -760,7 +763,11 @@ impl MessageSubmissionMetrics {
 
 #[cfg(test)]
 mod test {
-    use std::{fmt::Debug, sync::Arc, time::Duration};
+    use std::{
+        fmt::Debug,
+        sync::Arc,
+        time::{Duration, Instant},
+    };
 
     use hyperlane_base::db::*;
     use hyperlane_core::*;
@@ -888,22 +895,23 @@ mod test {
     fn test_calculate_msg_backoff_does_not_overflow() {
         use super::PendingMessage;
         use std::time::Duration;
-        let ten_weeks = Duration::from_secs(
-            chrono::Duration::weeks(10)
-                .num_seconds()
-                .try_into()
-                .unwrap(),
-        );
+        let ten_weeks_from_now = Instant::now()
+            + Duration::from_secs(
+                chrono::Duration::weeks(10)
+                    .num_seconds()
+                    .try_into()
+                    .unwrap(),
+            );
 
-        // the backoff should be at least 10 weeks into the future
-        // this is really an overflow check more than anything
-        assert!(PendingMessage::calculate_msg_backoff(
+        // this is really an overflow check
+        let next_prepare_attempt = PendingMessage::next_attempt_after(
             DEFAULT_MAX_MESSAGE_RETRIES,
             DEFAULT_MAX_MESSAGE_RETRIES,
-            None
         )
-        .unwrap()
-        .gt(&ten_weeks));
+        .unwrap();
+
+        // the backoff should be at least 10 weeks into the future
+        assert!(next_prepare_attempt.gt(&ten_weeks_from_now));
     }
 
     #[test]
```
