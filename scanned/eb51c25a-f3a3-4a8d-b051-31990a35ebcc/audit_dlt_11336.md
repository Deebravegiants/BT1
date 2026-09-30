# [?] fix: prevent check_can_mutate crashing on undefined variable (#6044)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-09-16
Source: https://github.com/noir-lang/noir/commit/b3accfc99249ccd198051ecb98cf7962af64a629
Type: security-commit

## Details
fix: prevent check_can_mutate crashing on undefined variable (#6044)

# Description

## Problem

I noticed that after #6037 got merged, doing `foo(&mut undefined)` when
`undefined` isn't declared crashes the compiler.

## Summary


## Additional Context

I wonder if instead of using a dummy ID we should use `Option` to
represent undefined variables (not for this PR, just for a later larger
refactor).

## Documentation

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/elaborator/expressions.rs
```diff
@@ -301,12 +301,13 @@ impl<'context> Elaborator<'context> {
         let expr = self.interner.expression(&expr_id);
         match expr {
             HirExpression::Ident(hir_ident, _) => {
-                let definition = self.interner.definition(hir_ident.id);
-                if !definition.mutable {
-                    self.push_err(TypeCheckError::CannotMutateImmutableVariable {
-                        name: definition.name.clone(),
-                        span,
-                    });
+                if let Some(definition) = self.interner.try_definition(hir_ident.id) {
+                    if !definition.mutable {
+                        self.push_err(TypeCheckError::CannotMutateImmutableVariable {
+                            name: definition.name.clone(),
+                            span,
+                        });
+                    }
                 }
             }
             HirExpression::MemberAccess(member_access) => {
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -3533,3 +3533,27 @@ fn cannot_mutate_immutable_variable_on_member_access() {
 
     assert_eq!(name, "foo");
 }
+
+#[test]
+fn does_not_crash_when_passing_mutable_undefined_variable() {
+    let src = r#"
+    fn main() {
+        mutate(&mut undefined);
+    }
+
+    fn mutate(foo: &mut Field) {
+        *foo = 1;
+    }
+    "#;
+
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    let CompilationError::ResolverError(ResolverError::VariableNotDeclared { name, .. }) =
+        &errors[0].0
+    else {
+        panic!("Expected a VariableNotDeclared error");
+    };
+
+    assert_eq!(name, "undefined");
+}
```
