# [?] fix: LcVarsIterMut::size_hint off-by-one and potential underflow (#412)

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/snark
Published: 2025-09-12
Source: https://github.com/arkworks-rs/snark/commit/845ce9d50bbe535792f04b44db78b009ee402ed7
Type: security-commit

## Details
fix: LcVarsIterMut::size_hint off-by-one and potential underflow (#412)

* fix: LcVarsIterMut::size_hint off-by-one and potential underflow

* add a test

## Patch
### relations/src/gr1cs/lc_map.rs
```diff
@@ -305,7 +305,7 @@ impl<'a> Iterator for LcVarsIterMut<'a> {
 
     #[inline]
     fn size_hint(&self) -> (usize, Option<usize>) {
-        let len = self.offsets.len() - 1;
+        let len = self.offsets.len();
         (len, Some(len))
     }
 }
@@ -566,4 +566,17 @@ mod tests {
 
         assert_eq!(flattened, expected);
     }
+
+    #[test]
+    fn test_lc_vars_iter_mut_size_hint_empty() {
+        // When there are no linear combinations, `LcMap::offsets` has length 1,
+        // so `offsets.windows(2)` yields zero windows. The iterator's size_hint
+        // must therefore be (0, Some(0)) and must not panic.
+        let mut lcmap = LcMap::<Fr>::new();
+
+        let mut it = lcmap.lc_vars_iter_mut();
+        let (lower, upper) = it.size_hint();
+        assert_eq!((lower, upper), (0, Some(0)));
+        assert!(it.next().is_none());
+    }
 }
```
