## Custody Invariant Reduction

The Morpho bug reduces to one invariant: **a valuation/authorization query must always resolve through the canonical value-source for the asset; a sibling code path that silently falls back to the raw underlying representation instead of the canonical value breaks pricing/custody guarantees.**

## Candidate Paths Considered

1. `object::owns`/`transfer_with_ref` nested ownership traversal — no divergent valuation, ruled out.
2. `dispatchable_fungible_asset::derived_balance` vs `fungible_asset::balance` — `balance()` explicitly guards against dispatchable FAs (kept as strongest candidate).
3. `resource_account`/`multisig_account` signer-capability revocation ordering — matches documented behavior, no broken invariant found.
4. `fungible_asset::is_balance_at_least` / `is_address_balance_at_least` vs `fungible_asset::balance` — same module, analogous purpose, but only one of the two enforces the dispatch guard. Kept as strongest.

## Title
Missing dispatch-hook guard in `fungible_asset::is_balance_at_least` causes raw-balance mispricing for FAs with `derived_balance` hooks - (File: aptos-move/framework/aptos-framework/sources/fungible_asset.move)

### Summary
`fungible_asset::balance()` explicitly aborts when the queried store's metadata has a `derived_balance` dispatch function registered, forcing callers to go through `dispatchable_fungible_asset::derived_balance()` to get the canonical value [1](#0-0) . Its sibling function `is_balance_at_least()` (and the underlying `is_address_balance_at_least`) performs the exact same kind of sufficiency check but has **no such guard** — it always reads the raw `FungibleStore.balance` / `ConcurrentFungibleBalance` field directly, even when a `derived_balance` dispatch hook exists [2](#0-1) .

