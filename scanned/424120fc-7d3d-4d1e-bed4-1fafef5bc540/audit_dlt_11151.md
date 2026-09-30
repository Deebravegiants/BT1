# [?] Add the occurs check to prevent stack overflows with infinite type unification (#3686)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-01-05
Source: https://github.com/FuelLabs/sway/commit/ccdd0fe04849db85baddb6bbec81d6ffefe01cf5
Type: security-commit

## Details
Add the occurs check to prevent stack overflows with infinite type unification (#3686)

This PR adds an "occurs check" to prevent recursive type unification
causing stack overflow. The occurs check, in it's most simple form,
checks to see if generic variable _V_ exists in type _S_ to prevent a
case in which unifying _V_ and _S_ would create recursive
unification---i.e. we shouldn't unify generic type _V_ with
non-generic-type _S_ if _S_ contains _V_ anywhere in it's type
definition because that unification would recurse infinitely.

Here's a little bit more about the occurs check:
https://en.wikipedia.org/wiki/Occurs_check
And here is a bit about how it relates to type unification:
https://papl.cs.brown.edu/2016/Type_Inference.html

Closes #3317

Co-authored-by: emilyaherbert <emily.herbert@fuel.sh>

## Patch
### sway-core/src/semantic_analysis/ast_node/expression/typed_expression.rs
```diff
@@ -489,7 +489,13 @@ impl ty::TyExpression {
             errors
         );
 
-        instantiate_function_application(ctx, function_decl, call_path_binding.inner, arguments)
+        instantiate_function_application(
+            ctx,
+            function_decl,
+            call_path_binding.inner,
+            arguments,
+            span,
+        )
     }
 
     fn type_check_lazy_operator(
@@ -1144,7 +1150,7 @@ impl ty::TyExpression {
                 warnings.append(&mut enum_probe_warnings);
                 errors.append(&mut enum_probe_errors);
                 check!(
-                    instantiate_enum(ctx, enum_decl, enum_name, variant_name, args),
+                    instantiate_enum(ctx, enum_decl, enum_name, variant_name, args, &span),
                     return err(warnings, errors),
                     warnings,
                     errors
@@ -1154,7 +1160,13 @@ impl ty::TyExpression {
                 warnings.append(&mut function_probe_warnings);
                 errors.append(&mut function_probe_errors);
                 check!(
-                    instantiate_function_application(ctx, func_decl, call_path_binding.inner, args,),
+                    instantiate_function_application(
+                        ctx,
+                        func_decl,
+                        call_path_binding.inner,
+                        args,
+                        span
+                    ),
                     return err(warnings, errors),
                     warnings,
                     errors
```

### sway-core/src/semantic_analysis/ast_node/expression/typed_expression/enum_instantiation.rs
```diff
@@ -6,7 +6,7 @@ use crate::{
 };
 
 use sway_error::error::CompileError;
-use sway_types::{Ident, Spanned};
+use sway_types::{Ident, Span, Spanned};
 
 /// Given an enum declaration and the instantiation expression/type arguments, construct a valid
 /// [ty::TyExpression].
@@ -17,6 +17,7 @@ pub(crate) fn instantiate_enum(
     enum_name: Ident,
     enum_variant_name: Ident,
     args: Vec<Expression>,
+    span: &Span,
 ) -> CompileResult<ty::TyExpression> {
     let mut warnings = vec![];
     let mut errors = vec![];
@@ -73,7 +74,7 @@ pub(crate) fn instantiate_enum(
                     declaration_engine,
                     typed_expr.return_type,
                     enum_variant.type_id,
-                    &typed_expr.span,
+                    span,
                     "Enum instantiator must match its declared variant type.",
                     None
                 )),
```

### sway-core/src/semantic_analysis/ast_node/expression/typed_expression/function_application.rs
```diff
@@ -14,6 +14,7 @@ pub(crate) fn instantiate_function_application(
     mut function_decl: ty::TyFunctionDeclaration,
     call_path: CallPath,
     arguments: Vec<Expression>,
+    span: Span,
 ) -> CompileResult<ty::TyExpression> {
     let mut warnings = vec![];
     let mut errors = vec![];
@@ -66,7 +67,6 @@ pub(crate) fn instantiate_function_application(
     );
     function_decl.replace_decls(&decl_mapping, engines);
     let return_type = function_decl.return_type;
-    let span = function_decl.span.clone();
     let new_decl_id = declaration_engine.insert_function(function_decl);
 
     let exp = ty::TyExpression {
```

### sway-core/src/type_system/mod.rs
```diff
@@ -2,6 +2,7 @@ mod collect_types_metadata;
 mod copy_types;
 mod create_type_id;
 mod length;
+mod occurs_check;
 mod replace_self_type;
 mod resolved_type;
 mod trait_constraint;
@@ -20,6 +21,7 @@ pub(crate) use collect_types_metadata::*;
 pub(crate) use copy_types::*;
 pub(crate) use create_type_id::*;
 pub use length::*;
+use occurs_check::*;
 pub(crate) use replace_self_type::*;
 pub(crate) use resolved_type::*;
 pub(crate) use trait_constraint::*;
```

### sway-core/src/type_system/occurs_check.rs
```diff
@@ -0,0 +1,53 @@
+use crate::{engine_threading::*, type_system::*};
+
+use sway_types::Span;
+
+/// Helper struct to perform the occurs check.
+///
+/// ---
+///
+/// "causes unification of a variable V and a structure S to fail if S
+/// contains V"
+/// https://en.wikipedia.org/wiki/Occurs_check
+///
+/// "occurs check: a check for whether the same variable occurs on both
+/// sides and, if it does, decline to unify"
+/// https://papl.cs.brown.edu/2016/Type_Inference.html
+pub(super) struct OccursCheck<'a> {
+    engines: Engines<'a>,
+}
+
+impl<'a> OccursCheck<'a> {
+    /// Creates a new [OccursCheck].
+    pub(super) fn new(engines: Engines<'a>) -> OccursCheck<'a> {
+        OccursCheck { engines }
+    }
+
+    /// Checks whether `generic` occurs in `other` and returns true if so.
+    ///
+    /// NOTE: This first-cut implementation takes the most simple approach---
+    /// does `other` contain `generic`? If so, return true.
+    /// TODO: In the future, we may need to expand this definition.
+    ///
+    /// NOTE: This implementation assumes that `other` =/ `generic`, in which
+    /// case the occurs check would return `false`, as this is a valid
+    /// unification.
+    pub(super) fn check(
+        &self,
+        generic: TypeInfo,
+        other: &TypeInfo,
+        span: &Span,
+    ) -> CompileResult<bool> {
+        let mut warnings = vec![];
+        let mut errors = vec![];
+
+        let other_generics = check!(
+            other.extract_nested_generics(self.engines, span),
+            return err(warnings, errors),
+            warnings,
+            errors
+        );
+        let occurs = other_generics.contains(&self.engines.help_out(generic));
+        ok(occurs, warnings, errors)
+    }
+}
```

### sway-core/src/type_system/unify.rs
```diff
@@ -6,7 +6,7 @@ use sway_error::{
 };
 use sway_types::{integer_bits::IntegerBits, Ident, Span, Spanned};
 
-use crate::{engine_threading::*, language::ty, type_system::*, Engines};
+use crate::{engine_threading::*, language::ty, type_system::*};
 
 /// Helper struct to aid in type unification.
 pub(super) struct Unifier<'a> {
@@ -230,11 +230,11 @@ impl<'a> Unifier<'a> {
                 self.engines.te().insert_unified_type(expected, received);
                 (vec![], vec![])
             }
-            (r @ UnknownGeneric { .. }, e) => {
+            (r @ UnknownGeneric { .. }, e) if !self.occurs_check(r.clone(), &e, span) => {
                 self.engines.te().insert_unified_type(expected, received);
                 self.replace_received_with_expected(received, expected, &r, e, span)
             }
-            (r, e @ UnknownGeneric { .. }) => {
+            (r, e @ UnknownGeneric { .. }) if !self.occurs_check(e.clone(), &r, span) => {
                 self.engines.te().insert_unified_type(received, expected);
                 self.replace_expected_with_received(received, expected, r, &e, span)
             }
@@ -255,6 +255,13 @@ impl<'a> Unifier<'a> {
         }
     }
 
+    fn occurs_check(&self, generic: TypeInfo, other: &TypeInfo, span: &Span) -> bool {
+        OccursCheck::new(self.engines)
+            .check(generic, other, span)
+            .value
+            .unwrap_or(true)
+    }
+
     fn unify_strs(
         &self,
         received: TypeId,
```

### sway-core/src/type_system/unify_check.rs
```diff
@@ -6,7 +6,7 @@ pub(super) struct UnifyCheck<'a> {
 }
 
 impl<'a> UnifyCheck<'a> {
-    /// Creates a new [Coercion].
+    /// Creates a new [UnifyCheck].
     pub(super) fn new(engines: Engines<'a>) -> UnifyCheck<'a> {
         UnifyCheck { engines }
     }
```

### test/src/e2e_vm_tests/test_programs/should_fail/recursive_type_unification/Forc.lock
```diff
@@ -0,0 +1,13 @@
+[[package]]
+name = 'core'
+source = 'path+from-root-07F1C570AB447C35'
+
+[[package]]
+name = 'recursive_type_unification'
+source = 'member'
+dependencies = ['std']
+
+[[package]]
+name = 'std'
+source = 'path+from-root-07F1C570AB447C35'
+dependencies = ['core']
```

### test/src/e2e_vm_tests/test_programs/should_fail/recursive_type_unification/Forc.toml
```diff
@@ -0,0 +1,9 @@
+[project]
+name = "recursive_type_unification"
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+license = "Apache-2.0"
+#implicit-std = false
+
+[dependencies]
+std = { path = "../../../../../../sway-lib-std" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/recursive_type_unification/src/main.sw
```diff
@@ -0,0 +1,13 @@
+script;
+
+fn foo<T>(value: T) -> Option<T> {
+    Option::Some(value)
+}
+
+fn bar<V>(value: V) -> Option<V> {
+    Option::Some::<V>(foo::<V>(value))
+}
+
+fn main() {
+    let x = bar(false);
+}
```

### test/src/e2e_vm_tests/test_programs/should_fail/recursive_type_unification/test.toml
```diff
@@ -0,0 +1,9 @@
+category = "fail"
+
+# check: $()error
+# nextln: recursive_type_unification/src/main.sw:8:5
+# check: $()Option::Some::<V>(foo::<V>(value))
+# nextln: $()Mismatched types.
+# nextln: $()expected: V
+# nextln: $()found:    Option<V>.
+# nextln: $()help: Enum instantiator must match its declared variant type.
```
