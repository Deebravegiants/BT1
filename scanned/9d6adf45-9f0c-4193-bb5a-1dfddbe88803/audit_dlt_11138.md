# [?] Fixes crash on encode_buffer_append with wrong args. (#6365)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-08-07
Source: https://github.com/FuelLabs/sway/commit/cd0213a47b2721a98cd7b106a5b7c61a65eb0a7b
Type: security-commit

## Details
Fixes crash on encode_buffer_append with wrong args. (#6365)

## Description
When encode_buffer_append was called with a wrong number of args an
array OOB panic was thrown.

With this fix we throw a CompileError::IntrinsicIncorrectNumArgs in case
the intrinsic encode_buffer_append is called with more or less than the
expected 2 arguments.

Fixes #6337

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

Co-authored-by: João Matos <joao@tritao.eu>

## Patch
### sway-core/src/semantic_analysis/ast_node/expression/intrinsic_function.rs
```diff
@@ -492,6 +492,14 @@ fn type_check_encode_append(
     _type_arguments: &[TypeArgument],
     span: Span,
 ) -> Result<(ty::TyIntrinsicFunctionKind, TypeId), ErrorEmitted> {
+    if arguments.len() != 2 {
+        return Err(handler.emit_err(CompileError::IntrinsicIncorrectNumArgs {
+            name: kind.to_string(),
+            expected: 2,
+            span,
+        }));
+    }
+
     let type_engine = ctx.engines.te();
     let engines = ctx.engines();
 
```

### test/src/e2e_vm_tests/test_programs/should_fail/encode_append_wrong_args/Forc.lock
```diff
@@ -0,0 +1,3 @@
+[[package]]
+name = "encode_append_wrong_args"
+source = "member"
```

### test/src/e2e_vm_tests/test_programs/should_fail/encode_append_wrong_args/Forc.toml
```diff
@@ -0,0 +1,6 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+license = "Apache-2.0"
+name = "encode_append_wrong_args"
+implicit-std = false
```

### test/src/e2e_vm_tests/test_programs/should_fail/encode_append_wrong_args/json_abi_oracle.json
```diff
@@ -0,0 +1 @@
+[]
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_fail/encode_append_wrong_args/src/main.sw
```diff
@@ -0,0 +1,17 @@
+library;
+
+pub struct Buffer {
+    buffer: u64
+}
+
+pub trait T {
+    fn ar(buffer: Buffer) -> Buffer;
+}
+
+impl T for str[10] {
+    fn ar(buffer: Buffer) -> Buffer {
+        Buffer {
+            buffer: __encode_buffer_append(buffer.buffer)
+        }
+    }
+}
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_fail/encode_append_wrong_args/test.toml
```diff
@@ -0,0 +1,7 @@
+category = "fail"
+
+# check: $()warning
+# check: $()buffer: __encode_buffer_append(buffer.buffer)
+
+# check: $()buffer: __encode_buffer_append(buffer.buffer)
+# nextln: $()Call to "encode_buffer_append" expects 2 arguments
```
