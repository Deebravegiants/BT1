# [?] fix string slice panic issue

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-19
Source: https://github.com/Conflux-Chain/conflux-rust/commit/0cabcf7fc50d04e482354e5dd48b56f3dbfaebe0
Type: security-commit

## Details
fix string slice panic issue

## Patch
### crates/execution/solidity-abi/src/utils.rs
```diff
@@ -145,10 +145,11 @@ pub fn string_revert_reason_decode(output: &Bytes) -> String {
     };
     match decode_result {
         Ok(str) => {
-            if str.len() < MAX_LENGTH {
+            if str.chars().count() <= MAX_LENGTH {
                 str
             } else {
-                format!("{}...", str[..MAX_LENGTH].to_string())
+                let truncated: String = str.chars().take(MAX_LENGTH).collect();
+                format!("{}...", truncated)
             }
         }
         Err(_) => "".to_string(),
@@ -158,6 +159,7 @@ pub fn string_revert_reason_decode(output: &Bytes) -> String {
 #[cfg(test)]
 mod test {
     use super::string_revert_reason_decode;
+    use cfx_bytes::Bytes;
     use rustc_hex::FromHex;
 
     #[test]
@@ -172,4 +174,45 @@ mod test {
             string_revert_reason_decode(&input_hex.from_hex().unwrap())
         );
     }
+
+    #[test]
+    fn test_decode_result_with_utf8_multibyte() {
+        // Build ABI-encoded Error(string) with 60 Chinese chars
+        let long_str: String = "测".repeat(60);
+        let data_len = long_str.len();
+        let padded_len = (data_len + 31) / 32 * 32;
+        let mut data = vec![0u8; 32 + 32 + padded_len];
+        // Offset to string data (32)
+        data[31] = 0x20;
+        // String length as big-endian U256
+        data[63] = data_len as u8;
+        // String data
+        data[64..64 + data_len].copy_from_slice(long_str.as_bytes());
+        let mut output = Bytes::from(vec![8, 195, 121, 160]);
+        output.extend(data);
+        let result = string_revert_reason_decode(&output);
+        // Should have 50 Chinese chars + "..."
+        assert_eq!(result.len(), 153); // 50 * 3 + 3
+        assert!(result.ends_with("..."));
+        assert_eq!(result.chars().count(), 53); // 50 chars + 3 dots
+    }
+
+    #[test]
+    fn test_decode_result_short_utf8() {
+        // Build ABI-encoded Error(string) with short Chinese string
+        let short_str = "中文测试";
+        let data_len = short_str.len();
+        let padded_len = (data_len + 31) / 32 * 32;
+        let mut data = vec![0u8; 32 + 32 + padded_len];
+        // Offset = 32
+        data[31] = 0x20;
+        // Length
+        data[63] = data_len as u8;
+        // Data
+        data[64..64 + data_len].copy_from_slice(short_str.as_bytes());
+        let mut output = Bytes::from(vec![8, 195, 121, 160]);
+        output.extend(data);
+        let result = string_revert_reason_decode(&output);
+        assert_eq!(result, "中文测试");
+    }
 }
```
