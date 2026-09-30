# [?] Fixes possible deadlock upon epoch close (#719)

## Summary
Severity: Unknown
Chain: Centrifuge
Component: centrifuge/centrifuge-chain
Published: 2022-03-29
Source: https://github.com/centrifuge/centrifuge-chain/commit/6c596864a8bfc230bc92932b1d0bb56555162d5a
Type: security-commit

## Details
Fixes possible deadlock upon epoch close (#719)

* pools logic for deadlock solution

* Fix tests

* Tests

* prepare dev runtime

* Fix loan tests

* Reverting deadlock logic approch with MinSubmissionTime

* allow equal solutions to be sumitted

* Adapt tests to same solutions allowed

* Test for zero submission

## Patch
### pallets/pools/src/lib.rs
```diff
@@ -1028,7 +1028,7 @@ pub mod pallet {
 				let new_solution = Self::score_solution(&pool, &epoch, &solution)?;
 				if let Some(ref previous_solution) = epoch.best_submission {
 					ensure!(
-						&new_solution > previous_solution,
+						&new_solution >= previous_solution,
 						Error::<T>::NotNewBestSubmission
 					);
 				}
@@ -1079,11 +1079,19 @@ pub mod pallet {
 					Error::<T>::NoSolutionAvailable
 				);
 
+				// The challenge period is some if we have submitted at least one valid
+				// solution since going into submission period. Hence, if it is none
+				// no solution beside the injected zero-solution is available.
 				ensure!(
-					match epoch.challenge_period_end {
-						Some(challenge_period_end) => challenge_period_end <= Self::now(),
-						None => false,
-					},
+					epoch.challenge_period_end.is_some(),
+					Error::<T>::NoSolutionAvailable
+				);
+
+				ensure!(
+					epoch
+						.challenge_period_end
+						.expect("Challenge period is some. qed.")
+						<= Self::now(),
 					Error::<T>::ChallengeTimeHasNotPassed
 				);
 
```

### pallets/pools/src/tests.rs
```diff
@@ -803,24 +803,21 @@ fn submission_period() {
 			]
 		));
 
-		// Can't submit the same solution twice
-		assert_err!(
-			Pools::submit_solution(
-				pool_owner_origin.clone(),
-				0,
-				vec![
-					TrancheSolution {
-						invest_fulfillment: Perquintill::one(),
-						redeem_fulfillment: Perquintill::from_float(0.01),
-					},
-					TrancheSolution {
-						invest_fulfillment: Perquintill::one(),
-						redeem_fulfillment: Perquintill::one(),
-					}
-				]
-			),
-			Error::<Test>::NotNewBestSubmission
-		);
+		// Can submit the same solution twice
+		assert_ok!(Pools::submit_solution(
+			pool_owner_origin.clone(),
+			0,
+			vec![
+				TrancheSolution {
+					invest_fulfillment: Perquintill::one(),
+					redeem_fulfillment: Perquintill::from_float(0.01),
+				},
+				TrancheSolution {
+					invest_fulfillment: Perquintill::one(),
+					redeem_fulfillment: Perquintill::one(),
+				}
+			]
+		));
 
 		// Slight risk buffer improvement
 		assert_ok!(Pools::submit_solution(
@@ -1640,3 +1637,113 @@ fn valid_tranche_structure_is_enforced() {
 		);
 	})
 }
+
+#[test]
+fn triger_challange_period_with_zero_solution() {
+	new_test_ext().execute_with(|| {
+		let junior_investor = Origin::signed(0);
+		let senior_investor = Origin::signed(1);
+		let pool_owner = 2_u64;
+		let pool_owner_origin = Origin::signed(pool_owner);
+
+		<<Test as Config>::Permission as PermissionsT<u64>>::add(
+			0,
+			ensure_signed(junior_investor.clone()).unwrap(),
+			PoolRole::TrancheInvestor(JuniorTrancheId::get(), u64::MAX),
+		)
+		.unwrap();
+
+		<<Test as Config>::Permission as PermissionsT<u64>>::add(
+			0,
+			ensure_signed(senior_investor.clone()).unwrap(),
+			PoolRole::TrancheInvestor(SeniorTrancheId::get(), u64::MAX),
+		)
+		.unwrap();
+
+		// Initialize pool with initial investments
+		const SECS_PER_YEAR: u64 = 365 * 24 * 60 * 60;
+		let senior_interest_rate = Rate::saturating_from_rational(10, 100)
+			/ Rate::saturating_from_integer(SECS_PER_YEAR)
+			+ One::one();
+
+		assert_ok!(Pools::create(
+			pool_owner_origin.clone(),
+			pool_owner.clone(),
+			0,
+			vec![
+				(TrancheType::Residual, None),
+				(
+					TrancheType::NonResidual {
+						interest_per_sec: senior_interest_rate,
+						min_risk_buffer: Perquintill::from_percent(10),
+					},
+					None
+				)
+			],
+			CurrencyId::Usd,
+			10_000 * CURRENCY
+		));
+
+		// Force min_epoch_time and challenge time to 0 without using update
+		// as this breaks the runtime-defined pool
+		// parameter bounds and update will not allow this.
+		crate::Pool::<Test>::try_mutate(0, |maybe_pool| -> Result<(), ()> {
+			maybe_pool.as_mut().unwrap().min_epoch_time = 0;
+			maybe_pool.as_mut().unwrap().challenge_time = 0;
+			maybe_pool.as_mut().unwrap().max_nav_age = u64::MAX;
+			Ok(())
+		})
+		.unwrap();
+
+		invest_close_and_collect(
+			0,
+			vec![
+				(
+					junior_investor.clone(),
+					JuniorTrancheId::get(),
+					500 * CURRENCY,
+				),
+				(
+					senior_investor.clone(),
+					SeniorTrancheId::get(),
+					500 * CURRENCY,
+				),
+			],
+		)
+		.unwrap();
+
+		// Attempt to redeem everything
+		assert_ok!(Pools::update_redeem_order(
+			junior_investor.clone(),
+			0,
+			TrancheLoc::Id(JuniorTrancheId::get()),
+			500 * CURRENCY
+		));
+		assert_ok!(Pools::close_epoch(pool_owner_origin.clone(), 0));
+
+		assert_err!(
+			Pools::execute_epoch(pool_owner_origin.clone(), 0),
+			Error::<Test>::NoSolutionAvailable
+		);
+
+		assert_ok!(Pools::submit_solution(
+			pool_owner_origin.clone(),
+			0,
+			vec![
+				TrancheSolution {
+					invest_fulfillment: Perquintill::zero(),
+					redeem_fulfillment: Perquintill::zero(),
+				},
+				TrancheSolution {
+					invest_fulfillment: Perquintill::zero(),
+					redeem_fulfillment: Perquintill::zero(),
+				}
+			]
+		));
+
+		next_block();
+
+		assert_ok!(Pools::execute_epoch(pool_owner_origin, 0));
+		assert!(!EpochExecution::<Test>::contains_key(0));
+	});
+}
```
