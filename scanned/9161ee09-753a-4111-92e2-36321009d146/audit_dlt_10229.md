# [?] Avoid panic in Staking component

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-03-31
Source: https://github.com/penumbra-zone/penumbra/commit/95b0d5688f102ad4591bd887ac245951ef2f70e2
Type: security-commit

## Details
Avoid panic in Staking component

This uses the `PenumbraStore` trait to avoid having to store chain parameters.

## Patch
### pd/src/components/staking.rs
```diff
@@ -6,31 +6,20 @@ use penumbra_transaction::Transaction;
 use tendermint::abci;
 
 use super::{Component, Overlay};
-use crate::{components::validator_set::BlockChanges, genesis, WriteOverlayExt};
+use crate::{components::validator_set::BlockChanges, genesis, PenumbraStore, WriteOverlayExt};
 
 // Stub component
 pub struct Staking {
     overlay: Overlay,
-
-    // TODO: this shouldn't be here -- we should grab this from a common location
-    // in the JMT, i.e. genesis/AppState but that's not available until #511 lands.
-    // since consensus can't yet change chain params on the fly, it's not an issue,
-    // but it definitely will be in the future!
-    chain_params: Option<ChainParams>,
 }
 
 #[async_trait]
 impl Component for Staking {
     async fn new(overlay: Overlay) -> Result<Self> {
-        Ok(Self {
-            overlay,
-            chain_params: None,
-        })
+        Ok(Self { overlay })
     }
 
     async fn init_chain(&mut self, app_state: &genesis::AppState) -> Result<()> {
-        self.chain_params = Some(app_state.chain_params.clone());
-
         Ok(())
     }
 
@@ -39,7 +28,7 @@ impl Component for Staking {
         let block_height = begin_block.header.height;
         let epoch = Epoch::from_height(
             block_height.into(),
-            self.chain_params.as_ref().unwrap().epoch_duration,
+            self.overlay.get_epoch_duration().await?,
         );
         // Reset all staking state in the JMT overlay
         let block_changes = BlockChanges {
```
