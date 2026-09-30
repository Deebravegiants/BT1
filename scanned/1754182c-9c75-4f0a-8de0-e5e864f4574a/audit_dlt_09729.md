# [?] core: fix panics decoding untrusted Duration and legacy SystemTime

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-11
Source: https://github.com/fedimint/fedimint/commit/e5de721dea27c702e7f7105516b8ebc7fa31a4ed
Type: security-commit

## Details
core: fix panics decoding untrusted Duration and legacy SystemTime

decode_legacy_system_time_from_finite_reader used UNIX_EPOCH + duration, which panics once duration is past what SystemTime can hold; use checked_add and return a DecodeError. Decodable for Duration accepted nsecs of one billion or more, which the encoder never writes, making decoding non-canonical and letting Duration::new panic. Both now return an error, and only input that previously aborted is rejected, so no persisted value becomes unreadable.

## Patch
### fedimint-core/src/encoding/mod.rs
```diff
@@ -299,7 +299,13 @@ pub fn decode_legacy_system_time_from_finite_reader<D: std::io::Read>(
     modules: &ModuleDecoderRegistry,
 ) -> Result<SystemTime, DecodeError> {
     let duration = Duration::consensus_decode_partial_from_finite_reader(decoder, modules)?;
-    Ok(UNIX_EPOCH + duration)
+    // `UNIX_EPOCH + duration` panics ("overflow when adding duration to instant")
+    // instead of erroring when `duration` is past what `SystemTime` can hold. A
+    // decoder must not abort the process on arbitrary bytes, so use the checked
+    // form. Anything that round-trips today still round-trips.
+    UNIX_EPOCH
+        .checked_add(duration)
+        .ok_or_else(|| DecodeError::from_str("SystemTime overflow: duration too large"))
 }
 
 /// Encodes an optional timestamp in the legacy `SystemTime` representation.
@@ -722,6 +728,13 @@ impl Decodable for Duration {
     ) -> Result<Self, DecodeError> {
         let secs = Decodable::consensus_decode_partial(d, modules)?;
         let nsecs = Decodable::consensus_decode_partial(d, modules)?;
+        // The encoder writes `subsec_nanos()`, which is always below one billion,
+        // so a larger `nsecs` is never something we wrote. Accepting it makes the
+        // encoding non-canonical and lets `Duration::new` panic when the carried
+        // second overflows `secs`.
+        if 1_000_000_000 <= nsecs {
+            return Err(DecodeError::from_str("Duration nanoseconds out of range"));
+        }
         Ok(Self::new(secs, nsecs))
     }
 }
@@ -1194,6 +1207,39 @@ mod tests {
         );
     }
 
+    #[test_log::test]
+    fn test_legacy_system_time_decode_overflow_is_an_error() {
+        // secs = u64::MAX is past what `SystemTime` can represent. No encoder we
+        // ship produces it, but a peer can put any u64 on the wire.
+        let mut bytes = Vec::new();
+        u64::MAX.consensus_encode(&mut bytes).unwrap();
+        0u32.consensus_encode(&mut bytes).unwrap();
+        decode_legacy_system_time_from_finite_reader(
+            &mut Cursor::new(bytes),
+            &ModuleDecoderRegistry::default(),
+        )
+        .expect_err("an unrepresentable timestamp must be a decode error, not a panic");
+    }
+
+    #[test_log::test]
+    fn test_duration_decode_rejects_out_of_range_nsecs() {
+        // secs = u64::MAX with nsecs = 1e9 carries a second and overflows `secs`
+        // inside `Duration::new`; it must be rejected instead.
+        let reg = ModuleDecoderRegistry::default();
+        let mut bad = Vec::new();
+        u64::MAX.consensus_encode(&mut bad).unwrap();
+        1_000_000_000u32.consensus_encode(&mut bad).unwrap();
+        Duration::consensus_decode_partial(&mut Cursor::new(bad), &reg)
+            .expect_err("nsecs of one billion must be rejected");
+
+        // The largest canonical nsecs must still decode.
+        let mut ok = Vec::new();
+        u64::MAX.consensus_encode(&mut ok).unwrap();
+        999_999_999u32.consensus_encode(&mut ok).unwrap();
+        Duration::consensus_decode_partial(&mut Cursor::new(ok), &reg)
+            .expect("the largest canonical nsecs must decode");
+    }
+
     #[test_log::test]
     fn test_finite_reader_shares_decode_limit_between_fields() {
         let field = vec![0u8; MAX_DECODE_SIZE / 2];
```
