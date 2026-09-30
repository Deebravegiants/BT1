# [?] fix: increment depth counter in follow_bindings to prevent stack overflow (#11461)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-02-04
Source: https://github.com/noir-lang/noir/commit/35bc8434211c6666dcce64ff4a7e07b0cb7d92f2
Type: security-commit

## Details
fix: increment depth counter in follow_bindings to prevent stack overflow (#11461)

## Patch
### compiler/noirc_frontend/src/hir_def/types.rs
```diff
@@ -2630,10 +2630,11 @@ impl Type {
     ///
     /// Expected to be called on an instantiated type (with no Type::Foralls)
     pub fn follow_bindings(&self) -> Type {
-        fn helper(this: &Type, i: u32) -> Type {
+        fn helper(this: &Type, mut i: u32) -> Type {
             if i >= TYPE_RECURSION_LIMIT {
                 panic!("Type recursion limit reached - types are too large")
             }
+            i += 1;
             let recur = |typ| helper(typ, i);
 
             use Type::*;
@@ -3477,3 +3478,60 @@ impl PartialEq for Type {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    /// Creates a tuple type nested to the specified depth.
+    /// For example, depth 3 creates: (((Field,),),)
+    fn create_nested_tuple(depth: usize) -> Type {
+        let mut typ = Type::FieldElement;
+        for _ in 0..depth {
+            typ = Type::Tuple(vec![typ]);
+        }
+        typ
+    }
+
+    #[test]
+    fn follow_bindings_on_shallow_tuple() {
+        // Depth 99 is within the limit
+        let typ = create_nested_tuple((TYPE_RECURSION_LIMIT - 1) as usize);
+        let result = typ.follow_bindings();
+        assert!(matches!(result, Type::Tuple(_)));
+    }
+
+    #[test]
+    #[should_panic(expected = "Type recursion limit reached - types are too large")]
+    fn follow_bindings_on_deeply_nested_tuple() {
+        // Depth 100 hits the limit
+        let typ = create_nested_tuple(TYPE_RECURSION_LIMIT as usize);
+        let _ = typ.follow_bindings();
+    }
+
+    /// Creates an array type nested to the specified depth.
+    /// For example, depth 3 creates: [[[Field; 1]; 1]; 1]
+    fn create_nested_array(depth: usize) -> Type {
+        let mut typ = Type::FieldElement;
+        for _ in 0..depth {
+            typ = Type::Array(Box::new(Type::Constant(1.into(), Kind::u32())), Box::new(typ));
+        }
+        typ
+    }
+
+    #[test]
+    fn follow_bindings_on_shallow_array() {
+        // Depth 99 is within the limit (siblings share depth)
+        let typ = create_nested_array((TYPE_RECURSION_LIMIT - 1) as usize);
+        let result = typ.follow_bindings();
+        assert!(matches!(result, Type::Array(_, _)));
+    }
+
+    #[test]
+    #[should_panic(expected = "Type recursion limit reached - types are too large")]
+    fn follow_bindings_on_deeply_nested_array() {
+        // Depth 100 hits the limit
+        let typ = create_nested_array(TYPE_RECURSION_LIMIT as usize);
+        let _ = typ.follow_bindings();
+    }
+}
```

### compiler/noirc_frontend/src/monomorphization/tests.rs
```diff
@@ -460,6 +460,7 @@ fn multiple_trait_impls_with_different_instantiations() {
 #[should_panic(expected = "Type recursion limit reached - types are too large")]
 fn extreme_type_alias_chain_stack_overflow() {
     // Generate a chain of 2,000 type aliases programmatically
+    // This exercises follow_bindings_shallow which handles alias chains.
     // ```
     // type Alias2000 = u8;
     // type Alias1999 = Alias2000;
@@ -492,6 +493,31 @@ fn extreme_type_alias_chain_stack_overflow() {
     let _ = get_monomorphized(&src);
 }
 
+#[test]
+#[should_panic(expected = "Type recursion limit reached - types are too large")]
+fn deeply_nested_tuple_type_stack_overflow() {
+    // Generate deeply nested tuple types by wrapping values repeatedly.
+    // This exercises follow_bindings which handles nested type structures.
+    // Each wrap adds one level: Field -> (Field,) -> ((Field,),) -> ...
+    use crate::TYPE_RECURSION_LIMIT;
+    const DEPTH: usize = TYPE_RECURSION_LIMIT as usize + 10;
+
+    let mut body = String::from("let v0: Field = 1;\n");
+    for i in 1..=DEPTH {
+        body.push_str(&format!("    let v{i} = (v{},);\n", i - 1));
+    }
+
+    let src = format!(
+        r#"
+fn main() {{
+    {body}
+}}
+"#
+    );
+
+    let _ = get_monomorphized(&src);
+}
+
 #[test]
 fn tuple_pattern_becomes_separate_params() {
     let src = r#"
```
