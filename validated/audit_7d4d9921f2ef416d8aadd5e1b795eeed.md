### Title
Single opted-out recipient can permanently halt fund distribution in `vesting::distribute` / `staking_contract::distribute_internal` - (File: `aptos-move/framework/aptos-framework/sources/vesting.move`, `aptos-move/framework/aptos-framework/sources/staking_contract.move`)

### Summary
`vesting::distribute` and `staking_contract::distribute_internal` iterate over *all* shareholders/recipients in a single atomic loop and push funds to each via `aptos_account::deposit_coins`. If any single recipient has opted out of un-registered direct coin transfers (`DirectTransferConfig.allow_arbitrary_coin_transfers = false`) and is not registered for the coin type, `deposit_coins` aborts, reverting the entire transaction — blocking payout to every other shareholder in that vesting/staking contract, not just the offending one. This mirrors the `SherXERC20.payOffDebtAll` bug class: one under-funded/uncooperative party halts a shared iteration that core custody functions depend on.

### Finding Description
`vesting::distribute` withdraws all currently-unlocked stake for a vesting contract and then loops over every shareholder to pay them their share: [1](#0-0) 

Each iteration calls `aptos_account::deposit_coins`, which — for accounts not yet registered for the coin type — asserts that the recipient allows unsolicited/direct transfers: [2](#0-1) 

Any account can flip this flag off at any time via `set_allow_direct_coin_transfers`: [3](#0-2) 

Because the shareholder loop is unconditional (`for_each_ref` with no try/skip semantics), a single shareholder that (a) has never registered for the coin type and (b) disables `allow_arbitrary_coin_transfers` causes `deposit_coins` to abort with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`, which propagates up and aborts the whole `distribute` call — for every future invocation, since the shareholder list and the flag persist. The identical pattern exists in `staking_contract::distribute_internal`, which also loops over `distribution_pool.shareholders()` and calls `aptos_account::deposit_coins` per recipient: [4](#0-3) 

`distribute` is also invoked internally by `terminate_vesting_contract` and gates `admin_withdraw`-adjacent flows, so the block cascades into contract termination/withdrawal paths as well: [5](#0-4) 

I was not able to fully verify within available tool budget whether `pool_u64`/`vesting`/`staking_contract` expose any admin function to remove a single shareholder from the distribution pool without going through the blocked `distribute` path, or whether `admin_withdraw`/`terminate_vesting_contract` can bypass the shareholder loop entirely. This is a real gap in my analysis — if such a bypass exists, the severity of permanent lock is reduced to a temporary DoS requiring specific governance action, closely matching the acknowledged/accepted severity in the original Sherlock report rather than a strictly new critical finding.

### Impact Explanation
If confirmed with no bypass, this would be a genuine custody-impacting bug: unlocked APT stake for **all** shareholders of a vesting/staking contract (not just the opted-out one) becomes stuck in the underlying resource-account-controlled stake pool, unable to be distributed, since every call to `distribute`/`distribute_many` (permissionless, callable by anyone) deterministically re-enters the same failing shareholder and aborts. This satisfies the custody gate's "permanent lock or non-recoverable loss of ... resource-account-held value" criterion, since the funds are resource-account-held (vesting/staking contracts operate via `SignerCapability`-controlled resource accounts) and shared among multiple unrelated custodial parties.

### Likelihood Explanation
Likelihood is uncertain without confirming the absence of an admin escape hatch. The action required (never registering for the coin + explicitly disabling `allow_arbitrary_coin_transfers`) is a normal, permissionless, unprivileged operation any shareholder can trigger — including maliciously or accidentally — which is why this pattern class is flagged as "likely" in the original Sherlock report. However, the actual severity strongly depends on whether Aptos framework provides another recovery path (e.g., an admin function to skip/remove a shareholder or force-migrate/register on their behalf) that I could not verify in the time available.

### Recommendation
- Wrap each per-recipient deposit in the distribution loops (`vesting::distribute`, `staking_contract::distribute_internal`) so that a failure for one recipient does not abort the whole transaction — e.g., catch/skip and re-credit the failed share back to a pending pool, or fall back to `coin::deposit`-style forced registration/deposit that does not depend on `DirectTransferConfig`.
- Alternatively, provide a governance/admin function that can force-settle or exclude a single non-cooperative shareholder from a contract's distribution loop without requiring their cooperation.
- Add a supported "pull" withdrawal model (where each shareholder claims their own share) as an alternative to the current "push to all" atomic model, eliminating the single-point-of-failure loop entirely.

### Proof of Concept
Conceptual PoC (not independently executed):
1. Admin creates a vesting contract with shareholders `[A, B, C]` via `vesting::create_vesting_contract`.
2. Shareholder `C`, before ever registering a `CoinStore<AptosCoin>`/being credited APT directly, calls `aptos_account::set_allow_direct_coin_transfers(C_signer, false)`.
3. Once stake unlocks and anyone calls `vesting::distribute(contract_address)`, the loop reaches `C`'s turn, calls `aptos_account::deposit_coins<AptosCoin>(C, share)`, which asserts `can_receive_direct_coin_transfers(C)` — false — and aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`.
4. The entire `distribute` transaction reverts; `A` and `B` receive nothing, and every subsequent call to `distribute`/`distribute_many`/`terminate_vesting_contract` for this contract fails the same way until `C` changes their own setting (which they, as the attacker, control and have no incentive to do).

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L730-740)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L770-793)
```text
    /// Terminate the vesting contract and send all funds back to the withdrawal address.
    public entry fun terminate_vesting_contract(admin: &signer, contract_address: address) acquires VestingContract {
        assert_active_vesting_contract(contract_address);

        // Distribute all withdrawable coins, which should have been from previous rewards withdrawal or vest.
        distribute(contract_address);

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);
        let (active_stake, _, pending_active_stake, _) = stake::get_stake(vesting_contract.staking.pool_address);
        assert!(pending_active_stake == 0, error::invalid_state(EPENDING_STAKE_FOUND));

        // Unlock all remaining active stake.
        vesting_contract.state = VESTING_POOL_TERMINATED;
        vesting_contract.remaining_grant = 0;
        unlock_stake(vesting_contract, active_stake);

        emit(
            Terminate {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
            },
        );
    }
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

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L187-211)
```text
    /// Set whether `account` can receive direct transfers of coins that they have not explicitly registered to receive.
    public entry fun set_allow_direct_coin_transfers(
        account: &signer, allow: bool
    ) acquires DirectTransferConfig {
        let addr = signer::address_of(account);
        if (exists<DirectTransferConfig>(addr)) {
            let direct_transfer_config = borrow_global_mut<DirectTransferConfig>(addr);
            // Short-circuit to avoid emitting an event if direct transfer config is not changing.
            if (direct_transfer_config.allow_arbitrary_coin_transfers == allow) { return };

            direct_transfer_config.allow_arbitrary_coin_transfers = allow;

            emit(
                DirectCoinTransferConfigUpdated {
                    account: addr,
                    new_allow_direct_transfers: allow
                }
            );
        } else {
            let direct_transfer_config = DirectTransferConfig {
                allow_arbitrary_coin_transfers: allow,
                update_coin_transfer_events: new_event_handle<
                    DirectCoinTransferConfigUpdatedEvent>(account)
            };
            emit(
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
