# [?] [IndexerFN] Update the timestamp conversion to avoid overflow. (#16732)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-05-30
Source: https://github.com/aptos-labs/aptos-core/commit/1adc0f07b58a1939ce7e62197193e6e5414f1f5d
Type: security-commit

## Details
[IndexerFN] Update the timestamp conversion to avoid overflow. (#16732)

## Patch
### ecosystem/indexer-grpc/indexer-grpc-fullnode/src/convert.rs
```diff
@@ -539,14 +539,15 @@ pub fn convert_event(event: &Event) -> transaction::Event {
 }
 
 pub fn convert_timestamp_secs(timestamp: u64) -> timestamp::Timestamp {
+    let timestamp = std::cmp::min(timestamp, i64::MAX as u64);
     timestamp::Timestamp {
         seconds: timestamp as i64,
         nanos: 0,
     }
 }
 
 pub fn convert_timestamp_usecs(timestamp: u64) -> timestamp::Timestamp {
-    let ts = Duration::from_nanos(timestamp * 1000);
+    let ts = Duration::from_micros(timestamp);
     timestamp::Timestamp {
         seconds: ts.as_secs() as i64,
         nanos: ts.subsec_nanos() as i32,
```
