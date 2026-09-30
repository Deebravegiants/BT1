# [?] Prevent stack overflow when defining a trait method with certain types (#3280)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-12-10
Source: https://github.com/FuelLabs/sway/commit/c9565f83ffdac2ef3f78eb442c85680b89509fb7
Type: security-commit

## Details
Prevent stack overflow when defining a trait method with certain types (#3280)

This PR fixes a bug that was causing a stack overflow when a trait method impl differentiated from a trait method definition. The fix was to draw a direct comparison between the expected type (the type from the definition) and the found type (the type from the impl) instead of trying to unify the found type into the expected type.

Closes #3271

## Patch
### sway-core/src/semantic_analysis/ast_node/declaration/impl_trait.rs
```diff
@@ -674,7 +674,7 @@ fn type_check_trait_implementation(
         // replace instances of `TypeInfo::SelfType` with a fresh
         // `TypeInfo::SelfType` to avoid replacing types in the original trait
         // declaration
-        impl_method_signature.replace_self_type(type_engine, ctx.self_type());
+        impl_method_signature.replace_self_type(type_engine, self_type);
 
         // ensure this fn decl's parameters and signature lines up with the one
         // in the trait
@@ -695,8 +695,8 @@ fn type_check_trait_implementation(
         // with the parameters of the function signature
         for (impl_method_signature_param, impl_method_param) in impl_method_signature
             .parameters
-            .iter()
-            .zip(&impl_method.parameters)
+            .iter_mut()
+            .zip(&mut impl_method.parameters)
         {
             // TODO use trait constraints as part of the type here to
             // implement trait constraint solver */
@@ -715,14 +715,13 @@ fn type_check_trait_implementation(
                 });
             }
 
-            let (new_warnings, new_errors) = type_engine.unify_right_with_self(
-                impl_method_param.type_id,
-                impl_method_signature_param.type_id,
-                ctx.self_type(),
-                &impl_method_signature_param.type_span,
-                ctx.help_text(),
-            );
-            if !new_warnings.is_empty() || !new_errors.is_empty() {
+            impl_method_param
+                .type_id
+                .replace_self_type(type_engine, self_type);
+            if !type_engine.look_up_type_id(impl_method_param.type_id).eq(
+                &type_engine.look_up_type_id(impl_method_signature_param.type_id),
+                type_engine,
+            ) {
                 errors.push(CompileError::MismatchedTypeInInterfaceSurface {
                     interface_name: interface_name(),
                     span: impl_method_param.type_span.clone(),
@@ -755,16 +754,13 @@ fn type_check_trait_implementation(
             });
         }
 
-        // unify the return type of the implemented function and the return
-        // type of the signature
-        let (new_warnings, new_errors) = type_engine.unify_right_with_self(
-            impl_method.return_type,
-            impl_method_signature.return_type,
-            ctx.self_type(),
-            &impl_method.return_type_span,
-            ctx.help_text(),
-        );
-        if !new_warnings.is_empty() || !new_errors.is_empty() {
+        impl_method
+            .return_type
+            .replace_self_type(type_engine, self_type);
+        if !type_engine.look_up_type_id(impl_method.return_type).eq(
+            &type_engine.look_up_type_id(impl_method_signature.return_type),
+            type_engine,
+        ) {
             errors.push(CompileError::MismatchedTypeInInterfaceSurface {
                 interface_name: interface_name(),
                 span: impl_method.return_type_span.clone(),
```

### sway-error/src/error.rs
```diff
@@ -155,8 +155,9 @@ pub enum CompileError {
     )]
     MultipleImmediates(Span),
     #[error(
-        "Expected: {expected} \n\
-         found:    {given}. The definition of this function must \
+        "expected: {expected} \n\
+         found:    {given} \n\
+         help:     The definition of this function must \
          match the one in the {interface_name} declaration."
     )]
     MismatchedTypeInInterfaceSurface {
```

### test/src/e2e_vm_tests/test_programs/should_fail/abi_method_signature_mismatch/test.toml
```diff
@@ -1,13 +1,16 @@
 category = "fail"
 
 # check: fn foo(s: str[7]) -> str[7] {
-# check: $()Expected: u64
-# check: $()found:    str[7]. The definition of this function must match the one in the ABI "MyContract" declaration.
+# check: $()expected: u64
+# check: $()found:    str[7]
+# check: $()The definition of this function must match the one in the ABI "MyContract" declaration.
 
 # check: fn bar() -> u64 {
-# check: $()Expected: u32
-# check: $()found:    u64. The definition of this function must match the one in the ABI "MyContract" declaration.
+# nextln: $()expected: u32
+# nextln: $()found:    u64
+# nextln: $()The definition of this function must match the one in the ABI "MyContract" declaration.
 
 # check: fn baz() {
-# check: $()Expected: u64
-# check: $()found:    (). The definition of this function must match the one in the ABI "MyContract" declaration.
+# nextln: $()expected: u64
+# nextln: $()found:    ()
+# nextln: $()The definition of this function must match the one in the ABI "MyContract" declaration.
```

### test/src/e2e_vm_tests/test_programs/should_fail/trait_method_signature_mismatch/Forc.lock
```diff
@@ -1,3 +1,13 @@
+[[package]]
+name = 'core'
+source = 'path+from-root-67618F664448A0EB'
+
+[[package]]
+name = 'std'
+source = 'path+from-root-67618F664448A0EB'
+dependencies = ['core']
+
 [[package]]
 name = 'trait_method_signature_mismatch'
 source = 'member'
+dependencies = ['std']
```

### test/src/e2e_vm_tests/test_programs/should_fail/trait_method_signature_mismatch/Forc.toml
```diff
@@ -3,4 +3,6 @@ authors = ["Fuel Labs <contact@fuel.sh>"]
 license = "Apache-2.0"
 name = "trait_method_signature_mismatch"
 entry = "main.sw"
-implicit-std = false
+
+[dependencies]
+std = { path = "../../../../../../sway-lib-std" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/trait_method_signature_mismatch/src/main.sw
```diff
@@ -3,6 +3,21 @@
 
 library test;
 
+struct MyStruct<T> {
+    val: T
+}
+
+trait MyTrait<T> {
+    fn set(self, val: T);
+}
+
+impl<T> MyTrait<T> for MyStruct<T> {
+    // This implementation uses an Option, but the definition does not
+    fn set(self, val: Option<T>) {
+
+    }
+}
+
 trait Foo {
     fn foo(x: u64) -> str[7];
     fn bar(variable: u64) -> bool;
```

### test/src/e2e_vm_tests/test_programs/should_fail/trait_method_signature_mismatch/test.toml
```diff
@@ -1,16 +1,24 @@
 category = "fail"
 
+# check: $()fn set(self, val: Option<T>) {
+# check: $()expected: T
+# check: $()found:    Option<T>
+# check: $()help:     The definition of this function must match the one in the trait "MyTrait" declaration.
+
 # check: fn foo(s: str[7]) -> str[7] {
-# check: $()Expected: u64
-# check: $()found:    str[7]. The definition of this function must match the one in the trait "Foo" declaration.
+# nextln: $()expected: u64
+# nextln: $()found:    str[7]
+# nextln: $()The definition of this function must match the one in the trait "Foo" declaration.
 
 # check: fn bar(ref mut variable: u64) -> bool {
 # check: $()Parameter mutability mismatch between the trait function declaration and its implementation.
 
 # check: fn baz() -> u64 {
-# check: $()Expected: u32
-# check: $()found:    u64. The definition of this function must match the one in the trait "Foo" declaration.
+# nextln: $()expected: u32
+# nextln: $()found:    u64
+# nextln: $()The definition of this function must match the one in the trait "Foo" declaration.
 
 # check: fn quux() {
-# check: $()Expected: u64
-# check: $()found:    (). The definition of this function must match the one in the trait "Foo" declaration.
+# nextln: $()expected: u64
+# nextln: $()found:    ()
+# nextln: $()The definition of this function must match the one in the trait "Foo" declaration.
```
