No vulnerability found for this question.

**Analysis:**

`transfer_assert_minimum_deposit` in `dispatchable_fungible_asset.move` computes `start`/`end` balances via `fungible_asset::balance()` calls that occur *after* the deposit hook has already run, so any fee/skim applied by a malicious deposit hook is fully reflected in `end - start` before the assertion executes. [1](#0-0) 

The `expected` parameter is supplied by the **sender** (the party invoking the entry function), not by the deposit-hook author or any third-party attacker. If a sender sets a low `expected`, they are only weakening their own protection guarantee — this does not let an attacker "cross the custody boundary" or corrupt the recipient's balance, because:

1. The actual deposited amount is whatever the registered deposit hook computes, and that hook can only be registered by the asset's creator holding the `ConstructorRef` at asset-creation time — a privileged action, not something an unprivileged caller can inject into an existing fungible asset's dispatch table. [2](#0-1) 

2. The assertion correctly aborts with `EAMOUNT_MISMATCH` whenever the post-hook deposit amount is less than `expected`, as demonstrated by the test `test_deflation_assert_min_deposit`, which sets `expected=11` against a deflationary hook that only delivers `10`, and confirms the abort. [3](#0-2) 

3. Positive-path tests (`test_deflation_e2e_basic_flow`, `test_deflation_native_dispatch`) confirm that when `expected` matches the hook-adjusted amount, the recipient's balance increases by exactly that adjusted amount and the check passes — no silent value skimming occurs beyond what the hook itself (controlled by the asset issuer, not an attacker) is designed to do. [4](#0-3) [5](#0-4) 

There is no path by which an unprivileged caller can pass an `expected` value that is "lower than the true dispatch-hook-adjusted deposit" in a way that harms anyone other than themselves (the sender), and no path by which the check can be bypassed to let the recipient receive less than what the assertion verified. The custody invariant — "the function either aborts or the recipient's balance increases by at least `expected`" — is enforced correctly using post-hook balances. This does not meet the bar for a custody-boundary violation.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L38-57)
```text
    public fun register_dispatch_functions(
        constructor_ref: &ConstructorRef,
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>,
    ) {
        fungible_asset::register_dispatch_functions(
            constructor_ref,
            withdraw_function,
            deposit_function,
            derived_balance_function,
        );
        let store_obj = &constructor_ref.generate_signer();
        move_to<TransferRefStore>(
            store_obj,
            TransferRefStore {
                transfer_ref: fungible_asset::generate_transfer_ref(constructor_ref),
            }
        );
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

**File:** aptos-move/framework/aptos-framework/tests/deflation_token_tests.move (L57-59)
```text
        dispatchable_fungible_asset::transfer_assert_minimum_deposit(creator, creator_store, aaron_store, 10, 10);
        assert!(fungible_asset::balance(creator_store) == 62, 42);
        assert!(fungible_asset::balance(aaron_store) == 35, 42);
```

**File:** aptos-move/framework/aptos-framework/tests/deflation_token_tests.move (L62-85)
```text
    #[test(creator = @aptos_framework, aaron = @0xface)]
    #[expected_failure(abort_code = 0x70002, location = aptos_framework::dispatchable_fungible_asset)]
    fun test_deflation_assert_min_deposit(
        creator: &signer,
        aaron: &signer,
    ) {
        features::change_feature_flags_for_testing(creator, vector[features::get_function_value_dispatch_feature()], vector[]);
        let (creator_ref, token_object) = fungible_asset::create_test_token(creator);
        let (mint, _, _, _) = fungible_asset::init_test_metadata(&creator_ref);
        let metadata = token_object.convert<TestToken, Metadata>();

        let creator_store = fungible_asset::create_test_store(creator, metadata);
        let aaron_store = fungible_asset::create_test_store(aaron, metadata);

        deflation_token::initialize(creator, &creator_ref);

        assert!(fungible_asset::supply(metadata) == option::some(0), 1);
        // Mint
        let fa = mint.mint(100);
        assert!(fungible_asset::supply(metadata) == option::some(100), 2);
        dispatchable_fungible_asset::deposit(creator_store, fa);

        dispatchable_fungible_asset::transfer_assert_minimum_deposit(creator, creator_store, aaron_store, 10, 11);
    }
```

**File:** aptos-move/framework/aptos-framework/tests/legacy_native_dispatch_tests.move (L50-54)
```text
        dispatchable_fungible_asset::transfer_assert_minimum_deposit(
            creator, creator_store, aaron_store, 10, 10
        );
        assert!(fungible_asset::balance(creator_store) == 78, 4);
        assert!(fungible_asset::balance(aaron_store) == 20, 5);
```