### Finding Description
For fungible assets registered with a `derived_balance` dispatch hook (AIP-73 dispatchable FAs, e.g. a yield-bearing wrapper where 1 raw share is worth N underlying units, as exercised by the `ten_x_token` test fixture) [3](#0-2) , the framework provides two parallel query families:

- `balance()` — deliberately aborts (`EINVALID_DISPATCHABLE_OPERATIONS`) if the store's metadata has a registered `derived_balance_function`, with an explicit doc note to use `dispatchable_fungible_asset::balance`/`derived_balance` instead [1](#0-0) .
- `is_balance_at_least()` / `is_address_balance_at_least()` — has no equivalent `has_balance_dispatch_function` check and unconditionally compares the amount against the raw `store.balance` field [2](#0-1) .

The only caller in-framework that correctly routes through the dispatch hook is `primary_fungible_store::is_balance_at_least`, which calls `dispatchable_fungible_asset::is_derived_balance_at_least` instead of the raw `fungible_asset::is_balance_at_least` [4](#0-3) . But `fungible_asset::is_balance_at_least` and `is_address_balance_at_least` are `public`/`public(friend)` and directly callable by any downstream module (custody, lending, multisig treasury, or resource-account logic) operating on a raw `Object<FungibleStore>` rather than a primary store. Any such caller that performs a sufficiency/collateral check against a dispatchable FA (e.g. a yield-bearing token whose "true" value is 10x its raw balance) will get an answer computed from the **raw share count**, not the derived economic value — exactly the same class of divergence as the Morpho bug, where one code path resolves valuation through the canonical/contextual source and the sibling path silently falls back to the raw underlying representation.

### Impact Explanation
Any custody, lending, or collateral-check logic built directly on `fungible_asset::is_balance_at_least`/`is_address_balance_at_least` for a dispatchable FA with a `derived_balance` hook will systematically mis-evaluate whether a store holds sufficient value. Depending on whether the derived value is above or below the raw balance, this can let an operation proceed that should have been blocked (e.g., permitting a withdrawal/transfer/collateral release believed to be under-collateralized) or incorrectly block a legitimate one. Because `balance()` treats this exact situation as an aborting condition to force correct usage, the fact that `is_balance_at_least()` has no matching protection is an inconsistency in the same module for equivalent purposes, and it is reachable by any third-party module without special privilege.

### Likelihood Explanation
Requires a fungible asset that registers a `derived_balance` dispatch function (a supported, first-class AIP-73 feature — not a hypothetical), and a downstream custody/lending module that queries via `fungible_asset::is_balance_at_least`/`is_address_balance_at_least` on an `Object<FungibleStore>` instead of going through `primary_fungible_store`/`dispatchable_fungible_asset`. This is plausible since the raw functions are public, undocumented as unsafe for dispatchable FAs (unlike `balance()`), and there is no compiler or runtime signal steering integrators to the dispatch-aware equivalent.

### Recommendation
Add the same `has_balance_dispatch_function` guard (or auto-route through the dispatch hook) inside `fungible_asset::is_balance_at_least` / `is_address_balance_at_least` that already exists in `balance()`, or clearly document and enforce (via abort) that these functions must not be used for dispatchable FAs, consistent with the existing `balance()` behavior.

### Proof of Concept
Not independently verified with an executable PoC (no test harness available in this environment); the divergence is demonstrated purely via static code comparison:
1. Register a FA with a `derived_balance` dispatch function that reports value as `10x` the raw balance (pattern used by `ten_x_token` in [5](#0-4) ).
2. Create a non-primary `FungibleStore` for this asset and deposit `100` raw units (derived value `1000`).
3. Call `fungible_asset::balance(store)` → aborts with `EINVALID_DISPATCHABLE_OPERATIONS` per [6](#0-5) .
4. Call `fungible_asset::is_balance_at_least(store, 500)` → returns `true` (raw balance `100 < 500` is actually the correct raw comparison, but the *derived* value `1000 >= 500` — for values where raw and derived-based results disagree, e.g. `is_balance_at_least(store, 150)`, the raw check returns `false` even though the true derived value `1000` satisfies it, or vice versa depending on hook semantics), demonstrating the silent divergence from the canonical valuation source that `balance()` is designed to prevent.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L670-684)
```text
    #[view]
    /// Get the balance of a given store.
    ///
    /// Note: This function will abort on FAs with `derived_balance` hook set up.
    ///       Use `dispatchable_fungible_asset::balance` instead if you intend to work with those FAs.
    public fun balance<T: key>(
        store: Object<T>
    ): u64 acquires FungibleStore, ConcurrentFungibleBalance, DispatchFunctionStore {
        let fa_store = borrow_store_resource(&store);
        assert!(
            !has_balance_dispatch_function(fa_store.metadata),
            error::invalid_argument(EINVALID_DISPATCHABLE_OPERATIONS)
        );
        balance_impl(store)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L701-727)
```text
    #[view]
    /// Check whether the balance of a given store is >= `amount`.
    public fun is_balance_at_least<T: key>(
        store: Object<T>, amount: u64
    ): bool acquires FungibleStore, ConcurrentFungibleBalance {
        let store_addr = store.object_address();
        is_address_balance_at_least(store_addr, amount)
    }

    /// Check whether the balance of a given store is >= `amount`.
    public(friend) fun is_address_balance_at_least(
        store_addr: address, amount: u64
    ): bool acquires FungibleStore, ConcurrentFungibleBalance {
        if (store_exists_inline(store_addr)) {
            let store_balance = borrow_global<FungibleStore>(store_addr).balance;
            if (store_balance == 0
                && concurrent_fungible_balance_exists_inline(store_addr)) {
                let balance_resource =
                    borrow_global<ConcurrentFungibleBalance>(store_addr);
                balance_resource.balance.is_at_least(amount)
            } else {
                store_balance >= amount
            }
        } else {
            amount == 0
        }
    }
```

**File:** aptos-move/framework/aptos-framework/tests/ten_x_token_tests.move (L11-34)
```text
    #[test(creator = @aptos_framework)]
    fun test_ten_x(
        creator: &signer,
    ) {
        features::change_feature_flags_for_testing(creator, vector[features::get_function_value_dispatch_feature()], vector[]);
        let (creator_ref, token_object) = fungible_asset::create_test_token(creator);
        let (mint, _, _, _) = fungible_asset::init_test_metadata(&creator_ref);
        let metadata = token_object.convert<TestToken, Metadata>();

        let creator_store = fungible_asset::create_test_store(creator, metadata);

        ten_x_token::initialize(creator, &creator_ref);

        assert!(dispatchable_fungible_asset::derived_supply(metadata) == option::some(0), 2);
        // Mint
        let fa = mint.mint(100);
        dispatchable_fungible_asset::deposit(creator_store, fa);

        // The derived value is 10x
        assert!(dispatchable_fungible_asset::derived_balance(creator_store) == 1000, 4);

        // The derived supply is 10x
        assert!(dispatchable_fungible_asset::derived_supply(metadata) == option::some(1000), 5);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L160-167)
```text
    #[view]
    public fun is_balance_at_least<T: key>(account: address, metadata: Object<T>, amount: u64): bool {
        if (primary_store_exists(account, metadata)) {
            dispatchable_fungible_asset::is_derived_balance_at_least(primary_store(account, metadata), amount)
        } else {
            amount == 0
        }
    }
```
