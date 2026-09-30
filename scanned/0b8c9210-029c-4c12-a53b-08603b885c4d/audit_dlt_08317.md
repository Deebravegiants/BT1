# [?] cli: Fix `anchor account` command panicking outside of workspace (#2620)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2023-09-01
Source: https://github.com/otter-sec/anchor/commit/b9fa898384748edeaeb26d00c1e7d50054d94717
Type: security-commit

## Details
cli: Fix `anchor account` command panicking outside of workspace (#2620)

## Patch
### CHANGELOG.md
```diff
@@ -33,6 +33,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - cli: Fix `anchor build --no-docs` adding docs to the IDL ([#2575](https://github.com/coral-xyz/anchor/pull/2575)).
 - ts: Load workspace programs on-demand rather than loading all of them at once ([#2579](https://github.com/coral-xyz/anchor/pull/2579)).
 - lang: Fix `associated_token::token_program` constraint ([#2603](https://github.com/coral-xyz/anchor/pull/2603)).
+- cli: Fix `anchor account` command panicking outside of workspace ([#2620](https://github.com/coral-xyz/anchor/pull/2620)).
 
 ### Breaking
 
```

### cli/src/lib.rs
```diff
@@ -2594,11 +2594,12 @@ fn account(
         },
     );
 
-    let mut cluster = &Config::discover(cfg_override)
-        .map(|cfg| cfg.unwrap())
-        .map(|cfg| cfg.provider.cluster.clone())
-        .unwrap_or(Cluster::Localnet);
-    cluster = cfg_override.cluster.as_ref().unwrap_or(cluster);
+    let cluster = match &cfg_override.cluster {
+        Some(cluster) => cluster.clone(),
+        None => Config::discover(cfg_override)?
+            .map(|cfg| cfg.provider.cluster.clone())
+            .unwrap_or(Cluster::Localnet),
+    };
 
     let data = create_client(cluster.url()).get_account_data(&address)?;
     if data.len() < 8 {
```
