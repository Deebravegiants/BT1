# [?] Fixes array oob on reassignment. (#6819)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-01-09
Source: https://github.com/FuelLabs/sway/commit/faf399e094c60898d379660f151ae14a8929e983
Type: security-commit

## Details
Fixes array oob on reassignment. (#6819)

## Description

When using literal on array reasignement we were not checking the array
length. We now throw an array oob error in this case.

Fixes #6393

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
### sway-core/src/semantic_analysis/ast_node/expression/typed_expression.rs
```diff
@@ -2536,12 +2536,27 @@ impl ty::TyExpression {
                     full_span_for_error = Span::join(full_span_for_error, index_span);
                 }
                 (
-                    TypeInfo::Array(elem_ty, _),
-                    ty::ProjectionKind::ArrayIndex { index_span, .. },
+                    TypeInfo::Array(elem_ty, array_length),
+                    ty::ProjectionKind::ArrayIndex { index, index_span },
                 ) => {
                     parent_rover = symbol;
                     symbol = elem_ty.type_id;
                     symbol_span = index_span.clone();
+
+                    if let Some(index_literal) = index
+                        .expression
+                        .as_literal()
+                        .and_then(|x| x.cast_value_to_u64())
+                    {
+                        if index_literal >= array_length.val() as u64 {
+                            return Err(handler.emit_err(CompileError::ArrayOutOfBounds {
+                                index: index_literal,
+                                count: array_length.val() as u64,
+                                span: index.span.clone(),
+                            }));
+                        }
+                    }
+
                     // `index_span` does not contain the enclosing square brackets.
                     // Which means, if this array index access is the last one before the
                     // erroneous expression, the `full_span_for_error` will be missing the
```

### test/src/e2e_vm_tests/test_programs/should_fail/array_oob_reassignment/Forc.lock
```diff
@@ -0,0 +1,8 @@
+[[package]]
+name = "array_oob_reassignment"
+source = "member"
+dependencies = ["core"]
+
+[[package]]
+name = "core"
+source = "path+from-root-CC73096846C1E083"
```

### test/src/e2e_vm_tests/test_programs/should_fail/array_oob_reassignment/Forc.toml
```diff
@@ -0,0 +1,9 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+license = "Apache-2.0"
+name = "array_oob_reassignment"
+entry = "main.sw"
+implicit-std = false
+
+[dependencies]
+core = { path = "../../../../../../sway-lib-core" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/array_oob_reassignment/src/main.sw
```diff
@@ -0,0 +1,16 @@
+script;
+
+fn main() {
+    let mut a = [u64; 0];
+    a[0] = 1;
+
+
+    let mut b = [[u64; 1]; 1];
+    b[0][1] = 1;
+
+
+    b[1][0] = 1;
+
+
+    a[0] = return;
+}
```

### test/src/e2e_vm_tests/test_programs/should_fail/array_oob_reassignment/test.toml
```diff
@@ -0,0 +1,19 @@
+category = "fail"
+
+# check: $()let mut a = [u64; 0];
+# nextln: $()This declaration is never used.
+
+# check: $()let mut b = [[u64; 1]; 1];
+# nextln: $()This declaration is never used.
+
+# check: $()a[0] = 1;
+# nextln: $()Index out of bounds; the length is 0 but the index is 0.
+
+# check: $()b[0][1] = 1;
+# nextln: $()Index out of bounds; the length is 1 but the index is 1.
+
+# check: $()b[1][0] = 1;
+# nextln: $()Index out of bounds; the length is 1 but the index is 1.
+
+# check: $()a[0] = return;
+# nextln: $()Index out of bounds; the length is 0 but the index is 0.
\ No newline at end of file
```
