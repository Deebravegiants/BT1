# [?] fix: Fix panic in `get_global_let_statement` (#5177)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-06-05
Source: https://github.com/noir-lang/noir/commit/b769b01fd06a6a2c66c72f9aa4e1d346b0fca123
Type: security-commit

## Details
fix: Fix panic in `get_global_let_statement` (#5177)

# Description

## Problem\*

Resolves <!-- Link to GitHub Issue -->

## Summary\*



## Additional Context



## Documentation\*

Check one:
- [ ] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [ ] I have tested the changes locally.
- [ ] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/node_interner.rs
```diff
@@ -891,8 +891,9 @@ impl NodeInterner {
         match def {
             Node::Statement(hir_stmt) => match hir_stmt {
                 HirStatement::Let(let_stmt) => Some(let_stmt.clone()),
-                _ => {
-                    panic!("ice: all globals should correspond to a let statement in the interner")
+                HirStatement::Error => None,
+                other => {
+                    panic!("ice: all globals should correspond to a let statement in the interner: {other:?}")
                 }
             },
             _ => panic!("ice: all globals should correspond to a statement in the interner"),
```
