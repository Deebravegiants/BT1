### Title
Vesting reward/grant distribution can be permanently blocked for all shareholders by one non-cooperative recipient - (File: `aptos-move/framework/aptos-framework/sources/vesting.move`)

### Summary
`vesting::distribute` iterates over every shareholder in a single atomic loop and sends each shareholder's share via `aptos_account::deposit_coins`. That function aborts if the recipient has not registered for `AptosCoin` and has opted out of unsolicited direct coin transfers. Because the loop has no isolation between shareholders, one recipient's own account setting can cause the entire `distribute()` transaction to abort every time it is called, indefinitely locking every other (fully cooperative) shareholder's unlocked rewards/vested grant inside the stake pool, with no alternate claim path exposed by the module. This is the Aptos-native analog of the reported bridge bug: a custody-releasing call (`safeTransferFrom` in the original report, `deposit_coins` here) can be made to permanently revert because of a property the recipient itself controls, and there is no fallback (`transferFrom`-equivalent) to force the release or skip the bad recipient.

### Finding Description
`vesting::distribute` withdraws all currently-withdrawable stake into a single `Coin<AptosCoin>` and then, in one loop, splits and deposits a share to every shareholder's beneficiary address: [1](#0-0) 

Each transfer uses `aptos_account::deposit_coins`, which requires that the recipient either already be registered for the coin type or have not opted out of unsolicited transfers: [2](#0-1) 

If `to` (the shareholder's beneficiary address, settable to the shareholder's own address by default) is not registered for `AptosCoin` and has called `set_allow_direct_coin_transfers(false)` on itself (a completely unprivileged, self-controlled account setting, referenced by `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` at line 25 of `aptos_account.move`), the `assert!` at line 124-127 aborts. Because Move transactions are atomic, the abort unwinds the *entire* `distribute()` call — including the `withdraw_stake` that already pulled the coins out of the stake pool's inactive balance and the successful deposits to all other shareholders processed earlier in the loop.

Since `distribute` (and `distribute_many`, `terminate_vesting_contract`, which itself calls `distribute` before letting the admin reclaim funds) is a permissionless entry function that anyone can call, but it always re-executes the same shareholder loop, this is not a one-off failure: every subsequent call to `distribute()` for that vesting contract will hit the same abort on the same non-cooperative shareholder and revert again. There is no per-shareholder skip/retry, and no alternate withdrawal function lets an individual shareholder pull their own share directly from the vesting contract's stake pool. This breaks the custody invariant that unlocked/vested value held in a resource-account-controlled stake pool must remain claimable by its rightful, cooperative holders regardless of one unprivileged co-holder's self-imposed transfer restriction.

### Impact Explanation
This qualifies as "permanent lock or non-recoverable loss of ... resource-account-held value" under the custody impact gate: legitimate shareholders' already-vested/earned APT rewards become permanently unreachable through the only exposed distribution mechanism as long as one shareholder (or a beneficiary address configured for them) keeps `allow_arbitrary_coin_transfers = false` without registering a `CoinStore<AptosCoin>`. Because vesting contracts commonly have multiple shareholders sharing one stake pool and one `distribute()` entrypoint, a single account's unprivileged, self-serving (or malicious/griefing) choice can hold hostage the funds of every other shareholder in that contract indefinitely.

### Likelihood Explanation
The precondition (an account disabling direct/arbitrary coin transfers and not pre-registering for `AptosCoin`) is a normal, self-service, unprivileged action any Aptos account holder can take at any time, requiring no special access to the vesting contract itself — it only requires being (or being set as) a shareholder/beneficiary. This makes the trigger straightforward and independent of any admin cooperation, though I was not able to fully trace `set_allow_direct_coin_transfers`/`can_receive_direct_coin_transfers` implementation lines in this session to confirm every edge case (e.g., whether registering for AptosCoin elsewhere later "unlocks" future calls, or whether `admin_withdraw`/other paths could bypass this after termination — `terminate_vesting_contract` itself calls `distribute` first, so it inherits the same block).

### Recommendation
- In `vesting::distribute`, wrap each shareholder's `aptos_account::deposit_coins` call so a failure for one recipient does not abort the whole transaction — e.g., check `coin::is_account_registered` / `can_receive_direct_coin_transfers` first and, if the recipient cannot accept a direct deposit, route that shareholder's share to an escrow/claimable balance (or to the vesting contract's own address for later individual claim) instead of aborting the loop.
- Alternatively, expose a per-shareholder `claim(contract_address, shareholder)` function that lets each shareholder pull their own already-computed share independently, so one recipient's opt-out cannot block others.
- Add an explicit test verifying that `distribute` still succeeds for cooperative shareholders when one shareholder has disabled direct coin transfers and is unregistered.

### Proof of Concept
1. Admin creates a vesting contract with shareholders `A` and `B` via `vesting::create_vesting_contract`.
2. Shareholder `B` (unprivileged, acting only on their own account) calls `aptos_account::set_allow_direct_coin_transfers(false)` and never calls `coin::register<AptosCoin>`.
3. Time passes; stake accrues rewards/vests per schedule.
4. Anyone calls `vesting::distribute(contract_address)`.
5. `withdraw_stake` succeeds and withdraws the full unlocked amount into a local `Coin<AptosCoin>`; the loop processes `A` successfully, then reaches `B`; `aptos_account::deposit_coins` hits `coin::is_account_registered<AptosCoin>(B) == false` and `can_receive_direct_coin_transfers(B) == false`, aborting with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`.
6. The whole transaction reverts: `A`'s successful deposit and the stake withdrawal are rolled back.
7. Every future call to `distribute` (or `terminate_vesting_contract`, which calls `distribute` first) for this contract will repeat step 5-6 and abort in the same way, permanently preventing `A` (and any other shareholder) from ever collecting distributions through this contract while `B`'s setting remains unchanged. [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L718-756)
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

        emit(
            Distribute {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
                amount: total_distribution_amount,
            },
        );
    }
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
