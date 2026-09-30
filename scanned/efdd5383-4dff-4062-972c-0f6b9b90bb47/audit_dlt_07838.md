# [?] Correct cache race condition

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-03-30
Source: https://github.com/sigp/lighthouse/commit/4fb95d06d1062e1779f24d4cda23a89c4f9a6f9f
Type: security-commit

## Details
Correct cache race condition

## Patch
### beacon_node/rpc/src/beacon_chain.rs
```diff
@@ -2,7 +2,7 @@ use beacon_chain::BeaconChain as RawBeaconChain;
 use beacon_chain::{
     db::ClientDB,
     fork_choice::ForkChoice,
-    parking_lot::RwLockReadGuard,
+    parking_lot::{RwLockReadGuard, RwLockWriteGuard},
     slot_clock::SlotClock,
     types::{BeaconState, ChainSpec, Signature},
     AttestationValidationError, BlockProductionError,
@@ -16,6 +16,8 @@ pub trait BeaconChain: Send + Sync {
 
     fn get_state(&self) -> RwLockReadGuard<BeaconState>;
 
+    fn get_mut_state(&self) -> RwLockWriteGuard<BeaconState>;
+
     fn process_block(&self, block: BeaconBlock)
         -> Result<BlockProcessingOutcome, BeaconChainError>;
 
@@ -46,6 +48,10 @@ where
         self.state.read()
     }
 
+    fn get_mut_state(&self) -> RwLockWriteGuard<BeaconState> {
+        self.state.write()
+    }
+
     fn process_block(
         &self,
         block: BeaconBlock,
```

### beacon_node/rpc/src/validator.rs
```diff
@@ -4,15 +4,15 @@ use futures::Future;
 use grpcio::{RpcContext, RpcStatus, RpcStatusCode, UnarySink};
 use protos::services::{ActiveValidator, GetDutiesRequest, GetDutiesResponse, ValidatorDuty};
 use protos::services_grpc::ValidatorService;
-use slog::{debug, info, warn, Logger};
+use slog::{trace, warn};
 use ssz::Decodable;
 use std::sync::Arc;
 use types::{Epoch, RelativeEpoch};
 
 #[derive(Clone)]
 pub struct ValidatorServiceInstance {
     pub chain: Arc<BeaconChain>,
-    pub log: Logger,
+    pub log: slog::Logger,
 }
 //TODO: Refactor Errors
 
@@ -27,13 +27,23 @@ impl ValidatorService for ValidatorServiceInstance {
         sink: UnarySink<GetDutiesResponse>,
     ) {
         let validators = req.get_validators();
-        debug!(self.log, "RPC request"; "endpoint" => "GetValidatorDuties", "epoch" => req.get_epoch());
+        trace!(self.log, "RPC request"; "endpoint" => "GetValidatorDuties", "epoch" => req.get_epoch());
+
+        let spec = self.chain.get_spec();
+        // update the caches if necessary
+        {
+            let mut mut_state = self.chain.get_mut_state();
+
+            let _ = mut_state.build_epoch_cache(RelativeEpoch::NextWithoutRegistryChange, spec);
+
+            let _ = mut_state.build_epoch_cache(RelativeEpoch::NextWithRegistryChange, spec);
+            let _ = mut_state.update_pubkey_cache();
+        }
 
         let epoch = Epoch::from(req.get_epoch());
         let mut resp = GetDutiesResponse::new();
         let resp_validators = resp.mut_active_validators();
 
-        let spec = self.chain.get_spec();
         let state = self.chain.get_state();
 
         let relative_epoch =
```

### eth2/types/src/test_utils/testing_beacon_state_builder.rs
```diff
@@ -120,7 +120,7 @@ impl TestingBeaconStateBuilder {
             })
             .collect();
 
-        let genesis_time = 1553932445; // arbitrary
+        let genesis_time = 1553950542; // arbitrary
 
         let mut state = BeaconState::genesis(
             genesis_time,
```
