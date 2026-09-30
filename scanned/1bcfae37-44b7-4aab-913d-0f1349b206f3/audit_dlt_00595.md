# [?] Fix race condition between validator duties service and proposer preferences (#9309)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2026-06-20
Source: https://github.com/sigp/lighthouse/commit/477c25db9f39bef5b3afb29643a257a8aa5d249b
Type: security-commit

## Details
Fix race condition between validator duties service and proposer preferences (#9309)

The proposer preferences service was attempting to publish preferences at the start of each epoch. This caused it to race with the validator duties service, it wouldn't calculate validator duties in time for the proposer preference service.

This PR first updates the validator duties service to calculate proposer duties for the current epoch and the next epoch. After Fulu we have the ability to look ahead one epoch for proposer duties, but we never updated the vc to leverage this feature.

This PR also updates the proposer preferences service to fire at every slot. We have an `(Epoch, DependentRoot)` map that prevents us from publishing the same preferences twice.

The changes here should prevent the race condition between the two services and make the proposer preferences service more robust in general.


  


Co-Authored-By: Eitan Seri- Levi <eserilev@gmail.com>

Co-Authored-By: Eitan Seri-Levi <eserilev@ucsc.edu>

Co-Authored-By: Michael Sproul <michaelsproul@users.noreply.github.com>

## Patch
### book/src/help_vc.md
```diff
@@ -200,6 +200,11 @@ Flags:
           If present, do not configure the system allocator. Providing this flag
           will generally increase memory usage, it should only be provided when
           debugging specific memory allocation issues.
+      --disable-proposer-duties-v2
+          Fetch proposer duties using the v1 beacon node endpoint instead of v2.
+          The v1 endpoint reports an incorrect dependent root which causes
+          spurious proposer duty re-org warnings. Only enable this flag if your
+          beacon node does not serve the v2 proposer duties endpoint.
       --disable-slashing-protection-web3signer
           Disable Lighthouse's slashing protection for all web3signer keys. This
           can reduce the I/O burden on the VC but is only safe if slashing
```

### lighthouse/tests/validator_client.rs
```diff
@@ -130,6 +130,21 @@ fn disable_auto_discover_flag() {
         .with_config(|config| assert!(config.disable_auto_discover));
 }
 
+#[test]
+fn disable_proposer_duties_v2_default() {
+    CommandLineTest::new()
+        .run()
+        .with_config(|config| assert!(!config.disable_proposer_duties_v2));
+}
+
+#[test]
+fn disable_proposer_duties_v2_flag() {
+    CommandLineTest::new()
+        .flag("disable-proposer-duties-v2", None)
+        .run()
+        .with_config(|config| assert!(config.disable_proposer_duties_v2));
+}
+
 #[test]
 fn init_slashing_protections_flag() {
     CommandLineTest::new()
```

### validator_client/src/cli.rs
```diff
@@ -105,6 +105,17 @@ pub struct ValidatorClient {
     )]
     pub disable_attesting: bool,
 
+    #[clap(
+        long,
+        help = "Fetch proposer duties using the v1 beacon node endpoint instead of v2. The v1 \
+                endpoint reports an incorrect dependent root which causes spurious proposer duty \
+                re-org warnings. Only enable this flag if your beacon node does not serve the v2 \
+                proposer duties endpoint.",
+        display_order = 0,
+        help_heading = FLAG_HEADER
+    )]
+    pub disable_proposer_duties_v2: bool,
+
     #[clap(
         long,
         help = "If present, the validator client will use longer timeouts for requests \
```

### validator_client/src/config.rs
```diff
@@ -92,6 +92,8 @@ pub struct Config {
     #[serde(flatten)]
     pub initialized_validators: InitializedValidatorsConfig,
     pub disable_attesting: bool,
+    /// Fetch proposer duties using the v1 endpoint instead of v2.
+    pub disable_proposer_duties_v2: bool,
 }
 
 impl Default for Config {
@@ -139,6 +141,7 @@ impl Default for Config {
             distributed: false,
             initialized_validators: <_>::default(),
             disable_attesting: false,
+            disable_proposer_duties_v2: false,
         }
     }
 }
@@ -402,6 +405,7 @@ impl Config {
             };
 
         config.disable_attesting = validator_client_config.disable_attesting;
+        config.disable_proposer_duties_v2 = validator_client_config.disable_proposer_duties_v2;
 
         Ok(config)
     }
```

### validator_client/src/lib.rs
```diff
@@ -502,6 +502,7 @@ impl<E: EthSpec> ProductionValidatorClient<E> {
                 .attestation_selection_proof_config(attestation_selection_proof_config)
                 .sync_selection_proof_config(sync_selection_proof_config)
                 .disable_attesting(config.disable_attesting)
+                .disable_proposer_duties_v2(config.disable_proposer_duties_v2)
                 .build()?,
         );
 
```

### validator_client/validator_services/src/duties_service.rs
```diff
@@ -305,6 +305,7 @@ pub struct DutiesServiceBuilder<S, T> {
     /// Create sync selection proof config
     sync_selection_proof_config: SelectionProofConfig,
     disable_attesting: bool,
+    disable_proposer_duties_v2: bool,
 }
 
 impl<S, T> Default for DutiesServiceBuilder<S, T> {
@@ -325,6 +326,7 @@ impl<S, T> DutiesServiceBuilder<S, T> {
             attestation_selection_proof_config: SelectionProofConfig::default(),
             sync_selection_proof_config: SelectionProofConfig::default(),
             disable_attesting: false,
+            disable_proposer_duties_v2: false,
         }
     }
 
@@ -382,6 +384,11 @@ impl<S, T> DutiesServiceBuilder<S, T> {
         self
     }
 
+    pub fn disable_proposer_duties_v2(mut self, disable_proposer_duties_v2: bool) -> Self {
+        self.disable_proposer_duties_v2 = disable_proposer_duties_v2;
+        self
+    }
+
     pub fn build(self) -> Result<DutiesService<S, T>, String> {
         Ok(DutiesService {
             attesters: Default::default(),
@@ -405,6 +412,7 @@ impl<S, T> DutiesServiceBuilder<S, T> {
             enable_high_validator_count_metrics: self.enable_high_validator_count_metrics,
             selection_proof_config: self.attestation_selection_proof_config,
             disable_attesting: self.disable_attesting,
+            disable_proposer_duties_v2: self.disable_proposer_duties_v2,
         })
     }
 }
@@ -437,6 +445,11 @@ pub struct DutiesService<S, T> {
     /// Pass the config for distributed or non-distributed mode.
     pub selection_proof_config: SelectionProofConfig,
     pub disable_attesting: bool,
+    /// Use the v1 proposer duties endpoint instead of v2. The v1 endpoint reports an incorrect
+    /// dependent root, causing spurious "Proposer duties re-org" warnings. This flag exists for
+    /// compatibility with beacon nodes that do not yet serve the v2 endpoint and can be removed
+    /// after Gloas.
+    pub disable_proposer_duties_v2: bool,
 }
 
 impl<S: ValidatorStore, T: SlotClock + 'static> DutiesService<S, T> {
@@ -1660,54 +1673,8 @@ async fn poll_beacon_proposers<S: ValidatorStore, T: SlotClock + 'static>(
     // Only download duties and push out additional block production events if we have some
     // validators.
     if !local_pubkeys.is_empty() {
-        let download_result = duties_service
-            .beacon_nodes
-            .first_success(|beacon_node| async move {
-                let _timer = validator_metrics::start_timer_vec(
-                    &validator_metrics::DUTIES_SERVICE_TIMES,
-                    &[validator_metrics::PROPOSER_DUTIES_HTTP_GET],
-                );
-                beacon_node
-                    .get_validator_duties_proposer(current_epoch)
-                    .await
-            })
-            .await;
-
-        match download_result {
-            Ok(response) => {
-                let dependent_root = response.dependent_root;
-
-                let relevant_duties = response
-                    .data
-                    .into_iter()
-                    .filter(|proposer_duty| local_pubkeys.contains(&proposer_duty.pubkey))
-                    .collect::<Vec<_>>();
-
-                debug!(
-                    %dependent_root,
-                    num_relevant_duties = relevant_duties.len(),
-                    "Downloaded proposer duties"
-                );
-
-                if let Some((prior_dependent_root, _)) = duties_service
-                    .proposers
-                    .write()
-                    .insert(current_epoch, (dependent_root, relevant_duties))
-                    && dependent_root != prior_dependent_root
-                {
-                    warn!(
-                        %prior_dependent_root,
-                        %dependent_root,
-                        msg = "this may happen from time to time",
-                        "Proposer duties re-org"
-                    )
-                }
-            }
-            // Don't return early here, we still want to try and produce blocks using the cached values.
-            Err(e) => error!(
-                err = %e,
-                "Failed to download proposer duties"
-            ),
+        for epoch in [current_epoch, current_epoch + 1] {
+            fetch_and_store_proposer_duties(duties_service, epoch, &local_pubkeys).await;
         }
 
         // Compute the block proposers for this slot again, now that we've received an update from
@@ -1750,6 +1717,70 @@ async fn poll_beacon_proposers<S: ValidatorStore, T: SlotClock + 'static>(
     Ok(())
 }
 
+async fn fetch_and_store_proposer_duties<S: ValidatorStore, T: SlotClock + 'static>(
+    duties_service: &DutiesService<S, T>,
+    epoch: Epoch,
+    local_pubkeys: &HashSet<PublicKeyBytes>,
+) {
+    let use_v2 = !duties_service.disable_proposer_duties_v2;
+    let download_result = duties_service
+        .beacon_nodes
+        .first_success(|beacon_node| async move {
+            let _timer = validator_metrics::start_timer_vec(
+                &validator_metrics::DUTIES_SERVICE_TIMES,
+                &[validator_metrics::PROPOSER_DUTIES_HTTP_GET],
+            );
+            // Prefer the v2 endpoint, which reports the correct dependent root. The v1 endpoint
+            // returns an incorrect dependent root, leading to spurious "Proposer duties re-org"
+            // warnings.
+            if use_v2 {
+                beacon_node.get_validator_duties_proposer_v2(epoch).await
+            } else {
+                beacon_node.get_validator_duties_proposer(epoch).await
+            }
+        })
+        .await;
+
+    match download_result {
+        Ok(response) => {
+            let dependent_root = response.dependent_root;
+
+            let relevant_duties = response
+                .data
+                .into_iter()
+                .filter(|proposer_duty| local_pubkeys.contains(&proposer_duty.pubkey))
+                .collect::<Vec<_>>();
+
+            debug!(
+                %dependent_root,
+                %epoch,
+                num_relevant_duties = relevant_duties.len(),
+                "Downloaded proposer duties"
+            );
+
+            if let Some((prior_dependent_root, _)) = duties_service
+                .proposers
+                .write()
+                .insert(epoch, (dependent_root, relevant_duties))
+                && dependent_root != prior_dependent_root
+            {
+                warn!(
+                    %prior_dependent_root,
+                    %dependent_root,
+                    %epoch,
+                    msg = "this may happen from time to time",
+                    "Proposer duties re-org"
+                )
+            }
+        }
+        Err(e) => error!(
+            err = %e,
+            %epoch,
+            "Failed to download proposer duties"
+        ),
+    }
+}
+
 /// Query the beacon node for ptc duties for any known validators.
 async fn poll_beacon_ptc_attesters<S: ValidatorStore + 'static, T: SlotClock + 'static>(
     duties_service: &Arc<DutiesService<S, T>>,
```

### validator_client/validator_services/src/proposer_preferences_service.rs
```diff
@@ -1,12 +1,14 @@
 use crate::duties_service::DutiesService;
 use beacon_node_fallback::BeaconNodeFallback;
+use eth2::types::ProposerData;
 use slot_clock::SlotClock;
+use std::collections::HashMap;
 use std::ops::Deref;
 use std::sync::Arc;
 use task_executor::TaskExecutor;
 use tokio::time::sleep;
 use tracing::{debug, error, info, warn};
-use types::{ChainSpec, Epoch, EthSpec, ForkName, ProposerPreferences};
+use types::{ChainSpec, Epoch, EthSpec, ForkName, Hash256, ProposerPreferences};
 use validator_store::ValidatorStore;
 
 pub struct Inner<S, T> {
@@ -66,52 +68,83 @@ impl<S: ValidatorStore + 'static, T: SlotClock + 'static> ProposerPreferencesSer
         let executor = self.executor.clone();
 
         let interval_fut = async move {
+            let mut published_preferences: HashMap<Epoch, Hash256> = HashMap::new();
+
             loop {
                 let Some(current_slot) = self.slot_clock.now() else {
                     error!("Failed to read slot clock");
                     sleep(slot_duration).await;
                     continue;
                 };
 
-                if !self
-                    .chain_spec
-                    .fork_name_at_slot::<S::E>(current_slot)
-                    .gloas_enabled()
-                {
-                    let duration_to_next_epoch = self
-                        .slot_clock
-                        .duration_to_next_epoch(S::E::slots_per_epoch())
-                        .unwrap_or_else(|| slot_duration * S::E::slots_per_epoch() as u32);
-                    sleep(duration_to_next_epoch).await;
-                    continue;
-                }
-
                 let current_epoch = current_slot.epoch(S::E::slots_per_epoch());
-                let fork_name = self.chain_spec.fork_name_at_slot::<S::E>(current_slot);
-                self.publish_proposer_preferences(current_epoch, fork_name)
+
+                self.poll_and_publish_preferences(current_epoch, &mut published_preferences)
                     .await;
 
-                let duration_to_next_epoch = self
+                let duration_to_next_slot = self
                     .slot_clock
-                    .duration_to_next_epoch(S::E::slots_per_epoch())
-                    .unwrap_or_else(|| slot_duration * S::E::slots_per_epoch() as u32);
-                sleep(duration_to_next_epoch).await;
+                    .duration_to_next_slot()
+                    .unwrap_or(slot_duration);
+                sleep(duration_to_next_slot).await;
             }
         };
 
         executor.spawn(interval_fut, "proposer_preferences_service");
         Ok(())
     }
 
-    async fn publish_proposer_preferences(&self, current_epoch: Epoch, fork_name: ForkName) {
-        let (dependent_root, duties) = {
-            let proposers = self.duties_service.proposers.read();
-            match proposers.get(&current_epoch) {
-                Some((root, duties)) => (*root, duties.clone()),
-                None => return,
+    /// Publish proposer preferences for `current_epoch` and `current_epoch + 1`.
+    /// Will only publish preferences for a given epoch once per dependent root.
+    async fn poll_and_publish_preferences(
+        &self,
+        current_epoch: Epoch,
+        published_preferences: &mut HashMap<Epoch, Hash256>,
+    ) {
+        for (epoch, fork_name) in [
+            (
+                current_epoch,
+                self.chain_spec.fork_name_at_epoch(current_epoch),
+            ),
+            (
+                current_epoch + 1,
+                self.chain_spec.fork_name_at_epoch(current_epoch + 1),
+            ),
+        ] {
+            if !fork_name.gloas_enabled() {
+                continue;
             }
-        };
 
+            let (dependent_root, duties) = {
+                let proposers = self.duties_service.proposers.read();
+                match proposers.get(&epoch) {
+                    Some((root, duties)) => (*root, duties.clone()),
+                    None => continue,
+                }
+            };
+
+            if published_preferences.get(&epoch) == Some(&dependent_root) {
+                continue;
+            }
+
+            if self
+                .publish_proposer_preferences(epoch, fork_name, dependent_root, duties)
+                .await
+            {
+                published_preferences.insert(epoch, dependent_root);
+            }
+        }
+
+        published_preferences.retain(|epoch, _| *epoch >= current_epoch);
+    }
+
+    async fn publish_proposer_preferences(
+        &self,
+        epoch: Epoch,
+        fork_name: ForkName,
+        dependent_root: Hash256,
+        duties: Vec<ProposerData>,
+    ) -> bool {
         let preferences_to_sign: Vec<_> = {
             let mut result = vec![];
             for duty in &duties {
@@ -144,11 +177,11 @@ impl<S: ValidatorStore + 'static, T: SlotClock + 'static> ProposerPreferencesSer
         };
 
         if preferences_to_sign.is_empty() {
-            return;
+            return false;
         }
 
         debug!(
-            %current_epoch,
+            %epoch,
             count = preferences_to_sign.len(),
             "Signing proposer preferences"
         );
@@ -172,7 +205,7 @@ impl<S: ValidatorStore + 'static, T: SlotClock + 'static> ProposerPreferencesSer
         }
 
         if signed.is_empty() {
-            return;
+            return false;
         }
 
         let count = signed.len();
@@ -213,17 +246,19 @@ impl<S: ValidatorStore + 'static, T: SlotClock + 'static> ProposerPreferencesSer
         match result {
             Ok(()) => {
                 info!(
-                    %current_epoch,
+                    %epoch,
                     %count,
                     "Successfully published proposer preferences"
                 );
+                true
             }
             Err(e) => {
                 error!(
                     error = %e,
-                    %current_epoch,
+                    %epoch,
                     "Failed to publish proposer preferences"
                 );
+                false
             }
         }
     }
```
