# [?] bug: fix algorithm overflow issues (#2173)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-09-11
Source: https://github.com/FuelLabs/fuel-core/commit/f308bae9c9c784860b7d82ef0d71a695f862065e
Type: security-commit

## Details
bug: fix algorithm overflow issues (#2173)

## Linked Issues/PRs
Closes https://github.com/FuelLabs/fuel-core/issues/2164
Closes https://github.com/FuelLabs/fuel-core/issues/2147

## Description
The main change with this code is "normalizaing" the costs and rewards
instead of keeping a total over all time. i.e. every time we receive a
DA block, we see if the reward is greater than the costs, or vice versa.
If the reward is higher, we set the reward to the difference and set the
the last known cost to `0` and adjust the projected cost accordingly.

In addition, we were using a random set of types for the algorithm and
also used casts in many places. This PR should fix a lot of those
problems.

Bonus: This fix prompted me to run the optimization again. Since the set
is much bigger now, I decided to enable running the simulation in
parallel tasks to speed up the code.

## Checklist
- [x] New behavior is reflected in tests

### Before requesting review
- [x] I have reviewed the code myself

---------

Co-authored-by: green <xgreenx9999@gmail.com>
Co-authored-by: Aaryamann Challani <43716372+rymnc@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -3812,6 +3812,7 @@ name = "fuel-gas-price-algorithm"
 version = "0.35.0"
 dependencies = [
  "proptest",
+ "rand",
  "serde",
  "thiserror",
 ]
```

### crates/fuel-gas-price-algorithm/Cargo.toml
```diff
@@ -15,6 +15,9 @@ name = "fuel_gas_price_algorithm"
 path = "src/lib.rs"
 
 [dependencies]
-proptest = { workspace = true }
 serde = { workspace = true, features = ["derive"] }
 thiserror = { workspace = true }
+
+[dev-dependencies]
+proptest = { workspace = true }
+rand = { workspace = true }
```

### crates/fuel-gas-price-algorithm/gas-price-analysis/Cargo.toml
```diff
@@ -11,7 +11,9 @@ anyhow = "1.0.86"
 clap = { version = "4.5.16", features = ["derive"] }
 csv = "1.3.0"
 fuel-gas-price-algorithm = { path = ".." }
+futures = "0.3.30"
 plotters = "0.3.5"
 rand = "0.8.5"
 rand_distr = "0.4.3"
 serde = { version = "1.0.209", features = ["derive"] }
+tokio = { version = "1.40.0", features = ["macros", "rt", "rt-multi-thread"] }
```

### crates/fuel-gas-price-algorithm/gas-price-analysis/src/main.rs
```diff
@@ -74,7 +74,8 @@ enum Source {
     },
 }
 
