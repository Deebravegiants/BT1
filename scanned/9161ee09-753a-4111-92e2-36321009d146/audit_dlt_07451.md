# [?] Fix overflow in historical scoring model point count summation

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-02-23
Source: https://github.com/lightningdevkit/rust-lightning/commit/43d0964474888cf3a8017d558bb61c11db93ca82
Type: security-commit

## Details
Fix overflow in historical scoring model point count summation

In adb0afc523f9fea44cd42e02a1022510a9c83a52 we started raising
bucket weights to the power four in the historical model. This
improved our model's accuracy greatly, but resulted in a much
larger `total_valid_points_tracked`. In the same commit we
converted `total_valid_points_tracked` to a float, but retained the
64-bit integer math to build it out of integer bucket values.

Sadly, 64 bits are not enough to sum 1024 bucket pairs of 16-bit
integers multiplied together and then squared (we need 16*4 + 10 =
74 bits to avoid overflow). Thus, here we replace the summation
with 128-bit integers.

## Patch
### lightning/src/routing/scoring.rs
```diff
@@ -2060,15 +2060,17 @@ mod bucketed_history {
 		}
 
 		fn recalculate_valid_point_count(&mut self) {
-			let mut total_valid_points_tracked = 0;
+			let mut total_valid_points_tracked = 0u128;
 			for (min_idx, min_bucket) in self.min_liquidity_offset_history.buckets.iter().enumerate() {
 				for max_bucket in self.max_liquidity_offset_history.buckets.iter().take(32 - min_idx) {
 					// In testing, raising the weights of buckets to a high power led to better
 					// scoring results. Thus, we raise the bucket weights to the 4th power here (by
-					// squaring the result of multiplying the weights).
+					// squaring the result of multiplying the weights). This results in
+					// bucket_weight having at max 64 bits, which means we have to do our summation
+					// in 128-bit math.
 					let mut bucket_weight = (*min_bucket as u64) * (*max_bucket as u64);
 					bucket_weight *= bucket_weight;
-					total_valid_points_tracked += bucket_weight;
+					total_valid_points_tracked += bucket_weight as u128;
 				}
 			}
 			self.total_valid_points_tracked = total_valid_points_tracked as f64;
@@ -2161,12 +2163,12 @@ mod bucketed_history {
 
 			let total_valid_points_tracked = self.tracker.total_valid_points_tracked;
 			#[cfg(debug_assertions)] {
-				let mut actual_valid_points_tracked = 0;
+				let mut actual_valid_points_tracked = 0u128;
 				for (min_idx, min_bucket) in min_liquidity_offset_history_buckets.iter().enumerate() {
 					for max_bucket in max_liquidity_offset_history_buckets.iter().take(32 - min_idx) {
 						let mut bucket_weight = (*min_bucket as u64) * (*max_bucket as u64);
 						bucket_weight *= bucket_weight;
-						actual_valid_points_tracked += bucket_weight;
+						actual_valid_points_tracked += bucket_weight as u128;
 					}
 				}
 				assert_eq!(total_valid_points_tracked, actual_valid_points_tracked as f64);
@@ -2193,7 +2195,7 @@ mod bucketed_history {
 				// max-bucket with at least BUCKET_FIXED_POINT_ONE.
 				let mut highest_max_bucket_with_points = 0;
 				let mut highest_max_bucket_with_full_points = None;
-				let mut total_weight = 0;
+				let mut total_weight = 0u128;
 				for (max_idx, max_bucket) in max_liquidity_offset_history_buckets.iter().enumerate() {
 					if *max_bucket >= BUCKET_FIXED_POINT_ONE {
 						highest_max_bucket_with_full_points = Some(cmp::max(highest_max_bucket_with_full_points.unwrap_or(0), max_idx));
@@ -2206,7 +2208,7 @@ mod bucketed_history {
 					// squaring the result of multiplying the weights), matching the logic in
 					// `recalculate_valid_point_count`.
 					let bucket_weight = (*max_bucket as u64) * (min_liquidity_offset_history_buckets[0] as u64);
-					total_weight += bucket_weight * bucket_weight;
+					total_weight += (bucket_weight * bucket_weight) as u128;
 				}
 				debug_assert!(total_weight as f64 <= total_valid_points_tracked);
 				// Use the highest max-bucket with at least BUCKET_FIXED_POINT_ONE, but if none is
@@ -2343,6 +2345,26 @@ mod bucketed_history {
 
 			assert_ne!(probability1, probability);
 		}
+
+		#[test]
+		fn historical_heavy_buckets_operations() {
+			// Checks that we don't hit overflows when working with tons of data (even an
+			// impossible-to-reach amount of data).
+			let mut tracker = HistoricalLiquidityTracker::new();
+			tracker.min_liquidity_offset_history.buckets = [0xffff; 32];
+			tracker.max_liquidity_offset_history.buckets = [0xffff; 32];
+			tracker.recalculate_valid_point_count();
+			tracker.merge(&tracker.clone());
+			assert_eq!(tracker.min_liquidity_offset_history.buckets, [0xffff; 32]);
+			assert_eq!(tracker.max_liquidity_offset_history.buckets, [0xffff; 32]);
+
+			let mut directed = tracker.as_directed_mut(true);
+			let default_params = ProbabilisticScoringFeeParameters::default();
+			directed.calculate_success_probability_times_billion(&default_params, 42, 1000);
+			directed.track_datapoint(42, 52, 1000);
+
+			tracker.decay_buckets(1.0);
+		}
 	}
 }
 
```
