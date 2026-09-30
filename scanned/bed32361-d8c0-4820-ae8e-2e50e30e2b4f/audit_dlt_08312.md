# [?] cli: Ignore non semver solana/agave releases to avoid panic (#3432)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2024-12-18
Source: https://github.com/otter-sec/anchor/commit/2233ee7ff2eb13e2509044533e0e7ab43199d2d4
Type: security-commit

## Details
cli: Ignore non semver solana/agave releases to avoid panic (#3432)

## Patch
### CHANGELOG.md
```diff
@@ -103,6 +103,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - lang: Require `zero` accounts to be unique ([#3409](https://github.com/coral-xyz/anchor/pull/3409)).
 - lang: Deduplicate `zero` accounts against `init` accounts ([#3422](https://github.com/coral-xyz/anchor/pull/3422)).
 - cli: Fix custom `provider.cluster` ([#3428](https://github.com/coral-xyz/anchor/pull/3428)).
+- cli: Ignore non semver solana/agave releases to avoid panic ([#3432](https://github.com/coral-xyz/anchor/pull/3432)).
 
 ### Breaking
 
```

### cli/src/lib.rs
```diff
@@ -556,16 +556,16 @@ fn override_toolchain(cfg_override: &ConfigOverride) -> Result<RestoreToolchainC
 
     let cfg = Config::discover(cfg_override)?;
     if let Some(cfg) = cfg {
-        fn parse_version(text: &str) -> String {
-            Regex::new(r"(\d+\.\d+\.\S+)")
-                .unwrap()
-                .captures_iter(text)
-                .next()
-                .unwrap()
-                .get(0)
-                .unwrap()
-                .as_str()
-                .to_string()
+        fn parse_version(text: &str) -> Option<String> {
+            Some(
+                Regex::new(r"(\d+\.\d+\.\S+)")
+                    .unwrap()
+                    .captures_iter(text)
+                    .next()?
+                    .get(0)?
+                    .as_str()
+                    .to_string(),
+            )
         }
 
         fn get_current_version(cmd_name: &str) -> Result<String> {
@@ -577,8 +577,8 @@ fn override_toolchain(cfg_override: &ConfigOverride) -> Result<RestoreToolchainC
             }
 
             let output_version = std::str::from_utf8(&output.stdout)?;
-            let version = parse_version(output_version);
-            Ok(version)
+            parse_version(output_version)
+                .ok_or_else(|| anyhow!("Failed to parse the version of `{cmd_name}`"))
         }
 
         if let Some(solana_version) = &cfg.toolchain.solana_version {
@@ -635,7 +635,8 @@ fn override_toolchain(cfg_override: &ConfigOverride) -> Result<RestoreToolchainC
                     // Hide the installation progress if the version is already installed
                     let is_installed = std::str::from_utf8(&output.stdout)?
                         .lines()
-                        .any(|line| parse_version(line) == version);
+                        .filter_map(parse_version)
+                        .any(|line_version| line_version == version);
                     let (stderr, stdout) = if is_installed {
                         (Stdio::null(), Stdio::null())
                     } else {
```
