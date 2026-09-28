### Title
Attacker-controlled swap route executes arbitrary pool code beneath caller authorization - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller accepts opaque attacker-supplied `swap` bytes on strategy entrypoints and forwards them unchanged to the configured aggregator through `execute_strategy`. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral`, `swap_debt`, and `repay_debt_with_collateral` all require the caller to be the account owner or an active delegate, but impose no structural validation on the route beyond non-empty bytes when input and output tokens differ. [3](#0-2) [4](#0-3) [5](#0-4) 

`swap_tokens` authorizes only the exact input-token transfer from the controller to the router, then executes the caller-provided route. [6](#0-5)  Its post-call checks bound the controller's routed input and require positive measured output, but they do not constrain what additional calls a route-selected venue performs under the caller's signed authorization tree. [7](#0-6) 

This is the Soroban analogue of substituting attacker-controlled data into an executable command: the route payload selects contract code and invocation arguments, while the signed invocation tree can incorporate an additional token transfer from the victim to the attacker. [8](#0-7) [9](#0-8) 

### Impact Explanation
A malicious route can return a valid swap output and satisfy the controller's balance-delta and final-risk checks while a route-selected contract also performs an unrelated token transfer from the victim's wallet to the attacker. [7](#0-6)  The financial impact is therefore theft of user funds, potentially exceeding the routed collateral or debt amount because the injected transfer is not bounded by `amount_in`, the route minimum, or the controller's post-swap checks. [10](#0-9) 

### Likelihood Explanation
An unprivileged attacker can deploy a malicious venue-compatible contract and supply a crafted route to a victim through an interface, quote, or copied payload. [11](#0-10)  Exploitation requires the victim to execute a strategy and sign the simulated authorization tree containing the extra transfer, so it is conditional on victim interaction rather than a purely unilateral state transition. [12](#0-11) 

### Recommendation
Do not treat route bytes as opaque trusted data. Constrain executable route venues to a governance-approved contract registry, or otherwise decode and validate the route before invoking it so that every pool and token address is explicitly authorized. [13](#0-12)  As a defense-in-depth measure, signing clients should reject a strategy authorization tree containing any child invocation other than the expected input transfer. [9](#0-8) 

### Proof of Concept
1. The attacker deploys a contract exposing the venue call expected by the router and configures it to invoke `token.transfer(victim, attacker, wallet_balance)` during the hop. [11](#0-10) 
2. The attacker crafts `swap` bytes naming that contract as a hop while also arranging for a fair `token_out` payment back to the controller. [8](#0-7) 
3. The victim calls `swap_collateral(caller, account_id, current, amount, new, swap)` or another route-bearing strategy with those bytes. [14](#0-13) 
4. The controller forwards `swap` unchanged to `execute_strategy`, while its authorization helper covers only the controller's exact input transfer to the router. [2](#0-1) [15](#0-14) 
5. If simulation records and the victim signs an authorization tree containing the malicious venue's extra `transfer` child, the strategy can still pass the controller's measured-output and account-finalization checks while the unrelated wallet transfer executes. [7](#0-6) [16](#0-15)

### Citations

**File:** contracts/controller/src/lib.rs (L255-302)
```rust
    /// Borrows `amount` of `new_debt`, converts it to `existing_debt` via `swap`
    /// and repays with the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
    fn swap_debt(
        env: Env,
        caller: Address,
        account_id: u64,
        existing_debt: HubAssetKey,
        amount: i128,
        new_debt: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_debt::process_swap_debt(
            &env,
            &caller,
            SwapDebtParams {
                account_id,
                existing_debt: &existing_debt,
                new_debt_amount: amount,
                new_debt: &new_debt,
                swap: &swap,
            },
        );
    }

    /// Withdraws `amount` of `current`, converts it to `new` via `swap` and
    /// redeposits the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_collateral::process_swap_collateral(
            &env,
            &caller,
            SwapCollateralParams {
                account_id,
                current: &current,
                from_amount: amount,
                new: &new,
                swap: &swap,
            },
        );
