# [?] fix(ssa): drain visit-once queues iteratively so wide array literals don't overflow the stack (#13702)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-09-14
Source: https://github.com/noir-lang/noir/commit/6723512315171f1314cf9362b51d15a630f01a81
Type: security-commit

## Details
fix(ssa): drain visit-once queues iteratively so wide array literals don't overflow the stack (#13702)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/constant_folding/mod.rs
```diff
@@ -1321,6 +1321,29 @@ mod test {
         assert_ssa_does_not_change(&src, |ssa| ssa.fold_constants(MIN_ITER));
     }
 
+    // Regression for noir-claude#1829.
+    // A repeated array literal `[v; N]` lowers to a `make_array` holding one value in all N element
+    // positions, so invalidating the cache for a mutation of it enqueues that value N times. Every
+    // copy after the first is a duplicate the worklist has to skip, and skipping them must cost no
+    // stack, or a wide enough literal aborts the compiler with a stack overflow.
+    #[test]
+    fn array_mutation_invalidation_does_not_recurse_over_repeated_elements() {
+        const WIDTH: usize = 100_000;
+
+        let elements = vec!["v0"; WIDTH].join(", ");
+        let src = format!(
+            "brillig(inline) fn main f0 {{
+              b0(v0: Field, v1: u32):
+                v2 = make_array [{elements}] : [Field; {WIDTH}]
+                v3 = array_set v2, index v1, value v0
+                return v3
+            }}
+            "
+        );
+
+        assert_ssa_does_not_change(&src, |ssa| ssa.fold_constants(MIN_ITER));
+    }
+
     // Regression for noir-claude#1224.
     // A constant zero-sized-type array (empty `element_types`, e.g. `[(); 3]`) passed as a
     // constant argument to a brillig call reaches the constant-folding interpreter, which must
```

### compiler/noirc_evaluator/src/ssa/visit_once_deque.rs
```diff
@@ -25,14 +25,25 @@ impl<T: Hash + Eq + Copy> VisitOnceDeque<T> {
         self.block_queue.extend(items);
     }
 
+    /// Skipping already-visited items is done with a loop rather than a recursive call: the queue
+    /// can hold an arbitrarily long run of duplicates (a `[v; N]` array literal enqueues one value
+    /// N times), and one stack frame per skipped item overflows the stack on large N.
     pub(crate) fn pop_front(&mut self) -> Option<T> {
-        let item = self.block_queue.pop_front()?;
-        if self.visited_blocks.insert(item) { Some(item) } else { self.pop_front() }
+        while let Some(item) = self.block_queue.pop_front() {
+            if self.visited_blocks.insert(item) {
+                return Some(item);
+            }
+        }
+        None
     }
 
     pub(crate) fn pop_back(&mut self) -> Option<T> {
-        let item = self.block_queue.pop_back()?;
-        if self.visited_blocks.insert(item) { Some(item) } else { self.pop_back() }
+        while let Some(item) = self.block_queue.pop_back() {
+            if self.visited_blocks.insert(item) {
+                return Some(item);
+            }
+        }
+        None
     }
 }
 
@@ -57,4 +68,13 @@ mod tests {
         assert_eq!(deque.pop_front(), None);
         assert_eq!(deque.pop_back(), None);
     }
+
+    #[test]
+    fn draining_a_long_run_of_duplicates_does_not_consume_stack() {
+        let mut deque = VisitOnceDeque::default();
+        deque.extend(std::iter::repeat_n(7u32, 1_000_000));
+
+        assert_eq!(deque.pop_front(), Some(7));
+        assert_eq!(deque.pop_front(), None);
+    }
 }
```

### compiler/noirc_evaluator/src/ssa/visit_once_priority_queue.rs
```diff
@@ -30,15 +30,26 @@ impl<P: Ord, T: Ord + Copy> VisitOncePriorityQueue<P, T> {
         }
     }
 
+    /// As in [`VisitOnceDeque`](crate::ssa::visit_once_deque::VisitOnceDeque), already-visited
+    /// items are skipped with a loop rather than a recursive call, so that the stack cost of a
+    /// drain stays constant however many duplicates the queue holds.
     pub(crate) fn pop_front(&mut self) -> Option<T> {
-        let (_, item) = self.queue.pop_first()?;
-        if self.visited.insert(item) { Some(item) } else { self.pop_front() }
+        while let Some((_, item)) = self.queue.pop_first() {
+            if self.visited.insert(item) {
+                return Some(item);
+            }
+        }
+        None
     }
 
     #[allow(unused)]
     pub(crate) fn pop_back(&mut self) -> Option<T> {
-        let (_, item) = self.queue.pop_last()?;
-        if self.visited.insert(item) { Some(item) } else { self.pop_back() }
+        while let Some((_, item)) = self.queue.pop_last() {
+            if self.visited.insert(item) {
+                return Some(item);
+            }
+        }
+        None
     }
 }
 
```
