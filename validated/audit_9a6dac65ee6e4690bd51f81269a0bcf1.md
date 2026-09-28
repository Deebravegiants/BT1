### Title
Arbitrary swap routes can attach unauthorized wallet-token transfers to a victim’s strategy authorization - (contracts/controller/src/strategies/swap.rs)

### Summary

`swap_collateral` lets the account owner or delegate supply an opaque `StrategySwap` route, which the controller forwards to the configured router without inspecting the pools, tokens, or contracts embedded in it. [1](#0-0) 

The controller constrains only its own exact input transfer to the router; it does not prevent contract code reached by the route from requesting another transfer from the account owner. [2](#0-1) 

As in the two-archive Tar traversal, the first apparently bounded operation establishes a trusted path and a later payload-selected component escapes that boundary. [3](#0-2) 

### Finding Description

`process_swap_collateral` requires authorization and verifies that the caller controls `account_id`, but it accepts `swap` as caller-controlled strategy data and passes it into `withdraw_and_swap_from_supply`. [4](#0-3) 

`swap_tokens` snapshots the controller’s input and output balances, authorizes one exact `token_in.transfer(controller, router, amount_in)`, invokes the configured router with the supplied strategy, and then checks only controller input spend plus positive output receipt. [5](#0-4) 

Those checks bound the controller’s own routed input and credited output, but they do not enumerate every nested invocation made by contracts reached through the route. [6](#0-5) 

A malicious venue can therefore issue an unrelated token transfer naming the strategy caller as `from` and an attacker address as `to`; the host records that request beneath the caller’s authorization entry and executes it if the caller signs the returned tree. [3](#0-2) 

The measured-output check remains satisfied because the malicious venue or the surrounding route can still deliver the expected output token. [7](#0-6) 

### Impact Explanation

An attacker can steal arbitrary wallet tokens held by the account owner, including tokens unrelated to the collateral being swapped. [3](#0-2) 

The loss is not bounded by `from_amount`, the route minimum output, or the account’s final health-factor checks: those checks cover the routed position assets, while the malicious nested transfer can drain a separate wallet balance. [6](#0-5) 

This is theft of user funds and therefore meets the requested impact threshold. [3](#0-2) 

### Likelihood Explanation

The attacker must induce the victim to execute a malicious route and sign the authorization tree containing the extra transfer. [3](#0-2) 

This is realistic where users select routes through a UI or aggregator and wallets present a complex authorization tree without clearly separating the protocol input transfer from venue-injected transfers. [3](#0-2) 

The attacker does not need a protocol privilege, leaked key, compromised router, or invalid oracle; a route can name attacker-controlled pool code because the controller treats `swap` as caller-controlled opaque strategy data. [1](#0-0) 

### Recommendation

Do not treat measured input/output settlement as sufficient route authorization. [6](#0-5) 

Maintain a governance-approved allowlist of concrete pool or venue contracts and require the router to reject any hop whose pool address is absent from it. [8](#0-7) 

Additionally, define a canonical authorization-tree contract for every strategy: honest routes must produce no caller child invocation beyond the exact input transfer, and conforming clients should fail closed when simulation returns any additional child. [9](#0-8) 

A regression test should route `swap_collateral` through a contract that attempts `token.transfer(victim, attacker, amount)` and assert that production rejects the route before the victim can sign the injected invocation. [10](#0-9) 

### Proof of Concept

1. The attacker deploys a contract exposing the interface expected for a route hop. [11](#0-10) 
2. During the swap callback, that contract calls `token.transfer(victim, attacker, wallet_balance)` for an unrelated token held by the victim. [12](#0-11) 
3. The victim invokes `swap_collateral(caller, account_id, current, from_amount, new, swap)`, where `swap` routes through the attacker contract. [13](#0-12) 
4. The controller authorizes only its own exact input transfer to the router and invokes the route. [2](#0-1) 
5. Simulation returns a caller authorization tree containing the attacker contract’s wallet-token transfer as a child invocation. [9](#0-8) 
6. If the victim signs that returned tree, the route can still produce positive measured output, pass the controller checks, and simultaneously transfer the victim’s unrelated wallet tokens to the attacker. [6](#0-5)

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L17-76)
```rust
pub(crate) struct SwapCollateralParams<'a> {
    pub account_id: u64,
    pub current: &'a HubAssetKey,
    pub from_amount: i128,
    pub new: &'a HubAssetKey,
    pub swap: &'a StrategySwap,
}

/// Withdraws current collateral, swaps into the new asset, then deposits and
/// checks the account's final risk. Matching assets across hubs pass through.
pub(crate) fn process_swap_collateral(
    env: &Env,
    caller: &Address,
    params: SwapCollateralParams<'_>,
) {
    let SwapCollateralParams {
        account_id,
        current,
        from_amount,
        new,
        swap,
    } = params;

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
    );

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

**File:** contracts/controller/src/strategies/swap.rs (L29-54)
```rust
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

**File:** contracts/controller/src/strategies/swap.rs (L74-83)
```rust
/// Returns the output balance increase; rejects zero or negative receipts.
fn verify_router_output(env: &Env, token_out: &Address, balance_before: i128) -> i128 {
    let received = balance_delta_since(
        env,
        token_out,
        &env.current_contract_address(),
        balance_before,
    );
    assert_with_error!(env, received > 0, StrategyError::NoSwapOutput);
    received
```

**File:** docs/explanation/threat-model.md (L154-164)
```markdown
That bound covers the controller's own grant only. The router calls the pool
and token addresses its payload names and keeps no allowlist of them, so a
route can put third-party code on the call stack below the caller's
authorization. A token transfer that such code makes from the caller is
recorded by an honest simulation as a child of the caller's authorization
entry, and it executes if the caller signs that tree. The loss is then the
caller's wallet, not the routed amount, and neither the payload minimum nor the
final risk gate bounds it. An honest swap strategy gives the caller no child
entry, and a direct router swap gives exactly one input transfer. A client must
decode the route it signs and refuse an authorization tree with any other
child. The direct `execute_strategy` path has the same exposure for every swap
```
