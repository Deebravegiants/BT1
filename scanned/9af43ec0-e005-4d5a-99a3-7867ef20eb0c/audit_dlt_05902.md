# [?] [fix] #3928: Fix double free in wasm tests

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger/iroha
Published: 2023-09-28
Source: https://github.com/hyperledger-iroha/iroha/commit/f6f4a9fdc5a66781027374aa1ad7b7d7667644c6
Type: security-commit

## Details
[fix] #3928: Fix double free in wasm tests

The `log` and `dbg` functions do not take the pointer ownership, but their mock versions used for testing did

Signed-off-by: Nikita Strygin <dcnick3@users.noreply.github.com>

## Patch
### wasm/src/debug.rs
```diff
@@ -169,15 +169,17 @@ mod tests {
 
     use webassembly_test::webassembly_test;
 
-    use crate::_decode_from_raw;
-
     fn get_dbg_message() -> &'static str {
         "dbg_message"
     }
 
     #[no_mangle]
     pub unsafe extern "C" fn _dbg_mock(ptr: *const u8, len: usize) {
-        assert_eq!(_decode_from_raw::<String>(ptr, len), get_dbg_message());
+        use parity_scale_codec::DecodeAll;
+
+        // can't use _decode_from_raw here, because we must NOT take the ownership
+        let bytes = core::slice::from_raw_parts(ptr, len);
+        assert_eq!(String::decode_all(&mut &*bytes).unwrap(), get_dbg_message());
     }
 
     #[webassembly_test]
```

### wasm/src/log.rs
```diff
@@ -88,15 +88,16 @@ mod tests {
     use webassembly_test::webassembly_test;
 
     use super::*;
-    use crate::_decode_from_raw;
 
     fn get_log_message() -> &'static str {
         "log_message"
     }
 
     #[no_mangle]
     pub unsafe extern "C" fn _log_mock(ptr: *const u8, len: usize) {
-        let (log_level, msg) = _decode_from_raw::<(u8, String)>(ptr, len);
+        // can't use _decode_from_raw here, because we must NOT take the ownership
+        let bytes = core::slice::from_raw_parts(ptr, len);
+        let (log_level, msg) = <(u8, String)>::decode_all(&mut &*bytes).unwrap();
         assert_eq!(log_level, 3);
         assert_eq!(msg, get_log_message());
     }
```
