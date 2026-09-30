# [?] Fix overflow when subtracting durations (#1194) (#1464)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2021-09-24
Source: https://github.com/hyperledger-iroha/iroha/commit/f3ee5943bf9736fb42000d27ca8b0bfd5a5d3c19
Type: security-commit

## Details
Fix overflow when subtracting durations (#1194) (#1464)

Signed-off-by: s8sato <49983831+s8sato@users.noreply.github.com>

## Patch
### iroha/src/tx.rs
```diff
@@ -181,7 +181,7 @@ impl AcceptedTransaction {
             .duration_since(SystemTime::UNIX_EPOCH)
             .expect("Failed to get System Time.");
 
-        (current_time - Duration::from_millis(self.payload.creation_time))
+        current_time.saturating_sub(Duration::from_millis(self.payload.creation_time))
             > min(
                 Duration::from_millis(self.payload.time_to_live_ms),
                 transaction_time_to_live,
```
