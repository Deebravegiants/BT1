# [?] fix: don't panic when migrating without existing config

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-07-19
Source: https://github.com/fedimint/fedimint/commit/e77fcca80da63ef30619481af3bb5d21c0676752
Type: security-commit

## Details
fix: don't panic when migrating without existing config

## Patch
### fedimint-client/src/db.rs
```diff
@@ -399,11 +399,10 @@ pub fn get_core_client_database_migrations() -> BTreeMap<DatabaseVersion, CoreMi
                 .collect::<Vec<_>>()
                 .await;
 
-            assert_eq!(config_v0.len(), 1);
-            let (id, config_v0) = config_v0
-                .into_iter()
-                .next()
-                .expect("We asserted that the database contains exactly one config");
+            assert!(config_v0.len() <= 1);
+            let Some((id, config_v0)) = config_v0.into_iter().next() else {
+                return Ok(());
+            };
 
             let global = GlobalClientConfig {
                 api_endpoints: config_v0.global.api_endpoints,
```
