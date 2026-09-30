# [?] stakepool: fix late mining report panic problem

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2021-08-21
Source: https://github.com/Phala-Network/phala-blockchain/commit/6958cabe3935fb82f7aef8585ef108d61538f53c
Type: security-commit

## Details
stakepool: fix late mining report panic problem

## Patch
### pallets/phala/src/stakepool.rs
```diff
@@ -129,6 +129,10 @@ pub mod pallet {
 		PoolSlashed(u64, BalanceOf<T>),
 		/// [pid, account, amount]
 		SlashSettled(u64, T::AccountId, BalanceOf<T>),
+		/// Some reward is dismissed because the worker is no longer bound to a pool.
+		RewardDismissedNotInPool(WorkerPublicKey, BalanceOf<T>),
+		/// Some reward is dismissed because the pool doesn't have any share.
+		RewardDismissedNoShare(u64, BalanceOf<T>),
 	}
 
 	#[pallet::error]
@@ -593,7 +597,11 @@ pub mod pallet {
 			pool_info: &mut PoolInfo<T::AccountId, BalanceOf<T>>,
 			rewards: BalanceOf<T>,
 		) {
-			if rewards > Zero::zero() && pool_info.total_shares > Zero::zero() {
+			if rewards > Zero::zero() {
+				if pool_info.total_shares == Zero::zero() {
+					Self::deposit_event(Event::<T>::RewardDismissedNoShare(pool_info.pid, rewards));
+					return;
+				}
 				let commission = pool_info.payout_commission.unwrap_or_default() * rewards;
 				pool_info.owner_reward.saturating_accrue(commission);
 				pool_info.distribute_reward(rewards - commission);
@@ -827,12 +835,20 @@ pub mod pallet {
 		/// would be clear once pool was updated
 		fn on_reward(settle: &Vec<SettleInfo>) {
 			for info in settle {
-				let pid = WorkerAssignments::<T>::get(&info.pubkey)
-					.expect("Mining workers must be in the pool; qed.");
-				let mut pool_info = Self::ensure_pool(pid).expect("Stake pool must exist; qed.");
-
 				let payout_fixed = FixedPoint::from_bits(info.payout);
 				let reward = BalanceOf::<T>::from_fixed(&payout_fixed);
+
+				let pid = match WorkerAssignments::<T>::get(&info.pubkey) {
+					Some(pid) => pid,
+					None => {
+						Self::deposit_event(Event::<T>::RewardDismissedNotInPool(
+							info.pubkey.clone(),
+							reward,
+						));
+						return;
+					}
+				};
+				let mut pool_info = Self::ensure_pool(pid).expect("Stake pool must exist; qed.");
 				Self::handle_pool_new_reward(&mut pool_info, reward);
 				StakePools::<T>::insert(&pid, &pool_info);
 			}
```
