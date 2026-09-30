# [?] fix(semantic): recover from a salsa cycle in enum_definition_data instead of panicking (#10268)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-07-28
Source: https://github.com/starkware-libs/cairo/commit/c1af765badecd9ec181bcdb0ba8b937b982af387
Type: security-commit

## Details
fix(semantic): recover from a salsa cycle in enum_definition_data instead of panicking (#10268)

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>

## Patch
### crates/cairo-lang-semantic/src/items/enm.rs
```diff
@@ -145,7 +145,7 @@ pub enum MatchArmSelector<'db> {
 }
 
 /// Returns the definition data of an enum.
-#[salsa::tracked(returns(ref))]
+#[salsa::tracked(returns(ref), cycle_fn=enum_definition_data_cycle, cycle_initial=enum_definition_data_initial)]
 fn enum_definition_data<'db>(
     db: &'db dyn Database,
     enum_id: EnumId<'db>,
@@ -215,6 +215,26 @@ fn enum_definition_data<'db>(
     })
 }
 
+/// Cycle handling for [enum_definition_data].
+fn enum_definition_data_cycle<'db>(
+    _db: &'db dyn Database,
+    _cycle: &salsa::Cycle<'_>,
+    _last_provisional_value: &Maybe<EnumDefinitionData<'db>>,
+    value: Maybe<EnumDefinitionData<'db>>,
+    _enum_id: EnumId<'db>,
+) -> Maybe<EnumDefinitionData<'db>> {
+    value
+}
+
+/// Cycle handling for [enum_definition_data].
+fn enum_definition_data_initial<'db>(
+    _db: &'db dyn Database,
+    _id: salsa::Id,
+    _enum_id: EnumId<'db>,
+) -> Maybe<EnumDefinitionData<'db>> {
+    Err(skip_diagnostic())
+}
+
 /// Query implementation of [EnumSemantic::enum_definition_diagnostics].
 #[salsa::tracked(returns(clone))]
 fn enum_definition_diagnostics<'db>(
```

### crates/cairo-lang-semantic/src/items/tests/enum
```diff
@@ -193,3 +193,39 @@ warning[E0001]: Unused variable. Consider ignoring by prefixing with `_`.
  --> lib.cairo:9:9
     let E = A::E(());
         ^
+
+//! > ==========================================================================
+
+//! > Test no ICE when a malformed module-level macro call re-enters the enum definition. The unresolved variant type's error must survive the cycle recovery.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {}
+
+//! > function_name
+foo
+
+//! > module_code
+enum MyEnum {
+    A: P,
+}
+MyEnum::A(());
+
+//! > expected_diagnostics
+error[E1012]: Expected a '!' after the identifier 'A' to start an inline macro.
+Did you mean to write `A!(...)'?
+ --> lib.cairo:4:9
+MyEnum::A(());
+        ^
+
+error[E0006]: Type not found.
+ --> lib.cairo:2:8
+    A: P,
+       ^
+
+error[E2156]: Inline macro `MyEnum::A` not found.
+ --> lib.cairo:4:1
+MyEnum::A(());
+^^^^^^^^^^^^^^
```
