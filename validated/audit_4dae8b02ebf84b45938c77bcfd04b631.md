## Finding



### Title
`transfer_assert_minimum_deposit` validates minimum-deposit guarantee against raw balance instead of the token's derived (dispatch-hook) balance - (File: aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move)

### Summary
`dispatchable_fungible_asset::transfer_assert_minimum_deposit` is the dispatchable-FA analog of a "quote/guarantee" function: it withdraws from a sender, deposits to a recipient through the token's custom hooks, and asserts that the recipient's balance increased by at least `expected`. For dispatchable fungible assets — which exist precisely to support custom accounting such as deflationary/fee-on-transfer tokens (see the framework's own `deflation_token` test module) — the true amount actually credited to a holder is exposed through the `derived_balance` dispatch hook, not the raw `FungibleStore.balance` field. The function nonetheless measures its guarantee using `fungible_asset::balance()` (raw storage) instead of `dispatchable_fungible_asset::derived_balance()`.

### Finding Description
`transfer_assert_minimum_deposit` is implemented as: [1](#0-0) 

It computes `start`/`end` via `fungible_asset::balance(to)`, then asserts `end - start >= expected`. But the module explicitly provides `derived_balance`/`is_derived_balance_at_least` as the correct way to read a dispatchable asset's true value, precisely because a registered `derived_balance_function` hook can make the economically-real balance diverge from the raw `FungibleStore.balance` field: [2](#0-1) 

The deposit path itself runs through the token issuer's custom `deposit` hook (which can mutate arbitrary auxiliary accounting state, not just the raw `FungibleStore.balance`): [3](#0-2) 

Because `transfer_assert_minimum_deposit` reads the raw balance rather than routing through the same dispatch hook (`derived_balance`) used to represent the asset's true value, the "minimum guaranteed deposit" assertion can pass or fail based on a value that does not correspond to what the recipient economically holds under the issuer's own accounting model — the same class of error as the external report's use of the pre/wrong reserve to compute a quoted amount instead of the value that reflects the actual post-operation state.

### Impact Explanation
Callers integrating with dispatchable fungible assets (the class of asset this function exists to serve) can be given a false assurance that a recipient received at least `expected` units, when the token's own derived accounting says otherwise (or vice versa). Protocols that rely on this entry function as a safety check before crediting downstream value (e.g., a swap or vault crediting shares based on "guaranteed" deposit amounts) can be misled into over- or under crediting holders, corrupting supply/custody accounting for the asset and potentially moving value to the wrong holder. This matches the "supply or custody accounting corruption that moves value to the wrong holder" impact category.

### Likelihood Explanation
This requires a fungible asset that registers a `derived_balance_function` diverging from raw store balance (e.g., a deflationary/rebasing token, matching the framework's own `deflation_token`/`clamped_token` test patterns) and a caller that depends on `transfer_assert_minimum_deposit`'s guarantee for such an asset. No privileged access is required to trigger the divergence — any dispatchable-FA issuer can register such hooks, and any unprivileged caller can invoke `transfer_assert_minimum_deposit`.

### Recommendation
Change `transfer_assert_minimum_deposit` to measure `start`/`end` using `derived_balance()` (or `is_derived_balance_at_least`) instead of `fungible_asset::balance()`, so the guarantee is checked against the asset's real, hook-derived value rather than the raw storage field, consistent with how `derived_balance`/`is_derived_balance_at_least` are documented and used elsewhere in the same module.

### Proof of Concept
1. Deploy a dispatchable fungible asset (modeled on the framework's `deflation_token` test pattern) that registers a `deposit` hook which increases the raw `FungibleStore.balance` by the full deposited amount but also mutates a separate internal ledger to actually credit the holder less (e.g., applies an out-of-band fee not reflected in `FungibleStore.balance`), and registers a `derived_balance_function` that reports the reduced, true amount.
2. A caller invokes `dispatchable_fungible_asset::transfer_assert_minimum_deposit(sender, from, to, amount, expected)` expecting `expected` to reflect the recipient's real economic gain.
3. Because `start`/`end` are read via `fungible_asset::balance()`, the raw balance shows a full, undiminished increase, so the assertion `end - start >= expected` passes even though `derived_balance(to)` (the value the token's own accounting says the recipient actually holds) increased by less than `expected`.
4. A downstream integrator that credits shares/value based on this "guaranteed minimum" ends up crediting more value than the recipient truly received under the asset's own accounting, corrupting custody accounting for that asset. [1](#0-0) [4](#0-3)

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L150-174)
```text
    #[view]
    /// Get the derived value of store using the overloaded hook.
    ///
    /// The semantics of value will be governed by the function specified in DispatchFunctionStore.
    public fun derived_balance<T: key>(store: Object<T>): u64 {
        let func_opt = fungible_asset::derived_balance_dispatch_function(store);
        if (func_opt.is_some()) {
            dispatched_derived_balance(store, func_opt.borrow())
        } else {
            fungible_asset::balance(store)
        }
    }

    #[view]
    /// Whether the derived value of store using the overloaded hook is at least `amount`
    ///
    /// The semantics of value will be governed by the function specified in DispatchFunctionStore.
    public fun is_derived_balance_at_least<T: key>(store: Object<T>, amount: u64): bool {
        let func_opt = fungible_asset::derived_balance_dispatch_function(store);
        if (func_opt.is_some()) {
            dispatched_derived_balance(store, func_opt.borrow()) >= amount
        } else {
            fungible_asset::is_balance_at_least(store, amount)
        }
    }
```
