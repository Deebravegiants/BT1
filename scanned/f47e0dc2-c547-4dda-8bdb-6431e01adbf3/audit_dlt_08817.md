# [?] fix(taiko-client-rs): prevent derivation panic on oversized manifest size field (#21948)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-07-13
Source: https://github.com/taikoxyz/taiko-mono/commit/f91132c4dcfa4f23f0a97192de465f6f3aef784c
Type: security-commit

## Details
fix(taiko-client-rs): prevent derivation panic on oversized manifest size field (#21948)

Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### packages/taiko-client-rs/crates/protocol/src/shasta/manifest.rs
```diff
@@ -162,15 +162,20 @@ fn decode_manifest_payload(bytes: &[u8], offset: usize) -> Result<Vec<u8>> {
         ProtocolError::InvalidPayload(format!("size field exceeds usize range: {size_u64}"))
     })?;
 
-    if bytes.len() < offset + 64 + size {
+    // Bound the compressed slice `[start, start + size)` with subtraction so a hostile `size`
+    // (attacker-controlled up to `u64::MAX` in a forced-inclusion blob) cannot overflow the
+    // `start + size` addition and panic. The header check above guarantees `start <= bytes.len()`,
+    // so `bytes.len() - start` never underflows, and `size <= remaining` keeps `start + size`
+    // within bounds. Mirrors the Go reference `DerivationSourceFetcher.manifestFromBlobBytes`.
+    let start = offset + 64;
+    let remaining = bytes.len() - start;
+    if remaining < size {
         return Err(ProtocolError::InvalidPayload(format!(
-            "payload too short for compressed data: expected {} bytes, got {}",
-            offset + 64 + size,
-            bytes.len()
+            "payload too short for compressed data: need {size} bytes after offset {start}, got {remaining}"
         )));
     }
 
-    let compressed = &bytes[offset + 64..offset + 64 + size];
+    let compressed = &bytes[start..start + size];
     let mut decoder = ZlibDecoder::new(compressed);
     let mut decoded = Vec::new();
     decoder
@@ -381,4 +386,48 @@ mod tests {
         let decoded = DerivationSourceManifest::decompress_and_decode(&encoded, 0).unwrap();
         assert_eq!(decoded.blocks.len(), manifest.blocks.len());
     }
+
+    #[test]
+    fn test_decode_manifest_payload_size_u64_max_returns_err() {
+        // A forced-inclusion blob can set the size word to u64::MAX. The bounds check must reject
+        // it with an error instead of overflowing `offset + 64 + size` and panicking (which would
+        // bypass the default-manifest fallback and crash derivation).
+        let mut payload = vec![0u8; 64];
+        payload[31] = SHASTA_PAYLOAD_VERSION;
+        payload[56..64].fill(0xFF); // size word low 64 bits = u64::MAX
+
+        let result = decode_manifest_payload(&payload, 0);
+        assert!(result.is_err());
+        assert!(result.unwrap_err().to_string().contains("payload too short for compressed data"));
+    }
+
+    #[test]
+    fn test_decompress_and_decode_size_u64_max_returns_default() {
+        // The overflow-triggering payload must degrade to the default manifest via the decode
+        // fallback, matching Go, rather than panicking the derivation pipeline.
+        let mut payload = vec![0u8; 64];
+        payload[31] = SHASTA_PAYLOAD_VERSION;
+        payload[56..64].fill(0xFF);
+
+        let decoded = DerivationSourceManifest::decompress_and_decode(&payload, 0)
+            .expect("hostile size must fall back to default, not return a hard error");
+        assert_eq!(decoded.blocks.len(), DerivationSourceManifest::default().blocks.len());
+        assert_eq!(
+            decoded.blocks[0].gas_limit,
+            DerivationSourceManifest::default().blocks[0].gas_limit
+        );
+    }
+
+    #[test]
+    fn test_decode_manifest_payload_size_exceeds_remaining_returns_err() {
+        // A `size` larger than the bytes available after the header (without overflowing) must be
+        // rejected so the compressed slice never reads out of bounds.
+        let mut payload = vec![0u8; 66]; // 64-byte header + 2 trailing bytes
+        payload[31] = SHASTA_PAYLOAD_VERSION;
+        payload[63] = 100; // size = 100, but only 2 bytes remain after the header
+
+        let result = decode_manifest_payload(&payload, 0);
+        assert!(result.is_err());
+        assert!(result.unwrap_err().to_string().contains("payload too short for compressed data"));
+    }
 }
```
