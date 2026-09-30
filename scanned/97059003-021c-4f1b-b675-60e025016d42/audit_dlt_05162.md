# [?] Fix: Out of bounds error with user defined `TrancheId` (#595)

## Summary
Severity: Unknown
Chain: Centrifuge
Component: centrifuge/centrifuge-chain
Published: 2022-01-19
Source: https://github.com/centrifuge/centrifuge-chain/commit/48aff40f50b565716a878968e48d330b4c45f00c
Type: security-commit

## Details
Fix: Out of bounds error with user defined `TrancheId` (#595)

* Refactor and ensure tranche-id not our of bounds

* Earlier error for no pool, expect msg enhanced

* Unified formating

* Cover invalid tranche-id with test-case

* Address review

## Patch
### pallets/pools/src/lib.rs
```diff
@@ -111,6 +111,15 @@ pub struct TrancheLocator<PoolId, TrancheId> {
 	pub tranche_id: TrancheId,
 }
 
+impl<PoolId, TrancheId> TrancheLocator<PoolId, TrancheId> {
+	fn new(pool_id: PoolId, tranche_id: TrancheId) -> Self {
+		TrancheLocator {
+			pool_id,
+			tranche_id,
+		}
+	}
+}
+
 /// A representation of a pool identifier that can be converted to an account address
 #[derive(Encode, Decode, Clone, Eq, PartialEq, RuntimeDebug, TypeInfo)]
 pub struct PoolLocator<PoolId> {
@@ -160,6 +169,17 @@ type LookUpSource<T> = <<T as frame_system::Config>::Lookup as StaticLookup>::So
 // Type that indicates a point in time
 type Moment = u64;
 
+// Types to ease function signatures
+type PoolDetailsOf<T> = PoolDetails<
+	<T as frame_system::Config>::AccountId,
+	<T as Config>::CurrencyId,
+	<T as Config>::EpochId,
+	<T as Config>::Balance,
+	<T as Config>::InterestRate,
+	<T as Config>::MaxSizeMetadata,
+>;
+type UserOrderOf<T> = UserOrder<<T as Config>::Balance, <T as Config>::EpochId>;
+
 #[frame_support::pallet]
 pub mod pallet {
 	use super::*;
@@ -400,6 +420,10 @@ pub mod pallet {
 		InvalidTrancheSeniority,
 		/// Invalid metadata passed
 		BadMetadata,
+		/// Invalid TrancheId passed. In most cases out-of-bound index
+		InvalidTrancheId,
+		/// Indicates that the new passed order equals the old-order
+		NoNewOrder,
 	}
 
 	#[pallet::call]
@@ -589,54 +613,27 @@ pub mod pallet {
 				),
 				BadOrigin
 			);
-			let (currency, epoch) = {
-				let pool = Pool::<T>::try_get(pool_id).map_err(|_| Error::<T>::NoSuchPool)?;
-				(pool.currency, pool.current_epoch)
-			};
-			let tranche = TrancheLocator {
-				pool_id,
-				tranche_id,
-			};
-			let pool_account = PoolLocator { pool_id }.into_account();
 
-			if let Ok(order) = Order::<T>::try_get(&tranche, &who) {
-				ensure!(
-					order.invest.saturating_add(order.redeem) == Zero::zero()
-						|| order.epoch == epoch,
-					Error::<T>::CollectRequired
-				)
-			}
+			Pool::<T>::try_mutate(pool_id, |pool| -> DispatchResult {
+				let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
 
-			Order::<T>::try_mutate(&tranche, &who, |order| -> DispatchResult {
-				if amount > order.invest {
-					let transfer_amount = amount.saturating_sub(order.invest);
-					Pool::<T>::try_mutate(pool_id, |pool| {
-						let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
-						let outstanding_invest_orders =
-							&mut pool.tranches[tranche_id.into()].outstanding_invest_orders;
-						*outstanding_invest_orders = outstanding_invest_orders
-							.checked_add(&transfer_amount)
-							.ok_or(Error::<T>::Overflow)?;
-						T::Tokens::transfer(currency, &who, &pool_account, transfer_amount)
-					})?;
-				} else if amount < order.invest {
-					let transfer_amount = order.invest.saturating_sub(amount);
-					Pool::<T>::try_mutate(pool_id, |pool| {
-						let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
-						let outstanding_invest_orders =
-							&mut pool.tranches[tranche_id.into()].outstanding_invest_orders;
-						*outstanding_invest_orders = outstanding_invest_orders
-							.checked_sub(&transfer_amount)
-							.ok_or(Error::<T>::Overflow)?;
-						T::Tokens::transfer(currency, &pool_account, &who, transfer_amount)
-					})?;
-				}
-				order.invest = amount;
-				order.epoch = epoch;
+				Order::<T>::try_mutate(
+					&TrancheLocator::new(pool_id, tranche_id),
+					&who,
+					|order| -> DispatchResult {
+						ensure!(
+							order.invest.saturating_add(order.redeem) == Zero::zero()
+								|| order.epoch == pool.current_epoch,
+							Error::<T>::CollectRequired
+						);
+
+						Self::do_update_invest_order(&who, pool, order, amount, pool_id, tranche_id)
+					},
+				)
+			})?;
 
-				Self::deposit_event(Event::InvestOrderUpdated(pool_id, who.clone()));
-				Ok(())
-			})
+			Self::deposit_event(Event::InvestOrderUpdated(pool_id, who));
+			Ok(())
 		}
 
 		#[pallet::weight(100)]
@@ -657,55 +654,26 @@ pub mod pallet {
 				BadOrigin
 			);
 
-			let epoch = {
-				let pool = Pool::<T>::try_get(pool_id).map_err(|_| Error::<T>::NoSuchPool)?;
-				pool.current_epoch
-			};
-			let currency = T::TrancheToken::tranche_token(pool_id, tranche_id);
-			let tranche = TrancheLocator {
-				pool_id,
-				tranche_id,
-			};
-			let pool_account = PoolLocator { pool_id }.into_account();
+			Pool::<T>::try_mutate(pool_id, |pool| -> DispatchResult {
+				let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
 
-			if let Ok(order) = Order::<T>::try_get(&tranche, &who) {
-				ensure!(
-					order.invest.saturating_add(order.redeem) == Zero::zero()
-						|| order.epoch == epoch,
-					Error::<T>::CollectRequired
+				Order::<T>::try_mutate(
+					&TrancheLocator::new(pool_id, tranche_id),
+					&who,
+					|order| -> DispatchResult {
+						ensure!(
+							order.invest.saturating_add(order.redeem) == Zero::zero()
+								|| order.epoch == pool.current_epoch,
+							Error::<T>::CollectRequired
+						);
+
+						Self::do_update_redeem_order(&who, pool, order, amount, pool_id, tranche_id)
+					},
 				)
-			}
+			})?;
 
-			Order::<T>::try_mutate(&tranche, &who, |order| -> DispatchResult {
-				if amount > order.redeem {
-					let transfer_amount = amount - order.redeem;
-					Pool::<T>::try_mutate(pool_id, |pool| {
-						let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
-						let outstanding_redeem_orders =
-							&mut pool.tranches[tranche_id.into()].outstanding_redeem_orders;
-						*outstanding_redeem_orders = outstanding_redeem_orders
-							.checked_add(&transfer_amount)
-							.ok_or(Error::<T>::Overflow)?;
-						T::Tokens::transfer(currency, &who, &pool_account, transfer_amount)
-					})?;
-				} else if amount < order.redeem {
-					let transfer_amount = order.redeem - amount;
-					Pool::<T>::try_mutate(pool_id, |pool| {
-						let pool = pool.as_mut().ok_or(Error::<T>::NoSuchPool)?;
-						let outstanding_redeem_orders =
-							&mut pool.tranches[tranche_id.into()].outstanding_redeem_orders;
-						*outstanding_redeem_orders = outstanding_redeem_orders
-							.checked_sub(&transfer_amount)
-							.ok_or(Error::<T>::Overflow)?;
-						T::Tokens::transfer(currency, &pool_account, &who, transfer_amount)
-					})?;
-				}
-				order.redeem = amount;
-				order.epoch = epoch;
-
-				Self::deposit_event(Event::InvestOrderUpdated(pool_id, who.clone()));
-				Ok(())
-			})
+			Self::deposit_event(Event::RedeemOrderUpdated(pool_id, who));
+			Ok(())
 		}
 
 		// TODO: this weight should likely scale based on collect_n_epochs
@@ -994,6 +962,95 @@ pub mod pallet {
 			T::Time::now().as_secs()
 		}
 
+		pub(crate) fn do_update_invest_order(
+			who: &T::AccountId,
+			pool: &mut PoolDetailsOf<T>,
+			order: &mut UserOrderOf<T>,
+			amount: T::Balance,
+			pool_id: T::PoolId,
+			tranche_id: T::TrancheId,
+		) -> DispatchResult {
+			let mut outstanding = &mut pool
+				.tranches
+				.get_mut(tranche_id.into())
+				.ok_or(Error::<T>::InvalidTrancheId)?
+				.outstanding_invest_orders;
+			let pool_account = PoolLocator { pool_id }.into_account();
+
+			let (send, recv, transfer_amount) = Self::update_order_amount(
+				who,
+				&pool_account,
+				&mut order.invest,
+				amount,
+				&mut outstanding,
+			)?;
+
+			order.epoch = pool.current_epoch;
+			T::Tokens::transfer(pool.currency, send, recv, transfer_amount)
+		}
+
+		pub(crate) fn do_update_redeem_order(
+			who: &T::AccountId,
+			pool: &mut PoolDetailsOf<T>,
+			order: &mut UserOrderOf<T>,
+			amount: T::Balance,
+			pool_id: T::PoolId,
+			tranche_id: T::TrancheId,
+		) -> DispatchResult {
+			let currency = T::TrancheToken::tranche_token(pool_id, tranche_id);
+			let mut outstanding = &mut pool
+				.tranches
+				.get_mut(tranche_id.into())
+				.ok_or(Error::<T>::InvalidTrancheId)?
+				.outstanding_redeem_orders;
+			let pool_account = PoolLocator { pool_id }.into_account();
+
+			let (send, recv, transfer_amount) = Self::update_order_amount(
+				who,
+				&pool_account,
+				&mut order.redeem,
+				amount,
+				&mut outstanding,
+			)?;
+
+			order.epoch = pool.current_epoch;
+			T::Tokens::transfer(currency, send, recv, transfer_amount)
+		}
+
+		fn update_order_amount<'a>(
+			who: &'a T::AccountId,
+			pool: &'a T::AccountId,
+			old_order: &mut T::Balance,
+			new_order: T::Balance,
+			pool_orders: &mut T::Balance,
+		) -> Result<(&'a T::AccountId, &'a T::AccountId, T::Balance), DispatchError> {
+			if new_order > *old_order {
+				let transfer_amount = new_order
+					.checked_sub(old_order)
+					.expect("New order larger than old order. qed.");
+
+				*pool_orders = pool_orders
+					.checked_add(&transfer_amount)
+					.ok_or(Error::<T>::Overflow)?;
+
+				*old_order = new_order;
+				Ok((who, pool, transfer_amount))
+			} else if new_order < *old_order {
+				let transfer_amount = old_order
+					.checked_sub(&new_order)
+					.expect("Old order larger than new order. qed.");
+
+				*pool_orders = pool_orders
+					.checked_sub(&transfer_amount)
+					.ok_or(Error::<T>::Overflow)?;
+
+				*old_order = new_order;
+				Ok((pool, who, transfer_amount))
+			} else {
+				Err(Error::<T>::NoNewOrder.into())
+			}
+		}
+
 		pub(crate) fn calculate_collect(
 			loc: TrancheLocator<T::PoolId, T::TrancheId>,
 			order: UserOrder<T::Balance, T::EpochId>,
```

### pallets/pools/src/tests.rs
```diff
@@ -726,3 +726,79 @@ fn test_approve_and_remove_roles() {
 		}
 	});
 }
+
+#[test]
+fn invalid_tranche_id_is_err() {
+	new_test_ext().execute_with(|| {
+		let junior_investor = Origin::signed(0);
+		let senior_investor = Origin::signed(1);
+
+		<<Test as Config>::Permission as PermissionsT<u64>>::add_permission(
+			0,
+			ensure_signed(junior_investor.clone()).unwrap(),
+			PoolRole::TrancheInvestor(1, u64::MAX),
+		)
+		.unwrap();
+
+		assert_ok!(Pools::create(
+			senior_investor.clone(),
+			0,
+			vec![TrancheInput {
+				interest_per_sec: None,
+				min_risk_buffer: None,
+				seniority: None,
+			},],
+			CurrencyId::Usd,
+			10_000 * CURRENCY
+		));
+
+		assert_noop!(
+			Pools::update_invest_order(junior_investor.clone(), 0, 1, 500 * CURRENCY),
+			Error::<Test>::InvalidTrancheId
+		);
+
+		assert_noop!(
+			Pools::update_redeem_order(junior_investor.clone(), 0, 1, 500 * CURRENCY),
+			Error::<Test>::InvalidTrancheId
+		);
+	});
+}
+
+#[test]
+fn updating_with_same_amount_is_err() {
+	new_test_ext().execute_with(|| {
+		let junior_investor = Origin::signed(0);
+		let senior_investor = Origin::signed(1);
+
+		<<Test as Config>::Permission as PermissionsT<u64>>::add_permission(
+			0,
+			ensure_signed(junior_investor.clone()).unwrap(),
+			PoolRole::TrancheInvestor(0, u64::MAX),
+		)
+		.unwrap();
+
+		assert_ok!(Pools::create(
+			senior_investor.clone(),
+			0,
+			vec![TrancheInput {
+				interest_per_sec: None,
+				min_risk_buffer: None,
+				seniority: None,
+			},],
+			CurrencyId::Usd,
+			10_000 * CURRENCY
+		));
+
+		assert_ok!(Pools::update_invest_order(
+			junior_investor.clone(),
+			0,
+			0,
+			500 * CURRENCY
+		));
+
+		assert_noop!(
+			Pools::update_invest_order(junior_investor.clone(), 0, 0, 500 * CURRENCY),
+			Error::<Test>::NoNewOrder
+		);
+	});
+}
```
