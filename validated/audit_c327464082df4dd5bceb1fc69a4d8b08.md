### Title

Caller-controlled swap routes can attach attacker token transfers to the victim’s signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary

`swap_collateral` accepts caller-supplied route bytes and executes them through the configured router without validating the pool addresses embedded in that route. [1](#0-0) [2](#0-1) 

A malicious route can name an attacker-controlled contract as a Soroswap pool; the router invokes that contract during the strategy. [3](#0-2) [4](#0-3) 

While executing under the victim’s top-level `swap_collateral` authorization, the malicious pool can request an unrelated `token.transfer(victim, attacker, amount)`, causing that transfer to appear as an additional child in the authorization tree produced by simulation. [5](#0-4) [6](#0-5) 

If the victim signs the simulated tree without independently decoding every nested authorization, the attacker receives the unrelated wallet tokens while the route can still return sufficient swap output to satisfy settlement checks. [7](#0-6) [8](#0-7) 

### Finding Description

`swap_collateral` authenticates the caller and ensures that the caller owns or delegates the target account, but it treats the opaque `swap` payload as routing data rather than as an authorization-relevant security boundary. [9](#0-8) 

The strategy withdraws collateral into controller custody and passes the caller’s `StrategySwap` to `swap_tokens_or_passthrough`. [10](#0-9) 

`swap_tokens` snapshots only the input and output token balances, authorizes the exact controller-to-router input transfer, invokes the configured router, and then checks measured input spending plus positive output. [11](#0-10) 

Those measurements constrain the controller’s routed input and output, but they do not constrain other token contracts that route-selected code may invoke under the victim’s authorization tree. [7](#0-6) [3](#0-2) 

The route format takes pool addresses from the payload’s unrestricted address registry, and a Soroswap hop invokes caller-selected `get_reserves` and `swap` functions on that address. [12](#0-11) [13](#0-12) 

An attacker can deploy a contract implementing those functions, return reserves that produce a valid requested output, perform or arrange the expected swap output, and additionally invoke `transfer(victim, attacker, amount)` on an unrelated token held by the victim. [13](#0-12) [14](#0-13) 

This is analogous to the browser vulnerability because attacker-controlled nested behavior can be presented beneath the trusted top-level action, while the decisive authorization UI context remains the victim’s `swap_collateral` call. [1](#0-0) 

### Impact Explanation

A successful attack steals arbitrary unrelated token balances from the victim’s wallet up to the amount included in the malicious authorization child. [15](#0-14) [16](#0-15) 

The loss is not limited to the collateral submitted to the strategy because the malicious pool can invoke a different listed or unlisted token contract with `from` set to the victim. [17](#0-16) [18](#0-17) 

The protocol’s positive-output and final-risk checks do not prevent the theft because the malicious venue can deliver economically valid output while performing the additional signed transfer. [7](#0-6) [14](#0-13) 

### Likelihood Explanation

The attacker can reach the vulnerable path by supplying a malicious `swap` argument to `swap_collateral`, and the same route trust boundary also affects other controller strategies that route caller-selected swaps. [19](#0-18) [20](#0-19) 

The attack requires social engineering or a compromised route-generation path because the victim must sign the simulated authorization tree containing the extra transfer. [5](#0-4) [21](#0-20) 

That requirement lowers the likelihood relative to an unauthenticated drain, but the operation is otherwise deterministic: the route selects the pool contract, the pool executes during the strategy, and a fair output lets the complete transaction succeed. [17](#0-16) [13](#0-12) 

### Recommendation

Do not allow strategy routes to invoke arbitrary pool addresses. [17](#0-16) 

Maintain an on-chain venue/pool allowlist for route hops, or restrict routes to venue adapters that only call governance-approved pool contracts. [18](#0-17) 

Clients should also decode the complete authorization tree before signing and reject any tree containing transfers or other invocations unrelated to the intended swap; this mitigates existing deployments but does not replace an on-chain pool allowlist. [2](#0-1) 

### Proof of Concept

1. The attacker deploys `RoguePool`, which implements `get_reserves()` and `swap(amount_0_out, amount_1_out, to)`. [13](#0-12) 
2. The victim owns lending account `A` with collateral in `current` and requests `swap_collateral(caller=victim, account_id=A, current, amount, new, swap=malicious_route)`. [1](#0-0) 
3. `malicious_route` encodes a Soroswap hop whose pool index resolves to `RoguePool`; the payload’s address registry is supplied by the caller rather than an on-chain pool allowlist. [22](#0-21) [12](#0-11) 
4. `RoguePool.get_reserves()` returns reserves that make the adapter calculate a positive `requested_out`. [23](#0-22) 
5. `RoguePool.swap()` calls `unrelated_token.transfer(victim, attacker, victim_balance)` and then causes the router’s `token_out` balance to increase by at least `requested_out`, for example by pre-funding and paying the output itself. [24](#0-23) [14](#0-13) 
6. Simulation returns a `swap_collateral` authorization tree containing the additional `unrelated_token.transfer(victim, attacker, victim_balance)` child; if the victim signs that tree, the token transfer and the otherwise valid collateral swap both execute. [5](#0-4) [7](#0-6)

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L27-48)
```rust
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

**File:** contracts/controller/src/strategies/swap.rs (L57-70)
```rust
/// Passes matching assets through only with an empty route; otherwise swaps.
pub(crate) fn swap_tokens_or_passthrough(
    env: &Env,
    refund_to: &Address,
    token_in: &Address,
    amount_in: i128,
    token_out: &Address,
    swap: &StrategySwap,
) -> i128 {
    if token_in == token_out {
        assert_with_error!(env, swap.is_empty(), GenericError::InvalidPayments);
        amount_in
    } else {
        swap_tokens(env, refund_to, token_in, amount_in, token_out, swap)
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-63)
```rust
pub(crate) fn run(env: Env, sender: Address, total_in: i128, payload: StrategyPayload) -> i128 {
    sender.require_auth();

    if total_in <= 0 {
        panic_with_error!(&env, Error::InvalidAmount);
    }

    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L78-86)
```rust
    let credited_in = transfer_amount_measured(
        &env,
        &input_token,
        &sender,
        &router,
        total_in,
        GenericError::AmountMustBePositive,
    );
    vault.deposit(&input_token, credited_in);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L111-118)
```rust
    for i in 0..program.len() {
        prev = execute_op(
            &ctx,
            &mut vault,
            program.op(&env, i),
            prev,
            &mut tokens_cache,
        );
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L125-135)
```rust
    let total_out = vault.balance_of(&output_token);
    if total_out < total_min_out {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    vault.withdraw(&output_token, total_out);
    token::Client::new(&env, &output_token).transfer(&router, &sender, &total_out);

    residual::accrue_residual_as_revenue(&env, &mut vault);

    total_out
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-165)
```rust
    match op.opcode {
        Opcode::Swap(venue) => {
            let hop = SwapHop {
                pool: ctx.assets.get_unchecked(op.idx_a),
                token_in: ctx.assets.get_unchecked(op.idx_b),
                token_out: ctx.assets.get_unchecked(op.idx_c),
                venue,
            };
            let amount_in = resolve_amount(ctx, vault, op.mode, &hop.token_in, prev);
            if amount_in <= 0 {
                panic_with_error!(ctx.env, Error::InvalidAmount);
            }

            vault.withdraw(&hop.token_in, amount_in);
            let out = venues::dispatch_hop(ctx.env, ctx.router, &hop, amount_in, tokens_cache);
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L51-87)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let token_in_is_0 = ctx.hop.token_in < ctx.hop.token_out;

    let no_args: Vec<Val> = vec![ctx.env];
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
    );
    let (reserve_in, reserve_out) = if token_in_is_0 {
        (reserve_0, reserve_1)
    } else {
        (reserve_1, reserve_0)
    };

    let requested_out = soroswap_amount_out(ctx.env, ctx.amount_in, reserve_in, reserve_out);
    if requested_out <= 0 {
        panic_with_error!(ctx.env, Error::ZeroOutput);
    }

    let token_client = token::Client::new(ctx.env, &ctx.hop.token_in);
    token_client.transfer(ctx.router, &ctx.hop.pool, &ctx.amount_in);

    let (amount_0_out, amount_1_out) = if token_in_is_0 {
        (0_i128, requested_out)
    } else {
        (requested_out, 0_i128)
    };
    let args: Vec<Val> = vec![
        ctx.env,
        amount_0_out.into_val(ctx.env),
        amount_1_out.into_val(ctx.env),
        ctx.router.into_val(ctx.env),
    ];
    let _: () = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
```

**File:** contracts/controller/src/strategies/legs.rs (L231-258)
```rust
/// Withdraws to the controller, then swaps its measured receipt into `token_out`.
/// Matching assets pass through unchanged; returns the available output.
pub(crate) fn withdraw_and_swap_from_supply(
    env: &Env,
    account: &mut Account,
    cache: &mut Context,
    caller: &Address,
    from: &HubAssetKey,
    amount: i128,
    token_out: &Address,
    swap: &StrategySwap,
    action: events::PositionAction,
) -> i128 {
    let supply_pos = get_supply_position_or_panic(env, account, from);

    let actual_withdrawn = withdraw_collateral_to_controller(
        env,
        account,
        cache,
        StrategyWithdraw {
            hub_asset: from,
            amount,
            position: &supply_pos,
            action,
        },
    );

    swap_tokens_or_passthrough(env, caller, &from.asset, actual_withdrawn, token_out, swap)
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L42-58)
```rust
    let received = ctx
        .output_balance()
        .checked_sub(before_out)
        .unwrap_or_else(|| panic_with_error!(env, Error::ZeroOutput));
    if received <= 0 {
        panic_with_error!(env, Error::ZeroOutput);
    }

    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }

    received
```

**File:** contracts/swap-aggregator/src/types.rs (L25-29)
```rust
pub struct SwapHop {
    pub pool: Address,
    pub token_in: Address,
    pub token_out: Address,
    pub venue: SwapVenue,
```

**File:** contracts/swap-aggregator/src/program.rs (L17-25)
```rust
//! instructions (5 * op_count bytes)
//!   [0]      opcode      -> Opcode
//!   [1]      mode        -> Mode
//!   [2]      idx_a       pool
//!   [3]      idx_b       token_in  | lp share token
//!   [4]      idx_c       token_out | amounts index
//! weights (3 * weight_count bytes)
//!   u24 big-endian parts-per-million, each in 1..=PPM_DENOMINATOR
//! ```
```
