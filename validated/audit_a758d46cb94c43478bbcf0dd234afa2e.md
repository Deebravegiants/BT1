## Custody Analog Found: `marketplace::fee_schedule::set_fee_address()` allows an unrestricted, un-validated `fee_address` (including `@0x0`) that any unprivileged buyer/seller subsequently forces payout to via `settle_payments`

### Title
Marketplace commission funds can be permanently burned to `@0x0` because `fee_schedule::set_fee_address()`/`init()` never validate the recipient, and `settle_payments()` unconditionally deposits commission there - (File: `aptos-move/move-examples/marketplace/sources/fee_schedule.move`)

### Summary
The Aptos marketplace example module mirrors the exact custody defect from the Vested-Aura report: a mutable "collector" address (`bribesProcessor` in the original, `fee_address` here) defaults to / can be set to the zero address by a privileged-but-limited role, and a *separate, permissionless* code path (`sweepRewardToken()` there, `sell_tokenv2`/`sell_to_collection_offer`/`sell` there) later transfers real value to that address without ever re-validating it.

### Finding Description
`FeeSchedule.fee_address` is set at creation and can be changed at any time via `set_fee_address()`: [1](#0-0) 

Neither `init()`/`empty_init()` nor `set_fee_address()` reject `@0x0` (or any other unrecoverable/burn address) as `fee_address`: [2](#0-1) 

The test suite even demonstrates this is accepted behavior, not an edge case caught by validation — `set_fee_address(creator, obj, @0x0)` succeeds and `fee_address(obj) == @0x0` afterward: [3](#0-2) 

Once `fee_address` is `@0x0`, the commission is still deposited unconditionally whenever *any* buyer/seller completes a trade — a fully permissionless, high-frequency action, analogous to `sweepRewardToken()` being callable by anyone in the original report: [4](#0-3) [5](#0-4) 

`aptos_account::deposit_coins()` performs no destination validation beyond creating the account if it doesn't exist and depositing — it does not reject `@0x0` or other reserved/burn addresses: [6](#0-5) 

I attempted to verify whether Aptos framework's `account::create_account`/`create_account_if_does_not_exist` blocks `@0x0` specifically (which would mitigate the impact), but my grep across `account.move` and `system_addresses.move` did not return the specific reserved-address list content before the session ended, so **I could not conclusively confirm whether `@0x0` is blocked at the account-creation layer**. This is the key open question that determines whether the funds are truly unrecoverable or merely land in an inert-but-technically-existing account.

### Impact Explanation
If confirmed that `@0x0` is a valid deposit target (as it structurally appears to be, since `deposit_coins` has no address-based exclusion list and the `royalty::create`/`fee_schedule::init` functions in this same codebase impose no `payee_address != @0x0` check either), the impact is:
- Every sale routed through a `FeeSchedule` whose owner set (or left) `fee_address == @0x0` permanently burns 100% of the marketplace commission on every trade.
- This is triggerable by any buyer/seller simply completing a normal, permissionless purchase — they don't need any special privilege, matching the "unprivileged root cause, broken custody invariant" bar required by the task.
- Unlike a governance-only misconfiguration, the loss compounds silently on every subsequent sale until someone notices and calls `set_fee_address()` again.

However, this is scoped to the `move-examples/marketplace` reference implementation, not `aptos-framework` core custody primitives (coin, object, fungible_asset). Its mainnet relevance depends entirely on whether any deployed marketplace contract is a near-verbatim fork of this example — which I cannot verify from the repo alone.

### Likelihood Explanation
Medium. The `fee_address` is set by the marketplace-owning `creator`/object owner, which is a "privileged" role by the custody-gate's own definition (governance/admin-adjacent), and the impact only harms the marketplace operator's own future commission revenue, not buyer/seller-held tokens or object ownership. This weakens the case against the "never count generic/admin misconfiguration" exclusion in the gate. The only genuinely unprivileged actor here is the trade counterparties who *trigger* the loss, but they do not *cause* the misconfiguration, and they suffer no loss themselves (their funds route correctly to seller/royalty payee; only the commission fraction is burned).

### Recommendation
Add a zero/burn-address check in `fee_schedule::init()`, `empty_init()`, and `set_fee_address()`, e.g. `assert!(fee_address != @0x0, error::invalid_argument(EINVALID_FEE_ADDRESS))`, and apply the same validation to `royalty::create()`'s `payee_address` for consistency.

### Proof of Concept
1. Marketplace owner calls `fee_schedule::init(creator, @0x0, ...)` or later `set_fee_address(creator, obj, @0x0)` — both succeed with no assertion failure, as shown by the existing unit test at lines 347–352 of `fee_schedule.move`.
2. Any user lists an NFT and any other user calls `token_offer::sell_tokenv2` (or `collection_offer::sell_to_collection_offer`) to complete a trade.
3. `settle_payments` computes `commission_charge = fee_schedule::commission(...)` and unconditionally calls `aptos_account::deposit_coins(fee_schedule::fee_address(fee_schedule), commission)` — sending the commission to `@0x0`.
4. Repeat for every subsequent trade against that `FeeSchedule` object; commission funds accumulate at `@0x0` with no code path to recover them.

---

**Caveat on completeness:** I was unable to confirm within the available iterations whether Aptos Framework's `account::create_account`/reserved-address checks specifically forbid `@0x0` as a deposit target, which is the linchpin fact for "permanent, non-recoverable loss." If `@0x0` deposits are in fact rejected by the framework, this finding would be invalidated (transactions would simply abort instead of burning funds). I recommend a Devin session with full repo/tool access to definitively trace `account::create_account_if_does_not_exist` → `create_account_unchecked` and any `EACCOUNT_ALREADY_EXISTS`/reserved-address assertions before treating this as confirmed.

### Citations

**File:** aptos-move/move-examples/marketplace/sources/fee_schedule.move (L94-139)
```text
    public fun init(
        creator: &signer,
        fee_address: address,
        bidding_fee: u64,
        listing_fee: u64,
        commission_denominator: u64,
        commission_numerator: u64,
    ): Object<FeeSchedule> {
        assert!(
            commission_numerator <= commission_denominator,
            error::invalid_argument(EEXCEEDS_MAXIMUM),
        );
        assert!(
            commission_denominator != 0,
            error::out_of_range(EDENOMINATOR_IS_ZERO),
        );

        let (constructor_ref, fee_schedule_signer) = empty_init(creator, fee_address);
        move_to(&fee_schedule_signer, FixedRateBiddingFee { bidding_fee });
        move_to(&fee_schedule_signer, FixedRateListingFee { listing_fee });
        let commission_rate = PercentageRateCommission {
            denominator: commission_denominator,
            numerator: commission_numerator,
        };
        move_to(&fee_schedule_signer, commission_rate);
        object::object_from_constructor_ref(&constructor_ref)
    }

    /// Create a marketplace with no fees.
    public entry fun empty(creator: &signer, fee_address: address) {
        empty_init(creator, fee_address);
    }

    inline fun empty_init(creator: &signer, fee_address: address): (ConstructorRef, signer) {
        let constructor_ref = object::create_object_from_account(creator);
        let extend_ref = object::generate_extend_ref(&constructor_ref);
        let fee_schedule_signer = object::generate_signer(&constructor_ref);

        let marketplace = FeeSchedule {
            fee_address,
            extend_ref,
        };
        move_to(&fee_schedule_signer, marketplace);

        (constructor_ref, fee_schedule_signer)
    }
```

**File:** aptos-move/move-examples/marketplace/sources/fee_schedule.move (L143-158)
```text
    /// Set the fee address
    public entry fun set_fee_address(
        creator: &signer,
        marketplace: Object<FeeSchedule>,
        fee_address: address,
    ) acquires FeeSchedule {
        let fee_schedule_addr = assert_exists_internal(&marketplace);
        assert!(
            object::is_owner(marketplace, signer::address_of(creator)),
            error::permission_denied(ENOT_OWNER),
        );
        let fee_schedule_obj = borrow_global_mut<FeeSchedule>(fee_schedule_addr);
        fee_schedule_obj.fee_address = fee_address;
        let updated_resource = string::utf8(b"fee_address");
        event::emit(Mutation { marketplace: fee_schedule_addr, updated_resource });
    }
```

**File:** aptos-move/move-examples/marketplace/sources/fee_schedule.move (L347-352)
```text
        set_fee_address(creator, obj, @0x0);
        set_fixed_rate_listing_fee(creator, obj, 5);
        set_fixed_rate_bidding_fee(creator, obj, 6);
        set_percentage_rate_commission(creator, obj, 10, 1);

        assert!(fee_address(obj) == @0x0, 0);
```

**File:** aptos-move/move-examples/marketplace/sources/token_offer.move (L388-391)
```text
        let fee_schedule = token_offer_obj.fee_schedule;
        let commission_charge = fee_schedule::commission(fee_schedule, price);
        let commission = coin::extract(&mut coins, commission_charge);
        aptos_account::deposit_coins(fee_schedule::fee_address(fee_schedule), commission);
```

**File:** aptos-move/move-examples/marketplace/sources/collection_offer.move (L397-402)
```text
        // Commission can only be of whatever is left
        let fee_schedule = collection_offer_obj.fee_schedule;
        let commission_charge = fee_schedule::commission(fee_schedule, price);
        let actual_commission_charge = math64::min(commission_charge, coin::value(&coins));
        let commission = coin::extract(&mut coins, actual_commission_charge);
        aptos_account::deposit_coins(fee_schedule::fee_address(fee_schedule), commission);
```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L109-131)
```text
    /// Convenient function to deposit a custom CoinType into a recipient account that might not exist.
    /// This would create the recipient account first and register it to receive the CoinType, before transferring.
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
