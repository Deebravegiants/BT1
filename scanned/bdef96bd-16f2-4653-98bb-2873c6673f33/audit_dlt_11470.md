# [?] Prevent overflow in fee amount computation (#1568)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2021-11-17
Source: https://github.com/informalsystems/hermes/commit/8918c22c1014256bd00cf34faac5cdb3cdaf19c7
Type: security-commit

## Details
Prevent overflow in fee amount computation (#1568)

Prevent a potential overflow when computing the fee for a tx to be sent to a chain which uses a denomination which high decimal places.

This is done by using infinite precision integers and rationals in the `mul_ceil` function. The resulting `BigInt` is then formatted as a string in the `Fee` proto.

Because the computation is now done will full precision, and because some decimal numbers cannot be represented precisely as a 64-bit IEEE-754 floating point number, the result of the computation may sometime change, eg. be rounded up to the next integer. This should not be a problem as the gas and fee computations are not fully precise anyway, given that they rely on the simulated gas.

---

* Fix clippy warning

* Compute fee amount using `BigInt`

* Propagate new signature of `mul_ceil` and check for overflow

* Add config validation step for `gas_adjustment`

* Add changelog entry

* Fix warning

* Fix unit tests

* Add unit test to demonstrate that the previous behavior would overflow when given high gas and price

* Fix typo in comment

* Turn debug assertions into normal ones

## Patch
### .changelog/unreleased/improvements/ibc-relayer-cli/1555-fee-amount-overflow.md
```diff
@@ -0,0 +1,3 @@
+- Compute fee amount using big integers to prevent overflow
+  when using denominations with high decimal places
+  ([#1555](https://github.com/informalsystems/ibc-rs/issues/1555))
\ No newline at end of file
```

### Cargo.lock
```diff
@@ -816,15 +816,6 @@ dependencies = [
  "percent-encoding",
 ]
 
-[[package]]
-name = "fraction"
-version = "0.9.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "aba3510011eee8825018be07f08d9643421de007eaf62a3bde58d89b058abfa7"
-dependencies = [
- "num",
-]
-
 [[package]]
 name = "funty"
 version = "1.1.0"
@@ -1340,7 +1331,6 @@ dependencies = [
  "dirs-next",
  "env_logger",
  "flex-error",
- "fraction",
  "futures",
  "hdpath",
  "hex",
@@ -1352,6 +1342,8 @@ dependencies = [
  "ibc-telemetry",
  "itertools",
  "k256",
+ "num-bigint",
+ "num-rational",
  "prost",
  "prost-types",
  "retry",
@@ -1764,26 +1756,15 @@ dependencies = [
 ]
 
 [[package]]
-name = "num"
-version = "0.2.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b8536030f9fea7127f841b45bb6243b27255787fb4eb83958aa1ef9d2fdc0c36"
-dependencies = [
- "num-complex",
- "num-integer",
- "num-iter",
- "num-rational",
- "num-traits",
-]
-
-[[package]]
-name = "num-complex"
-version = "0.2.4"
+name = "num-bigint"
+version = "0.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b6b19411a9719e753aff12e5187b74d60d3dc449ec3f4dc21e3989c3f554bc95"
+checksum = "f93ab6289c7b344a8a9f60f88d80aa20032336fe78da341afc91c8a2341fc75f"
 dependencies = [
  "autocfg",
+ "num-integer",
  "num-traits",
+ "serde",
 ]
 
 [[package]]
@@ -1807,26 +1788,17 @@ dependencies = [
  "num-traits",
 ]
 
-[[package]]
-name = "num-iter"
-version = "0.1.42"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b2021c8337a54d21aca0d59a92577a029af9431cb59b909b03252b9c164fad59"
-dependencies = [
- "autocfg",
- "num-integer",
- "num-traits",
-]
-
 [[package]]
 name = "num-rational"
-version = "0.2.4"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c000134b5dbf44adc5cb772486d335293351644b801551abe8f75c84cfa4aef"
+checksum = "d41702bd167c2df5520b384281bc111a4b5efcf7fbc4c9c222c815b07e0a6a6a"
 dependencies = [
  "autocfg",
+ "num-bigint",
  "num-integer",
  "num-traits",
+ "serde",
 ]
 
 [[package]]
```

### config.toml
```diff
@@ -151,9 +151,10 @@ max_gas = 300000
 # the denomination of the fee. Required
 gas_price = { price = 0.001, denom = 'stake' }
 
-# Specify by ratio to increase the gas estimate used to compute the fee,
+# Specify the ratio by which to increase the gas estimate used to compute the fee,
 # to account for potential estimation error. Default: 0.1, ie. 10%.
-gas_adjustment = 0.1
+# Valid range: 0.0 to 1.0 (inclusive)
+gas_adjustment = 1.0
 
 # Specify how many IBC messages at most to include in a single transaction.
 # Default: 30
```

### relayer-cli/src/config.rs
```diff
@@ -57,9 +57,20 @@ define_error! {
                 reason: String
             }
             |e| {
-                format!("config file specifies an invalid trust threshold ({0}) for the chain with id {1}, caused by: {2}",
+                format!("config file specifies an invalid `trust_threshold` ({0}) for the chain with id {1}, caused by: {2}",
                     e.threshold, e.chain_id, e.reason)
             },
+
+        InvalidGasAdjustment
+            {
+                gas_adjustment: f64,
+                chain_id: ChainId,
+                reason: String
+            }
+            |e| {
+                format!("config file specifies an invalid `gas_adjustment` ({0}) for the chain with id {1}, caused by: {2}",
+                    e.gas_adjustment, e.chain_id, e.reason)
+            },
     }
 }
 
@@ -80,6 +91,9 @@ pub fn validate_config(config: &Config) -> Result<(), Diagnostic<Error>> {
         }
 
         validate_trust_threshold(&c.id, c.trust_threshold)?;
+
+        // Validate gas-related settings
+        validate_gas_settings(&c.id, c.gas_adjustment)?;
     }
 
     // Check for invalid mode config
@@ -139,3 +153,19 @@ fn validate_trust_threshold(
 
     Ok(())
 }
+
+fn validate_gas_settings(
+    id: &ChainId,
+    gas_adjustment: Option<f64>,
+) -> Result<(), Diagnostic<Error>> {
+    match gas_adjustment {
+        Some(gas_adjustment) if !(0.0..=1.0).contains(&gas_adjustment) => {
+            Err(Diagnostic::Error(Error::invalid_gas_adjustment(
+                gas_adjustment,
+                id.clone(),
+                "gas adjustment must be between 0.0 and 1.0 inclusive".to_string(),
+            )))
+        }
+        _ => Ok(()),
+    }
+}
```

### relayer/Cargo.toml
```diff
@@ -60,11 +60,18 @@ http = "0.2.4"
 flex-error = { version = "0.4.4", default-features = false }
 signature = "1.3.0"
 anyhow = "1.0.45"
-fraction = { version = "0.9.0", default-features = false }
 semver = "1.0"
 uint = "0.9"
 humantime = "2.1.0"
 
+[dependencies.num-bigint]
+version = "0.4"
+features = ["serde"]
+
+[dependencies.num-rational]
+version = "0.4.0"
+features = ["num-bigint", "serde"]
+
 [dependencies.tendermint]
 version = "=0.23.0"
 features = ["secp256k1"]
```

### relayer/src/chain/cosmos.rs
```diff
@@ -6,6 +6,8 @@ use core::{
     str::FromStr,
     time::Duration,
 };
+use num_bigint::BigInt;
+use num_rational::BigRational;
 use std::{fmt, thread, time::Instant};
 
 use bech32::{ToBase32, Variant};
@@ -189,9 +191,10 @@ impl CosmosSdkChain {
             })?;
 
         let max_bound = result.consensus_params.block.max_bytes;
-        let max_allowed = mul_ceil(max_bound, GENESIS_MAX_BYTES_MAX_FRACTION) as usize;
+        let max_allowed = mul_ceil(max_bound, GENESIS_MAX_BYTES_MAX_FRACTION);
+        let max_tx_size = BigInt::from(self.max_tx_size());
 
-        if self.max_tx_size() > max_allowed {
+        if max_tx_size > max_allowed {
             return Err(Error::config_validation_tx_size_out_of_bounds(
                 self.id().clone(),
                 self.max_tx_size(),
@@ -449,10 +452,15 @@ impl CosmosSdkChain {
     /// The actual gas cost, when a transaction is executed, may be slightly higher than the
     /// one returned by the simulation.
     fn apply_adjustment_to_gas(&self, gas_amount: u64) -> u64 {
-        min(
-            gas_amount + mul_ceil(gas_amount, self.gas_adjustment()),
-            self.max_gas(),
-        )
+        assert!(self.gas_adjustment() <= 1.0);
+
+        let (_, digits) = mul_ceil(gas_amount, self.gas_adjustment()).to_u64_digits();
+        assert!(digits.len() == 1);
+
+        let adjustment = digits[0];
+        let gas = gas_amount.checked_add(adjustment).unwrap_or(u64::MAX);
+
+        min(gas, self.max_gas())
     }
 
     /// The maximum fee the relayer pays for a transaction
@@ -2007,8 +2015,7 @@ fn packet_from_tx_search_response(
         .tx_result
         .events
         .into_iter()
-        .filter_map(|ev| filter_matching_event(ev, request, seq))
-        .next()
+        .find_map(|ev| filter_matching_event(ev, request, seq))
 }
 
 // Extracts from the Tx the update client event for the requested client and height.
@@ -2379,14 +2386,13 @@ fn calculate_fee(adjusted_gas_amount: u64, gas_price: &GasPrice) -> Coin {
     }
 }
 
-/// Multiply `a` with `f` and round to result up to the nearest integer.
-fn mul_ceil(a: u64, f: f64) -> u64 {
-    use fraction::Fraction as F;
+/// Multiply `a` with `f` and round the result up to the nearest integer.
+fn mul_ceil(a: u64, f: f64) -> BigInt {
+    assert!(f.is_finite());
 
-    // Safe to unwrap below as are multiplying two finite fractions
-    // together, and rounding them to the nearest integer.
-    let n = (F::from(a) * F::from(f)).ceil();
-    n.numer().unwrap() / n.denom().unwrap()
+    let a = BigInt::from(a);
+    let f = BigRational::from_float(f).expect("f is finite");
+    (f * a).ceil().to_integer()
 }
 
 /// Compute the `max_clock_drift` for a (new) client state
@@ -2416,17 +2422,45 @@ mod tests {
         Height,
     };
 
-    use crate::chain::cosmos::client_id_suffix;
+    use crate::{chain::cosmos::client_id_suffix, config::GasPrice};
+
+    use super::calculate_fee;
 
     #[test]
     fn mul_ceil() {
-        assert_eq!(super::mul_ceil(300_000, 0.001), 300);
-        assert_eq!(super::mul_ceil(300_004, 0.001), 301);
-        assert_eq!(super::mul_ceil(300_040, 0.001), 301);
-        assert_eq!(super::mul_ceil(300_400, 0.001), 301);
-        assert_eq!(super::mul_ceil(304_000, 0.001), 304);
-        assert_eq!(super::mul_ceil(340_000, 0.001), 340);
-        assert_eq!(super::mul_ceil(340_001, 0.001), 341);
+        // Because 0.001 cannot be expressed precisely
+        // as a 64-bit floating point number (it is
+        // stored as 0.001000000047497451305389404296875),
+        // `num_rational::BigRational` will represent it as
+        // 1152921504606847/1152921504606846976 instead
+        // which will sometimes round up to the next
+        // integer in the computations below.
+        // This is not a problem for the way we compute the fee
+        // and gas adjustment as those are already based on simulated
+        // gas which is not 100% precise.
+        assert_eq!(super::mul_ceil(300_000, 0.001), 301.into());
+        assert_eq!(super::mul_ceil(300_004, 0.001), 301.into());
+        assert_eq!(super::mul_ceil(300_040, 0.001), 301.into());
+        assert_eq!(super::mul_ceil(300_400, 0.001), 301.into());
+        assert_eq!(super::mul_ceil(304_000, 0.001), 305.into());
+        assert_eq!(super::mul_ceil(340_000, 0.001), 341.into());
+        assert_eq!(super::mul_ceil(340_001, 0.001), 341.into());
+    }
+
+    /// Before https://github.com/informalsystems/ibc-rs/pull/1568,
+    /// this test would have panic'ed with:
+    ///
+    /// thread 'chain::cosmos::tests::fee_overflow' panicked at 'attempt to multiply with overflow'
+    #[test]
+    fn fee_overflow() {
+        let gas_amount = 90000000000000_u64;
+        let gas_price = GasPrice {
+            price: 1000000000000.0,
+            denom: "uatom".to_string(),
+        };
+
+        let fee = calculate_fee(gas_amount, &gas_price);
+        assert_eq!(&fee.amount, "90000000000000000000000000");
     }
 
     #[test]
```
