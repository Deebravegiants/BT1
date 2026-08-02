## Analysis

**Custody invariant extracted from the report:** a token/escrow system exposes a "canonical" balance-changing entry point that is supposed to run custom custody logic (mint/burn/mirror/allowlist) on every deposit, but a hard-coded/immutable configuration path allows certain code to skip that logic silently, corrupting the token's supply/custody accounting with no recovery path.

**Candidate paths explored on Aptos:**
1. `dispatchable_fungible_asset` register-once hooks (direct restatement of the external bug — creator misconfigures/omits deposit hook at creation) — rejected, too close to a restatement of the original finding.
2. `object.move` `allow_ungated_transfer`/`Untransferable` — correctly enforced consistently across `transfer`, `transfer_raw`, `transfer_with_ref`; no bypass found.
3. `multisig_account.move` / `resource_account.move` capability flows — auth-key rotation to `0x0` and `SignerCapability` custody look correctly gated; no unprivileged escape found.
4. **`fungible_asset.move` dispatch-hook bypass asymmetry between `deposit()` and `mint_to()`/`burn_from()`** — kept as strongest candidate.

### Title
Silent bypass of dispatchable deposit/withdraw custody hooks in `fungible_asset::mint_to`/burn paths - (File: `aptos-move/framework/aptos-framework/sources/fungible_asset.move`)

### Summary
`fungible_asset::deposit()` explicitly refuses to touch a store whose metadata has a registered custom deposit hook — it calls `deposit_sanity_check(store, true)` which aborts with `EINVALID_DISPATCHABLE_OPERATIONS` if a hook exists, forcing callers to go through `dispatchable_fungible_asset::deposit` so the issuer's custom logic always runs. `mint_to`, however, calls the very same sanity-check function with `abort_on_dispatch = false`, silently skipping the deposit hook and writing straight into the store via `unchecked_deposit`, with no error and no warning comment (unlike `deposit`, which carries an explicit doc warning). [1](#0-0) [2](#0-1) 

