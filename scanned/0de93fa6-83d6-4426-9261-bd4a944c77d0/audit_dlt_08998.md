# [?] Fix wsv panic at adding asset

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2021-04-14
Source: https://github.com/hyperledger-iroha/iroha/commit/ed7d9ff29e9071f3febb04908744b6982845be2d
Type: security-commit

## Details
Fix wsv panic at adding asset

Signed-off-by: i1i1 <vanyarybin1@live.ru>

## Patch
### iroha/src/asset.rs
```diff
@@ -55,7 +55,7 @@ pub mod isi {
                 None => world_state_view.add_asset(Asset::with_quantity(
                     self.destination_id.clone(),
                     self.object,
-                )),
+                ))?,
             }
             Ok(world_state_view)
         }
@@ -83,7 +83,7 @@ pub mod isi {
                 None => world_state_view.add_asset(Asset::with_big_quantity(
                     self.destination_id.clone(),
                     self.object,
-                )),
+                ))?,
             }
             Ok(world_state_view)
         }
@@ -112,7 +112,7 @@ pub mod isi {
                     self.key,
                     self.value,
                     asset_metadata_limits,
-                )?),
+                )?)?,
             }
             Ok(world_state_view)
         }
```

### iroha/src/query.rs
```diff
@@ -201,7 +201,7 @@ mod tests {
             Value::Vec(vec![Value::U32(1), Value::U32(2), Value::U32(3)]),
             MetadataLimits::new(10, 100),
         );
-        wsv.add_asset(Asset::new(asset_id.clone(), AssetValue::Store(store)));
+        wsv.add_asset(Asset::new(asset_id.clone(), AssetValue::Store(store)))?;
         let bytes =
             FindAssetKeyValueByIdAndKey::new(asset_id, "Bytes".to_string()).execute(&wsv)?;
         assert_eq!(
```

### iroha/src/wsv.rs
```diff
@@ -5,6 +5,7 @@ use std::collections::HashMap;
 
 use config::Configuration;
 use iroha_data_model::prelude::*;
+use iroha_error::{error, Result};
 
 use crate::prelude::*;
 
@@ -196,12 +197,15 @@ impl WorldStateView {
     }
 
     /// Add new `Asset` entity.
-    pub fn add_asset(&mut self, asset: Asset) {
+    /// # Errors
+    /// Fails if there is no account for asset
+    pub fn add_asset(&mut self, asset: Asset) -> Result<()> {
         let _ = self
             .account(&asset.id.account_id)
-            .expect("Failed to find an account.")
+            .ok_or_else(|| error!("Failed to find account"))?
             .assets
             .insert(asset.id.clone(), asset);
+        Ok(())
     }
 
     /// Get `AssetDefinitionEntry` without an ability to modify it.
```
