# [?] fix(cli): avoid panic on invalid remappings env and validate config path (#13660)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-06-29
Source: https://github.com/foundry-rs/foundry/commit/15399d199d1a4e734b341a82a8305a3971a0c809
Type: security-commit

## Details
fix(cli): avoid panic on invalid remappings env and validate config path (#13660)

## Patch
### crates/cli/src/opts/build/paths.rs
```diff
@@ -58,7 +58,11 @@ pub struct ProjectPathOpts {
     pub hardhat: bool,
 
     /// Path to the config file.
-    #[arg(long, value_hint = ValueHint::FilePath, value_name = "FILE")]
+    #[arg(
+        long,
+        value_hint = ValueHint::FilePath,
+        value_name = "FILE"
+    )]
     #[serde(skip)]
     pub config_path: Option<PathBuf>,
 }
@@ -81,15 +85,63 @@ impl ProjectPathOpts {
     /// Returns the remappings to add to the config
     pub fn get_remappings(&self) -> Vec<Remapping> {
         let mut remappings = self.remappings.clone();
-        if let Some(env_remappings) =
-            self.remappings_env.as_ref().and_then(|env| remappings_from_env_var(env))
+        if let Some(remappings_env) = self.remappings_env.as_deref()
+            && let Some(env_remappings) = remappings_from_env_var(remappings_env)
         {
-            remappings.extend(env_remappings.expect("Failed to parse env var remappings"));
+            match env_remappings {
+                Ok(env_remappings) => remappings.extend(env_remappings),
+                Err(err) => {
+                    let _ = sh_warn!(
+                        "failed to parse env var remappings from `{remappings_env}`: {err}"
+                    );
+                }
+            }
         }
         remappings
     }
 }
 
+#[cfg(test)]
+mod tests {
+    use super::ProjectPathOpts;
+
+    #[test]
+    fn get_remappings_ignores_invalid_remappings_env_var() {
+        let env_name = "FOUNDRY_CLI_TEST_INVALID_REMAPPINGS";
+        unsafe {
+            std::env::set_var(env_name, "this-is-not-a-remapping");
+        }
+
+        let opts =
+            ProjectPathOpts { remappings_env: Some(env_name.to_string()), ..Default::default() };
+        let remappings = opts.get_remappings();
+        assert!(remappings.is_empty());
+
+        unsafe {
+            std::env::remove_var(env_name);
+        }
+    }
+
+    #[test]
+    fn get_remappings_parses_valid_remappings_env_var() {
+        let env_name = "FOUNDRY_CLI_TEST_VALID_REMAPPINGS";
+        unsafe {
+            std::env::set_var(env_name, "forge-std/=lib/forge-std/src/");
+        }
+
+        let opts =
+            ProjectPathOpts { remappings_env: Some(env_name.to_string()), ..Default::default() };
+        let remappings = opts.get_remappings();
+        assert_eq!(remappings.len(), 1);
+        assert_eq!(remappings[0].name, "forge-std/");
+        assert_eq!(remappings[0].path, "lib/forge-std/src/");
+
+        unsafe {
+            std::env::remove_var(env_name);
+        }
+    }
+}
+
 foundry_config::impl_figment_convert!(ProjectPathOpts);
 
 // Make this args a `figment::Provider` so that it can be merged into the `Config`
```
