# [?] Fixes OOB in type_check_analyze of ImplTrait. (#6551)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-09-17
Source: https://github.com/FuelLabs/sway/commit/a073a95f6b69297e132064a285a6127134daa45f
Type: security-commit

## Details
Fixes OOB in type_check_analyze of ImplTrait. (#6551)

## Description

An unused line of code threw an OOB panic because of a parser error.
Removing the unused line of code fixes the issue.

Fixes #6331

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

Co-authored-by: Joshua Batty <joshpbatty@gmail.com>

## Patch
### sway-core/src/semantic_analysis/ast_node/declaration/impl_trait.rs
```diff
@@ -1629,8 +1629,7 @@ impl TypeCheckAnalysis for ty::ImplSelfOrTrait {
         ctx.push_nodes_for_impl_trait(self);
 
         // Now lets analyze each impl trait item.
-        for (i, item) in impl_trait.items.iter().enumerate() {
-            let _node = ctx.items_node_stack[i];
+        for item in impl_trait.items.iter() {
             item.type_check_analyze(handler, ctx)?;
         }
 
```

### test/src/e2e_vm_tests/test_programs/should_fail/mismatch_closing_delimiters/Forc.lock
```diff
@@ -0,0 +1,8 @@
+[[package]]
+name = "core"
+source = "path+from-root-F62FA9D54ABC8F01"
+
+[[package]]
+name = "mismatch_closing_delimiters"
+source = "member"
+dependencies = ["core"]
```

### test/src/e2e_vm_tests/test_programs/should_fail/mismatch_closing_delimiters/Forc.toml
```diff
@@ -0,0 +1,9 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+license = "Apache-2.0"
+name = "mismatch_closing_delimiters"
+entry = "main.sw"
+implicit-std = false
+
+[dependencies]
+core = { path = "../../../../../../sway-lib-core" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/mismatch_closing_delimiters/src/main.sw
```diff
@@ -0,0 +1,14 @@
+script;
+
+struct Struct{x:u}
+impl Struct{
+    fn w()->f{{(()}}
+    trait Supertrait{}
+    impl Supertrait for Struct{)
+}
+
+fn s<A>(b:B) where A:t{}fn n(){}
+
+fn main() -> u64 {
+    0
+}
```

### test/src/e2e_vm_tests/test_programs/should_fail/mismatch_closing_delimiters/test.toml
```diff
@@ -0,0 +1,4 @@
+category = "fail"
+
+# check: $()fn w()->f{{(()}}
+# nextln: $()mismatched delimiters
```