-fn main() -> anyhow::Result<()> {
+#[tokio::main]
+async fn main() -> anyhow::Result<()> {
     let args = Arg::parse();
 
     const UPDATE_PERIOD: usize = 12;
@@ -103,7 +104,7 @@ fn main() -> anyhow::Result<()> {
             );
             let simulator = Simulator::new(da_cost_per_byte);
             let (results, (p, d)) =
-                naive_optimisation(&simulator, iterations as usize, UPDATE_PERIOD);
+                naive_optimisation(&simulator, iterations as usize, UPDATE_PERIOD).await;
             println!(
                 "Optimization results: P: {}, D: {}",
                 prettify_number(p),
```

### crates/fuel-gas-price-algorithm/gas-price-analysis/src/optimisation.rs
```diff
@@ -1,4 +1,5 @@
 use super::*;
+use futures::future::join_all;
 
 fn da_pid_factors(size: usize) -> Vec<(i64, i64)> {
     let mut rng = StdRng::seed_from_u64(10902);
@@ -11,19 +12,28 @@ fn da_pid_factors(size: usize) -> Vec<(i64, i64)> {
         .collect()
 }
 
-pub fn naive_optimisation(
+pub async fn naive_optimisation(
     simulator: &Simulator,
     iterations: usize,
     da_recording_rate: usize,
 ) -> (SimulationResults, (i64, i64)) {
-    da_pid_factors(iterations)
-        .iter()
+    let tasks = da_pid_factors(iterations)
+        .into_iter()
         .map(|(p, d)| {
-            (
-                simulator.run_simulation(*p, *d, da_recording_rate),
-                (*p, *d),
-            )
+            let new_simulator = simulator.clone();
+            let f = move || {
+                (
+                    new_simulator.run_simulation(p, d, da_recording_rate),
+                    (p, d),
+                )
+            };
+            tokio::task::spawn_blocking(f)
         })
+        .collect::<Vec<_>>();
+    join_all(tasks)
+        .await
+        .into_iter()
+        .map(Result::unwrap)
         .min_by_key(|(results, _)| {
             let SimulationResults { actual_profit, .. } = results;
             let err = actual_profit.iter().map(|p| p.abs()).sum::<i128>();
```

### crates/fuel-gas-price-algorithm/gas-price-analysis/src/simulation.rs
```diff
@@ -2,15 +2,7 @@ use fuel_gas_price_algorithm::v1::{
     AlgorithmUpdaterV1,
     RecordedBlock,
 };
-use std::{
-    iter,
-    iter::{
-        Enumerate,
-        Zip,
-    },
-    num::NonZeroU64,
-    slice::Iter,
-};
+use std::num::NonZeroU64;
 
 use super::*;
 
@@ -27,6 +19,7 @@ pub struct SimulationResults {
     pub pessimistic_costs: Vec<u128>,
 }
 
+#[derive(Clone, Debug)]
 pub struct Simulator {
     da_cost_per_byte: Vec<u64>,
 }
@@ -82,17 +75,17 @@ impl Simulator {
             gas_price_factor: NonZeroU64::new(gas_price_factor).unwrap(),
             l2_block_height: 0,
             // Choose the ideal fullness percentage for the L2 block
-            l2_block_fullness_threshold_percent: 50,
+            l2_block_fullness_threshold_percent: 50u8.into(),
             // Increase to make the exec price change faster
             exec_gas_price_change_percent: 2,
             // Increase to make the da price change faster
             max_da_gas_price_change_percent: 10,
-            total_da_rewards: 0,
+            total_da_rewards_excess: 0,
             da_recorded_block_height: 0,
             // Change to adjust the cost per byte of the DA on block 0
             latest_da_cost_per_byte: 0,
             projected_total_da_cost: 0,
-            latest_known_total_da_cost: 0,
+            latest_known_total_da_cost_excess: 0,
             unrecorded_blocks: vec![],
             da_p_component,
             da_d_component,
@@ -123,18 +116,6 @@ impl Simulator {
             exec_gas_prices.push(updater.new_scaled_exec_price);
             let gas_price = updater.algorithm().calculate(max_block_bytes);
             gas_prices.push(gas_price);
-            // Update DA blocks on the occasion there is one
-
-            if let Some(mut da_blocks) = da_block.clone() {
-                let mut total_costs = updater.latest_known_total_da_cost;
-                for block in &mut da_blocks {
-                    total_costs += block.block_cost as u128;
-                    actual_costs.push(total_costs);
-                }
-                updater.update_da_record_data(da_blocks.to_owned()).unwrap();
-                assert_eq!(total_costs, updater.projected_total_da_cost);
-                assert_eq!(total_costs, updater.latest_known_total_da_cost);
-            }
             updater
                 .update_l2_block_data(
                     height,
@@ -147,17 +128,26 @@ impl Simulator {
             da_gas_prices.push(updater.last_da_gas_price);
             pessimistic_costs
                 .push(max_block_bytes as u128 * updater.latest_da_cost_per_byte);
-            actual_reward_totals.push(updater.total_da_rewards);
+            actual_reward_totals.push(updater.total_da_rewards_excess);
             projected_cost_totals.push(updater.projected_total_da_cost);
-        }
 
+            // Update DA blocks on the occasion there is one
+            if let Some(da_blocks) = &da_block {
+                let mut total_cost = updater.latest_known_total_da_cost_excess;
+                for block in da_blocks {
+                    total_cost += block.block_cost as u128;
+                    actual_costs.push(total_cost);
+                }
+                updater.update_da_record_data(&da_blocks).unwrap();
+            }
+        }
         let (fullness_without_capacity, bytes): (Vec<_>, Vec<_>) =
             fullness_and_bytes.iter().cloned().unzip();
-        let fullness = fullness_without_capacity
+        let fullness: Vec<_> = fullness_without_capacity
             .iter()
             .map(|&fullness| (fullness, capacity))
             .collect();
-        let bytes_and_costs = bytes
+        let bytes_and_costs: Vec<_> = bytes
             .iter()
             .zip(self.da_cost_per_byte.iter())
             .map(|(bytes, cost_per_byte)| (*bytes, (*bytes * cost_per_byte) as u64))
```

### crates/fuel-gas-price-algorithm/gas-price-analysis/src/simulation/da_cost_per_byte.rs
```diff
@@ -25,6 +25,7 @@ pub fn get_da_cost_per_byte_from_source(
     }
 }
 
+#[allow(dead_code)]
 #[derive(Debug, serde::Deserialize)]
 struct Record {
     block_number: u64,
```

### crates/fuel-gas-price-algorithm/src/v1.rs
```diff
@@ -1,8 +1,5 @@
 use std::{
-    cmp::{
-        max,
-        min,
-    },
+    cmp::max,
     num::NonZeroU64,
 };
 
@@ -55,22 +52,23 @@ pub struct AlgorithmV1 {
     new_exec_price: u64,
     /// The gas price for the DA portion of the last block. This can be used to calculate
     last_da_price: u64,
-    /// The maximum percentage that the DA portion of the gas price can change in a single block
-    max_change_percent: u8,
+    /// The maximum percentage that the DA portion of the gas price can change in a single block.
+    ///   Using `u16` because it can go above 100% and possibly over 255%
+    max_change_percent: u16,
     /// The latest known cost per byte for recording blocks on the DA chain
     latest_da_cost_per_byte: u128,
     /// The cumulative reward from the DA portion of the gas price
-    total_rewards: u64,
+    total_rewards: u128,
     /// The cumulative cost of recording L2 blocks on the DA chain as of the last recorded block
     total_costs: u128,
     /// The P component of the PID control for the DA gas price
     da_p_factor: i64,
     /// The D component of the PID control for the DA gas price
     da_d_factor: i64,
     /// The average profit over the last `avg_window` blocks
-    last_profit: i64,
+    last_profit: i128,
     /// the previous profit
-    second_to_last_profit: i64,
+    second_to_last_profit: i128,
 }
 
 impl AlgorithmV1 {
@@ -82,36 +80,41 @@ impl AlgorithmV1 {
         self.assemble_price(da_change)
     }
 
-    fn p(&self) -> i64 {
-        let checked_p = self.last_profit.checked_div(self.da_p_factor);
+    fn p(&self) -> i128 {
+        let upcast_p: i128 = self.da_p_factor.into();
+        let checked_p = self.last_profit.checked_div(upcast_p);
         // If the profit is positive, we want to decrease the gas price
         checked_p.unwrap_or(0).saturating_mul(-1)
     }
 
-    fn d(&self) -> i64 {
+    fn d(&self) -> i128 {
+        let upcast_d: i128 = self.da_d_factor.into();
         let slope = self.last_profit.saturating_sub(self.second_to_last_profit);
-        let checked_d = slope.checked_div(self.da_d_factor);
+        let checked_d = slope.checked_div(upcast_d);
         // if the slope is positive, we want to decrease the gas price
         checked_d.unwrap_or(0).saturating_mul(-1)
     }
 
-    fn change(&self, p: i64, d: i64) -> i64 {
+    fn change(&self, p: i128, d: i128) -> i128 {
         let pd_change = p.saturating_add(d);
+        let upcast_percent = self.max_change_percent.into();
         let max_change = self
             .last_da_price
-            .saturating_mul(self.max_change_percent as u64)
-            .saturating_div(100) as i64;
-        let sign = pd_change.signum();
-        let signless_da_change = min(max_change, pd_change.abs());
-        sign.saturating_mul(signless_da_change)
+            .saturating_mul(upcast_percent)
+            .saturating_div(100)
+            .into();
+        let clamped_change = pd_change.abs().min(max_change);
+        pd_change.signum().saturating_mul(clamped_change)
     }
 
-    fn assemble_price(&self, change: i64) -> u64 {
-        let last_da_gas_price = self.last_da_price as i128;
-        let maybe_new_da_gas_price = last_da_gas_price
-            .saturating_add(change as i128)
+    fn assemble_price(&self, change: i128) -> u64 {
+        let upcast_last_da_price: i128 = self.last_da_price.into();
+        let new_price_oversized = upcast_last_da_price.saturating_add(change);
+
+        let maybe_new_da_gas_price: u64 = new_price_oversized
             .try_into()
-            .unwrap_or(self.min_da_gas_price);
+            .unwrap_or(if change.is_positive() { u64::MAX } else { 0 });
+
         let new_da_gas_price = max(self.min_da_gas_price, maybe_new_da_gas_price);
         self.new_exec_price.saturating_add(new_da_gas_price)
     }
@@ -135,13 +138,14 @@ pub struct AlgorithmUpdaterV1 {
     /// The lowest the algorithm allows the exec gas price to go
     pub min_exec_gas_price: u64,
     /// The Percentage the execution gas price will change in a single block, either increase or decrease
-    /// based on the fullness of the last L2 block
-    pub exec_gas_price_change_percent: u64,
+    /// based on the fullness of the last L2 block. Using `u16` because it can go above 100% and
+    /// possibly over 255%
+    pub exec_gas_price_change_percent: u16,
     /// The height of the next L2 block
     pub l2_block_height: u32,
     /// The threshold of gas usage above and below which the gas price will increase or decrease
     /// This is a percentage of the total capacity of the L2 block
-    pub l2_block_fullness_threshold_percent: u64,
+    pub l2_block_fullness_threshold_percent: ClampedPercentage,
     // DA
     /// The gas price for the DA portion of the last block. This can be used to calculate
     /// the DA portion of the next block
@@ -151,13 +155,14 @@ pub struct AlgorithmUpdaterV1 {
     /// The lowest the algorithm allows the da gas price to go
     pub min_da_gas_price: u64,
     /// The maximum percentage that the DA portion of the gas price can change in a single block
-    pub max_da_gas_price_change_percent: u8,
+    ///   Using `u16` because it can go above 100% and possibly over 255%
+    pub max_da_gas_price_change_percent: u16,
     /// The cumulative reward from the DA portion of the gas price
-    pub total_da_rewards: u64,
+    pub total_da_rewards_excess: u128,
     /// The height of the las L2 block recorded on the DA chain
     pub da_recorded_block_height: u32,
     /// The cumulative cost of recording L2 blocks on the DA chain as of the last recorded block
-    pub latest_known_total_da_cost: u128,
+    pub latest_known_total_da_cost_excess: u128,
     /// The predicted cost of recording L2 blocks on the DA chain as of the last L2 block
     /// (This value is added on top of the `latest_known_total_da_cost` if the L2 height is higher)
     pub projected_total_da_cost: u128,
@@ -166,15 +171,43 @@ pub struct AlgorithmUpdaterV1 {
     /// The D component of the PID control for the DA gas price
     pub da_d_component: i64,
     /// The last profit
-    pub last_profit: i64,
+    pub last_profit: i128,
     /// The profit before last
-    pub second_to_last_profit: i64,
+    pub second_to_last_profit: i128,
     /// The latest known cost per byte for recording blocks on the DA chain
     pub latest_da_cost_per_byte: u128,
     /// The unrecorded blocks that are used to calculate the projected cost of recording blocks
     pub unrecorded_blocks: Vec<BlockBytes>,
 }
 
+/// A value that represents a value between 0 and 100. Higher values are clamped to 100
+#[derive(serde::Serialize, serde::Deserialize, Debug, Clone, PartialEq)]
+pub struct ClampedPercentage {
+    value: u8,
+}
+
+impl ClampedPercentage {
+    pub fn new(maybe_value: u8) -> Self {
+        Self {
+            value: maybe_value.min(100),
+        }
+    }
+}
+
+impl From<u8> for ClampedPercentage {
+    fn from(value: u8) -> Self {
+        Self::new(value)
+    }
+}
+
+impl core::ops::Deref for ClampedPercentage {
+    type Target = u8;
+
+    fn deref(&self) -> &Self::Target {
+        &self.value
+    }
+}
+
 #[derive(Debug, Clone)]
 pub struct RecordedBlock {
     pub height: u32,
@@ -191,12 +224,13 @@ pub struct BlockBytes {
 impl AlgorithmUpdaterV1 {
     pub fn update_da_record_data(
         &mut self,
-        blocks: Vec<RecordedBlock>,
+        blocks: &[RecordedBlock],
     ) -> Result<(), Error> {
         for block in blocks {
             self.da_block_update(block.height, block.block_bytes, block.block_cost)?;
         }
         self.recalculate_projected_cost();
+        self.normalize_rewards_and_costs();
         Ok(())
     }
 
@@ -222,15 +256,15 @@ impl AlgorithmUpdaterV1 {
                 .new_scaled_exec_price
                 .saturating_div(self.gas_price_factor.into());
             // TODO: fix this nonsense when we fix the types https://github.com/FuelLabs/fuel-core/issues/2147
-            let projected_total_da_cost = i64::try_from(self.projected_total_da_cost)
+            let projected_total_da_cost = i128::try_from(self.projected_total_da_cost)
                 .map_err(|_| {
                     Error::FailedTooIncludeL2BlockData(format!(
                         "Converting {:?} to an i64 from u256",
                         self.projected_total_da_cost
                     ))
                 })?;
-            let last_profit =
-                (self.total_da_rewards as i64).saturating_sub(projected_total_da_cost);
+            let rewards = self.total_da_rewards_excess.try_into().unwrap_or(i128::MAX);
+            let last_profit = rewards.saturating_sub(projected_total_da_cost);
             self.update_last_profit(last_profit);
             let block_projected_da_cost =
                 (block_bytes as u128).saturating_mul(self.latest_da_cost_per_byte);
@@ -241,24 +275,27 @@ impl AlgorithmUpdaterV1 {
             self.last_da_gas_price = gas_price.saturating_sub(last_exec_price);
             self.update_exec_gas_price(used, capacity);
             let block_da_reward = used.saturating_mul(self.last_da_gas_price);
-            self.total_da_rewards = self.total_da_rewards.saturating_add(block_da_reward);
+            self.total_da_rewards_excess = self
+                .total_da_rewards_excess
+                .saturating_add(block_da_reward.into());
             Ok(())
         }
     }
 
-    fn update_last_profit(&mut self, new_profit: i64) {
+    fn update_last_profit(&mut self, new_profit: i128) {
         self.second_to_last_profit = self.last_profit;
         self.last_profit = new_profit;
     }
 
     fn update_exec_gas_price(&mut self, used: u64, capacity: NonZeroU64) {
+        let threshold = *self.l2_block_fullness_threshold_percent as u64;
         let mut exec_gas_price = self.new_scaled_exec_price;
         let fullness_percent = used
             .saturating_mul(100)
             .checked_div(capacity.into())
-            .unwrap_or(self.l2_block_fullness_threshold_percent);
+            .unwrap_or(threshold);
 
-        match fullness_percent.cmp(&self.l2_block_fullness_threshold_percent) {
+        match fullness_percent.cmp(&threshold) {
             std::cmp::Ordering::Greater => {
                 let change_amount = self.change_amount(exec_gas_price);
                 exec_gas_price = exec_gas_price.saturating_add(change_amount);
@@ -274,7 +311,7 @@ impl AlgorithmUpdaterV1 {
 
     fn change_amount(&self, principle: u64) -> u64 {
         principle
-            .saturating_mul(self.exec_gas_price_change_percent)
+            .saturating_mul(self.exec_gas_price_change_percent as u64)
             .saturating_div(100)
     }
 
@@ -299,9 +336,9 @@ impl AlgorithmUpdaterV1 {
                 })?;
             self.da_recorded_block_height = height;
             let new_block_cost = self
-                .latest_known_total_da_cost
+                .latest_known_total_da_cost_excess
                 .saturating_add(block_cost as u128);
-            self.latest_known_total_da_cost = new_block_cost;
+            self.latest_known_total_da_cost_excess = new_block_cost;
             self.latest_da_cost_per_byte = new_cost_per_byte;
             Ok(())
         }
@@ -320,7 +357,7 @@ impl AlgorithmUpdaterV1 {
             })
             .sum();
         self.projected_total_da_cost = self
-            .latest_known_total_da_cost
+            .latest_known_total_da_cost_excess
             .saturating_add(projection_portion);
     }
 
@@ -336,12 +373,42 @@ impl AlgorithmUpdaterV1 {
             max_change_percent: self.max_da_gas_price_change_percent,
 
             latest_da_cost_per_byte: self.latest_da_cost_per_byte,
-            total_rewards: self.total_da_rewards,
+            total_rewards: self.total_da_rewards_excess,
             total_costs: self.projected_total_da_cost,
             last_profit: self.last_profit,
             second_to_last_profit: self.second_to_last_profit,
             da_p_factor: self.da_p_component,
             da_d_factor: self.da_d_component,
         }
     }
+
+    // We only need to track the difference between the rewards and costs after we have true DA data
+    // Normalize, or zero out the lower value and subtract it from the higher value
+    fn normalize_rewards_and_costs(&mut self) {
+        let (excess, projected_cost_excess) =
+            if self.total_da_rewards_excess > self.latest_known_total_da_cost_excess {
+                (
+                    self.total_da_rewards_excess
+                        .saturating_sub(self.latest_known_total_da_cost_excess),
+                    self.projected_total_da_cost
+                        .saturating_sub(self.latest_known_total_da_cost_excess),
+                )
+            } else {
+                (
+                    self.latest_known_total_da_cost_excess
+                        .saturating_sub(self.total_da_rewards_excess),
+                    self.projected_total_da_cost
+                        .saturating_sub(self.total_da_rewards_excess),
+                )
+            };
+
+        self.projected_total_da_cost = projected_cost_excess;
+        if self.total_da_rewards_excess > self.latest_known_total_da_cost_excess {
+            self.total_da_rewards_excess = excess;
+            self.latest_known_total_da_cost_excess = 0;
+        } else {
+            self.total_da_rewards_excess = 0;
+            self.latest_known_total_da_cost_excess = excess;
+        }
+    }
 }
```

### crates/fuel-gas-price-algorithm/src/v1/tests.rs
```diff
@@ -19,23 +19,23 @@ pub struct UpdaterBuilder {
     min_da_gas_price: u64,
     starting_exec_gas_price: u64,
     starting_da_gas_price: u64,
-    exec_gas_price_change_percent: u64,
-    max_change_percent: u8,
+    exec_gas_price_change_percent: u16,
+    max_change_percent: u16,
 
     da_p_component: i64,
     da_d_component: i64,
 
     l2_block_height: u32,
-    l2_block_capacity_threshold: u64,
+    l2_block_capacity_threshold: u8,
 
-    total_rewards: u64,
+    total_rewards: u128,
     da_recorded_block_height: u32,
     da_cost_per_byte: u128,
     project_total_cost: u128,
     latest_known_total_cost: u128,
     unrecorded_blocks: Vec<BlockBytes>,
-    last_profit: i64,
-    second_to_last_profit: i64,
+    last_profit: i128,
+    second_to_last_profit: i128,
     da_gas_price_factor: u64,
 }
 
@@ -47,7 +47,7 @@ impl UpdaterBuilder {
             starting_exec_gas_price: 0,
             starting_da_gas_price: 0,
             exec_gas_price_change_percent: 0,
-            max_change_percent: u8::MAX,
+            max_change_percent: u16::MAX,
 
             da_p_component: 0,
             da_d_component: 0,
@@ -87,12 +87,12 @@ impl UpdaterBuilder {
         self
     }
 
-    fn with_exec_gas_price_change_percent(mut self, percent: u64) -> Self {
+    fn with_exec_gas_price_change_percent(mut self, percent: u16) -> Self {
         self.exec_gas_price_change_percent = percent;
         self
     }
 
-    fn with_da_max_change_percent(mut self, max_change_percent: u8) -> Self {
+    fn with_da_max_change_percent(mut self, max_change_percent: u16) -> Self {
         self.max_change_percent = max_change_percent;
         self
     }
@@ -114,13 +114,13 @@ impl UpdaterBuilder {
 
     fn with_l2_block_capacity_threshold(
         mut self,
-        l2_block_capacity_threshold: u64,
+        l2_block_capacity_threshold: u8,
     ) -> Self {
         self.l2_block_capacity_threshold = l2_block_capacity_threshold;
         self
     }
 
-    fn with_total_rewards(mut self, total_rewards: u64) -> Self {
+    fn with_total_rewards(mut self, total_rewards: u128) -> Self {
         self.total_rewards = total_rewards;
         self
     }
@@ -150,7 +150,7 @@ impl UpdaterBuilder {
         self
     }
 
-    fn with_last_profit(mut self, last_profit: i64, last_last_profit: i64) -> Self {
+    fn with_last_profit(mut self, last_profit: i128, last_last_profit: i128) -> Self {
         self.last_profit = last_profit;
         self.second_to_last_profit = last_last_profit;
         self
@@ -168,13 +168,13 @@ impl UpdaterBuilder {
             da_d_component: self.da_d_component,
 
             l2_block_height: self.l2_block_height,
-            l2_block_fullness_threshold_percent: self.l2_block_capacity_threshold,
-            total_da_rewards: self.total_rewards,
+            l2_block_fullness_threshold_percent: self.l2_block_capacity_threshold.into(),
+            total_da_rewards_excess: self.total_rewards,
 
             da_recorded_block_height: self.da_recorded_block_height,
             latest_da_cost_per_byte: self.da_cost_per_byte,
             projected_total_da_cost: self.project_total_cost,
-            latest_known_total_da_cost: self.latest_known_total_cost,
+            latest_known_total_da_cost_excess: self.latest_known_total_cost,
             unrecorded_blocks: self.unrecorded_blocks,
             last_profit: self.last_profit,
             second_to_last_profit: self.second_to_last_profit,
```

### crates/fuel-gas-price-algorithm/src/v1/tests/algorithm_v1_tests.rs
```diff
@@ -8,13 +8,13 @@ fn calculate__even_profit_maintains_price() {
     let starting_cost = 500;
     let latest_gas_per_byte = 10;
     let da_gas_price_denominator = 1;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let starting_reward = starting_cost + block_bytes * latest_gas_per_byte;
     let updater = UpdaterBuilder::new()
         .with_starting_exec_gas_price(starting_exec_gas_price)
         .with_starting_da_gas_price(starting_da_gas_price)
         .with_da_p_component(da_gas_price_denominator)
-        .with_total_rewards(starting_reward)
+        .with_total_rewards(starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
@@ -38,7 +38,7 @@ fn calculate__negative_profit_increase_gas_price() {
     let latest_gas_per_byte = 10;
     let da_p_component = 100;
     let da_d_component = 10;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let last_profit = -100;
     let last_last_profit = 0;
     let arb_value = 1000;
@@ -49,7 +49,7 @@ fn calculate__negative_profit_increase_gas_price() {
         .with_starting_da_gas_price(last_da_gas_price)
         .with_da_p_component(da_p_component)
         .with_da_d_component(da_d_component)
-        .with_total_rewards(smaller_starting_reward)
+        .with_total_rewards(smaller_starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
@@ -61,11 +61,12 @@ fn calculate__negative_profit_increase_gas_price() {
     let actual = algo.calculate(block_bytes);
 
     // then
-    let da_p_comp = last_profit / da_p_component;
+    let da_p_comp = last_profit / da_p_component as i128;
     let slope = last_profit - last_last_profit;
-    let da_d_comp = slope / da_d_component;
-    let expected =
-        starting_exec_gas_price as i64 + last_da_gas_price as i64 - da_p_comp - da_d_comp;
+    let da_d_comp = slope / da_d_component as i128;
+    let expected = starting_exec_gas_price as i128 + last_da_gas_price as i128
+        - da_p_comp
+        - da_d_comp;
     assert_eq!(expected as u64, actual);
 }
 
@@ -78,7 +79,7 @@ fn calculate__positive_profit_decrease_gas_price() {
     let latest_gas_per_byte = 10;
     let da_p_component = 100;
     let da_d_component = 10;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let last_profit = 100;
     let last_last_profit = 0;
     let arb_value = 1000;
@@ -89,12 +90,12 @@ fn calculate__positive_profit_decrease_gas_price() {
         .with_da_p_component(da_p_component)
         .with_da_d_component(da_d_component)
         .with_starting_da_gas_price(last_da_gas_price)
-        .with_total_rewards(larger_starting_reward)
+        .with_total_rewards(larger_starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
         .with_last_profit(last_profit, last_last_profit)
-        .with_da_max_change_percent(u8::MAX)
+        .with_da_max_change_percent(u16::MAX)
         .with_exec_gas_price_change_percent(0)
         .build();
 
@@ -103,11 +104,12 @@ fn calculate__positive_profit_decrease_gas_price() {
     let actual = algo.calculate(block_bytes);
 
     // then
-    let da_p_comp = last_profit / da_p_component;
+    let da_p_comp = last_profit / da_p_component as i128;
     let slope = last_profit - last_last_profit;
-    let da_d_comp = slope / da_d_component;
-    let expected =
-        starting_exec_gas_price as i64 + last_da_gas_price as i64 - da_p_comp - da_d_comp;
+    let da_d_comp = slope / da_d_component as i128;
+    let expected = starting_exec_gas_price as i128 + last_da_gas_price as i128
+        - da_p_comp
+        - da_d_comp;
     assert_eq!(expected as u64, actual);
 }
 
@@ -120,7 +122,7 @@ fn calculate__price_does_not_decrease_more_than_max_percent() {
     let latest_gas_per_byte = 10;
     let da_p_component = 100;
     let da_d_component = 10;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let last_profit = 100000; // Large, positive profit to decrease da price
     let last_last_profit = 0;
     let max_change_percent = 5;
@@ -132,7 +134,7 @@ fn calculate__price_does_not_decrease_more_than_max_percent() {
         .with_da_p_component(da_p_component)
         .with_da_d_component(da_d_component)
         .with_starting_da_gas_price(last_da_gas_price)
-        .with_total_rewards(larger_starting_reward)
+        .with_total_rewards(larger_starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
@@ -159,7 +161,7 @@ fn calculate__da_price_does_not_increase_more_than_max_percent() {
     let latest_gas_per_byte = 10;
     let da_p_component = 1000;
     let da_d_component = 10;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let last_profit = -1000000; // large, negative profit to increase da price
     let last_last_profit = 0;
     let arb_value = 1000;
@@ -172,7 +174,7 @@ fn calculate__da_price_does_not_increase_more_than_max_percent() {
         .with_starting_da_gas_price(last_da_gas_price)
         .with_da_p_component(da_p_component)
         .with_da_d_component(da_d_component)
-        .with_total_rewards(smaller_starting_reward)
+        .with_total_rewards(smaller_starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
@@ -203,7 +205,7 @@ fn calculate__da_gas_price_never_drops_below_minimum() {
     let latest_gas_per_byte = 10;
     let da_p_component = 100;
     let da_d_component = 10;
-    let block_bytes = 500;
+    let block_bytes = 500u64;
     let profit_avg = 100;
     let avg_window = 10;
     let arb_value = 1000;
@@ -214,7 +216,7 @@ fn calculate__da_gas_price_never_drops_below_minimum() {
         .with_da_p_component(da_p_component)
         .with_da_d_component(da_d_component)
         .with_starting_da_gas_price(last_da_gas_price)
-        .with_total_rewards(larger_starting_reward)
+        .with_total_rewards(larger_starting_reward as u128)
         .with_known_total_cost(starting_cost as u128)
         .with_projected_total_cost(starting_cost as u128)
         .with_da_cost_per_byte(latest_gas_per_byte as u128)
```

### crates/fuel-gas-price-algorithm/src/v1/tests/update_da_record_data_tests.rs
```diff
@@ -4,6 +4,12 @@ use crate::v1::{
     Error,
     RecordedBlock,
 };
+use proptest::{
+    prelude::Rng,
+    prop_compose,
+    proptest,
+};
+use rand::SeedableRng;
 
 #[test]
 fn update_da_record_data__increases_block() {
@@ -27,7 +33,7 @@ fn update_da_record_data__increases_block() {
     ];
 
     // when
-    updater.update_da_record_data(blocks).unwrap();
+    updater.update_da_record_data(&blocks).unwrap();
 
     // then
     let expected = 2;
@@ -57,7 +63,7 @@ fn update_da_record_data__throws_error_if_out_of_order() {
     ];
 
     // when
-    let actual_error = updater.update_da_record_data(blocks).unwrap_err();
+    let actual_error = updater.update_da_record_data(&blocks).unwrap_err();
 
     // then
     let expected_error = Error::SkippedDABlock {
@@ -84,7 +90,7 @@ fn update_da_record_data__updates_cost_per_byte() {
         block_cost,
     }];
     // when
-    updater.update_da_record_data(blocks).unwrap();
+    updater.update_da_record_data(&blocks).unwrap();
 
     // then
     let expected = new_cost_per_byte as u128;
@@ -128,10 +134,10 @@ fn update_da_record_data__updates_known_total_cost() {
         },
     ];
     // when
-    updater.update_da_record_data(blocks).unwrap();
+    updater.update_da_record_data(&blocks).unwrap();
 
     // then
-    let actual = updater.latest_known_total_da_cost;
+    let actual = updater.latest_known_total_da_cost_excess;
     let expected = known_total_cost + (3 * block_cost as u128);
     assert_eq!(actual, expected);
 }
@@ -193,18 +199,19 @@ fn update_da_record_data__if_da_height_matches_l2_height_prjected_and_known_matc
         },
     ];
     // when
-    updater.update_da_record_data(blocks).unwrap();
+    updater.update_da_record_data(&blocks).unwrap();
 
     // then
     assert_eq!(updater.l2_block_height, updater.da_recorded_block_height);
     assert_eq!(
         updater.projected_total_da_cost,
-        updater.latest_known_total_da_cost
+        updater.latest_known_total_da_cost_excess
     );
 }
 
 #[test]
-fn update__da_block_updates_projected_total_cost_with_known_and_guesses_on_top() {
+fn update_da_record_data__da_block_updates_projected_total_cost_with_known_and_guesses_on_top(
+) {
     // given
     let da_cost_per_byte = 20;
     let da_recorded_block_height = 10;
@@ -271,7 +278,7 @@ fn update__da_block_updates_projected_total_cost_with_known_and_guesses_on_top()
         },
     ];
     // when
-    updater.update_da_record_data(blocks).unwrap();
+    updater.update_da_record_data(&blocks).unwrap();
 
     // then
     let actual = updater.projected_total_da_cost;
@@ -283,3 +290,127 @@ fn update__da_block_updates_projected_total_cost_with_known_and_guesses_on_top()
     let expected = new_known_total_cost + guessed_part;
     assert_eq!(actual, expected as u128);
 }
+
+prop_compose! {
+    fn arb_vec_of_da_blocks()(last_da_block: u32, count in 1..123usize, rng_seed: u64) -> Vec<RecordedBlock> {
+        let rng = &mut rand::rngs::StdRng::seed_from_u64(rng_seed);
+        let mut blocks = Vec::with_capacity(count);
+        for i in 0..count {
+            let block_bytes = rng.gen_range(100..131_072);
+            let cost_per_byte = rng.gen_range(1..1000000);
+            let block_cost = block_bytes * cost_per_byte;
+            blocks.push(RecordedBlock {
+                height: last_da_block + 1 + i as u32,
+                block_bytes,
+                block_cost,
+            });
+        }
+        blocks
+    }
+}
+
+prop_compose! {
+    fn reward_greater_than_cost_with_da_blocks()(cost: u64, extra: u64, blocks in arb_vec_of_da_blocks()) -> (u128, u128, Vec<RecordedBlock>) {
+        let cost_from_blocks = blocks.iter().map(|block| block.block_cost as u128).sum::<u128>();
+        let reward = cost as u128 + cost_from_blocks + extra as u128;
+        (cost as u128, reward, blocks)
+    }
+}
+
+proptest! {
+    #[test]
+    fn update_da_record_data__when_reward_is_greater_than_cost_will_zero_cost_and_subtract_from_reward(
+        (cost, reward, blocks) in reward_greater_than_cost_with_da_blocks()
+    ) {
+        _update_da_record_data__when_reward_is_greater_than_cost_will_zero_cost_and_subtract_from_reward(
+            cost,
+            reward,
+            blocks
+        )
+    }
+}
+
+fn _update_da_record_data__when_reward_is_greater_than_cost_will_zero_cost_and_subtract_from_reward(
+    known_total_cost: u128,
+    total_rewards: u128,
+    blocks: Vec<RecordedBlock>,
+) {
+    // given
+    let da_cost_per_byte = 20;
+    let da_recorded_block_height = blocks.first().unwrap().height - 1;
+    let l2_block_height = 15;
+    let mut updater = UpdaterBuilder::new()
+        .with_da_cost_per_byte(da_cost_per_byte)
+        .with_da_recorded_block_height(da_recorded_block_height)
+        .with_l2_block_height(l2_block_height)
+        .with_known_total_cost(known_total_cost)
+        .with_total_rewards(total_rewards)
+        .build();
+
+    let new_costs = blocks.iter().map(|block| block.block_cost).sum::<u64>();
+
+    // when
+    updater.update_da_record_data(&blocks).unwrap();
+
+    // then
+    let expected = total_rewards - new_costs as u128 - known_total_cost;
+    let actual = updater.total_da_rewards_excess;
+    assert_eq!(actual, expected);
+
+    let expected = 0;
+    let actual = updater.latest_known_total_da_cost_excess;
+    assert_eq!(actual, expected);
+}
+
+prop_compose! {
+    fn cost_greater_than_reward_with_da_blocks()(reward: u64, extra: u64, blocks in arb_vec_of_da_blocks()) -> (u128, u128, Vec<RecordedBlock>) {
+        let cost_from_blocks = blocks.iter().map(|block| block.block_cost as u128).sum::<u128>();
+        let cost = reward as u128 + cost_from_blocks + extra as u128;
+        (cost, reward as u128, blocks)
+    }
+}
+
+proptest! {
+    #[test]
+    fn update_da_record_data__when_cost_is_greater_than_reward_will_zero_reward_and_subtract_from_cost(
+        (cost, reward, blocks) in cost_greater_than_reward_with_da_blocks()
+    ) {
+        _update_da_record_data__when_cost_is_greater_than_reward_will_zero_reward_and_subtract_from_cost(
+            cost,
+            reward,
+            blocks
+        )
+    }
+}
+
+fn _update_da_record_data__when_cost_is_greater_than_reward_will_zero_reward_and_subtract_from_cost(
+    known_total_cost: u128,
+    total_rewards: u128,
+    blocks: Vec<RecordedBlock>,
+) {
+    // given
+    let da_cost_per_byte = 20;
+    let da_recorded_block_height = blocks.first().unwrap().height - 1;
+    let l2_block_height = 15;
+    let mut updater = UpdaterBuilder::new()
+        .with_da_cost_per_byte(da_cost_per_byte)
+        .with_da_recorded_block_height(da_recorded_block_height)
+        .with_l2_block_height(l2_block_height)
+        .with_known_total_cost(known_total_cost)
+        .with_total_rewards(total_rewards)
+        .build();
+
+    let new_costs = blocks.iter().map(|block| block.block_cost).sum::<u64>();
+
+    // when
+    updater.update_da_record_data(&blocks).unwrap();
+
+    // then
+    let expected = 0;
+    let actual = updater.total_da_rewards_excess;
+    assert_eq!(actual, expected);
+
+    let expected = known_total_cost + new_costs as u128 - total_rewards;
+    let actual = updater.latest_known_total_da_cost_excess;
+    assert_eq!(actual, expected);
+}
```
