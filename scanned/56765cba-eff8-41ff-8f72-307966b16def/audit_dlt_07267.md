# [?] core-fellowship: avoid panic on undersized Params salary/period vectors (#13182)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-09-15
Source: https://github.com/paritytech/polkadot-sdk/commit/a0fae9d44617843c51674469a1bc04dd4f884111
Type: security-commit

## Details
core-fellowship: avoid panic on undersized Params salary/period vectors (#13182)

`Pallet::get_salary` computed an index from the member's rank and then
indexed the `active_salary `or `passive_salary` vector directly. The
bump and promote calls did the same thing to `demotion_period `and
`min_promotion_period`. All four of these vectors are BoundedVec fields
bounded only by MaxRank, so a privileged set_params call is free to
store a shorter vector, including the empty default. Once that happens,
any of these three call sites panics for a member whose rank sits past
the end of the stored vector, which traps the extrinsic instead of
failing gracefully.

This changes all three sites to look up the index with get and fall back
to the type's default when the entry is missing, so a rank past the end
of the vector now degrades to zero salary, a zero demotion period or a
zero minimum promotion period, the same way the pallet already treats
rank 0 and untracked members. No panic path remains.

Added three unit tests that configure an undersized vector for each of
the three call sites and assert the graceful fallback instead of a
panic.

Closes #13141

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: Bastian Köcher <git@kchr.de>
Co-authored-by: muharem <ismailov.m.h@gmail.com>

## Patch
### prdoc/pr_13182.prdoc
```diff
@@ -0,0 +1,12 @@
+title: 'core-fellowship: avoid panic on undersized Params salary/period vectors'
+doc:
+- audience: Runtime Dev
+  description: |-
+    `Pallet::get_salary` computed an index from the member's rank and then indexed the `active_salary `or `passive_salary` vector directly. The bump and promote calls did the same thing to `demotion_period `and `min_promotion_period`. All four of these vectors are BoundedVec fields bounded only by MaxRank, so a privileged set_params call is free to store a shorter vector, including the empty default. Once that happens, any of these three call sites panics for a member whose rank sits past the end of the stored vector, which traps the extrinsic instead of failing gracefully.
+
+    This changes all three sites to look up the index with get and fall back to the type's default when the entry is missing, so a rank past the end of the vector now degrades to zero salary, a zero demotion period or a zero minimum promotion period, the same way the pallet already treats rank 0 and untracked members. No panic path remains.
+
+    Closes #13141
+crates:
+- name: pallet-core-fellowship
+  bump: patch
```

### substrate/frame/core-fellowship/src/lib.rs
```diff
@@ -369,7 +369,7 @@ pub mod pallet {
 				params.offboard_timeout
 			} else {
 				let rank_index = Self::rank_to_index(rank).ok_or(Error::<T, I>::InvalidRank)?;
-				params.demotion_period[rank_index]
+				*params.demotion_period.get(rank_index).ok_or(Error::<T, I>::InvalidRank)?
 			};
 
 			if demotion_period.is_zero() {
@@ -519,7 +519,8 @@ pub mod pallet {
 
 			let params = Params::<T, I>::get();
 			let rank_index = Self::rank_to_index(to_rank).ok_or(Error::<T, I>::InvalidRank)?;
-			let min_period = params.min_promotion_period[rank_index];
+			let min_period =
+				*params.min_promotion_period.get(rank_index).ok_or(Error::<T, I>::InvalidRank)?;
 			// Ensure enough time has passed.
 			ensure!(
 				member.last_promotion.saturating_add(min_period) <= now,
@@ -760,7 +761,10 @@ pub mod pallet {
 			let params = Params::<T, I>::get();
 			let salary =
 				if member.is_active { params.active_salary } else { params.passive_salary };
-			salary[index]
+			// `GetSalary::get_salary` returns `T::Balance` directly, not a `Result`, so an
+			// out-of-range rank can't be rejected here the way `bump`/`promote` reject it; fall
+			// back to zero, consistent with the early returns above.
+			salary.get(index).copied().unwrap_or_default()
 		}
 	}
 }
```

### substrate/frame/core-fellowship/src/tests/unit.rs
```diff
@@ -546,3 +546,50 @@ fn active_changing_get_salary_works() {
 		}
 	});
 }
+
+#[test]
+fn get_salary_undersized_vec_works() {
+	new_test_ext().execute_with(|| {
+		set_rank(14, 5);
+		assert_ok!(CoreFellowship::import(signed(14)));
+
+		// Shorter than `MaxRank`, but still legal, since only the maximum length is bounded.
+		let mut params = Params::<Test>::get();
+		params.active_salary = bounded_vec![10, 20, 30, 40];
+		assert_ok!(CoreFellowship::set_params(signed(1), Box::new(params)));
+
+		assert_eq!(CoreFellowship::get_salary(4, &14), 40);
+		// Rank 5 is past the end of the stored vector; it must pay zero, not panic.
+		assert_eq!(CoreFellowship::get_salary(5, &14), 0);
+	});
+}
+
+#[test]
+fn bump_undersized_demotion_period_vec_works() {
+	new_test_ext().execute_with(|| {
+		set_rank(14, 5);
+		assert_ok!(CoreFellowship::import(signed(14)));
+
+		let mut params = Params::<Test>::get();
+		params.demotion_period = bounded_vec![2, 4, 6, 8];
+		assert_ok!(CoreFellowship::set_params(signed(1), Box::new(params)));
+
+		// Rank 5 has no `demotion_period` entry; that's rejected, not a panic.
+		assert_noop!(CoreFellowship::bump(signed(0), 14), Error::<Test>::InvalidRank);
+	});
+}
+
+#[test]
+fn promote_undersized_min_promotion_period_vec_works() {
+	new_test_ext().execute_with(|| {
+		set_rank(14, 4);
+		assert_ok!(CoreFellowship::import(signed(14)));
+
+		let mut params = Params::<Test>::get();
+		params.min_promotion_period = bounded_vec![2, 4, 6, 8];
+		assert_ok!(CoreFellowship::set_params(signed(1), Box::new(params)));
+
+		// Rank 5 has no `min_promotion_period` entry; that's rejected, not a panic.
+		assert_noop!(CoreFellowship::promote(signed(5), 14, 5), Error::<Test>::InvalidRank);
+	});
+}
```
