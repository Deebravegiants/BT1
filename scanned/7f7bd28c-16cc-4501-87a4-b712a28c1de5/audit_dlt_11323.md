# [?] fix: don't crash on broken impl syntax (#7512)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-02-25
Source: https://github.com/noir-lang/noir/commit/677c10c50e6944e9e11d5579048f77cab59cf91a
Type: security-commit

## Details
fix: don't crash on broken impl syntax (#7512)

## Patch
### compiler/noirc_frontend/src/elaborator/mod.rs
```diff
@@ -2134,7 +2134,7 @@ impl<'context> Elaborator<'context> {
                     let span = location.span;
                     let found = trait_impl.r#trait.typ.to_string();
                     self.push_err(ResolverError::ExpectedTrait { span, found }, location.file);
-                    continue;
+                    (None, GenericTypeArgs::default(), location)
                 }
             };
 
```

### test_programs/compile_failure/broken_impl/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "broken_impl"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.26.0"
+
+[dependencies]
```

### test_programs/compile_failure/broken_impl/src/main.nr
```diff
@@ -0,0 +1,2 @@
+// This used to crash the compiler
+impl< Foo for
```