```

**File:** contracts/controller/src/strategies/swap.rs (L24-54)
```rust
    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);

    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });

    // Reject input gains or overspending; refund only this swap's unused input.
    let in_after = token_in_client.balance(&controller);
    assert_with_error!(env, in_after <= in_before, StrategyError::RouterOverspend);
    let actual_spent = in_before - in_after;
    assert_with_error!(
        env,
        actual_spent <= amount_in,
        StrategyError::RouterOverspend
    );
    let leftover = amount_in - actual_spent;
    if leftover > 0 {
        token_in_client.transfer(&controller, refund_to, &leftover);
    }

    verify_router_output(env, token_out, out_before)
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-64)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    // Check the destination before withdrawing existing collateral.
    require_can_supply(env, &mut cache, account.spoke_id, new);

    let extra_assets = vec![env, current.asset.clone(), new.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let swapped_amount = withdraw_and_swap_from_supply(
        env,
        &mut account,
        &mut cache,
        caller,
        current,
        from_amount,
        &new.asset,
        swap,
        events::PositionAction::SwColWd,
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L67-76)
```rust
    let deposit_assets = vec![env, (new.clone(), swapped_amount)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L37-72)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(
        env,
        existing_debt != new_debt,
        GenericError::AssetsAreTheSame
    );
    config::require_hub_active(env, existing_debt.hub_id);
    require_positive_amount(env, new_debt_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    let existing_pos = get_debt_position_or_panic(env, &account, existing_debt);

    let extra_assets = vec![env, existing_debt.asset.clone(), new_debt.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let amount_received = borrow_into_controller(
        env,
        &mut account,
        new_debt,
        new_debt_amount,
        true,
        PositionAction::SwDebtR,
        &mut cache,
    );

    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L44-78)
```rust
    require_authorized_caller(env, caller);

    require_positive_amount(env, collateral_amount);
    config::require_hub_active(env, collateral.hub_id);
    config::require_hub_active(env, debt.hub_id);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);

    let extra_assets = vec![env, collateral.asset.clone(), debt.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    if collateral == debt {
        // Same-market netting moves no tokens, so a swap route is invalid.
        assert_with_error!(env, swap.is_empty(), GenericError::InvalidPayments);
        net_settle_collateral_against_debt(
            env,
            &mut account,
            &mut cache,
            collateral,
            collateral_amount,
            events::PositionAction::RpColNet,
        );
    } else {
        repay_via_collateral_swap(
            env,
            caller,
            &mut account,
            &mut cache,
            collateral,
            collateral_amount,
            debt,
            swap,
        );
```

**File:** common/src/types/shared.rs (L9-10)
```rust
/// Encoded swap route passed to the aggregator router's `execute_strategy` entry point.
pub type StrategySwap = Bytes;
```

**File:** common/src/token.rs (L33-51)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```

**File:** contracts/controller/src/risk/validation.rs (L1-20)
```rust
use crate::risk;
use crate::spec_hooks;
use common::constants::{MIN_BORROWABLE_ASSET_DECIMALS, MIN_WHOLE_UNIT_COLLATERAL};
use common::errors::*;
use common::math::fp::Wad;
use common::types::{Account, AccountPositionType, AggregatedPayments, HubAssetKey};
use soroban_sdk::{assert_with_error, panic_with_error, Address, Env, Map, Vec};

use crate::storage::iter_typed_positions;
use crate::{context::Context, storage};

/// Authenticates `caller` and rejects execution during a flash loan.
pub(crate) fn require_authorized_caller(env: &Env, caller: &Address) {
    caller.require_auth();
    require_not_flash_loaning(env);
}

/// Rejects execution while the temporary flash-loan flag is set.
pub(crate) fn require_not_flash_loaning(env: &Env) {
    assert_with_error!(
```

**File:** interfaces/controller/src/lib.rs (L88-117)
```rust
    fn swap_debt(
        env: Env,
        caller: Address,
        account_id: u64,
        existing_debt: HubAssetKey,
        amount: i128,
        new_debt: HubAssetKey,
        swap: Bytes,
    );

    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    );

    fn repay_debt_with_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        collateral: HubAssetKey,
        collateral_amount: i128,
        debt: HubAssetKey,
        swap: Bytes,
        close_position: bool,
    );
```
