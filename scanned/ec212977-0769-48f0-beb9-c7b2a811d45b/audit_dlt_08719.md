# [?] Merge branch 'master' into fix-stopandwait-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-10
Source: https://github.com/OffchainLabs/nitro/commit/84309211f2791bbeb903afc740328aed036eadeb
Type: security-commit

## Details
Merge branch 'master' into fix-stopandwait-deadlock

## Patch
### arbitrator/arbutil/src/evm/api.rs
```diff
@@ -252,7 +252,7 @@ pub trait EvmApi<D: DataReader>: Send + 'static {
 
     /// Returns the code and the access cost in gas.
     /// Analogous to `vm.EXTCODECOPY`.
-    fn account_code(&mut self, address: Bytes20, gas_left: Gas) -> (D, Gas);
+    fn account_code(&mut self, arbos_version: u64, address: Bytes20, gas_left: Gas) -> (D, Gas);
 
     /// Gets the hash of the given address's code.
     /// Returns the hash and the access cost in gas.
```

### arbitrator/arbutil/src/evm/mod.rs
```diff
@@ -76,6 +76,7 @@ pub const GASPRICE_GAS: Gas = GAS_QUICK_STEP;
 pub const ORIGIN_GAS: Gas = GAS_QUICK_STEP;
 
 pub const ARBOS_VERSION_STYLUS_CHARGING_FIXES: u64 = 32;
+pub const ARBOS_VERSION_STYLUS_LAST_CODE_CACHE_FIX: u64 = 40;
 
 #[derive(Clone, Copy, Debug, Default)]
 #[repr(C)]
```

### arbitrator/arbutil/src/evm/req.rs
```diff
@@ -265,7 +265,7 @@ impl<D: DataReader, H: RequestHandler<D>> EvmApi<D> for EvmApiRequestor<D, H> {
         (res.try_into().unwrap(), cost)
     }
 
-    fn account_code(&mut self, address: Bytes20, gas_left: Gas) -> (D, Gas) {
+    fn account_code(&mut self, arbos_version: u64, address: Bytes20, gas_left: Gas) -> (D, Gas) {
         if let Some((stored_address, data)) = self.last_code.as_ref() {
             if address == *stored_address {
                 return (data.clone(), Gas(0));
@@ -276,7 +276,9 @@ impl<D: DataReader, H: RequestHandler<D>> EvmApi<D> for EvmApiRequestor<D, H> {
         req.extend(gas_left.to_be_bytes());
 
         let (_, data, cost) = self.request(EvmApiMethod::AccountCode, req);
-        self.last_code = Some((address, data.clone()));
+        if !data.slice().is_empty() || arbos_version < super::ARBOS_VERSION_STYLUS_LAST_CODE_CACHE_FIX {
+            self.last_code = Some((address, data.clone()));
+        }
         (data, cost)
     }
 
```

### arbitrator/stylus/src/test/api.rs
```diff
@@ -180,7 +180,7 @@ impl EvmApi<VecReader> for TestEvmApi {
         unimplemented!()
     }
 
-    fn account_code(&mut self, _address: Bytes20, _gas_left: Gas) -> (VecReader, Gas) {
+    fn account_code(&mut self, _arbos_version: u64, _address: Bytes20, _gas_left: Gas) -> (VecReader, Gas) {
         unimplemented!()
     }
 
```

### arbitrator/wasm-libraries/user-host-trait/src/lib.rs
```diff
@@ -609,8 +609,10 @@ pub trait UserHost<DR: DataReader>: GasMeteredMachine {
         let address = self.read_bytes20(address)?;
         let gas = self.gas_left()?;
 
+        let arbos_version = self.evm_data().arbos_version;
+
         // we pass `gas` to check if there's enough before loading from the db
-        let (code, gas_cost) = self.evm_api().account_code(address, gas);
+        let (code, gas_cost) = self.evm_api().account_code(arbos_version, address, gas);
         self.buy_gas(gas_cost)?;
 
         let code = code.slice();
@@ -639,8 +641,10 @@ pub trait UserHost<DR: DataReader>: GasMeteredMachine {
         let address = self.read_bytes20(address)?;
         let gas = self.gas_left()?;
 
+        let arbos_version = self.evm_data().arbos_version;
+
         // we pass `gas` to check if there's enough before loading from the db
-        let (code, gas_cost) = self.evm_api().account_code(address, gas);
+        let (code, gas_cost) = self.evm_api().account_code(arbos_version, address, gas);
         self.buy_gas(gas_cost)?;
 
         let code = code.slice();
```

### arbitrator/wasm-libraries/user-test/src/program.rs
```diff
@@ -196,7 +196,7 @@ impl EvmApi<VecReader> for MockEvmApi {
         unimplemented!()
     }
 
-    fn account_code(&mut self, _address: Bytes20, _gas_left: Gas) -> (VecReader, Gas) {
+    fn account_code(&mut self, _arbos_version: u64, _address: Bytes20, _gas_left: Gas) -> (VecReader, Gas) {
         unimplemented!()
     }
 
```

### timeboost/errors.go
```diff
@@ -13,8 +13,8 @@ var (
 	ErrNoOnchainController      = errors.New("NO_ONCHAIN_CONTROLLER")
 	ErrWrongAuctionContract     = errors.New("WRONG_AUCTION_CONTRACT")
 	ErrNotExpressLaneController = errors.New("NOT_EXPRESS_LANE_CONTROLLER")
-	ErrDuplicateSequenceNumber  = errors.New("SUBMISSION_NONCE_ALREADY_SEEN")
-	ErrSequenceNumberTooLow     = errors.New("SUBMISSION_NONCE_TOO_LOW")
+	ErrDuplicateSequenceNumber  = errors.New("SEQUENCE_NUMBER_ALREADY_SEEN")
+	ErrSequenceNumberTooLow     = errors.New("SEQUENCE_NUMBER_TOO_LOW")
 	ErrTooManyBids              = errors.New("PER_ROUND_BID_LIMIT_REACHED")
 	ErrAcceptedTxFailed         = errors.New("Accepted timeboost tx failed")
 )
```
