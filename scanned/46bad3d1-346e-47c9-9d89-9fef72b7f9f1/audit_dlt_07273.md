# [?] Fix warnings related to panic and assert (#8272)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2021-03-05
Source: https://github.com/paritytech/substrate/commit/3233d2992eaef30e7c1ce7d2e8ec6ea08d4091b9
Type: security-commit

## Details
Fix warnings related to panic and assert (#8272)

We were using the wrong syntax and that will be dropped with Rust 2021.
The compiler already starts to hint the wrong syntax with warnings. So,
we fix this here.

## Patch
### client/service/test/src/client/light.rs
```diff
@@ -684,10 +684,13 @@ fn changes_proof_is_generated_and_checked_when_headers_are_not_pruned() {
 		}).unwrap();
 
 		// ..and ensure that result is the same as on remote node
-		match local_result == expected_result {
-			true => (),
-			false => panic!(format!("Failed test {}: local = {:?}, expected = {:?}",
-									index, local_result, expected_result)),
+		if local_result != expected_result {
+			panic!(
+				"Failed test {}: local = {:?}, expected = {:?}",
+				index,
+				local_result,
+				expected_result,
+			);
 		}
 	}
 }
```

### client/service/test/src/client/mod.rs
```diff
@@ -988,10 +988,13 @@ fn key_changes_works() {
 			None,
 			&StorageKey(key),
 		).unwrap();
-		match actual_result == expected_result {
-			true => (),
-			false => panic!(format!("Failed test {}: actual = {:?}, expected = {:?}",
-			                        index, actual_result, expected_result)),
+		if actual_result != expected_result {
+			panic!(
+				"Failed test {}: actual = {:?}, expected = {:?}",
+				index,
+				actual_result,
+				expected_result,
+			);
 		}
 	}
 }
```

### client/tracing/src/logging/mod.rs
```diff
@@ -427,7 +427,9 @@ mod tests {
 		let output = String::from_utf8(output.stderr).unwrap();
 		assert!(
 			re.is_match(output.trim()),
-			format!("Expected:\n{}\nGot:\n{}", re, output),
+			"Expected:\n{}\nGot:\n{}",
+			re,
+			output,
 		);
 	}
 
@@ -475,7 +477,9 @@ mod tests {
 		let output = String::from_utf8(output.stderr).unwrap();
 		assert!(
 			re.is_match(output.trim()),
-			format!("Expected:\n{}\nGot:\n{}", re, output),
+			"Expected:\n{}\nGot:\n{}",
+			re,
+			output,
 		);
 	}
 
```

### frame/democracy/src/tests.rs
```diff
@@ -236,7 +236,7 @@ fn set_balance_proposal_hash_and_note(value: u64) -> H256 {
 	match Democracy::note_preimage(Origin::signed(6), p) {
 		Ok(_) => (),
 		Err(x) if x == Error::<Test>::DuplicatePreimage.into() => (),
-		Err(x) => panic!(x),
+		Err(x) => panic!("{:?}", x),
 	}
 	h
 }
```

### frame/election-provider-multi-phase/src/lib.rs
```diff
@@ -673,8 +673,9 @@ pub mod pallet {
 			witness: SolutionOrSnapshotSize,
 		) -> DispatchResultWithPostInfo {
 			ensure_none(origin)?;
-			let error_message = "Invalid unsigned submission must produce invalid block and \
-			                     deprive validator from their authoring reward.";
+			let error_message =
+				"Invalid unsigned submission must produce invalid block and \
+				 deprive validator from their authoring reward.";
 
 			// Check score being an improvement, phase, and desired targets.
 			Self::unsigned_pre_dispatch_checks(&solution).expect(error_message);
@@ -684,8 +685,8 @@ pub mod pallet {
 				Self::snapshot_metadata().expect(error_message);
 
 			// NOTE: we are asserting, not `ensure`ing -- we want to panic here.
-			assert!(voters as u32 == witness.voters, error_message);
-			assert!(targets as u32 == witness.targets, error_message);
+			assert!(voters as u32 == witness.voters, "{}", error_message);
+			assert!(targets as u32 == witness.targets, "{}", error_message);
 
 			let ready =
 				Self::feasibility_check(solution, ElectionCompute::Unsigned).expect(error_message);
```

### frame/offences/benchmarking/src/lib.rs
```diff
@@ -227,7 +227,7 @@ fn check_events<T: Config, I: Iterator<Item = <T as SystemConfig>::Event>>(expec
 	}
 
 	if !length_mismatch.is_empty() {
-		panic!(length_mismatch);
+		panic!("{}", length_mismatch);
 	}
 }
 
```
