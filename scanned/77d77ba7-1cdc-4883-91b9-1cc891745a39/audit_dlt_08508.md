# [?] Fix panic in telemetry (#4336)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2019-12-09
Source: https://github.com/paritytech/substrate/commit/1caae8b62e910637ca2e6f3b716f5f3c4f1ea019
Type: security-commit

## Details
Fix panic in telemetry (#4336)

## Patch
### client/telemetry/src/async_record.rs
```diff
@@ -103,7 +103,6 @@ impl Serializer for ToSendSerializer {
 		Ok(())
 	}
 
-	#[cfg(feature = "nested-values")]
 	fn emit_serde(&mut self, key: Key, value: &slog::SerdeValue) -> slog::Result {
 		let val = value.to_sendable();
 		take(&mut self.kv, |kv| Box::new((kv, SingleKV(key, val))));
@@ -153,4 +152,4 @@ impl AsyncRecord {
 			BorrowedKV(&self.kv),
 		), &self.logger_values)
 	}
-}    
\ No newline at end of file
+}
```
