## Title
Frozen/blocked FA recipient permanently locks `vesting::distribute` and `staking_contract::distribute_internal` payouts for all other shareholders - ([File: aptos-move/framework/aptos-framework/sources/vesting.move])

### Summary
`vesting::distribute` (and analogously `staking_contract::distribute_internal`) withdraws the entire batch of unlocked coins from the underlying stake pool and then loops over *all* shareholders in a single atomic transaction, calling `aptos_account::deposit_coins`/`aptos_account::deposit_coins` for each one [1](#0-0) . Since `aptos_account::deposit_coins` ultimately routes to `coin::deposit`/`primary_fungible_store::deposit`, and Aptos fungible assets support dispatchable deposit hooks (`dispatchable_fungible_asset::deposit`) as well as store-level freezing [2](#0-1) , a single shareholder whose store is frozen or whose custom deposit hook aborts (e.g. a denylist/pause similar to USDC) will cause the entire `distribute()` transaction to abort. This is the same custody invariant break as the external report: an unprivileged, blocklisted party's forced-push failure blocks legitimate value that belongs to *other, unrelated* holders.

### Finding Description
`distribute_internal`/`distribute` extract the *entire* withdrawable amount up front and then iterate `shareholders()` in one Move transaction, depositing to each recipient with no isolation or try/catch semantics [3](#0-2)  and [4](#0-3) . `aptos_account::deposit_coins`/`deposit_fungible_assets` do not shield callers from a reverting recipient store: `coin::deposit` and `primary_fungible_store::deposit` (via `dispatchable_fungible_asset::deposit`) can abort if the store is frozen or if a custom deposit hook registered by the asset issuer rejects the transfer [5](#0-4) . Because Move transactions are atomic, one shareholder's blocked deposit aborts the whole distribution, and since the function always re-derives the full withdrawable pool on every call, retrying `distribute()` will deterministically fail again — permanently locking every other shareholder's already-vested/earned funds inside the stake pool/vesting contract with no way to skip the blocked party.

### Impact Explanation
This breaks the custody invariant that legitimate holders' funds must remain recoverable independent of an unrelated third party's frozen/denylisted status. All co-shareholders in a vesting or staking-contract pool (not just the blocked one) lose access to unlocked rewards/principal indefinitely, since `distribute`/`distribute_many` and `distribute_internal` provide no mechanism to exclude or checkpoint a failing recipient.

### Likelihood Explanation
Low-to-moderate: this requires the vesting/staking-contract distribution pool to include a shareholder whose primary fungible store becomes frozen (e.g., an admin-controlled freeze/denylist FA is used, or the account itself calls `object::burn` on its own primary store combined with unusual reentrant dispatch logic) or a shareholder address that stops accepting deposits. For plain APT (the framework's own native use of `vesting`/`staking_contract`), APT cannot be frozen or dispatched (see the comment in `aptos_account::fungible_transfer_only` noting "APT cannot be frozen or have dispatch") [6](#0-5) , so likelihood is low for the framework's primary intended usage, but the code path itself (loop over untrusted recipients within one atomic distribution) is a latent design flaw that would manifest with any freezable/dispatchable coin.

### Recommendation
Change `distribute`/`distribute_internal` to a pull/claim pattern: credit each shareholder's share to an internal balance/`Pool` record and let shareholders withdraw individually (mirroring the external report's remediation), rather than force-pushing deposits to all shareholders in a single atomic loop. Alternatively, wrap each per-shareholder deposit so failures are isolated (e.g., skip and re-queue a failing recipient's share) so one shareholder cannot block payouts to the rest.

### Proof of Concept
Not independently verified end-to-end (would require constructing a fungible-asset-based vesting/staking-contract test where a shareholder's coin store is frozen via a `TransferRef`/dispatch hook, then calling `vesting::distribute` and observing the abort blocks all other shareholders' payouts). This is a design-level trace based on the loop in `vesting.move:730-741` and `staking_contract.move:888-911` combined with `aptos_account::deposit_coins`/`primary_fungible_store::deposit`'s reliance on non-reverting recipients; a Devin session with test execution would be needed to confirm concretely whether current mainnet-relevant coin types (all currently non-freezable/non-dispatchable APT) make this exploitable today, or whether it is latent pending adoption of dispatchable/freezable coins in these pools.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L718-747)
```text
    /// Distribute any withdrawable stake from the stake pool.
    public entry fun distribute(contract_address: address) acquires VestingContract {
        assert_active_vesting_contract(contract_address);

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        let coins = withdraw_stake(vesting_contract, contract_address);
        let total_distribution_amount = coin::value(&coins);
        if (total_distribution_amount == 0) {
            coin::destroy_zero(coins);
            return
        };

        // Distribute coins to all shareholders in the vesting contract.
        let grant_pool = &vesting_contract.grant_pool;
        let shareholders = &grant_pool.shareholders();
        shareholders.for_each_ref(|shareholder| {
            let shareholder = *shareholder;
            let shares = pool_u64::shares(grant_pool, shareholder);
            let amount = pool_u64::shares_to_amount_with_total_coins(grant_pool, shares, total_distribution_amount);
            let share_of_coins = coin::extract(&mut coins, amount);
            let recipient_address = get_beneficiary(vesting_contract, shareholder);
            aptos_account::deposit_coins(recipient_address, share_of_coins);
        });

        // Send any remaining "dust" (leftover due to rounding error) to the withdrawal address.
        if (coin::value(&coins) > 0) {
            aptos_account::deposit_coins(vesting_contract.withdrawal_address, coins);
        } else {
            coin::destroy_zero(coins);
        };
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L187-199)
```text
    /// Deposit fungible asset `fa` to the given account's primary store.
    public fun deposit(owner: address, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(owner, metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }

    /// Deposit fungible asset `fa` to the given account's primary store using signer.
    public fun deposit_with_signer(owner: &signer, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(signer::address_of(owner), metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L888-911)
```text
        // Buy all recipients out of the distribution pool.
        while (distribution_pool.shareholders_count() > 0) {
            let recipients = distribution_pool.shareholders();
            let recipient = recipients[0];
            let current_shares = distribution_pool.shares(recipient);
            let amount_to_distribute =
                distribution_pool.redeem_shares(recipient, current_shares);
            // If the recipient is the operator, send the commission to the beneficiary instead.
            if (recipient == operator) {
                recipient = beneficiary_for_operator(operator);
            };
            aptos_account::deposit_coins(
                recipient, coin::extract(&mut coins, amount_to_distribute)
            );

            emit(
                Distribute {
                    operator,
                    pool_address,
                    recipient,
                    amount: amount_to_distribute
                }
            );
        };
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L97-119)
```text
    /// Deposit `amount` of the fungible asset to `store`.
    ///
    /// The semantics of deposit will be governed by the function specified in DispatchFunctionStore.
    public fun deposit<T: key>(store: Object<T>, fa: FungibleAsset) acquires TransferRefStore {
        fungible_asset::deposit_sanity_check(store, false);
        let func_opt = fungible_asset::deposit_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_deposit_hook(store, fa, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_deposit(
                    store,
                    fa,
                    borrow_transfer_ref(store),
                    func
                )
            }
        } else {
            fungible_asset::unchecked_deposit(store.object_address(), fa)
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L250-259)
```text

        // use internal APIs, as they skip:
        // - owner, frozen and dispatchable checks
        // as APT cannot be frozen or have dispatch, and PFS cannot be transfered
        // (PFS could potentially be burned. regular transfer would permanently unburn the store.
        // Ignoring the check here has the equivalent of unburning, transfers, and then burning again)
        fungible_asset::unchecked_deposit(
            recipient_store, fungible_asset::unchecked_withdraw(sender_store, amount)
        );
    }
```
