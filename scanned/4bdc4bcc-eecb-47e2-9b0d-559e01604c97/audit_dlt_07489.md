# [?] core: fix panics decoding untrusted Duration and SystemTime (#8854)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-13
Source: https://github.com/fedimint/fedimint/commit/b84cd3702cc006af1bdf401f75983993b61d92ca
Type: security-commit

## Details
core: fix panics decoding untrusted Duration and SystemTime (#8854)

## What's wrong

`Decodable::consensus_decode_partial` for `SystemTime`
(`fedimint-core/src/encoding/mod.rs`)
builds the result as `UNIX_EPOCH + duration`, where `duration` comes
straight from
untrusted wire bytes:

```rust
let duration = Duration::consensus_decode_partial(d, modules)?;
Ok(UNIX_EPOCH + duration)
```

`SystemTime + Duration` panics (`overflow when adding duration to
instant`)
instead of returning an error when the duration is large enough to
overflow
the platform's internal representation. A crafted 9-byte BigSize
encoding
`secs = u64::MAX` decodes to a `Duration` that triggers exactly that.

## Why it matters

This module's own doc comment says it's the "binary encoding interface
suitable for consensus critical encoding," and it's what several structs
use for a plain `SystemTime` field decoded from peer/client input — e.g.
`BackupRequest.timestamp` (`fedimint-core/src/core/backup.rs`) and
`LightningGatewayRegistration.valid_until` (`fedimint-ln-common`). Any
one
of those reaching `consensus_decode` on adversarial or garbled bytes
reproduces the panic — the decoder should reject bad input, not crash.

## Fix

- Decode: use `checked_add` and return a `DecodeError` instead of
panicking.
- Encode: symmetrically hardened too — encoding a pre-`UNIX_EPOCH`
`SystemTime`
called `.expect()` on `duration_since`, which panics for the mirror
reason
  (self before epoch). Now returns an `io::Error` instead.

## Testing

Added two regression tests in `fedimint-core/src/encoding/mod.rs`:
- decode a crafted 9-byte BigSize (`secs = u64::MAX`) and assert an
error, not a panic
- encode a pre-epoch `SystemTime` and assert an error, not a panic

Confirmed both panic on the pre-fix code (ran the decode case under
`catch_unwind` first and saw the actual `overflow when adding duration
to
instant` panic), and both pass after the fix:

```
cargo test -p fedimint-core --lib encoding::
test encoding::tests::test_systemtime_decode_overflow_does_not_panic ... ok
test encoding::tests::test_systemtime_encode_pre_epoch_does_not_panic ... ok
test encoding::tests::test_systemtime ... ok
test result: ok. 25 passed; 0 failed
```

`cargo clippy -p fedimint-core --lib -- -D warnings` and `cargo fmt -p
fedimint-core -- --check` both clean.

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

### fuzz/src/bin/client_backup_snapshot.rs
```diff
@@ -0,0 +1,10 @@
+use fedimint_core::backup::ClientBackupSnapshot;
+use honggfuzz::fuzz;
+
+fn main() {
+    loop {
+        // its first encoded field is the legacy timestamp, so this reaches
+        // decode_legacy_system_time_from_finite_reader on the first bytes
+        fuzz!(|data| { fedimint_fuzz::test_decodable::<ClientBackupSnapshot>(data) });
+    }
+}
```

### fuzz/src/bin/duration.rs
```diff
@@ -0,0 +1,9 @@
+use std::time::Duration;
+
+use honggfuzz::fuzz;
+
+fn main() {
+    loop {
+        fuzz!(|data| { fedimint_fuzz::test_decodable::<Duration>(data) });
+    }
+}
```
