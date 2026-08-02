## Custody Invariant Reduction

The external bug reduces to one invariant: **a contract must report and move only the value it explicitly computed as its own operation's output, never the ambient balance of its custody address**, because any value accidentally sitting in that address (donations, stray transfers) gets silently absorbed into the next accounted operation and paid out to whoever triggers it.

## Candidate Paths Considered

1. `aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move` — hook dispatch returns caller-supplied `FunctionInfo` results; deposit/withdraw amounts are still passed explicitly and checked via `EAMOUNT_MISMATCH` in `transfer_assert_minimum_deposit` [1](#0-0) . No unchecked "balance-of" substitution for a return value — discarded.
2. `aptos-move/move-examples/shared_account/sources/shared_account.move` `disperse` — uses `coin::balance<CoinType>(resource_addr)` as the full amount to redistribute [2](#0-1) , structurally identical to the wstETH bug, but this lives under `move-examples`, which is explicitly excluded by the custody impact gate. Discarded.
3. `aptos-move/framework/aptos-framework/sources/resource_account.move` container/capability retrieval — correctly bounded by `simple_map` key checks; no balance substitution. Discarded.
4. `aptos-move/framework/aptos-framework/sources/vesting.move` `withdraw_stake` — kept as strongest candidate.

## Strongest Candidate: `vesting.move::withdraw_stake`

```move
fun withdraw_stake(vesting_contract: &VestingContract, contract_address: address): Coin<AptosCoin> {
    // Claim any withdrawable distribution from the staking contract. The withdrawn coins will be sent directly to
    // the vesting contract's account.
    staking_contract::distribute(contract_address, vesting_contract.staking.operator);
    let withdrawn_coins = coin::balance<AptosCoin>(contract_address);
    let contract_signer = &get_vesting_account_signer_internal(vesting_contract);
    coin::withdraw<AptosCoin>(contract_signer, withdrawn_coins)
}
``` [3](#0-2) 

Instead of tracking the actual amount `staking_contract::distribute` released into the vesting resource account, it reads `coin::balance<AptosCoin>(contract_address)` — the entire APT balance sitting at the resource-account address — and treats that whole amount as "withdrawn stake" for downstream distribution to shareholders per the pool's share structure, as documented: "shareholders can call distribute() to send all withdrawable funds to all shareholders based on the original grant's shares structure" [4](#0-3) .

The vesting contract account is a `resource_account` created via `account::create_resource_account` inside `create_vesting_contract_account` [5](#0-4) , and its address is public (`contract_address`), so anyone can send APT to it directly with a plain coin transfer.

## Impact

Any APT accidentally (or intentionally) transferred to a vesting contract's resource-account address is swept up the next time `distribute()` is triggered, because `withdraw_stake` cannot distinguish "genuinely unlocked stake rewards" from "ambient balance." That value is then split among the `grant_pool` shareholders per `pool_u64` shares — i.e., control/custody of that value is silently reassigned from the original sender to the vesting contract's shareholder set, with no recovery path for the sender. This is a supply/custody accounting corruption that moves APT to the wrong holder, matching the required impact class of "supply or custody accounting corruption that moves value to the wrong holder."

## Likelihood / Caveats

`unlock_rewards`, `vest`, and (per the module doc) `distribute` are permissionless entry points taking only `contract_address`, so no privileged signer is required to trigger the sweep — this satisfies the "unprivileged root cause" requirement. I was not able to fully read the body of the public `distribute` entry function in this pass (only `withdraw_stake`, `unlock_rewards`, and `vest` were confirmed) — the exact call chain from `distribute()` to `withdraw_stake` and the final coin distribution to shareholders should be verified before treating this as conclusively exploitable, since it's possible additional guards (e.g., only counting a tracked "unlocked" delta elsewhere) exist that I did not see in the reviewed span.

### Recommendation
`withdraw_stake` should use the actual amount returned/reported by `staking_contract::distribute` (or a before/after balance delta computed *before* any external transfer could land) rather than the raw `coin::balance` of the resource account, so that only genuinely unlocked staking rewards are distributed to shareholders. Any unrelated balance in the resource account should be handled through a separate, admin-gated rescue path rather than silently entering the distribution flow.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L136-148)
```text
    public entry fun transfer_assert_minimum_deposit<T: key>(
        sender: &signer,
        from: Object<T>,
        to: Object<T>,
        amount: u64,
        expected: u64
    ) acquires TransferRefStore {
        let start = fungible_asset::balance(to);
        let fa = withdraw(sender, from, amount);
        deposit(to, fa);
        let end = fungible_asset::balance(to);
        assert!(end - start >= expected, error::aborted(EAMOUNT_MISMATCH));
    }
```

**File:** aptos-move/move-examples/shared_account/sources/shared_account.move (L65-78)
```text
    public entry fun disperse<CoinType>(resource_addr: address) acquires SharedAccount {
        assert!(exists<SharedAccount>(resource_addr), error::invalid_argument(ERESOURCE_DNE));

        let total_balance = coin::balance<CoinType>(resource_addr);
        assert!(total_balance > 0, error::out_of_range(EINSUFFICIENT_BALANCE));

        let shared_account = borrow_global<SharedAccount>(resource_addr);
        let resource_signer = account::create_signer_with_capability(&shared_account.signer_capability);

        vector::for_each_ref(&shared_account.share_record, |shared_record|{
            let shared_record: &Share = shared_record;
            let current_amount = shared_record.num_shares * total_balance / shared_account.total_shares;
            coin::transfer<CoinType>(&resource_signer, shared_record.share_holder, current_amount);
        });
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L17-18)
```text
/// 3. After the unlocked rewards become fully withdrawable (as it's subject to staking lockup), shareholders can call
/// distribute() to send all withdrawable funds to all shareholders based on the original grant's shares structure.
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L1030-1050)
```text
    fun create_vesting_contract_account(
        admin: &signer,
        contract_creation_seed: vector<u8>,
    ): (signer, SignerCapability) acquires AdminStore {
        let admin_store = borrow_global_mut<AdminStore>(signer::address_of(admin));
        let seed = bcs::to_bytes(&signer::address_of(admin));
        seed.append(bcs::to_bytes(&admin_store.nonce));
        admin_store.nonce += 1;

        // Include a salt to avoid conflicts with any other modules out there that might also generate
        // deterministic resource accounts for the same admin address + nonce.
        seed.append(VESTING_POOL_SALT);
        seed.append(contract_creation_seed);

        let (account_signer, signer_cap) = account::create_resource_account(admin, seed);
        // Register the vesting contract account to receive APT as it'll be sent to it when claiming unlocked stake from
        // the underlying staking contract.
        coin::register<AptosCoin>(&account_signer);

        (account_signer, signer_cap)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L1071-1078)
```text
    fun withdraw_stake(vesting_contract: &VestingContract, contract_address: address): Coin<AptosCoin> {
        // Claim any withdrawable distribution from the staking contract. The withdrawn coins will be sent directly to
        // the vesting contract's account.
        staking_contract::distribute(contract_address, vesting_contract.staking.operator);
        let withdrawn_coins = coin::balance<AptosCoin>(contract_address);
        let contract_signer = &get_vesting_account_signer_internal(vesting_contract);
        coin::withdraw<AptosCoin>(contract_signer, withdrawn_coins)
    }
```
