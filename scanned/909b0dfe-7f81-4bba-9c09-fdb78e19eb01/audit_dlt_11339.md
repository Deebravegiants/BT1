# [?] fix: Don't panic when a macro fails to resolve (#5537)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-18
Source: https://github.com/noir-lang/noir/commit/6109ddc4a12a4f7593c87fcc42a059737febd470
Type: security-commit

## Details
fix: Don't panic when a macro fails to resolve (#5537)

# Description

## Problem\*

Resolves https://github.com/noir-lang/noir/issues/5539

## Summary\*

Use `try_definition` instead of `definition` in case there is an error
when resolving a macro.

## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/elaborator/expressions.rs
```diff
@@ -750,19 +750,23 @@ impl<'context> Elaborator<'context> {
         &mut self,
         func: ExprId,
         location: Location,
-    ) -> Result<FuncId, ResolverError> {
+    ) -> Result<Option<FuncId>, ResolverError> {
         match self.interner.expression(&func) {
             HirExpression::Ident(ident, _generics) => {
-                let definition = self.interner.definition(ident.id);
-                if let DefinitionKind::Function(function) = definition.kind {
-                    let meta = self.interner.function_modifiers(&function);
-                    if meta.is_comptime {
-                        Ok(function)
+                if let Some(definition) = self.interner.try_definition(ident.id) {
+                    if let DefinitionKind::Function(function) = definition.kind {
+                        let meta = self.interner.function_modifiers(&function);
+                        if meta.is_comptime {
+                            Ok(Some(function))
+                        } else {
+                            Err(ResolverError::MacroIsNotComptime { span: location.span })
+                        }
                     } else {
-                        Err(ResolverError::MacroIsNotComptime { span: location.span })
+                        Err(ResolverError::InvalidSyntaxInMacroCall { span: location.span })
                     }
                 } else {
-                    Err(ResolverError::InvalidSyntaxInMacroCall { span: location.span })
+                    // Assume a name resolution error has already been issued
+                    Ok(None)
                 }
             }
             _ => Err(ResolverError::InvalidSyntaxInMacroCall { span: location.span }),
@@ -783,7 +787,7 @@ impl<'context> Elaborator<'context> {
         });
 
         let function = match self.try_get_comptime_function(func, location) {
-            Ok(function) => function,
+            Ok(function) => function?,
             Err(error) => {
                 self.push_err(error);
                 return None;
```
