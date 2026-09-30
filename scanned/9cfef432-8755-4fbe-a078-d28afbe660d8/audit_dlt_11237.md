# [?] fix(elaborator): detect cyclic type aliases to prevent stack overflow (#12633)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-05-15
Source: https://github.com/noir-lang/noir/commit/c7a3bec082b671950aa2eee917c451645e30a45f
Type: security-commit

## Details
fix(elaborator): detect cyclic type aliases to prevent stack overflow (#12633)

## Patch
### compiler/noirc_frontend/src/elaborator/mod.rs
```diff
@@ -531,6 +531,9 @@ impl<'context> Elaborator<'context> {
             self.define_type_alias(alias_id, alias);
         }
 
+        // Check for type aliases cycles
+        self.push_errors(self.interner.check_for_dependency_cycles());
+
         // Must resolve types before we resolve globals.
         self.collect_struct_definitions(&items.structs);
         self.collect_enum_definitions(&items.enums);
```

### compiler/noirc_frontend/src/node_interner/dependency.rs
```diff
@@ -108,9 +108,6 @@ impl NodeInterner {
                 }
                 DependencyId::Alias(alias_id) => {
                     let alias = self.get_type_alias(alias_id);
-                    // If type aliases form a cycle, break the cycle to prevent infinite recursion in later phases.
-                    alias.borrow_mut().typ = Type::Error;
-
                     let alias = alias.borrow();
                     push_error(alias.name.to_string(), scc, scc_index, alias.name.location());
                     true
@@ -154,6 +151,28 @@ impl NodeInterner {
         let strongly_connected_components = tarjan_scc(&self.dependency_graph);
         for scc in strongly_connected_components {
             if scc.len() > 1 {
+                // If any alias in this SCC has already had its body replaced with
+                // `Type::Error`, the cycle was broken (and reported) by an earlier
+                // pass. Skip the entire SCC to avoid duplicate diagnostics when
+                // `check_for_dependency_cycles` is called more than once.
+                let already_reported = scc.iter().any(|&node_index| {
+                    if let DependencyId::Alias(alias_id) = self.dependency_graph[node_index] {
+                        matches!(self.get_type_alias(alias_id).borrow().typ, Type::Error)
+                    } else {
+                        false
+                    }
+                });
+                if already_reported {
+                    continue;
+                }
+
+                // Break every alias in the cycle
+                for &node_index in &scc {
+                    if let DependencyId::Alias(alias_id) = self.dependency_graph[node_index] {
+                        self.get_type_alias(alias_id).borrow_mut().typ = Type::Error;
+                    }
+                }
+
                 // If a SCC contains a type, type alias, or global, it must be the only element in the SCC
                 for (scc_index, node_index) in scc.iter().enumerate() {
                     if push_error_from_index(&scc, scc_index, *node_index) {
```

### compiler/noirc_frontend/src/tests/aliases.rs
```diff
@@ -1162,6 +1162,30 @@ fn no_false_cycle_from_stale_current_item_after_type_alias() {
     assert_no_errors(src);
 }
 
+/// Regression test: a pair of mutually-referencing type aliases used to overflow the stack.
+#[test]
+fn cyclic_type_aliases_referenced_from_comptime_global_do_not_stack_overflow() {
+    let src = r#"
+        type A = B;
+        type B = A;
+             ^ Dependency cycle found
+             ~ 'B' recursively depends on itself: B -> A -> B
+
+        global G: u32 = f();
+
+        fn f() -> u32 {
+            let _ = A::foo();
+                    ^ Could not resolve 'A' in path
+            1
+        }
+
+        fn main() {
+            let _ = G;
+        }
+    "#;
+    check_errors(src);
+}
+
 #[test]
 fn unused_expression_result_correct_span() {
     let src = r#"
```
