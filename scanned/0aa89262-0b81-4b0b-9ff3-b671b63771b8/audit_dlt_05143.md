# [?] Fix panic when deserializing `Duration`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-10-24
Source: https://github.com/lightningdevkit/rust-lightning/commit/7b9bde12156f15b4268c53e2b3a7727fab0d10d5
Type: security-commit

## Details
Fix panic when deserializing `Duration`

`Duration::new` adds any nanoseconds in excess of a second to the
second part. This can overflow, however, panicking. In 0.2 we
introduced a few further cases where we store `Duration`s,
specifically some when handling network messages.

Sadly, that introduced a remotely-triggerable crash where someone
can send us, for example, a malicious blinded path context which
can cause us to panic.

Found by the `onion_message` fuzzer

## Patch
### lightning/src/util/ser.rs
```diff
@@ -1688,7 +1688,14 @@ impl Readable for Duration {
 	fn read<R: Read>(r: &mut R) -> Result<Self, DecodeError> {
 		let secs = Readable::read(r)?;
 		let nanos = Readable::read(r)?;
-		Ok(Duration::new(secs, nanos))
+		// Duration::new panics if the nanosecond part in excess of a second, added to the second
+		// part, overflows. To ensure this won't happen, we simply reject any case where there are
+		// nanoseconds in excess of a second, which is invalid anyway.
+		if nanos >= 1_000_000_000 {
+			Err(DecodeError::InvalidValue)
+		} else {
+			Ok(Duration::new(secs, nanos))
+		}
 	}
 }
 
```
