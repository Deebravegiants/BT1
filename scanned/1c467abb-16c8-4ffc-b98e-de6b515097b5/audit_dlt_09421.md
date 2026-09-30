# [?] Fix crowdloan reentrancy bug

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-23
Source: https://github.com/RaoFoundation/subtensor/commit/bb71e41e573cd2b0b94526c9e2091dec86cd48a4
Type: security-commit

## Details
Fix crowdloan reentrancy bug

## Patch
### pallets/crowdloan/src/lib.rs
```diff
@@ -620,6 +620,9 @@ pub mod pallet {
             ensure!(crowdloan.raised == crowdloan.cap, Error::<T>::CapNotRaised);
             ensure!(!crowdloan.finalized, Error::<T>::AlreadyFinalized);
 
+            crowdloan.finalized = true;
+            Crowdloans::<T>::insert(crowdloan_id, &crowdloan);
+
             match (&crowdloan.call, &crowdloan.target_address) {
                 (Some(call), None) => {
                     // Set the current crowdloan id so the dispatched call
@@ -659,9 +662,6 @@ pub mod pallet {
                 }
             }
 
-            crowdloan.finalized = true;
-            Crowdloans::<T>::insert(crowdloan_id, &crowdloan);
-
             Self::deposit_event(Event::<T>::Finalized { crowdloan_id });
 
             Ok(())
```

### pallets/crowdloan/src/tests.rs
```diff
@@ -1875,6 +1875,134 @@ fn test_finalize_fails_if_call_fails() {
         });
 }
 
+// The finalize `call` cannot re-enter `withdraw` on the same crowdloan: it is rejected and
+// the extrinsic reverts, so no funds move and `raised` stays consistent with the real balance.
+#[test]
+fn test_finalize_blocks_reentrant_withdraw() {
+    TestState::default()
+        .with_balance(U256::from(1), 200.into()) // creator
+        .with_balance(U256::from(2), 200.into()) // contributor
+        .build_and_execute(|| {
+            let creator: AccountOf<Test> = U256::from(1);
+            let contributor: AccountOf<Test> = U256::from(2);
+            let deposit: BalanceOf<Test> = 50.into();
+            let min_contribution: BalanceOf<Test> = 10.into();
+            let cap: BalanceOf<Test> = 100.into();
+            let end: BlockNumberFor<Test> = 50;
+            let crowdloan_id: CrowdloanId = 0;
+
+            // The finalize call re-enters `withdraw` on the same crowdloan.
+            let reentrant_call = Box::new(RuntimeCall::Crowdloan(
+                pallet_crowdloan::Call::<Test>::withdraw { crowdloan_id },
+            ));
+
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(reentrant_call),
+                None,
+            ));
+            run_to_block(10);
+
+            // Creator contributes 30 over the deposit (total 80); contributor fills the cap.
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(creator),
+                crowdloan_id,
+                30.into()
+            ));
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id,
+                20.into()
+            ));
+
+            let funds_account = pallet_crowdloan::Pallet::<Test>::funds_account(crowdloan_id);
+            assert_eq!(Balances::free_balance(funds_account), cap);
+            let creator_balance_before = Balances::free_balance(creator);
+
+            run_to_block(60);
+
+            // Finalize dispatches the re-entrant withdraw, which is rejected with
+            // `AlreadyFinalized`. Wrap in a storage layer to model the per-extrinsic
+            // transaction the runtime applies in production, so the revert is observable.
+            let outcome = frame_support::storage::with_storage_layer(|| {
+                Crowdloan::finalize(RuntimeOrigin::signed(creator), crowdloan_id)
+            });
+            assert_err!(outcome, pallet_crowdloan::Error::<Test>::AlreadyFinalized);
+
+            // No funds were extracted and accounting is intact.
+            assert_eq!(Balances::free_balance(creator), creator_balance_before);
+            assert_eq!(Balances::free_balance(funds_account), cap);
+            assert_eq!(pallet_crowdloan::CurrentCrowdloanId::<Test>::get(), None);
+            let crowdloan = pallet_crowdloan::Crowdloans::<Test>::get(crowdloan_id).unwrap();
+            assert!(!crowdloan.finalized);
+            assert_eq!(crowdloan.raised, cap);
+
+            // Contributor funds are not frozen: the contributor can still withdraw.
+            assert_ok!(Crowdloan::withdraw(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id
+            ));
+            assert_eq!(Balances::free_balance(contributor), 200.into());
+        });
+}
+
+// A re-entrant `refund` embedded as the finalize call is likewise rejected before moving funds.
+#[test]
+fn test_finalize_blocks_reentrant_refund() {
+    TestState::default()
+        .with_balance(U256::from(1), 200.into()) // creator
+        .with_balance(U256::from(2), 200.into()) // contributor
+        .build_and_execute(|| {
+            let creator: AccountOf<Test> = U256::from(1);
+            let contributor: AccountOf<Test> = U256::from(2);
+            let deposit: BalanceOf<Test> = 50.into();
+            let min_contribution: BalanceOf<Test> = 10.into();
+            let cap: BalanceOf<Test> = 100.into();
+            let end: BlockNumberFor<Test> = 50;
+            let crowdloan_id: CrowdloanId = 0;
+
+            let reentrant_call = Box::new(RuntimeCall::Crowdloan(
+                pallet_crowdloan::Call::<Test>::refund { crowdloan_id },
+            ));
+
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(reentrant_call),
+                None,
+            ));
+            run_to_block(10);
+
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(creator),
+                crowdloan_id,
+                30.into()
+            ));
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id,
+                20.into()
+            ));
+
+            let funds_account = pallet_crowdloan::Pallet::<Test>::funds_account(crowdloan_id);
+            run_to_block(60);
+
+            // The re-entrant refund hits the `finalized` guard before transferring anything.
+            assert_err!(
+                Crowdloan::finalize(RuntimeOrigin::signed(creator), crowdloan_id),
+                pallet_crowdloan::Error::<Test>::AlreadyFinalized
+            );
+            assert_eq!(Balances::free_balance(funds_account), cap);
+        });
+}
+
 #[test]
 fn test_refund_succeeds() {
     TestState::default()
```
