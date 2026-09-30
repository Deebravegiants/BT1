# [?] [compiler] Fixing cyclic type replacement leading to stack overflow (#16473)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-04-27
Source: https://github.com/aptos-labs/aptos-core/commit/5a9898905a88e7b30300076a11af0556730fae50
Type: security-commit

## Details
[compiler] Fixing cyclic type replacement leading to stack overflow (#16473)

* [compiler] Fixing a bug in inferred type defaults

Inferred type defaults where not checked for abilities. Closes #16405

* [compiler] Fixing cyclic type replacement leading to stack overflow

When creating default types from constraints during type finalization we can run into cycles, leading to stack overflow. This adds a visiting set to the replacement algorithm to bail out in this case.

Closes #16435

* Update comment.

## Patch
### third_party/move/move-compiler-v2/tests/checking-lang-v2.2/lambda/self_application.exp
```diff
@@ -0,0 +1,13 @@
+
+Diagnostics:
+error: unable to infer instantiation of type `||||..|_ has ..|_||` (consider providing type arguments or annotating the type)
+  ┌─ tests/checking-lang-v2.2/lambda/self_application.move:4:18
+  │
+4 │         let f = |func| func();
+  │                  ^^^^
+
+error: unable to infer instantiation of type `||||..|_ has ..|||` (consider providing type arguments or annotating the type)
+  ┌─ tests/checking-lang-v2.2/lambda/self_application.move:4:17
+  │
+4 │         let f = |func| func();
+  │                 ^^^^^^^^^^^^^
```

### third_party/move/move-compiler-v2/tests/checking-lang-v2.2/lambda/self_application.move
```diff
@@ -0,0 +1,7 @@
+// Fixes #16435
+module 0xc0ffee::m {
+    public fun test() {
+        let f = |func| func();
+        f(f);
+    }
+}
```

### third_party/move/move-model/src/ty.rs
```diff
@@ -108,7 +108,7 @@ pub enum PrimitiveType {
 }
 
 /// A type substitution.
-#[derive(Debug, Clone, Default)]
+#[derive(Clone, Default)]
 pub struct Substitution {
     /// Assignment of types to variables.
     subs: BTreeMap<u32, Type>,
@@ -1211,7 +1211,7 @@ impl Type {
         if params.is_empty() {
             self.clone()
         } else {
-            self.replace(Some(params), None, false)
+            self.replace(Some(params), None, false, &mut BTreeSet::new())
         }
     }
 
@@ -1248,11 +1248,12 @@ impl Type {
         params: Option<&[Type]>,
         subs: Option<&Substitution>,
         use_constr: bool,
+        visiting: &mut BTreeSet<u32>,
     ) -> Type {
-        let replace_vec = |types: &[Type]| -> Vec<Type> {
+        let replace_vec = |types: &[Type], visited: &mut BTreeSet<u32>| -> Vec<Type> {
             types
                 .iter()
-                .map(|t| t.replace(params, subs, use_constr))
+                .map(move |t| t.replace(params, subs, use_constr, visited))
                 .collect()
         };
         match self {
@@ -1268,14 +1269,34 @@ impl Type {
                     if let Some(t) = s.subs.get(i) {
                         // Recursively call replacement again here, in case the substitution s
                         // refers to type variables.
-                        // TODO: a more efficient approach is to maintain that type assignments
-                        // are always fully specialized w.r.t. to the substitution.
-                        t.replace(params, subs, use_constr)
+                        //
+                        // We need to check for cycles here because a type created by
+                        // `Constraint::default_type_for` below can introduce a cyclic
+                        // replacement. As an example, consider:
+                        //
+                        //   v1 -> v5
+                        //   v5 where SomeFunctionValue(v1, t)
+                        //
+                        // In this case, we abandon replacement which leads to free type variables
+                        // and produces an inference error.
+                        if visiting.insert(*i) {
+                            let result = t.replace(params, subs, use_constr, visiting);
+                            visiting.remove(i);
+                            result
+                        } else {
+                            t.clone()
+                        }
                     } else if use_constr {
                         if let Some(default_ty) = s.constraints.get(i).and_then(|ctrs| {
                             Constraint::default_type_for(ctrs.iter().map(|(_, _, c)| c))
                         }) {
-                            default_ty.replace(params, subs, use_constr)
+                            if visiting.insert(*i) {
+                                let result = default_ty.replace(params, subs, use_constr, visiting);
+                                visiting.remove(i);
+                                result
+                            } else {
+                                default_ty
+                            }
                         } else {
                             self.clone()
                         }
@@ -1286,23 +1307,28 @@ impl Type {
                     self.clone()
                 }
             },
-            Type::Reference(kind, bt) => {
-                Type::Reference(*kind, Box::new(bt.replace(params, subs, use_constr)))
-            },
-            Type::Struct(mid, sid, args) => Type::Struct(*mid, *sid, replace_vec(args)),
+            Type::Reference(kind, bt) => Type::Reference(
+                *kind,
+                Box::new(bt.replace(params, subs, use_constr, visiting)),
+            ),
+            Type::Struct(mid, sid, args) => Type::Struct(*mid, *sid, replace_vec(args, visiting)),
             Type::Fun(arg, result, abilities) => Type::Fun(
-                Box::new(arg.replace(params, subs, use_constr)),
-                Box::new(result.replace(params, subs, use_constr)),
+                Box::new(arg.replace(params, subs, use_constr, visiting)),
+                Box::new(result.replace(params, subs, use_constr, visiting)),
                 *abilities,
             ),
-            Type::Tuple(args) => Type::Tuple(replace_vec(args)),
-            Type::Vector(et) => Type::Vector(Box::new(et.replace(params, subs, use_constr))),
-            Type::TypeDomain(et) => {
-                Type::TypeDomain(Box::new(et.replace(params, subs, use_constr)))
+            Type::Tuple(args) => Type::Tuple(replace_vec(args, visiting)),
+            Type::Vector(et) => {
+                Type::Vector(Box::new(et.replace(params, subs, use_constr, visiting)))
             },
-            Type::ResourceDomain(mid, sid, args_opt) => {
-                Type::ResourceDomain(*mid, *sid, args_opt.as_ref().map(|args| replace_vec(args)))
+            Type::TypeDomain(et) => {
+                Type::TypeDomain(Box::new(et.replace(params, subs, use_constr, visiting)))
             },
+            Type::ResourceDomain(mid, sid, args_opt) => Type::ResourceDomain(
+                *mid,
+                *sid,
+                args_opt.as_ref().map(|args| replace_vec(args, visiting)),
+            ),
             Type::Primitive(..) | Type::Error => self.clone(),
         }
     }
@@ -1827,6 +1853,23 @@ impl AbilityContext for NoUnificationContext {
     }
 }
 
+impl Debug for Substitution {
+    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
+        for (i, ty) in &self.subs {
+            writeln!(f, "Var({}) => {:?}", i, ty)?
+        }
+        for (i, ctrs) in &self.constraints {
+            writeln!(
+                f,
+                "Var({}) where {:?}",
+                i,
+                ctrs.iter().map(|(_, _, c)| c).collect_vec()
+            )?
+        }
+        Ok(())
+    }
+}
+
 impl Substitution {
     /// Creates a new substitution.
     pub fn new() -> Self {
@@ -1946,7 +1989,8 @@ impl Substitution {
             ty = self.specialize(&ty)
         }
 
-        // Occurs check
+        // Occurs check. Since we specialized the type, we do not need to
+        // check transitively.
         if ty.get_vars().contains(&var) {
             Err(TypeUnificationError::CyclicSubstitution(Type::Var(var), ty))
         } else {
@@ -2351,14 +2395,14 @@ impl Substitution {
 
     /// Specializes the type, substituting all variables bound in this substitution.
     pub fn specialize(&self, t: &Type) -> Type {
-        t.replace(None, Some(self), false)
+        t.replace(None, Some(self), false, &mut BTreeSet::new())
     }
 
     /// Similar like `specialize`, but if a variable is not resolvable but has constraints,
     /// attempts to derive a default from the constraints. For instance, a `SomeNumber(..u64..)`
     /// constraint can default to `u64`.
     pub fn specialize_with_defaults(&self, t: &Type) -> Type {
-        t.replace(None, Some(self), true)
+        t.replace(None, Some(self), true, &mut BTreeSet::new())
     }
 
     /// Checks whether the type is a number, considering constraints.
```
