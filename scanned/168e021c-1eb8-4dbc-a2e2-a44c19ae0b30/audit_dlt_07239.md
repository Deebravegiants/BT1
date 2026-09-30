# [?] [read/write set analysis] fix crash when updating return value via join

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-04-22
Source: https://github.com/move-language/move/commit/45f2ed0be3529c906ae79ca841b50686b6c6e6e4
Type: security-commit

## Details
[read/write set analysis] fix crash when updating return value via join

The analysis had an assertion that was meant to guard against updating `Return` variables more than once (since that should never happen). However, the assertion was overzealous in that although a `Return` can only be assigned once, the value associated with a `Return` can be updated via a join (e.g., when a procedure returns from several different control locations).

This PR adds a test that crashed the old analysis + removes the overzealous assertion.

Closes: #8258

## Patch
### language/move-prover/bytecode/src/access_path_trie.rs
```diff
@@ -235,22 +235,17 @@ impl<T: FootprintDomain> AccessPathTrie<T> {
         mut weak_update: bool,
     ) {
         let (root, offsets) = ap.into();
-        let key = match root {
-            Root::Local(i) =>
+        let needs_weak_update = match &root {
             // local base. strong update possible because of Move aliasing semantics
-            {
-                Root::local(i)
-            }
-            Root::Global(g) =>
+            Root::Local(_) | Root::Return(_) => false,
             // global base. must do weak update unless g is statically known
-            {
-                weak_update = weak_update || !g.is_statically_known();
-                Root::global(g)
-            }
-            Root::Return(_) => panic!("Invalid: updating return"),
+            Root::Global(g) => !g.is_statically_known(),
+        };
+        if needs_weak_update {
+            weak_update = true
         };
 
-        let mut node = self.0.entry(key).or_insert_with(TrieNode::default);
+        let mut node = self.0.entry(root).or_insert_with(TrieNode::default);
         for offset in offsets.into_iter() {
             // if one of the offsets is not statically known, we must do a weak update
             weak_update = weak_update || !offset.is_statically_known();
```

### language/move-prover/bytecode/tests/read_write_set/update_return.exp
```diff
@@ -0,0 +1,95 @@
+============ initial translation from Move ================
+
+[variant baseline]
+public fun UpdateReturn::abort_or_write($t0|s: &mut UpdateReturn::S, $t1|b: bool, $t2|x: u64): u64 {
+     var $t3: bool
+     var $t4: &mut UpdateReturn::S
+     var $t5: u64
+     var $t6: &mut UpdateReturn::S
+     var $t7: u64
+     var $t8: u64
+  0: $t3 := copy($t1)
+  1: if ($t3) goto 4 else goto 2
+  2: label L1
+  3: goto 9
+  4: label L0
+  5: $t4 := move($t0)
+  6: destroy($t4)
+  7: $t5 := 77
+  8: abort($t5)
+  9: label L2
+ 10: $t6 := move($t0)
+ 11: $t7 := copy($t2)
+ 12: $t8 := UpdateReturn::write_f($t6, $t7)
+ 13: return $t8
+}
+
+
+[variant baseline]
+public fun UpdateReturn::write_f($t0|s: &mut UpdateReturn::S, $t1|x: u64): u64 {
+     var $t2: u64
+     var $t3: &mut UpdateReturn::S
+     var $t4: &mut u64
+     var $t5: u64
+  0: $t2 := 7
+  1: $t3 := move($t0)
+  2: $t4 := borrow_field<UpdateReturn::S>.f($t3)
+  3: write_ref($t4, $t2)
+  4: $t5 := copy($t1)
+  5: return $t5
+}
+
+============ after pipeline `read_write_set` ================
+
+[variant baseline]
+public fun UpdateReturn::abort_or_write($t0|s: &mut UpdateReturn::S, $t1|b: bool, $t2|x: u64): u64 {
+     var $t3: bool
+     var $t4: &mut UpdateReturn::S
+     var $t5: u64
+     var $t6: &mut UpdateReturn::S
+     var $t7: u64
+     var $t8: u64
+     # Accesses:
+     # Loc(0)/f: Write
+     #
+     # Locals:
+     # Ret(0): {Loc(2), Ret(0), }
+     #
+  0: $t3 := copy($t1)
+  1: if ($t3) goto 4 else goto 2
+  2: label L1
+  3: goto 9
+  4: label L0
+  5: $t4 := move($t0)
+  6: destroy($t4)
+  7: $t5 := 77
+  8: abort($t5)
+  9: label L2
+ 10: $t6 := move($t0)
+ 11: $t7 := copy($t2)
+ 12: $t8 := UpdateReturn::write_f($t6, $t7)
+ 13: return $t8
+}
+
+
+[variant baseline]
+public fun UpdateReturn::write_f($t0|s: &mut UpdateReturn::S, $t1|x: u64): u64 {
+     var $t2: u64
+     var $t3: &mut UpdateReturn::S
+     var $t4: &mut u64
+     var $t5: u64
+     # Accesses:
+     # Loc(0)/f: Write
+     #
+     # Locals:
+     # Loc(0): Loc(0)
+     # Loc(0)/f: Loc(0)/f
+     # Ret(0): Loc(1)
+     #
+  0: $t2 := 7
+  1: $t3 := move($t0)
+  2: $t4 := borrow_field<UpdateReturn::S>.f($t3)
+  3: write_ref($t4, $t2)
+  4: $t5 := copy($t1)
+  5: return $t5
+}
```

### language/move-prover/bytecode/tests/read_write_set/update_return.move
```diff
@@ -0,0 +1,17 @@
+address 0x1 {
+module UpdateReturn {
+
+    struct S has key { f: u64 }
+
+    public fun write_f(s: &mut S, x: u64): u64 {
+        s.f = 7;
+        x
+    }
+
+    // this function will update the return value via a join
+    public fun abort_or_write(s: &mut S, b: bool, x: u64): u64 {
+        if (b) abort(77);
+        write_f(s, x)
+    }
+}
+}
```
