# [?] Corrects read/write race condition

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-03-28
Source: https://github.com/sigp/lighthouse/commit/cc4ccd4017c0e85bdbfed08fc92454da6b110285
Type: security-commit

## Details
Corrects read/write race condition

## Patch
### beacon_node/rpc/src/validator.rs
```diff
@@ -4,7 +4,7 @@ use futures::Future;
 use grpcio::{RpcContext, RpcStatus, RpcStatusCode, UnarySink};
 use protos::services::{ActiveValidator, GetDutiesRequest, GetDutiesResponse, ValidatorDuty};
 use protos::services_grpc::ValidatorService;
-use slog::{debug, warn, Logger};
+use slog::{debug, info, warn, Logger};
 use ssz::Decodable;
 use std::sync::Arc;
 use types::{Epoch, RelativeEpoch};
@@ -72,6 +72,7 @@ impl ValidatorService for ValidatorServiceInstance {
         };
 
         // get the duties for each validator
+        dbg!(validators.get_public_keys());
         for validator_pk in validators.get_public_keys() {
             let mut active_validator = ActiveValidator::new();
 
@@ -82,12 +83,13 @@ impl ValidatorService for ValidatorServiceInstance {
                     let f = sink
                         .fail(RpcStatus::new(
                             RpcStatusCode::InvalidArgument,
-                            Some("apurple  Invalid public_key".to_string()),
+                            Some("Invalid public_key".to_string()),
                         ))
                         .map_err(move |e| warn!(log_clone, "failed to reply {:?}", req));
                     return ctx.spawn(f);
                 }
             };
+            info!(self.log,""; "Public key" => format!("{:?}",public_key));
 
             // get the validator index
             let val_index = match state.get_validator_index(&public_key) {
```

### validator_client/src/duties/grpc.rs
```diff
@@ -1,9 +1,11 @@
 use super::epoch_duties::{EpochDuties, EpochDuty};
 use super::traits::{BeaconNode, BeaconNodeError};
+use grpcio::CallOption;
 use protos::services::{GetDutiesRequest, Validators};
 use protos::services_grpc::ValidatorServiceClient;
 use ssz::ssz_encode;
 use std::collections::HashMap;
+use std::time::Duration;
 use types::{Epoch, PublicKey, Slot};
 
 impl BeaconNode for ValidatorServiceClient {
@@ -21,6 +23,9 @@ impl BeaconNode for ValidatorServiceClient {
         validators.set_public_keys(pubkeys.iter().map(|v| ssz_encode(v)).collect());
         req.set_validators(validators);
 
+        // set a timeout for requests
+        // let call_opt = CallOption::default().timeout(Duration::from_secs(2));
+
         // send the request, get the duties reply
         let reply = self
             .get_validator_duties(&req)
```

### validator_client/src/duties/mod.rs
```diff
@@ -51,20 +51,23 @@ impl<U: BeaconNode> DutiesManager<U> {
     /// be a wall-clock (e.g., system time, remote server time, etc.).
     fn update(&self, epoch: Epoch) -> Result<UpdateOutcome, Error> {
         let duties = self.beacon_node.request_duties(epoch, &self.pubkeys)?;
-        // If these duties were known, check to see if they're updates or identical.
-        if let Some(known_duties) = self.duties_map.read()?.get(&epoch) {
-            if *known_duties == duties {
-                return Ok(UpdateOutcome::NoChange(epoch));
-            } else {
-                //TODO: Duties could be large here. Remove from display and avoid the clone.
-                self.duties_map.write()?.insert(epoch, duties.clone());
-                return Ok(UpdateOutcome::DutiesChanged(epoch, duties));
+        {
+            // If these duties were known, check to see if they're updates or identical.
+            if let Some(known_duties) = self.duties_map.read()?.get(&epoch) {
+                if *known_duties == duties {
+                    return Ok(UpdateOutcome::NoChange(epoch));
+                }
             }
-        } else {
+        }
+        if !self.duties_map.read()?.contains_key(&epoch) {
             //TODO: Remove clone by removing duties from outcome
             self.duties_map.write()?.insert(epoch, duties.clone());
             return Ok(UpdateOutcome::NewDuties(epoch, duties));
-        };
+        }
+        // duties have changed
+        //TODO: Duties could be large here. Remove from display and avoid the clone.
+        self.duties_map.write()?.insert(epoch, duties.clone());
+        return Ok(UpdateOutcome::DutiesChanged(epoch, duties));
     }
 
     /// A future wrapping around `update()`. This will perform logic based upon the update
```

