## Custody analog identified

This is a `move-examples` package, not deployed framework code — see caveat at the end.

### Title
Auction bid refund via unconditional push-transfer can permanently trap escrowed token and bid funds when a coin/FA custody path aborts - (`aptos-move/move-examples/marketplace/sources/coin_listing.move`)

### Summary
`coin_listing::bid` refunds the outbid previous bidder by directly pushing coins to their address with `aptos_account::deposit_coins`/`transfer_coins` inside the same atomic call that installs the new bid. This mirrors the reported bug class exactly: a state-transition function that must succeed to release custody (here: replace the current bid and eventually let `complete_auction` transfer the listed object) is made to depend on an unconditional push-transfer to a third party whose ability to receive funds is outside the protocol's control.

### Finding Description
`bid<CoinType>` extracts the previous bidder's `Bid`, and immediately calls `aptos_account::deposit_coins(bidder, coins)` before it will accept the new bid: [1](#0-0) 

`aptos_account::deposit_coins` (coin path) requires the recipient to be registered or "opted-in" to direct transfers, and for the fungible-asset path (`deposit_fungible_assets` → `primary_fungible_store::deposit` → `dispatchable_fungible_asset::deposit` → `fungible_asset::deposit_sanity_check`) it aborts if the recipient's primary store is frozen: [2](#0-1) [3](#0-2) 

