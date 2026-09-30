# [?] fix: upgrade warn to a panic

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-11-16
Source: https://github.com/fedimint/fedimint/commit/4c643aaa07c99c9b52a9b03f5f12be12a84bc73f
Type: security-commit

## Details
fix: upgrade warn to a panic

## Patch
### fedimint-core/src/db/mod.rs
```diff
@@ -1126,12 +1126,7 @@ where
         K::Value: MaybeSend + MaybeSync,
     {
         if let Some(prev) = self.insert_entry(key, value).await {
-            debug_assert!(
-                false,
-                "Database overwriting element when expecting insertion of new entry. Key: {key:?} Prev Value: {prev:?}"
-            );
-            warn!(
-                target: LOG_DB,
+            panic!(
                 "Database overwriting element when expecting insertion of new entry. Key: {key:?} Prev Value: {prev:?}"
             );
         }
```

### modules/fedimint-lnv2-server/src/lib.rs
```diff
@@ -404,7 +404,7 @@ impl ServerModule for Lightning {
                             return Err(LightningInputError::InvalidPreimage);
                         }
 
-                        dbtx.insert_new_entry(&PreimageKey(*contract_id), preimage)
+                        dbtx.insert_entry(&PreimageKey(*contract_id), preimage)
                             .await;
 
                         contract.claim_pk
```
