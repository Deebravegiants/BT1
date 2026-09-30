# [?] Fix non-deterministic metadata query bug

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-09-17
Source: https://github.com/MystenLabs/sui/commit/6b6b625c7a5ff24e958d33fd459f95e9257db63a
Type: security-commit

## Details
Fix non-deterministic metadata query bug

## Patch
### crates/sui-rosetta/src/unit_tests/lib_tests.rs
```diff
@@ -86,14 +86,17 @@ async fn test_cache() {
         .into_iter()
         .find_map(|change| {
             if let ObjectChange::Created { object_type, .. } = change {
-                if object_type.to_string().contains("2::coin::TreasuryCap") {
+                let type_str = object_type.to_string();
+                if type_str.contains("2::coin::TreasuryCap")
+                    && type_str.contains("::my_coin::MY_COIN>")
+                {
                     let coin_tag = object_type.type_params.into_iter().next().unwrap();
                     return Some(coin_tag);
                 }
             }
             None
         })
-        .unwrap();
+        .expect("MY_COIN treasury cap not found");
 
     let coin_cache = CoinMetadataCache::new(client.clone(), NonZeroUsize::new(1).unwrap());
 
```
