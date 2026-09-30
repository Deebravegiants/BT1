# [?] fix(kona): return error instead of panic on unknown batch type (#20000)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-10
Source: https://github.com/ethereum-optimism/optimism/commit/88cd69c83a01986e98508b4ab9415e45de7415fa
Type: security-commit

## Details
fix(kona): return error instead of panic on unknown batch type (#20000)

* fix(kona): return error instead of panic on unknown batch type

BatchType::from(u8) panicked on unknown batch type values. This is a
protocol deviation — the OP spec requires unknown batch versions to be
treated as invalid and ignored, matching op-node's behavior of returning
an error and skipping to the next channel.

Replace From<u8> with TryFrom<u8>, add UnknownBatchType variant to
BatchDecodingError, and propagate the error in Batch::decode.

Fixes ethereum-optimism/optimism-private#484

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(kona): rustfmt

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### rust/kona/crates/protocol/protocol/src/batch/core.rs
```diff
@@ -42,7 +42,7 @@ impl Batch {
         }
 
         // Read the batch type
-        let batch_type = BatchType::from(r[0]);
+        let batch_type = BatchType::try_from(r[0]).map_err(BatchDecodingError::UnknownBatchType)?;
         r.advance(1);
 
         match batch_type {
@@ -131,6 +131,13 @@ mod tests {
         }), decoded);
     }
 
+    #[test]
+    fn test_unknown_batch_type_returns_error() {
+        let data = [0xFF, 0x00]; // unknown batch type 0xFF followed by dummy data
+        let result = Batch::decode(&mut data.as_slice(), &RollupConfig::default());
+        assert_eq!(result, Err(BatchDecodingError::UnknownBatchType(0xFF)));
+    }
+
     #[test]
     fn test_empty_span_batch() {
         let mut out = Vec::new();
```

### rust/kona/crates/protocol/protocol/src/batch/errors.rs
```diff
@@ -40,6 +40,9 @@ pub enum BatchDecodingError {
     /// Empty buffer
     #[error("Empty buffer")]
     EmptyBuffer,
+    /// Unknown batch type
+    #[error("Unknown batch type: {0}")]
+    UnknownBatchType(u8),
     /// Error decoding an Alloy RLP
     #[error("Error decoding an Alloy RLP: {0}")]
     AlloyRlpError(alloy_rlp::Error),
```

### rust/kona/crates/protocol/protocol/src/batch/type.rs
```diff
@@ -28,12 +28,14 @@ pub enum BatchType {
     Span = SPAN_BATCH_TYPE,
 }
 
-impl From<u8> for BatchType {
-    fn from(val: u8) -> Self {
+impl TryFrom<u8> for BatchType {
+    type Error = u8;
+
+    fn try_from(val: u8) -> Result<Self, Self::Error> {
         match val {
-            SINGLE_BATCH_TYPE => Self::Single,
-            SPAN_BATCH_TYPE => Self::Span,
-            _ => panic!("Invalid batch type: {val}"),
+            SINGLE_BATCH_TYPE => Ok(Self::Single),
+            SPAN_BATCH_TYPE => Ok(Self::Span),
+            _ => Err(val),
         }
     }
 }
@@ -51,7 +53,7 @@ impl Encodable for BatchType {
 impl Decodable for BatchType {
     fn decode(buf: &mut &[u8]) -> alloy_rlp::Result<Self> {
         let val = u8::decode(buf)?;
-        Ok(Self::from(val))
+        Self::try_from(val).map_err(|_| alloy_rlp::Error::Custom("invalid batch type"))
     }
 }
 
@@ -68,4 +70,25 @@ mod test {
         let decoded = BatchType::decode(&mut buf.as_slice()).unwrap();
         assert_eq!(batch_type, decoded);
     }
+
+    #[test]
+    fn test_try_from_valid_types() {
+        assert_eq!(BatchType::try_from(SINGLE_BATCH_TYPE), Ok(BatchType::Single));
+        assert_eq!(BatchType::try_from(SPAN_BATCH_TYPE), Ok(BatchType::Span));
+    }
+
+    #[test]
+    fn test_try_from_unknown_type_returns_error() {
+        assert_eq!(BatchType::try_from(0xFF), Err(0xFF));
+        assert_eq!(BatchType::try_from(0x02), Err(0x02));
+    }
+
+    #[test]
+    fn test_rlp_decode_unknown_type_returns_error() {
+        let mut buf = Vec::new();
+        // RLP-encode an invalid batch type byte
+        0xFFu8.encode(&mut buf);
+        let result = BatchType::decode(&mut buf.as_slice());
+        assert!(result.is_err());
+    }
 }
```
