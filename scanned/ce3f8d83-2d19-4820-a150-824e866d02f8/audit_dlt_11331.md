# [?] fix: Fix panic in comptime code (#6361)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-10-25
Source: https://github.com/noir-lang/noir/commit/2f376100d3ee7ab519d6ea30153395bb3e7af7b1
Type: security-commit

## Details
fix: Fix panic in comptime code (#6361)

## Patch
### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -554,8 +554,8 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
         match &definition.kind {
             DefinitionKind::Function(function_id) => {
                 let typ = self.elaborator.interner.id_type(id).follow_bindings();
-                let bindings =
-                    Rc::new(self.elaborator.interner.get_instantiation_bindings(id).clone());
+                let bindings = self.elaborator.interner.try_get_instantiation_bindings(id);
+                let bindings = Rc::new(bindings.map_or(TypeBindings::default(), Clone::clone));
                 Ok(Value::Function(*function_id, typ, bindings))
             }
             DefinitionKind::Local(_) => self.lookup(&ident),
```
