# [?] Fix panic in election-provider offchain worker. (#8732)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2021-05-05
Source: https://github.com/paritytech/substrate/commit/0f849efc2616685f0e32fec3cc5ccd174ff142ac
Type: security-commit

## Details
Fix panic in election-provider offchain worker. (#8732)

## Patch
### frame/election-provider-multi-phase/src/unsigned.rs
```diff
@@ -437,6 +437,11 @@ impl<T: Config> Pallet<T> {
 		let mut high = assignments.len();
 		let mut low = 0;
 
+		// not much we can do if assignments are already empty.
+		if high == low {
+			return Ok(());
+		}
+
 		while high - low > 1 {
 			let test = (high + low) / 2;
 			if encoded_size_of(&assignments[..test])? <= max_allowed_length {
@@ -446,13 +451,13 @@ impl<T: Config> Pallet<T> {
 			}
 		}
 		let maximum_allowed_voters =
-			if encoded_size_of(&assignments[..low + 1])? <= max_allowed_length {
+			if low < assignments.len() && encoded_size_of(&assignments[..low + 1])? <= max_allowed_length {
 				low + 1
 			} else {
 				low
 			};
 
-		// ensure our postconditions are correct
+		// ensure our post-conditions are correct
 		debug_assert!(
 			encoded_size_of(&assignments[..maximum_allowed_voters]).unwrap() <= max_allowed_length
 		);
@@ -1256,8 +1261,7 @@ mod tests {
 
 	#[test]
 	fn trim_assignments_length_does_not_modify_when_short_enough() {
-		let mut ext = ExtBuilder::default().build();
-		ext.execute_with(|| {
+		ExtBuilder::default().build_and_execute(|| {
 			roll_to(25);
 
 			// given
@@ -1281,8 +1285,7 @@ mod tests {
 
 	#[test]
 	fn trim_assignments_length_modifies_when_too_long() {
-		let mut ext = ExtBuilder::default().build();
-		ext.execute_with(|| {
+		ExtBuilder::default().build().execute_with(|| {
 			roll_to(25);
 
 			// given
@@ -1307,8 +1310,7 @@ mod tests {
 
 	#[test]
 	fn trim_assignments_length_trims_lowest_stake() {
-		let mut ext = ExtBuilder::default().build();
-		ext.execute_with(|| {
+		ExtBuilder::default().build().execute_with(|| {
 			roll_to(25);
 
 			// given
@@ -1340,13 +1342,59 @@ mod tests {
 		});
 	}
 
+	#[test]
+	fn trim_assignments_length_wont_panic() {
+		// we shan't panic if assignments are initially empty.
+		ExtBuilder::default().build_and_execute(|| {
+			let encoded_size_of = Box::new(|assignments: &[IndexAssignmentOf<Runtime>]| {
+				CompactOf::<Runtime>::try_from(assignments).map(|compact| compact.encoded_size())
+			});
+
+			let mut assignments = vec![];
+
+			// since we have 16 fields, we need to store the length fields of 16 vecs, thus 16 bytes
+			// minimum.
+			let min_compact_size = encoded_size_of(&assignments).unwrap();
+			assert_eq!(min_compact_size, CompactOf::<Runtime>::LIMIT);
+
+			// all of this should not panic.
+			MultiPhase::trim_assignments_length(0, &mut assignments, encoded_size_of.clone())
+				.unwrap();
+			MultiPhase::trim_assignments_length(1, &mut assignments, encoded_size_of.clone())
+				.unwrap();
+			MultiPhase::trim_assignments_length(
+				min_compact_size as u32,
+				&mut assignments,
+				encoded_size_of,
+			)
+			.unwrap();
+		});
+
+		// or when we trim it to zero.
+		ExtBuilder::default().build_and_execute(|| {
+			// we need snapshot for `trim_helpers` to work.
+			roll_to(25);
+			let TrimHelpers { mut assignments, encoded_size_of, .. } = trim_helpers();
+			assert!(assignments.len() > 0);
+
+			// trim to min compact size.
+			let min_compact_size = CompactOf::<Runtime>::LIMIT as u32;
+			MultiPhase::trim_assignments_length(
+				min_compact_size,
+				&mut assignments,
+				encoded_size_of,
+			)
+			.unwrap();
+			assert_eq!(assignments.len(), 0);
+		});
+	}
+
 	// all the other solution-generation functions end up delegating to `mine_solution`, so if we
 	// demonstrate that `mine_solution` solutions are all trimmed to an acceptable length, then
 	// we know that higher-level functions will all also have short-enough solutions.
 	#[test]
 	fn mine_solution_solutions_always_within_acceptable_length() {
-		let mut ext = ExtBuilder::default().build();
-		ext.execute_with(|| {
+		ExtBuilder::default().build_and_execute(|| {
 			roll_to(25);
 
 			// how long would the default solution be?
```
