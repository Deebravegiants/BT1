# [?] Ignore vulnerability `RUSTSEC-2024-0336` (#1842)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-04-19
Source: https://github.com/FuelLabs/fuel-core/commit/2ef6078b19a89320a5272a2468dd2d718d5c24a5
Type: security-commit

## Details
Ignore vulnerability `RUSTSEC-2024-0336` (#1842)

Issue for tracking the vulnerability:
https://github.com/FuelLabs/fuel-core/issues/1843

## Checklist
- [ ] Breaking changes are clearly marked as such in the PR description
and changelog
- [ ] New behavior is reflected in tests
- [ ] [The specification](https://github.com/FuelLabs/fuel-specs/)
matches the implemented behavior (link update PR if changes are needed)

### Before requesting review
- [x] I have reviewed the code myself
- [x] I have created follow-up issues caused by this PR and linked them
here

### After merging, notify other teams

[Add or remove entries as needed]

- [ ] [Rust SDK](https://github.com/FuelLabs/fuels-rs/)
- [ ] [Sway compiler](https://github.com/FuelLabs/sway/)
- [ ] [Platform
documentation](https://github.com/FuelLabs/devrel-requests/issues/new?assignees=&labels=new+request&projects=&template=NEW-REQUEST.yml&title=%5BRequest%5D%3A+)
(for out-of-organization contributors, the person merging the PR will do
this)
- [ ] Someone else?

## Patch
### .cargo/audit.toml
```diff
@@ -1,2 +1,5 @@
 [advisories]
-ignore = ["RUSTSEC-2023-0052"] # https://github.com/FuelLabs/fuel-core/issues/1317
\ No newline at end of file
+ignore = [
+    "RUSTSEC-2023-0052", # https://github.com/FuelLabs/fuel-core/issues/1316
+    "RUSTSEC-2024-0336" # https://github.com/FuelLabs/fuel-core/issues/1843
+    ]
\ No newline at end of file
```

### CHANGELOG.md
```diff
@@ -8,6 +8,10 @@ and this project adheres to [Semantic Versioning](http://semver.org/).
 
 Description of the upcoming release here.
 
+### Fixed
+
+- [1842](https://github.com/FuelLabs/fuel-core/pull/1842): Ignore RUSTSEC-2024-0336: `rustls::ConnectionCommon::complete_io` could fall into an infinite loop based on network
+
 ## [Version 0.25.1]
 
 ### Fixed
```
