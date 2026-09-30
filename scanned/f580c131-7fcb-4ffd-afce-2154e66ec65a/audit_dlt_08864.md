# [?] Prevented panic on unexpected generic args for methods. (#6217)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-08-15
Source: https://github.com/starkware-libs/cairo/commit/95fd09bab0cc44c4f101987c62491454890e3ba4
Type: security-commit

## Details
Prevented panic on unexpected generic args for methods. (#6217)

## Patch
### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -1765,8 +1765,7 @@ fn compute_method_function_call_data(
         }
     };
     let (function_id, n_snapshots) =
-        infer_impl_by_self(ctx, trait_function_id, self_ty, method_syntax, generic_args_syntax)
-            .unwrap();
+        infer_impl_by_self(ctx, trait_function_id, self_ty, method_syntax, generic_args_syntax)?;
 
     let signature = ctx.db.trait_function_signature(trait_function_id).unwrap();
     let first_param = signature.params.into_iter().next().unwrap();
```

### crates/cairo-lang-semantic/src/expr/test_data/generics
```diff
@@ -91,11 +91,21 @@ fn foo() {
     bar::<felt252, felt252>();
     bar::<felt252>();
     bar::<usize, -1, A>();
+    1_felt252.method_no_generics::<felt252>();
+    1_felt252.method_one_generic::<felt252, felt252>();
+    1_felt252.method_two_generics::<felt252, felt252, felt252>();
 }
 
 //! > module_code
 fn bar<A, const B: usize, impl C: MyTrait<felt252>>() {}
 
+#[generate_trait]
+impl MyImpl of Generics {
+    fn method_no_generics(self: felt252) {}
+    fn method_one_generic<T>(self: felt252) {}
+    fn method_two_generics<T, S>(self: felt252) {}
+}
+
 //! > function_name
 foo
 
@@ -106,25 +116,40 @@ fn bar<A, const B: usize, impl C: MyTrait<felt252>>() {}
                                   ^*****^
 
 error: Expected 3 generic arguments, found 4.
- --> lib.cairo:3:20
+ --> lib.cairo:10:20
     bar::<1, 1, 1, 1>();
                    ^
 
 error: Expected variable or constant, found type.
- --> lib.cairo:4:20
+ --> lib.cairo:11:20
     bar::<felt252, felt252>();
                    ^*****^
 
 error: The value does not fit within the range of type core::integer::u32.
- --> lib.cairo:6:18
+ --> lib.cairo:13:18
     bar::<usize, -1, A>();
                  ^^
 
 error: Impl not found.
- --> lib.cairo:6:22
+ --> lib.cairo:13:22
     bar::<usize, -1, A>();
                      ^
 
+error: Expected 0 generic arguments, found 1.
+ --> lib.cairo:14:36
+    1_felt252.method_no_generics::<felt252>();
+                                   ^*****^
+
+error: Expected 1 generic arguments, found 2.
+ --> lib.cairo:15:45
+    1_felt252.method_one_generic::<felt252, felt252>();
+                                            ^*****^
+
+error: Expected 2 generic arguments, found 3.
+ --> lib.cairo:16:55
+    1_felt252.method_two_generics::<felt252, felt252, felt252>();
+                                                      ^*****^
+
 //! > ==========================================================================
 
 //! > Test generic impl
```

### crates/cairo-lang-semantic/src/items/imp.rs
```diff
@@ -1862,30 +1862,31 @@ pub fn infer_impl_by_self(
     self_ty: TypeId,
     stable_ptr: SyntaxStablePtrId,
     generic_args_syntax: Option<Vec<GenericArg>>,
-) -> Option<(FunctionId, usize)> {
+) -> Maybe<(FunctionId, usize)> {
     let lookup_context = ctx.resolver.impl_lookup_context();
-    let (concrete_trait_id, n_snapshots) = ctx.resolver.inference().infer_concrete_trait_by_self(
-        trait_function_id,
-        self_ty,
-        &lookup_context,
-        Some(stable_ptr),
-        |_| {},
-    )?;
+    let (concrete_trait_id, n_snapshots) = ctx
+        .resolver
+        .inference()
+        .infer_concrete_trait_by_self(
+            trait_function_id,
+            self_ty,
+            &lookup_context,
+            Some(stable_ptr),
+            |_| {},
+        )
+        .ok_or_else(skip_diagnostic)?;
 
     let concrete_trait_function_id =
         ConcreteTraitGenericFunctionLongId::new(ctx.db, concrete_trait_id, trait_function_id)
             .intern(ctx.db);
     let trait_func_generic_params =
         ctx.db.concrete_trait_function_generic_params(concrete_trait_function_id).unwrap();
-    let generic_args = ctx
-        .resolver
-        .resolve_generic_args(
-            ctx.diagnostics,
-            &trait_func_generic_params,
-            &generic_args_syntax.unwrap_or_default(),
-            stable_ptr,
-        )
-        .unwrap();
+    let generic_args = ctx.resolver.resolve_generic_args(
+        ctx.diagnostics,
+        &trait_func_generic_params,
+        &generic_args_syntax.unwrap_or_default(),
+        stable_ptr,
+    )?;
 
     let impl_lookup_context = ctx.resolver.impl_lookup_context();
     let inference = &mut ctx.resolver.inference();
@@ -1895,7 +1896,7 @@ pub fn infer_impl_by_self(
         Some(stable_ptr),
     );
 
-    Some((
+    Ok((
         FunctionLongId { function: ConcreteFunction { generic_function, generic_args } }
             .intern(ctx.db),
         n_snapshots,
```
