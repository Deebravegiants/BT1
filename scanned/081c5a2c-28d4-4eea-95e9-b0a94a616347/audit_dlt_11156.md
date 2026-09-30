# [?] Fix bug where `forc` panics if dep declared with both package and path (#1289)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-04-18
Source: https://github.com/FuelLabs/sway/commit/4d617a227502fb638a0e724e85a2732b3bef37a6
Type: security-commit

## Details
Fix bug where `forc` panics if dep declared with both package and path (#1289)

This allows us to point the `forc` E2E package dependency test to the
local `std`. This makes it easier to iterate on changes in `sway-core`
that might require breaking changes in `std` without breaking this test.

Closes #1053.

## Patch
### forc-pkg/src/pkg.rs
```diff
@@ -525,18 +525,18 @@ pub fn graph_to_path_map(
                 })?
             }
             SourcePinned::Path => {
-                let parent_node = graph
+                let (parent_node, dep_name) = graph
                     .edges_directed(dep_node, Direction::Incoming)
                     .next()
-                    .ok_or_else(|| anyhow!("more than one root package detected in graph"))?
-                    .source();
+                    .map(|edge| (edge.source(), edge.weight().clone()))
+                    .ok_or_else(|| anyhow!("more than one root package detected in graph"))?;
                 let parent = &graph[parent_node];
                 let parent_path = &path_map[&parent.id()];
                 let parent_manifest = ManifestFile::from_dir(parent_path, sway_git_tag)?;
                 let detailed = parent_manifest
                     .dependencies
                     .as_ref()
-                    .and_then(|deps| match &deps[&dep.name] {
+                    .and_then(|deps| match &deps[&dep_name] {
                         Dependency::Detailed(detailed) => Some(detailed),
                         Dependency::Simple(_) => None,
                     })
```

### test/src/e2e_vm_tests/test_programs/should_pass/forc/dependency_package_field/Forc.lock
```diff
@@ -1,13 +1,11 @@
 [[package]]
 name = 'core'
-source = 'git+https://github.com/FuelLabs/sway-lib-core?branch=master#082bc8eb0616586ac0000825bfe6e9d47b0c713f'
 dependencies = []
 
 [[package]]
 name = 'dependency_package_field'
-dependencies = ['(std-alt) std git+https://github.com/FuelLabs/sway-lib-std?branch=master#dc036471ced326e41f076700c0501efc1b442455']
+dependencies = ['(std-alt) std']
 
 [[package]]
 name = 'std'
-source = 'git+https://github.com/FuelLabs/sway-lib-std?branch=master#dc036471ced326e41f076700c0501efc1b442455'
-dependencies = ['core git+https://github.com/FuelLabs/sway-lib-core?branch=master#082bc8eb0616586ac0000825bfe6e9d47b0c713f']
+dependencies = ['core']
```

### test/src/e2e_vm_tests/test_programs/should_pass/forc/dependency_package_field/Forc.toml
```diff
@@ -6,5 +6,4 @@ name = "dependency_package_field"
 
 [dependencies]
 # Use `std` package as `std_alt` to test `package` field.
-# TODO need https://github.com/FuelLabs/sway/issues/1053 before this can be changed to a local path
-std-alt = { git = "https://github.com/FuelLabs/sway-lib-std", branch = "master", package = "std" }
+std-alt = { path = "../../../../../../../sway-lib-std", package = "std" }
```
