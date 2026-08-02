## Title
Confidential Asset pool lets a frozen/blacklisted fungible-asset holder still extract already-veiled value to an arbitrary unfrozen address — ([File: aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move])

### Summary
The `confidential_asset` module wraps ordinary (non-dispatchable) fungible assets into an encrypted-balance "veil" system. Deposits into the veil are gated by the normal `FungibleStore.frozen` check, but once value is veiled, `withdraw_to()` and `confidential_transfer()` never re-check the *depositor's own* store-frozen status — only the destination store's frozen status is checked, and the destination address is an attacker-supplied parameter. This lets an address that an FA issuer freezes (via `TransferRef::set_frozen_flag`, e.g. a compliance blacklist analogous to `SOFT_RESTRICTED_STAKER_ROLE` in the referenced report) continue to move already-veiled funds to any other address it controls, defeating the freeze.

### Finding Description
`is_safe_for_confidentiality()` restricts the module to non-dispatchable FAs specifically to avoid dispatch-based restriction bypass: [1](#0-0) 

This explicitly acknowledges the same bug class as the external report — that sender-side restrictions (e.g. blocklists) enforced via withdraw hooks must not be silently skipped. However, the module still permits FAs whose restriction mechanism is the *plain* `FungibleStore.frozen` flag (set via `fungible_asset::set_frozen_flag`, as used by `managed_fungible_asset`/`FACoin`-style issuers). This is the standard compliance/freeze mechanism for FAs on Aptos: [2](#0-1) 

- `deposit()` moves funds from the depositor's primary store into the module-owned pool via `dispatchable_fungible_asset::transfer`, which does enforce `withdraw_sanity_check` (checks `!fa_store.frozen`) on the depositor's store: [3](#0-2) 
So a user must not be frozen *at the time they veil funds* — but they can veil funds while unrestricted and only be frozen later.

- `withdraw_to()` (called from `withdraw_to_raw`/`normalize`) checks only `is_emergency_paused()` and `is_safe_for_confidentiality()`, never the sender's own FA-store frozen state, and moves funds from the module-owned `pool_fa_store` to an arbitrary caller-supplied `to` address: [4](#0-3) 
The only frozen check exercised here is on the *destination* store (`deposit_sanity_check` inside `dispatchable_fungible_asset::deposit`), and the attacker controls that destination address, so they simply choose an unfrozen recipient: [5](#0-4) 

- `confidential_transfer()` similarly never checks the sender's own frozen status, only `incoming_transfers_paused(to, ...)` for the recipient's confidential store: [6](#0-5) 

A direct grep of the module confirms there is no reference to `frozen` anywhere in `confidential_asset.move`, meaning the module has no compliance hook to re-validate a holder's frozen/restricted status once value is inside the veil.

### Impact Explanation
This breaks the custody invariant that "fungible asset ... freeze state must preserve supply and holder identity." An FA issuer who freezes a user's `FungibleStore` (e.g., due to sanctions/compliance/theft investigation) expects that address to be unable to move that asset. If the user had previously deposited into the confidential asset pool (a legitimate, permissionless action available to any non-frozen holder), they retain full custody and control of that value via encrypted balances, and can call `withdraw_to`/`confidential_transfer` to move it to any other address they control — completely circumventing the freeze. This is a compliance/custody-control bypass, structurally identical to the external report's restricted-staker-bypass-via-composer: a restriction enforced at one entry point (direct FA transfer/deposit) is not propagated into an alternate value-routing layer (the confidential pool) that ultimately controls the same underlying asset.

### Likelihood Explanation
Likelihood is moderate-to-high for any FA issuer that (a) enables confidentiality for its asset type via `set_confidentiality_for_asset_type`, and (b) relies on `TransferRef`-based freezing for compliance (a very common Aptos FA pattern, as shown by the framework's own `managed_fungible_asset` and `FACoin` examples). No privileged action is required by the attacker beyond ordinary use of `deposit()` before being frozen and `withdraw_to()`/`confidential_transfer()` afterward — both are public entry functions available to any registered user.

### Recommendation
Track and re-validate the frozen status of the sender's primary `FungibleStore` (or an equivalent per-asset restriction flag) at the time of `withdraw_to()`/`confidential_transfer()`/`rollover_pending_balance()`, not just at deposit time. Alternatively, disallow confidentiality registration/veiling for FA types whose issuer holds freeze authority (`TransferRef`) unless the module exposes a compliance hook allowing the issuer to freeze a user's *confidential* balance directly, mirroring the FA-level freeze semantics.

### Proof of Concept
1. FA issuer creates a non-dispatchable, freezable FA (e.g. via `managed_fungible_asset`) and calls `set_confidentiality_for_asset_type(true)`.
2. User registers a confidential store and calls `confidential_asset::deposit(user, asset_type, 1000)` while unfrozen — funds move from user's primary store into the module's pool store; balance now exists as an encrypted `pending_balance`/`available_balance` in `ConfidentialStore`.
3. Issuer detects suspicious activity and calls `managed_fungible_asset::freeze_account(admin, user_addr)`, setting `user`'s primary `FungibleStore.frozen = true` — per the framework's intended semantics this should block the user from moving that asset.
4. User (still fully in control of their confidential store) submits a valid `withdraw_to_raw`/`withdraw_to(user, asset_type, other_unfrozen_addr, 1000, proof)` call. `withdraw_to()` checks only `is_emergency_paused()`, `is_safe_for_confidentiality()`, and the destination `other_unfrozen_addr` store's frozen flag — none of which reference `user`'s frozen primary store.
5. The transfer succeeds: 1000 units move from the pool to `other_unfrozen_addr`, which the user controls, fully bypassing the freeze the issuer applied in step 3.

*(Note: I was unable to independently execute this against a live test harness in this environment; the analysis is based on static review of the cited functions and their absence of any `frozen`/compliance check on the sender path. This should be validated with a Move unit/integration test exercising steps 1–5 before treating it as fully confirmed.)*

### Citations

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move (L398-415)
```text
    /// Dispatchable fungible asset (DFA) types can, for example, dynamically change user balances upon a call to
    /// `fungible_asset::balance()`, based say, on a multiplier. We do not yet see how to *generically* handle such
    /// dynamic behavior in a confidential context, where balances are encrypted on-chain and cannot be modified in
    /// arbitrary ways. Similarly, we also forbid "total supply" dispatch functions, out of an abundance of caution.
    ///
    /// Furthermore, even for DFAs that only have custom "withdraw/deposit" dispatch functions, it is unclear how to
    /// *generically* support any such functionality. As a result, for now we only support non-dispatchable (vanilla)
    /// fungible asset (FA) types.
    ///
    /// For example, sender blocklists implemented via "withdraw" dispatching would only be enforced when users veil/
    /// unveil their tokens into/from the confidential asset pool. (This is because a `confidential_transfer` cannot,
    /// by definition, interact with any (D)FA functions, or it would be forced to leak amounts/balances). In the future,
    /// we could add support for dispatch functions that only look at the sender's address (and not at the amount/
    /// balances). This way, we could *generically* handle them here, given they are implemented in a type-safe way that
    /// allows us to check they are enabled.
    fun is_safe_for_confidentiality(asset_type: &Object<fungible_asset::Metadata>): bool {
        !fungible_asset::is_asset_type_dispatchable(*asset_type)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move (L450-491)
```text
    /// Deposits tokens from the sender's primary FA store into their pending balance.
    public entry fun deposit(
        depositor: &signer,
        asset_type: Object<fungible_asset::Metadata>,
        amount: u64
    ) acquires ConfidentialStore, GlobalConfig, AssetConfig {
        let addr = signer::address_of(depositor);

        assert!(!is_emergency_paused(), error::invalid_state(E_EMERGENCY_PAUSED));
        assert!(is_safe_for_confidentiality(&asset_type), error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));
        assert!(is_confidentiality_enabled_for_asset_type(asset_type), error::invalid_argument(E_ASSET_TYPE_DISALLOWED));
        assert!(!incoming_transfers_paused(addr, asset_type), error::invalid_state(E_INCOMING_TRANSFERS_PAUSED));
        assert!(amount != 0, error::invalid_argument(E_POINTLESSLY_DEPOSITING_ZERO));

        // Note: Gets the "confidential asset pool" for this asset type, or sets it up if this asset type is veiled for the first time
        let pool_fa_store = ensure_pool_fa_store(asset_type);

        // Step 1: Transfer the asset from the user's account into the confidential asset pool.
        //
        // Note: Dispatchable transfers may deliver less than `amount` (e.g., due to fees for deflationary tokens), so
        // we measure the pool balance before & after to credit only what was actually received.
        let before = fungible_asset::balance(pool_fa_store);
        let depositor_fa_store = primary_fungible_store::primary_store(addr, asset_type);
        dispatchable_fungible_asset::transfer(depositor, depositor_fa_store, pool_fa_store, amount);

        // Step 2: "Mint" corresponding confidential assets for the depositor, and add them to their pending balance.
        let ca_store = borrow_confidential_store_mut(addr, asset_type);

        add_assign_pending(&mut ca_store.pending_balance, &new_pending_u64_no_randomness(amount));
        ca_store.transfers_received += 1;

        // Make sure the depositor has "room" in their pending balance for this deposit
        assert!(
            ca_store.transfers_received <= MAX_TRANSFERS_BEFORE_ROLLOVER,
            error::invalid_state(E_PENDING_BALANCE_MUST_BE_ROLLED_OVER)
        );

        event::emit(Deposited::V1 { addr, amount, asset_type, new_pending_balance: ca_store.pending_balance });

        // Abundantly-paranoid: Re-asserting dispatchable FA functionality that charges fees on withdraw/deposit was not invoked.
        assert!(amount == fungible_asset::balance(pool_fa_store) - before, error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move (L514-564)
```text
    /// Withdraws tokens from the sender's available balance to recipient's primary FA store. Also used internally by `normalize` (amount = 0).
    public(friend) fun withdraw_to(
        sender: &signer,
        asset_type: Object<fungible_asset::Metadata>,
        to: address,
        amount: u64,
        proof: WithdrawalProof
    ) acquires ConfidentialStore, GlobalConfig, AssetConfig {
        assert!(!is_emergency_paused(), error::invalid_state(E_EMERGENCY_PAUSED));
        assert!(is_safe_for_confidentiality(&asset_type), error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));

        // WARNING: We do not assert `is_confidentiality_enabled_for_asset_type` because we want to give users a way to
        // withdraw from the confidential into their public balance after an asset type is disabled.

        let sender_addr = signer::address_of(sender);

        // Read values before mutable borrow to avoid conflicting borrows of ConfidentialStore
        let ek = get_encryption_key(sender_addr, asset_type);
        let old_balance = get_available_balance(sender_addr, asset_type);
        let effective_auditor = get_effective_auditor_config(asset_type);

        let compressed_new_balance = assert_valid_withdrawal_proof(
            sender, asset_type,
            &ek, amount, &old_balance, &effective_auditor.config.ek, proof
        );

        let ca_store = borrow_confidential_store_mut(sender_addr, asset_type);
        if(amount == 0 && ca_store.normalized) {
            abort(error::invalid_state(E_ALREADY_NORMALIZED));
        };
        ca_store.normalized = true;
        ca_store.available_balance = compressed_new_balance;
        ca_store.update_auditor_hint(&effective_auditor); // enables auditor to later tell whether their balance ciphertext is stale

        // Copy state for the event (before any further borrows)
        let new_available_balance = ca_store.available_balance;
        let auditor_hint = ca_store.auditor_hint;

        if (amount > 0) {
            let pool_fa_store = get_pool_fa_store(asset_type);  // must exist b.c. sender's CA store exists
            let before = fungible_asset::balance(pool_fa_store);

            dispatchable_fungible_asset::transfer(&get_global_config_signer(), pool_fa_store, primary_fungible_store::ensure_primary_store_exists(to, asset_type), amount);
            event::emit(Withdrawn::V1 { from: sender_addr, to, amount, asset_type, new_available_balance, auditor_hint });

            // Re-asserting dispatchable FA functionality that charges fees on withdraw/deposit was not invoked.
            assert!(amount == before - fungible_asset::balance(pool_fa_store), error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));
        } else {
            event::emit(Normalized::V1 { addr: sender_addr, asset_type, new_available_balance, auditor_hint });
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move (L616-627)
```text
    public(friend) fun confidential_transfer(
        sender: &signer,
        asset_type: Object<fungible_asset::Metadata>,
        to: address,
        proof: TransferProof,
        memo: vector<u8>,
    ) acquires ConfidentialStore, AssetConfig, GlobalConfig {
        assert!(!is_emergency_paused(), error::invalid_state(E_EMERGENCY_PAUSED));
        assert!(is_safe_for_confidentiality(&asset_type), error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));
        assert!(is_confidentiality_enabled_for_asset_type(asset_type), error::invalid_argument(E_ASSET_TYPE_DISALLOWED));
        assert!(!incoming_transfers_paused(to, asset_type), error::invalid_state(E_INCOMING_TRANSFERS_PAUSED));
        assert!(memo.length() <= MAX_MEMO_BYTES, error::invalid_argument(E_MEMO_TOO_LONG));
```

**File:** aptos-move/move-examples/fungible_asset/fa_coin/sources/FACoin.move (L146-160)
```text
    /// Freeze an account so it cannot transfer or receive fungible assets.
    public entry fun freeze_account(admin: &signer, account: address) acquires ManagedFungibleAsset {
        let asset = get_metadata();
        let transfer_ref = &authorized_borrow_refs(admin, asset).transfer_ref;
        let wallet = primary_fungible_store::ensure_primary_store_exists(account, asset);
        fungible_asset::set_frozen_flag(transfer_ref, wallet, true);
    }

    /// Unfreeze an account so it can transfer or receive fungible assets.
    public entry fun unfreeze_account(admin: &signer, account: address) acquires ManagedFungibleAsset {
        let asset = get_metadata();
        let transfer_ref = &authorized_borrow_refs(admin, asset).transfer_ref;
        let wallet = primary_fungible_store::ensure_primary_store_exists(account, asset);
        fungible_asset::set_frozen_flag(transfer_ref, wallet, false);
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
