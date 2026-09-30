# [?] Fixes panic error on decl_to_type_info. (#6552)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-09-17
Source: https://github.com/FuelLabs/sway/commit/520bfe916844046741cf84a60caff7c41132e228
Type: security-commit

## Details
Fixes panic error on decl_to_type_info. (#6552)

## Description

Doing an unwrap without checking if the value was none was causing a
panic. Fixed by throwing an error so we can also see the previous
errors.

Fixes #6330

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
### sway-core/src/semantic_analysis/namespace/root.rs
```diff
@@ -935,6 +935,12 @@ impl Root {
                 ty::TyDecl::EnumDecl(enum_ty_decl) => TypeInfo::Enum(enum_ty_decl.decl_id),
                 ty::TyDecl::TraitTypeDecl(type_decl) => {
                     let type_decl = engines.de().get_type(&type_decl.decl_id);
+                    if type_decl.ty.is_none() {
+                        return Err(handler.emit_err(CompileError::Internal(
+                            "Trait type declaration has no type",
+                            symbol.span(),
+                        )));
+                    }
                     (*engines.te().get(type_decl.ty.clone().unwrap().type_id)).clone()
                 }
                 _ => {
```

### test/src/e2e_vm_tests/test_programs/should_fail/parser_associated_type_error/Forc.lock
```diff
@@ -0,0 +1,13 @@
+[[package]]
+name = "core"
+source = "path+from-root-6C2FF70C66B98326"
+
+[[package]]
+name = "parser_associated_type_error"
+source = "member"
+dependencies = ["std"]
+
+[[package]]
+name = "std"
+source = "path+from-root-6C2FF70C66B98326"
+dependencies = ["core"]
```

### test/src/e2e_vm_tests/test_programs/should_fail/parser_associated_type_error/Forc.toml
```diff
@@ -0,0 +1,8 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+license = "Apache-2.0"
+name = "parser_associated_type_error"
+
+[dependencies]
+std = { path = "../../../../../../sway-lib-std" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/parser_associated_type_error/src/main.sw
```diff
@@ -0,0 +1,3 @@
+script;
+
+trait T{type E const C:Self::E::E}
```

### test/src/e2e_vm_tests/test_programs/should_fail/parser_associated_type_error/test.toml
```diff
@@ -0,0 +1,6 @@
+category = "fail"
+
+# check: $()trait T{type E const C:Self::E::E}
+# nextln: $()Expected `;`.
+
+# check: $()Trait type declaration has no type
```
