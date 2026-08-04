### Title
Item value can be devalued via attribute/metadata mutation between `set_price` and `buy_item`, mirroring the Teller "collateral not locked at listing" honeypot pattern - (File: `substrate/frame/nfts/src/features/buy_sell.rs`, `substrate/frame/nfts/src/features/attributes.rs`)

### Summary
The Teller bug stems from the fact that the borrower retains full control over the "collateral" asset between the moment a lender is shown an attractive offer (`submitBid`) and the moment the lender's acceptance transaction actually executes (`lenderAcceptBid`), letting the borrower devalue the collateral in between. The `pallet-nfts` / `pallet-uniques` marketplace primitives (`set_price` → `buy_item`) have the analogous structural gap: the seller (item owner) is never required to relinquish control of the item when listing it for sale, and can freely mutate the item's on-chain attributes/metadata up until the exact block the buyer's `buy_item` extrinsic executes, without `do_buy_item` validating that the item's state still matches what the buyer expects.

### Finding Description
`do_set_price` (`substrate/frame/nfts/src/features/buy_sell.rs:72-113`) only writes an `(price, whitelisted_buyer)` tuple into `ItemPriceOf`; it never locks the item or freezes its attributes/metadata. The item's `owner` remains unchanged and retains all owner-level permissions.

`do_buy_item` (`substrate/frame/nfts/src/features/buy_sell.rs:128-171`) only re-reads `Item` for ownership/details and `ItemPriceOf` for price at execution time, then transfers currency and calls `do_transfer`: [1](#0-0) 

Nothing in this path checks whether the item's `AttributeNamespace::ItemOwner` attributes or metadata have changed since the price was set. Meanwhile, `do_set_attribute` (`substrate/frame/nfts/src/features/attributes.rs:50-86`) only gates the `CollectionOwner` namespace on the `UnlockedAttributes`/`UnlockedItemAttributes` lock settings: [2](#0-1) 

The `ItemOwner` namespace (which the item owner controls via their own `is_valid_namespace` check) and item metadata (`do_set_item_metadata`, gated only by `ItemSetting::UnlockedMetadata`, which is enabled by default) can both still be freely rewritten by the current owner at any time before `buy_item` executes — including in the same block, front-running the buyer's transaction.

This is structurally identical to the Teller root cause: the asset being "sold"/"pledged" is not escrowed or its material properties frozen at the time the offer is advertised (`set_price` / `submitBid`), so the party who benefits from the trade completing (the seller/borrower) can unilaterally alter the asset's value between advertisement and finalization (`buy_item` / `lenderAcceptBid`), and the finalization logic performs no re-validation of the asset's state.

### Impact Explanation
A buyer who inspects an item's attributes/metadata (e.g., a claimed rarity trait, a linked "backing" attribute, or descriptive data used off-chain by a marketplace UI to justify the listed price) and submits `buy_item` at the advertised price can have the seller front-run/precede that transaction with `set_attribute`/`clear_attribute`/`set_metadata` calls that strip or alter the very attributes that justified the price, while `do_buy_item` still executes the trade unconditionally as long as `bid_price >= price_info.0`. The buyer pays full price for an item whose material value has been reduced immediately beforehand, with no way for the pallet logic to detect or prevent it. This is a direct funds-loss vector for the buyer, same class of harm as in the Teller report (lender pays full value, receives devalued backing asset).

### Likelihood Explanation
Any unprivileged account that owns an NFT item can execute this: `set_price`, then `set_attribute`/`clear_attribute` calls, both are plain `ensure_signed` extrinsics with no special role required beyond being the item owner. No trusted role, no bridge/node access, and no mocked path is required — the entire flow (`set_price` → attribute mutation → `buy_item`) runs through real, reachable dispatchables in `pallet-nfts`/`pallet-uniques`. The attacker only needs to time their attribute-mutation transaction to land in the same block as, or immediately before, the victim's `buy_item` call, which is a standard front-running pattern achievable by any account with mempool visibility.

### Recommendation
- Snapshot (or hash) the relevant attribute/metadata state at `set_price` time and require `buy_item` to pass a matching commitment (e.g., a hash of the attributes the buyer inspected), rejecting the buy if the on-chain state has diverged.
- Alternatively, lock item attributes/metadata (`ItemSetting::UnlockedAttributes`/`UnlockedMetadata`) automatically for the `ItemOwner` namespace whenever `ItemPriceOf` is set, and only unlock them again once the price is cleared or the sale completes.
- Document clearly (as Teller's team did) that buyers should treat any NFT with mutable, unlocked attributes as carrying this risk, and expose a way for marketplaces/front-ends to check `ItemSetting::UnlockedAttributes`/`UnlockedMetadata` before recommending a purchase.

### Proof of Concept
1. Owner `A` mints item `X` in a collection with `ItemSetting::Transferable` and (default) `UnlockedMetadata`/attributes for `ItemOwner` namespace.
2. `A` sets `ItemOwner`-namespace attribute `"trait" -> "rare"` via `set_attribute` and calls `Nfts::set_price(collection, X, Some(100), None)`.
3. Buyer `B`, seeing attribute `"trait" = "rare"`, submits `Nfts::buy_item(collection, X, 100)`.
4. `A` submits `Nfts::set_attribute(collection, Some(X), ItemOwner, "trait", "common")` (or clears/rewrites metadata) in the same block, ordered before `B`'s transaction (e.g. via higher tip/front-running).
5. Both transactions execute successfully: `do_set_attribute` succeeds unconditionally for the `ItemOwner` namespace (no interaction with `ItemPriceOf`), and `do_buy_item` succeeds because it only checks `bid_price >= price_info.0` and ownership — never the attribute state.
6. Result: `B` pays 100 and receives item `X` now carrying attribute `"trait" = "common"`, having paid the "rare" price for a "common" item, with no on-chain mechanism having prevented or even flagged the change.

### Citations

**File:** substrate/frame/nfts/src/features/buy_sell.rs (L139-160)
```rust
		let details = Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownItem)?;
		ensure!(details.owner != buyer, Error::<T, I>::NoPermission);

		let price_info =
			ItemPriceOf::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::NotForSale)?;

		ensure!(bid_price >= price_info.0, Error::<T, I>::BidTooLow);

		if let Some(only_buyer) = price_info.1 {
			ensure!(only_buyer == buyer, Error::<T, I>::NoPermission);
		}

		T::Currency::transfer(
			&buyer,
			&details.owner,
			price_info.0,
			ExistenceRequirement::KeepAlive,
		)?;

		let old_owner = details.owner.clone();

		Self::do_transfer(collection, item, buyer.clone(), |_, _| Ok(()))?;
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L70-86)
```rust
		// for the `CollectionOwner` namespace we need to check if the collection/item is not locked
		match namespace {
			AttributeNamespace::CollectionOwner => match maybe_item {
				None => {
					ensure!(
						collection_config.is_setting_enabled(CollectionSetting::UnlockedAttributes),
						Error::<T, I>::LockedCollectionAttributes
					)
				},
				Some(item) => {
					let maybe_is_locked = Self::get_item_config(&collection, &item)
						.map(|c| c.has_disabled_setting(ItemSetting::UnlockedAttributes))?;
					ensure!(!maybe_is_locked, Error::<T, I>::LockedItemAttributes);
				},
			},
			_ => (),
		}
```