### Finding Description
`deposit_sanity_check` only enforces the always-on `frozen` flag; the dispatch-hook check is conditional on the `abort_on_dispatch` argument: [3](#0-2) 

`fungible_asset::deposit` (line 1005-1010) passes `true`, so any FA that has registered a deposit dispatch hook (per `dispatchable_fungible_asset::register_dispatch_functions`, used for denylists, deflation, loyalty payments, or supply-mirroring per the module's own documentation) will reject plain `deposit` calls and require routing through the hook-aware `dispatchable_fungible_asset::deposit`, guaranteeing the custom logic runs. [4](#0-3) 

`mint_to` (line 1027-1032) passes `false`. Consequently, for the exact same metadata/store with the exact same registered deposit hook, `mint_to` does not abort and does not invoke the hook — it deposits unconditionally via `unchecked_deposit`. The only invariant preserved is the primitive `frozen` boolean; any custody policy implemented purely inside the custom deposit hook (denylist enforcement, wrapped/derivative supply mirroring, deflation-on-receipt, loyalty-fee skimming) is silently not applied when value enters a store through minting.

This mirrors the original Inverse Finance bug precisely: a boolean gate (`callOnDepositCallback` there, `abort_on_dispatch` here) determines whether custody-critical callback logic executes on a value-entering operation, and one code path (constructor misconfiguration there, `mint_to` here) is hard-wired to skip it — except here the skip is unconditional framework behavior for every dispatchable FA, not a one-time deployer mistake, and it is undocumented (no warning comment, unlike `deposit`).

### Impact Explanation
Any protocol built on `dispatchable_fungible_asset` that relies on its deposit hook for custody enforcement (e.g., a denylist that blocks certain addresses from ever holding the asset, or logic that must mint/track a companion wrapped asset whenever the underlying token is received) can have that invariant broken by any code path that holds the `MintRef` and calls `fungible_asset::mint_to` directly instead of going through `dispatchable_fungible_asset`. This can:
- Deposit tokens into a store that the issuer's own hook logic is supposed to permanently block (denylist bypass — unauthorized custody/holder assignment).
- Desynchronize supply accounting between a primary asset and a hook-mirrored derivative/wrapped asset, corrupting the recovery/redemption relationship between the two (an accounting corruption that "moves value to the wrong holder or destroys recovery rights," matching the custody impact gate).

Because `MintRef` is frequently handed to auxiliary modules (rewards distributors, bridges, vault contracts) that are logically separate from the main FA module that defines the deposit hook, this is not purely a "privileged admin misuse" scenario — a legitimately-scoped MintRef holder, acting within its intended role, can unknowingly violate custody invariants the FA issuer believed were globally enforced.

### Likelihood Explanation
Requires: (1) an FA registers a deposit dispatch hook that encodes custody-relevant logic beyond the basic `frozen` flag, and (2) some code path with access to that FA's `MintRef` calls `fungible_asset::mint_to` instead of routing new supply through `dispatchable_fungible_asset`. Both conditions are realistic in composed DeFi systems (e.g., a lending/staking module holding `MintRef` for reward emission on a denylist- or wrapper-enabled FA) and are not prevented by the framework — there is no `abort_on_dispatch=true` enforcement, nor a warning comment, on `mint_to` as exists on `deposit`.

### Recommendation
Make `mint_to` (and the analogous `burn_from`/other privileged-ref paths that use `abort_on_dispatch=false`) consistent with `deposit`/`withdraw`: either invoke the registered deposit/withdraw dispatch function unconditionally when one exists, or `abort_on_dispatch=true` so callers are forced to use `dispatchable_fungible_asset` for FAs with hooks — removing the silent, undocumented divergence between the two APIs.

### Proof of Concept
1. Issuer creates a fungible asset via `primary_fungible_store::create_primary_store_enabled_fungible_asset` and registers a deposit dispatch function via `dispatchable_fungible_asset::register_dispatch_functions` whose custom `deposit` implements a denylist check (analogous to the FACoin pattern but with a real denylist instead of only `paused`). [5](#0-4) 
2. A separate module holding the `MintRef` (e.g., a rewards module) calls `fungible_asset::mint_to(mint_ref, denylisted_store, amount)` directly. [2](#0-1) 
3. Unlike a call to `fungible_asset::deposit`, which would abort with `EINVALID_DISPATCHABLE_OPERATIONS` due to `deposit_sanity_check(store, true)`, `mint_to`'s `deposit_sanity_check(store, false)` succeeds silently and the tokens land in the denylisted store via `unchecked_deposit`, without the custom deposit hook (and its denylist/mirroring logic) ever executing.

**Uncertainty note:** I was not able to fully trace every consumer of `MintRef`/`BurnRef` across the entire repo (e.g., all `move-examples` and DeFi-style modules) to find a live, in-repo example where a *separate untrusted module* holds a `MintRef` for a hook-bearing FA — the FACoin example keeps `MintRef` private to the same module that defines the hook, so this exact scenario is an architectural gap in the framework API rather than a demonstrated exploit against a specific in-repo protocol. This should be verified with full read access to confirm whether any bundled Aptos module (e.g., `managed_fungible_asset`, DeFi examples) splits `MintRef` custody from deposit-hook custody in a way that's directly exploitable on mainnet.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1001-1010)
```text
    /// Deposit `amount` of the fungible asset to `store`.
    ///
    /// Note: This function can be in-place replaced by `dispatchable_fungible_asset::deposit`. You should use
    ///       that function unless you DO NOT want to support fungible assets with dispatchable hooks.
    public fun deposit<T: key>(
        store: Object<T>, fa: FungibleAsset
    ) acquires FungibleStore, DispatchFunctionStore, ConcurrentFungibleBalance {
        deposit_sanity_check(store, true);
        unchecked_deposit(store.object_address(), fa);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1026-1032)
```text
    /// Mint the specified `amount` of the fungible asset to a destination store.
    public fun mint_to<T: key>(
        self: &MintRef, store: Object<T>, amount: u64
    ) acquires FungibleStore, Supply, ConcurrentSupply, DispatchFunctionStore, ConcurrentFungibleBalance {
        deposit_sanity_check(store, false);
        unchecked_deposit(store.object_address(), self.mint(amount));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L1-17)
```text
/// This defines the fungible asset module that can issue fungible asset of any `Metadata` object. The
/// metadata object can be any object that equipped with `Metadata` resource.
///
/// The dispatchable_fungible_asset wraps the existing fungible_asset module and adds the ability for token issuer
/// to customize the logic for withdraw and deposit operations. For example:
///
/// - Deflation token: a fixed percentage of token will be destructed upon transfer.
/// - Transfer allowlist: token can only be transfered to addresses in the allow list.
/// - Predicated transfer: transfer can only happen when some certain predicate has been met.
/// - Loyalty token: a fixed loyalty will be paid to a designated address when a fungible asset transfer happens
///
/// The api listed here intended to be an in-place replacement for defi applications that uses fungible_asset api directly
/// and is safe for non-dispatchable (aka vanilla) fungible assets as well.
///
/// See AIP-73 for further discussion
///
module aptos_framework::dispatchable_fungible_asset {
```

**File:** aptos-move/move-examples/fungible_asset/fa_coin/sources/FACoin.move (L67-87)
```text
        // Override the deposit and withdraw functions which mean overriding transfer.
        // This ensures all transfer will call withdraw and deposit functions in this module
        // and perform the necessary checks.
        // This is OPTIONAL. It is an advanced feature and we don't NEED a global state to pause the FA coin.
        let deposit = function_info::new_function_info(
            admin,
            string::utf8(b"fa_coin"),
            string::utf8(b"deposit"),
        );
        let withdraw = function_info::new_function_info(
            admin,
            string::utf8(b"fa_coin"),
            string::utf8(b"withdraw"),
        );
        dispatchable_fungible_asset::register_dispatch_functions(
            constructor_ref,
            option::some(withdraw),
            option::some(deposit),
            option::none(),
        );
    }
```
