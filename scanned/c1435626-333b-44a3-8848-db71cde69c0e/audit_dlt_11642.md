# [?] Merge rust-bitcoin/rust-bitcoin#6946: Fix integer overflow in `get_array`

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-09-28
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/c6e80843437072a6c66fb85e3dc59453b9ef5e6a
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#6946: Fix integer overflow in `get_array`

56fb1287d8f590f1a739b5b23f0d621efa89dc33 Fix integer overflow in `get_array` (Martin Habovstiak)

Pull request description:

  The `get_array` method promised to return `None` in case of out-of-bounds access but internally tried to add caller-controlled values which would result in integer overflow. In case overflow happens the attempted read is certainly out of bounds - goes beyond address space. Therefore this commit treats it as such and fixes it to return `None`.
  
  **This bug was found by creusot.** :tada: :tada: :tada: 
  
  Though now that I think about it, it would only cause crashes with debug assertions but ironically, without them it would work fine because the garbage `end` value would make the range invalid causing `get` to return `None.` Still, I believe this fix is better than changing it to `wrapping_add` because it's less confusing for both humans and creusot and there's a good chance the compiler will optimize-out the check.


ACKs for top commit:
  apoelstra:
    ACK 56fb1287d8f590f1a739b5b23f0d621efa89dc33; successfully ran local tests
  tcharding:
    ACK 56fb1287d8f590f1a739b5b23f0d621efa89dc33


Tree-SHA512: 970ed2cbbf7a8510854a307ba85929221fefb8b18fe34beed560e116cbe9d111b14150579ee329fdcb97ef0f2da1b8da6bc58e45133f2b1573fa9d7d2f8bd177

## Patch
### internals/src/slice.rs
```diff
@@ -96,7 +96,8 @@ impl<T> SliceExt for [T] {
     }
 
     fn get_array<const ARRAY_LEN: usize>(&self, offset: usize) -> Option<&[Self::Item; ARRAY_LEN]> {
-        self.get(offset..(offset + ARRAY_LEN)).map(|slice| {
+        let end = offset.checked_add(ARRAY_LEN)?;
+        self.get(offset..end).map(|slice| {
             slice
                 .try_into()
                 .expect("the arguments to `get` evaluate to the same length the return type uses")
```
