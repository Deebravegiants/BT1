# [?] Fixes panic on unwrapping in type_check_trait_implementation. (#6434)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-08-23
Source: https://github.com/FuelLabs/sway/commit/4f08020bb7512231d2b302ce6aa80bf8da3207f7
Type: security-commit

## Details
Fixes panic on unwrapping in type_check_trait_implementation. (#6434)

## Description

This PR fixes panic on unwrapping by only performing the required
behavior with the unwrapped value when it is available.

Fixes #6336

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

Co-authored-by: Sophie Dankel <47993817+sdankel@users.noreply.github.com>
Co-authored-by: Joshua Batty <joshpbatty@gmail.com>

## Patch
### sway-core/src/semantic_analysis/ast_node/declaration/impl_trait.rs
```diff
@@ -831,22 +831,28 @@ fn type_check_trait_implementation(
                         None,
                     ),
                 };
-                trait_type_mapping.extend(&TypeSubstMap::from_type_parameters_and_type_arguments(
-                    vec![type_engine.insert(
-                        engines,
-                        old_type_decl_info1,
-                        type_decl.name.span().source_id(),
-                    )],
-                    vec![type_decl.ty.clone().unwrap().type_id],
-                ));
-                trait_type_mapping.extend(&TypeSubstMap::from_type_parameters_and_type_arguments(
-                    vec![type_engine.insert(
-                        engines,
-                        old_type_decl_info2,
-                        type_decl.name.span().source_id(),
-                    )],
-                    vec![type_decl.ty.clone().unwrap().type_id],
-                ));
+                if let Some(type_arg) = type_decl.ty.clone() {
+                    trait_type_mapping.extend(
+                        &TypeSubstMap::from_type_parameters_and_type_arguments(
+                            vec![type_engine.insert(
+                                engines,
+                                old_type_decl_info1,
+                                type_decl.name.span().source_id(),
+                            )],
+                            vec![type_arg.type_id],
+                        ),
+                    );
+                    trait_type_mapping.extend(
+                        &TypeSubstMap::from_type_parameters_and_type_arguments(
+                            vec![type_engine.insert(
+                                engines,
+                                old_type_decl_info2,
+                                type_decl.name.span().source_id(),
+                            )],
+                            vec![type_arg.type_id],
+                        ),
+                    );
+                }
             }
         }
     }
```

### test/src/e2e_vm_tests/test_programs/should_fail/associated_type_not_in_trait/Forc.lock
```diff
@@ -0,0 +1,3 @@
+[[package]]
+name = "associated_type_not_in_trait"
+source = "member"
```

### test/src/e2e_vm_tests/test_programs/should_fail/associated_type_not_in_trait/Forc.toml
```diff
@@ -0,0 +1,6 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+license = "Apache-2.0"
+name = "associated_type_not_in_trait"
+implicit-std = false
```

### test/src/e2e_vm_tests/test_programs/should_fail/associated_type_not_in_trait/src/main.sw
```diff
@@ -0,0 +1,4 @@
+script;
+trait Trait{}
+struct Struct0{}
+impl Trait for Struct0{type u;const u=0;}
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_fail/associated_type_not_in_trait/test.toml
```diff
@@ -0,0 +1,3 @@
+category = "fail"
+
+# check: $()Type "u" is not a part of trait "Trait"'s interface surface.
```
