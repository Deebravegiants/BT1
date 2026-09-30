# [?] fix: Fix panic during monomorphization when calling a non-function enum variant as a function (#11165)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-12
Source: https://github.com/noir-lang/noir/commit/f06ded9c9de4047effbb60899bc20b6ee61f1332
Type: security-commit

## Details
fix: Fix panic during monomorphization when calling a non-function enum variant as a function (#11165)

## Patch
### compiler/noirc_frontend/src/monomorphization/tests.rs
```diff
@@ -24,7 +24,7 @@ fn bounded_recursive_type_errors() {
         }
         ";
     let features = vec![UnstableFeature::Enums];
-    check_monomorphization_error_using_features(src, &features);
+    check_monomorphization_error_using_features(src, &features, false);
 }
 
 #[test]
@@ -59,7 +59,7 @@ fn recursive_type_with_alias_errors() {
         }
         ";
     let features = vec![UnstableFeature::Enums];
-    check_monomorphization_error_using_features(src, &features);
+    check_monomorphization_error_using_features(src, &features, false);
 }
 
 #[test]
@@ -84,7 +84,7 @@ fn mutually_recursive_types_error() {
         ";
     // cSpell:enable
     let features = vec![UnstableFeature::Enums];
-    check_monomorphization_error_using_features(src, &features);
+    check_monomorphization_error_using_features(src, &features, false);
 }
 
 #[test]
@@ -114,7 +114,7 @@ fn mutually_recursive_types_with_structs_error() {
 
     // cSpell:enable
     let features = vec![UnstableFeature::Enums];
-    check_monomorphization_error_using_features(src, &features);
+    check_monomorphization_error_using_features(src, &features, false);
 }
 
 #[test]
@@ -456,3 +456,29 @@ fn multiple_trait_impls_with_different_instantiations() {
     }
     ");
 }
+
+#[test]
+fn fail_to_call_enum_member_without_panic() {
+    // The 'Unexpected Type::Error found during monomorphization' error doesn't occur
+    // when running this code as a real source file because in actual Noir code we don't
+    // run the monomorphizer if there were previous errors. Here we do want to do that to
+    // ensure this panic does not re-emerge.
+    let src = "
+        enum Foo {
+            A
+        }
+
+        fn main() {
+            let foo: Foo = Foo::A;
+            foo(foo);
+            ^^^^^^^^ Expected a function, but found a(n) Foo
+            ^^^^^^^^ Unexpected Type::Error found during monomorphization
+        }
+
+        fn foo(f: Foo) {
+            let _ = f;
+        }
+    ";
+    let features = vec![UnstableFeature::Enums];
+    check_monomorphization_error_using_features(src, &features, true);
+}
```

### compiler/noirc_frontend/src/node_interner/function.rs
```diff
@@ -130,10 +130,12 @@ impl NodeInterner {
                 }
                 Some(DefinitionKind::Global(global_id)) => {
                     let info = self.get_global(*global_id);
-                    let HirStatement::Let(HirLetStatement { expression, .. }) =
-                        self.statement(&info.let_statement)
-                    else {
-                        unreachable!("global refers to a let statement");
+                    let expression = match self.statement(&info.let_statement) {
+                        HirStatement::Let(HirLetStatement { expression, .. })
+                        | HirStatement::Expression(expression) => expression,
+                        other => unreachable!(
+                            "Expected global to be a let statement or expression but found: {other:?}"
+                        ),
                     };
                     self.lookup_function_from_expr(&expression)
                 }
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -100,33 +100,47 @@ fn assert_no_errors_and_to_string(src: &str) -> String {
 /// will produce errors at those locations and with/ those messages.
 fn check_errors(src: &str) {
     let allow_parser_errors = false;
+    let allow_elaborator_errors = true;
     let monomorphize = false;
     check_errors_with_options(
         src,
         allow_parser_errors,
+        allow_elaborator_errors,
         monomorphize,
         FrontendOptions::test_default(),
     );
 }
 
 fn check_errors_using_features(src: &str, features: &[UnstableFeature]) {
     let allow_parser_errors = false;
+    let allow_elaborator_errors = true;
     let monomorphize = false;
     let options =
         FrontendOptions { enabled_unstable_features: features, ..FrontendOptions::test_default() };
-    check_errors_with_options(src, allow_parser_errors, monomorphize, options);
+    check_errors_with_options(
+        src,
+        allow_parser_errors,
+        allow_elaborator_errors,
+        monomorphize,
+        options,
+    );
 }
 
 pub(super) fn check_monomorphization_error(src: &str) {
-    check_monomorphization_error_using_features(src, &[]);
+    check_monomorphization_error_using_features(src, &[], false);
 }
 
-pub(super) fn check_monomorphization_error_using_features(src: &str, features: &[UnstableFeature]) {
+pub(super) fn check_monomorphization_error_using_features(
+    src: &str,
+    features: &[UnstableFeature],
+    allow_elaborator_errors: bool,
+) {
     let allow_parser_errors = false;
     let monomorphize = true;
     check_errors_with_options(
         src,
         allow_parser_errors,
+        allow_elaborator_errors,
         monomorphize,
         FrontendOptions { enabled_unstable_features: features, ..FrontendOptions::test_default() },
     );
@@ -135,6 +149,7 @@ pub(super) fn check_monomorphization_error_using_features(src: &str, features: &
 fn check_errors_with_options(
     src: &str,
     allow_parser_errors: bool,
+    allow_elaborator_errors: bool,
     monomorphize: bool,
     options: FrontendOptions,
 ) {
@@ -198,12 +213,12 @@ fn check_errors_with_options(
     let (_, mut context, errors) = get_program_with_options(&src, allow_parser_errors, options);
     let mut errors = errors.iter().map(CustomDiagnostic::from).collect::<Vec<_>>();
 
-    if monomorphize {
-        if !errors.is_empty() {
-            report_all(context.file_manager.as_file_map(), &errors, false, false);
-            panic!("Expected no errors before monomorphization");
-        }
+    if !allow_elaborator_errors && !errors.is_empty() {
+        report_all(context.file_manager.as_file_map(), &errors, false, false);
+        panic!("Expected no elaborator errors");
+    }
 
+    if monomorphize {
         let main = context.get_main_function(context.root_crate_id()).unwrap_or_else(|| {
             panic!("get_monomorphized: test program contains no 'main' function")
         });
```