For a dispatchable/managed `CoinType`-backed FA with a denylist/pause hook (the pattern shown in the framework's own `usdk.move`/`fa_coin.move` examples), the deposit-hook can unconditionally abort for a denylisted or paused holder: [4](#0-3) 

Because the refund and the acceptance of the new bid happen in the same transaction/function with no pull-based fallback, if the current highest bidder becomes denylisted/frozen (or, on the legacy `Coin` path, opts out of direct transfers via `set_allow_direct_coin_transfers(false)`) after bidding but before being outbid, **every subsequent `bid` call aborts**. The `Bid{bidder, coins}` remains permanently trapped inside `AuctionListing`, no higher bid can ever be installed, and once `auction_end_time` passes, `complete_auction` will pay out to that same trapped bidder — object custody transfer succeeds, but the seller/marketplace lose the ability to ever get a better price, and if the CoinType deposit to the *winning* bidder itself is what's blocked (same denylist condition, since `complete_purchase`/`complete_auction` also push funds via `aptos_account::deposit_coins`), the listed token object becomes permanently un-transferable through this contract's normal path. [5](#0-4) [6](#0-5) 

### Impact Explanation
The custody invariant broken is: "escrowed value (bid coins + listed object) must remain recoverable regardless of a third party's receive-capability." Here, an unprivileged party (the bidder itself, by causing its own store to be denylisted/frozen/opted-out, or an issuer denylisting it) can render the auction's escrow un-settleable — permanently locking the previous bid's coins and effectively freezing forward progress of the auction (no `Untransferable`/reclaim path exists in this module). This matches "permanent lock or non-recoverable loss of object/asset-held value" from the custody gate.

### Likelihood Explanation
Requires only that `CoinType` be a coin/FA with an issuer-controlled deny/freeze mechanism (a realistic and even documented pattern in this repo's own example stablecoins) or a legacy account that opts out via `set_allow_direct_coin_transfers(false)`. Any auction participant bidding with such an asset and then having that receive-path revoked (self-inflicted or issuer-inflicted) triggers the lock — no attacker-privileged action or governance assumption is needed, only a frozen/denylisted external state on the asset, exactly analogous to the USDC-blacklist precondition in the source report.

### Recommendation
Do not push refunds synchronously inside `bid`/`complete_auction`. Instead, credit the outbid amount to a claimable/pull-based balance (e.g., a `SimpleMap<address, Coin<CoinType>>` or an internal escrow store) that the previous bidder withdraws later, so a blocked recipient cannot stall the auction's core state transition. Apply the same pull-based pattern to `complete_purchase`'s royalty/commission/seller payouts.

### Proof of Concept
Not executable in this analysis; the abort path is derivable by code inspection: (1) issuer denylists bidder B's primary store for `CoinType` (per the `usdk.move`/`fa_coin.move` pause/denylist pattern), (2) any account calls `coin_listing::bid` to outbid B, (3) `aptos_account::deposit_coins(B, coins)` reaches `fungible_asset::deposit_sanity_check`/custom `deposit` hook and aborts, reverting the whole `bid` transaction, permanently blocking new bids while B's `Bid` remains embedded in `AuctionListing`.

**Caveat**: `coin_listing.move` lives under `aptos-move/move-examples/`, which is example/reference code rather than a framework module deployed at a fixed system address. Its custody-grade, mainnet-relevance is therefore weaker than a finding in `aptos-framework`/`aptos-token-objects`; this should be validated against whether any production Aptos-ecosystem contract reuses this exact `bid` pattern before treating it as a live custody bug.

### Citations

**File:** aptos-move/move-examples/marketplace/sources/coin_listing.move (L405-412)
```text
        let (previous_bidder, previous_bid, minimum_bid) = if (option::is_some(&auction_listing.current_bid)) {
            let Bid { bidder, coins } = option::extract(&mut auction_listing.current_bid);
            let current_bid = coin::value(&coins);
            aptos_account::deposit_coins(bidder, coins);
            (option::some(bidder), option::some(current_bid), current_bid + auction_listing.bid_increment)
        } else {
            (option::none(), option::none(), auction_listing.starting_bid)
        };
```

**File:** aptos-move/move-examples/marketplace/sources/coin_listing.move (L450-483)
```text
    /// Once the current time has elapsed the auctions run time, allow the auction to be settled by
    /// distributing out the asset to the winner or the auction seller if no one bid as well as
    /// giving any fees to the marketplace that hosted the auction.
    public entry fun complete_auction<CoinType>(
        completer: &signer,
        object: Object<Listing>,
    ) acquires AuctionListing {
        let listing_addr = listing::assert_started(&object);
        assert!(exists<AuctionListing<CoinType>>(listing_addr), error::not_found(ENO_LISTING));

        let AuctionListing {
            starting_bid: _,
            bid_increment: _,
            current_bid,
            auction_end_time,
            minimum_bid_time_before_end: _,
            buy_it_now_price: _,
        } = move_from<AuctionListing<CoinType>>(listing_addr);

        let now = timestamp::now_seconds();
        assert!(auction_end_time <= now, error::invalid_state(EAUCTION_NOT_ENDED));

        let seller = listing::seller(object);

        let (purchaser, coins) = if (option::is_some(&current_bid)) {
            let Bid { bidder, coins } = option::destroy_some(current_bid);
            (bidder, coins)
        } else {
            option::destroy_none(current_bid);
            (seller, coin::zero<CoinType>())
        };

        complete_purchase(completer, purchaser, object, coins, string::utf8(AUCTION_TYPE));
    }
```

**File:** aptos-move/move-examples/marketplace/sources/coin_listing.move (L485-510)
```text
    inline fun complete_purchase<CoinType>(
        completer: &signer,
        purchaser_addr: address,
        object: Object<Listing>,
        coins: Coin<CoinType>,
        type: String,
    ) {
        let token_metadata = listing::token_metadata(object);

        let price = coin::value(&coins);
        let (royalty_addr, royalty_charge) = listing::compute_royalty(object, price);
        let (seller, fee_schedule) = listing::close(completer, object, purchaser_addr);

        // Take royalty first
        if (royalty_charge != 0) {
            let royalty = coin::extract(&mut coins, royalty_charge);
            aptos_account::deposit_coins(royalty_addr, royalty);
        };

        // Take commission of what's left, creators get paid first
        let commission_charge = fee_schedule::commission(fee_schedule, price);
        let actual_commission_charge = math64::min(coin::value(&coins), commission_charge);
        let commission = coin::extract(&mut coins, actual_commission_charge);
        aptos_account::deposit_coins(fee_schedule::fee_address(fee_schedule), commission);

        // Seller gets what is left
```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L111-131)
```text
    public fun deposit_coins<CoinType>(
        to: address, coins: Coin<CoinType>
    ) acquires DirectTransferConfig {
        if (!account::exists_at(to)) {
            create_account(to);
            spec {
                // TODO(fa_migration)
                // assert coin::spec_is_account_registered<AptosCoin>(to);
                // assume aptos_std::type_info::type_of<CoinType>() == aptos_std::type_info::type_of<AptosCoin>() ==>
                //     coin::spec_is_account_registered<CoinType>(to);
            };
        };
        if (!coin::is_account_registered<CoinType>(to)) {
            assert!(
                can_receive_direct_coin_transfers(to),
                error::permission_denied(EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS)
            );
            coin::register<CoinType>(&create_signer(to));
        };
        coin::deposit<CoinType>(to, coins)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L990-999)
```text
    public fun deposit_sanity_check<T: key>(
        store: Object<T>, abort_on_dispatch: bool
    ) acquires FungibleStore, DispatchFunctionStore {
        let fa_store = borrow_store_resource(&store);
        assert!(
            !abort_on_dispatch || !has_deposit_dispatch_function(fa_store.metadata),
            error::invalid_argument(EINVALID_DISPATCHABLE_OPERATIONS)
        );
        assert!(!fa_store.frozen, error::permission_denied(ESTORE_IS_FROZEN));
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L190-210)
```text
    /// Deposit function override to ensure that the account is not denylisted and the stablecoin is not paused.
    public fun deposit<T: key>(
        store: Object<T>,
        fa: FungibleAsset,
        transfer_ref: &TransferRef,
    ) acquires State {
        assert_not_paused();
        assert_not_denylisted(object::owner(store));
        fungible_asset::deposit_with_ref(transfer_ref, store, fa);
    }

    /// Withdraw function override to ensure that the account is not denylisted and the stablecoin is not paused.
    public fun withdraw<T: key>(
        store: Object<T>,
        amount: u64,
        transfer_ref: &TransferRef,
    ): FungibleAsset acquires State {
        assert_not_paused();
        assert_not_denylisted(object::owner(store));
        fungible_asset::withdraw_with_ref(transfer_ref, store, amount)
    }
```
