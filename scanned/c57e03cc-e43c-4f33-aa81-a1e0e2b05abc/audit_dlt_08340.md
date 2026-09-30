# [?] [built-package] fix panic caused by script in dependency (#14886)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-10-07
Source: https://github.com/aptos-labs/aptos-core/commit/ea47ce542bce0d307c5bc9088f69029101185a8e
Type: security-commit

## Details
[built-package] fix panic caused by script in dependency (#14886)

## Patch
### aptos-move/framework/src/built_package.rs
```diff
@@ -472,16 +472,17 @@ impl BuiltPackage {
             .package
             .deps_compiled_units
             .iter()
-            .map(|(name, unit)| {
-                let package_name = name.as_str().to_string();
-                let account = match &unit.unit {
-                    CompiledUnit::Module(m) => AccountAddress::new(m.address.into_bytes()),
-                    _ => panic!("script not a dependency"),
-                };
-                PackageDep {
-                    account,
-                    package_name,
-                }
+            .flat_map(|(name, unit)| match &unit.unit {
+                CompiledUnit::Module(m) => {
+                    let package_name = name.as_str().to_string();
+                    let account = AccountAddress::new(m.address.into_bytes());
+
+                    Some(PackageDep {
+                        account,
+                        package_name,
+                    })
+                },
+                CompiledUnit::Script(_) => None,
             })
             .collect::<BTreeSet<_>>()
             .into_iter()
```
