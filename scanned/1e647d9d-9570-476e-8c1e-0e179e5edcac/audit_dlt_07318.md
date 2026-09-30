# [?] fix: Fix underflow in xnet_compatibility (#5529)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-06-12
Source: https://github.com/dfinity/ic/commit/2204d193d87a6a4584211101f97087dec3debd17
Type: security-commit

## Details
fix: Fix underflow in xnet_compatibility (#5529)

If targeted_latency_seconds is higher than runtime, check_success'
computation of the expected number of responses underflows. Use
saturating_sub() to prevent that.

## Patch
### rs/tests/message_routing/xnet/slo_test_lib/xnet_slo_test_lib.rs
```diff
@@ -425,9 +425,10 @@ pub fn check_success(
             m.latency_distribution.buckets().last().unwrap().1 + m.reject_responses;
         // All messages sent more than `targeted_latency_seconds` before the end of the
         // test should have gotten a response.
+        let runtime_seconds = config.runtime.as_secs();
         let responses_expected = ((m.calls_attempted - m.call_errors) as f64
-            * (config.runtime.as_secs() - config.targeted_latency_seconds) as f64
-            / config.runtime.as_secs() as f64) as usize;
+            * runtime_seconds.saturating_sub(config.targeted_latency_seconds) as f64
+            / runtime_seconds as f64) as usize;
         // Account for requests enqueued this round (in case canister messages were
         // executed before ingress messages, i.e. the heartbeat was executed before
         // metrics collection) or uncounted responses (if ingress executed first).
@@ -438,7 +439,7 @@ pub fn check_success(
             config.subnet_to_subnet_rate,
             responses_received
         );
-        let responses_expected = responses_expected - config.subnet_to_subnet_rate;
+        let responses_expected = responses_expected.saturating_sub(config.subnet_to_subnet_rate);
         let actual = format!(
             "{}/{}",
             responses_received,
```
