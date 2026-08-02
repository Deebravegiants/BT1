Confirmed: there is no `remove_minter` function anywhere in the repository. The `usdk.move` stablecoin example only exposes `add_minter` and has no counterpart to revoke a minter's privileges once granted.

### Title
Minters cannot be revoked once added, allowing permanent unauthorized mint/burn authority - (File: aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move)

### Summary
The `usdk` stablecoin example module implements a `Roles` resource tracking a `master_minter` and a `minters` vector [1](#0-0) . The `master_minter` can grant minter privileges via `add_minter` [2](#0-1) , but there is no corresponding `remove_minter` (or similarly named revoke) function anywhere in the module or the broader repository, confirmed by an exhaustive search for `remove_minter`/`revoke_minter`. This is a direct on-chain analog of the reported "strategists can't be removed" bug class: a role that is custody-critical (mint and burn authority over the fungible asset's supply) can be granted but never revoked.

### Finding Description
`assert_is_minter` grants unlimited mint/burn authority to any address in `roles.minters` or equal to `roles.master_minter` [3](#0-2) . This authority is used directly in `mint` to create new tokens backed by the `MintRef` stored in `Management`, and deposited to arbitrary non-denylisted recipients [4](#0-3) , and in `burn_from` to withdraw and destroy tokens from any account's store using the `TransferRef`/`BurnRef` [5](#0-4) .

Once `add_minter` is called, the granted address's mint/burn authority is permanent — there is no `remove_minter`, no expiry, and no way for `master_minter` (or any other role) to strip an entry from `roles.minters`. Other roles in the same module (`pauser`, `denylister`) are single fixed addresses set at `init_module` and not even reassignable, and the denylist itself supports both `denylist` and `undenylist` (add/remove) [6](#0-5)  — showing the module's own design pattern includes revocation for other custody-relevant lists, but omits it specifically for the minter role, which is the most powerful (supply-mutating) role in the contract.

### Impact Explanation
A compromised, rogue, or intentionally malicious minter key retains permanent, irrevocable ability to mint unlimited new supply of the asset (subject only to `paused` and denylist state) and to burn funds from any user's primary store. Since `master_minter` has no mechanism to strip a minter's privilege, the only mitigation is pausing the entire stablecoin (`set_pause`) or denylisting individual users, neither of which removes the minter's standing capability — pausing halts the whole system for all users, and denylisting an address doesn't stop the minter from targeting other addresses. This directly corrupts supply/custody accounting (unauthorized mint) and can destroy user holdings (unauthorized burn) with no path to restore the correct authority set without a module upgrade.

### Likelihood Explanation
Likelihood is high in any real deployment: minter keys are operational hot-signer keys used routinely for mint/burn workflows, making them more exposed to compromise than deployer/admin keys. Once any single minter key leaks or an employee's access should be revoked, there is no on-chain remedy — this is a certain-to-occur operational scenario for any project adopting this reference implementation as-is, mirroring exactly the rulebook's guidance that upgradeability is not an acceptable substitute for a working revocation control.

### Recommendation
Add a `remove_minter` entry function, callable only by `master_minter`, that removes the target address from `roles.minters` (mirroring the existing `vector::contains`/`swap_remove` pattern already used elsewhere, e.g. `multisig_account::update_owner_schema` [7](#0-6) ), and emit a corresponding event for auditability, analogous to `denylist`/`undenylist`.

### Proof of Concept
1. `master_minter` calls `add_minter(admin, minter_addr)` [8](#0-7) , granting `minter_addr` permanent mint/burn rights.
2. `minter_addr`'s key is later leaked, or the entity should be offboarded.
3. `master_minter` has no function to call to remove `minter_addr` from `roles.minters` — grepping the codebase confirms no `remove_minter`/`revoke_minter` function exists.
4. `minter_addr` continues to call `mint(minter_addr, attacker_addr, huge_amount)` [9](#0-8)  indefinitely, inflating supply, or calls `burn_from` against arbitrary user stores [10](#0-9)  to destroy user balances, with the only available defense being a full-system `set_pause(true)` that halts legitimate operations for every user.

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L29-35)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    struct Roles has key {
        master_minter: address,
        minters: vector<address>,
        pauser: address,
        denylister: address,
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L212-230)
```text
    /// Mint new tokens to the specified account. This checks that the caller is a minter, the stablecoin is not paused,
    /// and the account is not denylisted.
    public entry fun mint(minter: &signer, to: address, amount: u64) acquires Management, Roles, State {
        assert_not_paused();
        assert_is_minter(minter);
        assert_not_denylisted(to);
        if (amount == 0) { return };

        let management = borrow_global<Management>(usdk_address());
        let tokens = fungible_asset::mint(&management.mint_ref, amount);
        // Ensure not to call pfs::deposit or dfa::deposit directly in the module.
        deposit(primary_fungible_store::ensure_primary_store_exists(to, metadata()), tokens, &management.transfer_ref);

        event::emit(Mint {
            minter: signer::address_of(minter),
            to,
            amount,
        });
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L237-262)
```text
    /// Burn tokens from the specified account's store. This checks that the caller is a minter and the stablecoin is
    /// not paused.
    public entry fun burn_from(
        minter: &signer,
        store: Object<FungibleStore>,
        amount: u64,
    ) acquires Management, Roles, State {
        assert_not_paused();
        assert_is_minter(minter);
        if (amount == 0) { return };

        let management = borrow_global<Management>(usdk_address());
        let tokens = fungible_asset::withdraw_with_ref(
            &management.transfer_ref,
            store,
            amount,
        );
        fungible_asset::burn(&management.burn_ref, tokens);

        event::emit(Burn {
            minter: signer::address_of(minter),
            from: object::owner(store),
            store,
            amount,
        });
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L278-306)
```text
    /// Add an account to the denylist. This checks that the caller is the denylister.
    public entry fun denylist(denylister: &signer, account: address) acquires Management, Roles, State {
        assert_not_paused();
        let roles = borrow_global<Roles>(usdk_address());
        assert!(signer::address_of(denylister) == roles.denylister, EUNAUTHORIZED);

        let freeze_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
        primary_fungible_store::set_frozen_flag(freeze_ref, account, true);

        event::emit(Denylist {
            denylister: signer::address_of(denylister),
            account,
        });
    }

    /// Remove an account from the denylist. This checks that the caller is the denylister.
    public entry fun undenylist(denylister: &signer, account: address) acquires Management, Roles, State {
        assert_not_paused();
        let roles = borrow_global<Roles>(usdk_address());
        assert!(signer::address_of(denylister) == roles.denylister, EUNAUTHORIZED);

        let freeze_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
        primary_fungible_store::set_frozen_flag(freeze_ref, account, false);

        event::emit(Denylist {
            denylister: signer::address_of(denylister),
            account,
        });
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L308-315)
```text
    /// Add a new minter. This checks that the caller is the master minter and the account is not already a minter.
    public entry fun add_minter(admin: &signer, minter: address) acquires Roles, State {
        assert_not_paused();
        let roles = borrow_global_mut<Roles>(usdk_address());
        assert!(signer::address_of(admin) == roles.master_minter, EUNAUTHORIZED);
        assert!(!vector::contains(&roles.minters, &minter), EALREADY_MINTER);
        vector::push_back(&mut roles.minters, minter);
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L317-321)
```text
    fun assert_is_minter(minter: &signer) acquires Roles {
        let roles = borrow_global<Roles>(usdk_address());
        let minter_addr = signer::address_of(minter);
        assert!(minter_addr == roles.master_minter || vector::contains(&roles.minters, &minter_addr), EUNAUTHORIZED);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1612-1625)
```text
        // If owners to remove provided, try to remove them.
        if (owners_to_remove.length() > 0) {
            let owners_ref_mut = &mut multisig_account_ref_mut.owners;
            let owners_removed = vector[];
            owners_to_remove.for_each_ref(|owner_to_remove_ref| {
                let (found, index) =
                    vector::index_of(owners_ref_mut, owner_to_remove_ref);
                if (found) {
                    vector::push_back(
                        &mut owners_removed,
                        vector::swap_remove(owners_ref_mut, index)
                    );
                }
            });
```
