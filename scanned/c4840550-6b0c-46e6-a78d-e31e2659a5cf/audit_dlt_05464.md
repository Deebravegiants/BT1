# [?] fix dust panic on first loop (#1255)

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-05-06
Source: https://github.com/Phala-Network/phala-blockchain/commit/efb85e6d39fe219708fec5cd12cd9a2a4bde9d27
Type: security-commit

## Details
fix dust panic on first loop (#1255)

* fix dust panic on first loop

* change min balance limit

* fix current data

* use variables instead of magic number

* use T::WPhaMinBalance

* use T::WPhaMinBalance

## Patch
### pallets/phala/src/compute/base_pool.rs
```diff
@@ -1020,7 +1020,12 @@ pub mod pallet {
 			pool_info: &mut BasePool<T::AccountId, BalanceOf<T>>,
 			nft: &NftAttr<BalanceOf<T>>,
 		) -> bool {
-			if is_nondust_balance(nft.shares) {
+			let price = match pool_info.share_price() {
+				Some(price) => price,
+				None => return false,
+			};
+			let current_balance = bmul(nft.shares, &price);
+			if current_balance > T::WPhaMinBalance::get() {
 				return false;
 			}
 			pool_info.total_shares -= nft.shares;
@@ -1063,6 +1068,12 @@ pub mod pallet {
 						Self::get_nft_attr_guard(pool_info.cid, withdraw.nft_id)
 							.expect("get nftattr should always success; qed.");
 					let mut withdraw_nft = withdraw_nft_guard.attr.clone();
+					if Self::maybe_remove_dust(pool_info, &withdraw_nft) {
+						pool_info.withdraw_queue.pop_front();
+						Self::burn_nft(&pallet_id(), pool_info.cid, withdraw.nft_id)
+							.expect("burn nft should always success");
+						continue;
+					}
 					// Try to fulfill the withdraw requests as much as possible
 					let free_shares = if price == fp!(0) {
 						withdraw_nft.shares // 100% slashed
```

### pallets/phala/src/test.rs
```diff
@@ -2002,7 +2002,7 @@ fn mock_asset_id() {
 		<Test as wrapped_balances::Config>::WPhaAssetId::get(),
 		1,
 		true,
-		1000000000,
+		100000000,
 	)
 	.expect("create should success .qed");
 }
```