### validator_client/src/service.rs
```diff
@@ -195,8 +195,8 @@ impl Service {
 
         // TODO: keypairs are randomly generated; they should be loaded from a file or generated.
         // https://github.com/sigp/lighthouse/issues/160
-        let keypairs = Arc::new(vec![Keypair::random()]);
-
+        let keypairs: Arc<Vec<Keypair>> =
+            Arc::new((0..10).into_iter().map(|_| Keypair::random()).collect());
         /* build requisite objects to pass to core thread */
 
         // Builds a mapping of Epoch -> Map(PublicKey, EpochDuty)
@@ -213,54 +213,59 @@ impl Service {
         });
 
         // run the core thread
-        runtime
-            .block_on(interval.for_each(move |_| {
-                let log = service.log.clone();
-
-                /* get the current slot and epoch */
-                let current_slot = match service.slot_clock.present_slot() {
-                    Err(e) => {
-                        error!(log, "SystemTimeError {:?}", e);
-                        return Ok(());
-                    }
-                    Ok(slot) => slot.expect("Genesis is in the future"),
-                };
-
-                let current_epoch = current_slot.epoch(service.slots_per_epoch);
-
-                debug_assert!(
-                    current_slot > service.current_slot,
-                    "The Timer should poll a new slot"
-                );
-
-                info!(log, "Processing slot: {}", current_slot.as_u64());
-
-                /* check for new duties */
-
-                let cloned_manager = manager.clone();
-                tokio::spawn(futures::future::poll_fn(move || {
-                    cloned_manager.run_update(current_epoch.clone(), log.clone())
-                }));
-
-                /* execute any specified duties */
-
-                if let Some(work) = manager.get_current_work(current_slot) {
-                    for (_public_key, work_type) in work {
-                        if work_type.produce_block {
-                            // TODO: Produce a beacon block in a new thread
+        runtime.block_on(
+            interval
+                .for_each(move |_| {
+                    let log = service.log.clone();
+
+                    /* get the current slot and epoch */
+                    let current_slot = match service.slot_clock.present_slot() {
+                        Err(e) => {
+                            error!(log, "SystemTimeError {:?}", e);
+                            return Ok(());
                         }
-                        if work_type.attestation_duty.is_some() {
-                            // available AttestationDuty info
-                            let attestation_duty =
-                                work_type.attestation_duty.expect("Cannot be None");
-                            //TODO: Produce an attestation in a new thread
+                        Ok(slot) => slot.expect("Genesis is in the future"),
+                    };
+
+                    let current_epoch = current_slot.epoch(service.slots_per_epoch);
+
+                    debug_assert!(
+                        current_slot > service.current_slot,
+                        "The Timer should poll a new slot"
+                    );
+
+                    info!(log, "Processing slot: {}", current_slot.as_u64());
+
+                    /* check for new duties */
+
+                    let cloned_manager = manager.clone();
+                    let cloned_log = log.clone();
+                    // spawn a new thread separate to the runtime
+                    std::thread::spawn(move || {
+                        cloned_manager.run_update(current_epoch.clone(), cloned_log.clone());
+                        dbg!("Finished thread");
+                    });
+
+                    /* execute any specified duties */
+
+                    if let Some(work) = manager.get_current_work(current_slot) {
+                        for (_public_key, work_type) in work {
+                            if work_type.produce_block {
+                                // TODO: Produce a beacon block in a new thread
+                            }
+                            if work_type.attestation_duty.is_some() {
+                                // available AttestationDuty info
+                                let attestation_duty =
+                                    work_type.attestation_duty.expect("Cannot be None");
+                                //TODO: Produce an attestation in a new thread
+                            }
                         }
                     }
-                }
 
-                Ok(())
-            }))
-            .map_err(|e| format!("Service thread failed: {:?}", e))?;
+                    Ok(())
+                })
+                .map_err(|e| format!("Service thread failed: {:?}", e)),
+        );
 
         // completed a slot process
         Ok(())
```
