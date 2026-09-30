# [?] Merge rust-bitcoin/rust-bitcoin#6879: primitives: Fix Witness::get index overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-09-15
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/1cbf4bd62ea99c558c6d8ef794edbd984a2a4684
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#6879: primitives: Fix Witness::get index overflow

ca6bf03d0b41521327e9041104612aaf538ff703 primitives: Test Witness::get index overflow (Jamil Lambert, PhD)
fb0bbc1dd77da590f0ab94b166b41dd942a6410e primitives: Fix Witness::get index overflow (Jamil Lambert, PhD)

Pull request description:

  `Witness::get` passes a caller-controlled index to `decode_cursor`, which computes `start_of_indices + index * 4` with unchecked arithmetic. A large index such as `usize::MAX / 4 + 1` overflows: with overflow checks off it wraps back to element 0's offset and returns the first element instead of `None`, and with them on it panics.
  
  Use checked arithmetic so an out-of-range index returns `None`.
  
  Closes project-loupe/audit-rust-bitcoin#159


ACKs for top commit:
  apoelstra:
    ACK ca6bf03d0b41521327e9041104612aaf538ff703; successfully ran local tests
  tcharding:
    ACK ca6bf03d0b41521327e9041104612aaf538ff703
  satsfy:
    tACK ca6bf03d0b41521327e9041104612aaf538ff703


Tree-SHA512: f6538c5d214b8fa935ce14896d31e33eab6e640160160e152a76be486b62971f042edfd83eb62f5d9ff6ce6ab59f516cef6c676ce7e39259ac5af72d4049ee51

## Patch
### primitives/src/witness.rs
```diff
@@ -359,7 +359,7 @@ fn encode_cursor(bytes: &mut [u8], start_of_indices: usize, index: usize, value:
 
 #[inline]
 fn decode_cursor(bytes: &[u8], start_of_indices: usize, index: usize) -> Option<usize> {
-    let start = start_of_indices + index * 4;
+    let start = start_of_indices.checked_add(index.checked_mul(4)?)?;
     let pos = bytes.get_array::<4>(start).map(|index_bytes| u32::from_ne_bytes(*index_bytes))?;
     usize::try_from(pos).ok()
 }
@@ -1192,6 +1192,14 @@ mod test {
         assert_eq!(witness.last(), Some(element_2));
     }
 
+    #[test]
+    fn get_rejects_index_arithmetic_overflow() {
+        let witness = Witness::from([[0x42u8]]);
+        let wrapping_index = usize::MAX / 4 + 1;
+
+        assert_eq!(witness.get(wrapping_index), None);
+    }
+
     #[test]
     fn exact_sized_iterator() {
         let arbitrary_element = [1_u8, 2, 3];
```
