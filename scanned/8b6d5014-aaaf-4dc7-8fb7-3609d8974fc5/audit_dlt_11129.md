# [?] Fix compiler panic on configurable initialization (#7068)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-04-07
Source: https://github.com/FuelLabs/sway/commit/2501c7600898c30ccf0ae493e76b8d5850eebdc6
Type: security-commit

## Details
Fix compiler panic on configurable initialization (#7068)

## Description

This PR fixes the compiler panic in the case of a configurable
initializer that couldn't be const evaluated, like e.g:
```sway
fn non_const_evaluable() -> u64 {
    asm() { fp: u64 }
}

configurable {
    CONFIG: u64 = non_const_evaluable(),
}
```

Instead of a panic:
```
thread 'main' panicked at sway-core/src/ir_generation/compile.rs:320:14:
called `Result::unwrap()` on an `Err` value: NonConstantDeclValue { span: Span { src (ptr): 0x564e0b311600, source_id: Some(SourceId(6291595)), start: 1009, end: 1019, as_str(): "CONFIG" } }
```
the compiler now emits an error:
```
CONFIG: u64 = non_const_evaluable(),
^^^^^^ Could not evaluate initializer to a const declaration.
```

## Checklist

- [ ] I have linked to any relevant issues.
- [ ] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [ ] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### sway-core/src/ir_generation/compile.rs
```diff
@@ -356,8 +356,7 @@ pub(crate) fn compile_configurables(
                 Some(module_ns),
                 None,
                 decl.value.as_ref().unwrap(),
-            )
-            .unwrap();
+            )?;
 
             let opt_metadata = md_mgr.span_to_md(context, &decl.span);
 
```

### test/src/e2e_vm_tests/test_programs/should_fail/configurables_initializer_not_const_eval/Forc.lock
```diff
@@ -0,0 +1,8 @@
+[[package]]
+name = "configurables_initializer_not_const_eval"
+source = "member"
+dependencies = ["std"]
+
+[[package]]
+name = "std"
+source = "path+from-root-4346025B37ED178A"
```

### test/src/e2e_vm_tests/test_programs/should_fail/configurables_initializer_not_const_eval/Forc.toml
```diff
@@ -0,0 +1,10 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+implicit-std = false
+license = "Apache-2.0"
+name = "configurables_initializer_not_const_eval"
+
+[dependencies]
+std = { path = "../../../reduced_std_libs/sway-lib-std-core" }
+
```

### test/src/e2e_vm_tests/test_programs/should_fail/configurables_initializer_not_const_eval/src/main.sw
```diff
@@ -0,0 +1,11 @@
+script;
+
+fn not_const_eval() -> u64 {
+    asm() { fp: u64 }
+}
+
+configurable {
+    CONFIG: u64 = not_const_eval(),
+}
+
+fn main() {}
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_fail/configurables_initializer_not_const_eval/test.toml
```diff
@@ -0,0 +1,5 @@
+category = "fail"
+
+#check: $()error
+#check: $()CONFIG: u64 = not_const_eval(),
+#nextln: $()Could not evaluate initializer to a const declaration.
```

### test/src/e2e_vm_tests/test_programs/should_fail/configurables_undefined_var/src/main.sw
```diff
@@ -4,6 +4,4 @@ configurable {
     VALUE: u64 = DOES_NOT_EXIST,
 }
 
-fn main() {
-    const CONSTANT: u64 = VALUE;
-}
+fn main() { }
```
