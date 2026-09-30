# [?] Fix underflow in `StorageVec`'s `insert` (#4508)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-04-28
Source: https://github.com/FuelLabs/sway/commit/1a5e59b60b1ea0a1db949f09e55d7dd0e799f93a
Type: security-commit

## Details
Fix underflow in `StorageVec`'s `insert` (#4508)

## Description
Fix #4489


## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### sway-lib-std/src/storage/storage_vec.sw
```diff
@@ -25,7 +25,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -59,7 +59,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -103,7 +103,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -152,7 +152,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -214,7 +214,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -269,7 +269,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -318,7 +318,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -362,7 +362,8 @@ impl<V> StorageKey<StorageVec<V>> {
             // shifts all the values up one index
             write::<V>(key, 0, read::<V>(sha256((count, self.slot)), 0).unwrap());
 
-            count -= 1
+            if count == 0 { break; }
+            count -= 1;
         }
 
         // inserts the value into the now unused index
@@ -382,7 +383,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -410,7 +411,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -442,7 +443,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
@@ -480,7 +481,7 @@ impl<V> StorageKey<StorageVec<V>> {
     /// ### Examples
     ///
     /// ```sway
-    /// use std::storage::StorageVec;
+    /// use std::storage::storage_vec::*;
     ///
     /// storage {
     ///     vec: StorageVec<u64> = StorageVec {}
```

### test/src/e2e_vm_tests/test_programs/should_pass/stdlib/storage_vec_insert/Forc.lock
```diff
@@ -0,0 +1,13 @@
+[[package]]
+name = 'core'
+source = 'path+from-root-D63F86D6205FE44D'
+
+[[package]]
+name = 'std'
+source = 'path+from-root-D63F86D6205FE44D'
+dependencies = ['core']
+
+[[package]]
+name = 'storage_vec_insert'
+source = 'member'
+dependencies = ['std']
```

### test/src/e2e_vm_tests/test_programs/should_pass/stdlib/storage_vec_insert/Forc.toml
```diff
@@ -0,0 +1,9 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "lib.sw"
+license = "Apache-2.0"
+name = "storage_vec_insert"
+implicit-std = false
+
+[dependencies]
+std = { path = "../../../../../../../sway-lib-std" }
```

### test/src/e2e_vm_tests/test_programs/should_pass/stdlib/storage_vec_insert/src/lib.sw
```diff
@@ -0,0 +1,27 @@
+contract;
+
+use std::storage::storage_vec::*;
+
+abi MyContract {
+    #[storage(read, write)]
+    fn test_function() -> bool;
+}
+
+storage {
+    foo: StorageVec<u32> = StorageVec {},
+}
+
+impl MyContract for Contract {
+    #[storage(read, write)]
+    fn test_function() -> bool {
+        storage.foo.push(0);
+        storage.foo.insert(0, 123);
+        true
+    }
+}
+
+#[test]
+fn test_test_function() {
+    let caller = abi(MyContract, CONTRACT_ID);
+    let res: bool = caller.test_function();
+}
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_pass/stdlib/storage_vec_insert/test.toml
```diff
@@ -0,0 +1 @@
+category = "unit_tests_pass"
```
