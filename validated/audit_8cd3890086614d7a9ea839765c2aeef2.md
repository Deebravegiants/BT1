### Title
Unvalidated swap routes let a malicious pool execute token transfers under the caller’s authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The lending controller accepts opaque route bytes in strategy entrypoints and passes them to the configured swap router. A route can name an arbitrary pool contract because hop addresses come from the caller-supplied `assets` registry rather than a venue allowlist. During a strategy such as `swap_collateral`, that pool executes inside the transaction containing the account owner’s `require_auth`; if the signed authorization tree includes the malicious nested token transfer disclosed by simulation, the pool can transfer unrelated wallet tokens to an attacker while still returning a valid swap output.

### Finding Description
`swap_collateral` authorizes the caller, verifies account ownership, withdraws the selected collateral, and calls `withdraw_and_swap_from_supply` with caller-provided `swap` bytes. [1](#0-0) 

The controller grants the configured router one exact authorization for `token_in.transfer(controller, router, amount_in)`, then invokes `execute_strategy` with the uninterpreted route. [2](#0-1) 

The router decodes a hop’s `pool`, `token_in`, and `token_out` addresses directly from the route’s `assets` registry and dispatches the venue adapter for that address. [3](#0-2) 

Venue dispatch trusts the supplied pool address as the code to invoke. For a Phoenix-labelled hop, the router authorizes the pool to pull the measured input and invokes the pool’s `swap` function. [4](#0-3) 

The measured-output checks only validate the router’s input and output balances; they do not constrain other code the selected pool executes during the hop. [5](#0-4) 

The regression test demonstrates the resulting auth behavior: a rogue pool’s `wallet_token.transfer(victim, attacker, amount)` is recorded as a child of the caller’s `swap_collateral` authorization, and enforcing-mode execution succeeds when the signed tree contains that child. [6](#0-5) [7](#0-6) 

### Impact Explanation
A malicious route can steal tokens held by the account owner that are completely unrelated to the lending position and were never supplied, approved, or declared as strategy input. The route can still consume the authorized collateral input, return the expected output token, satisfy minimum-output and account-risk checks, and leave the lending transaction valid. The existing balance-delta and overspend checks bound only the controller’s routed assets; they do not prevent an additional token transfer authorized by the caller elsewhere in the transaction’s auth tree. This is theft of user funds.

### Likelihood Explanation
Exploitation requires the victim or their client to submit a crafted route and sign the poisoned authorization tree returned by simulation. That makes it less likely than a purely unauthenticated exploit, but opaque XDR route bytes and nested authorization trees are difficult for users to audit, matching the user-interaction pattern of the untrusted-search-path report. Any unprivileged attacker can deploy the malicious pool and construct the route; no protocol privilege, oracle manipulation, leaked key, or account ownership is required. The reachable entrypoints include `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` wherever a non-empty strategy route is accepted.

### Recommendation
Do not allow arbitrary pool addresses in production routes. Verify every route’s venue/pool against an allowlist or a registry of validated pools before invocation, or derive venue addresses from protocol-owned configuration rather than caller-controlled `assets`. Additionally, clients should display and validate the complete simulated authorization tree and reject any child invocation other than the expected strategy token transfer. The protocol cannot safely rely on `min_out` or balance-delta checks to constrain unrelated transfers under the caller’s root authorization.

### Proof of Concept
1. Victim owns a Normal lending account with supplied USDC collateral and also holds an unrelated `WALLET` token.
2. Attacker deploys `RoguePool` exposing a Phoenix-compatible `swap(sender, token_in, amount_in, ...)`.
3. `RoguePool::swap`:
   - pulls `amount_in` USDC from the router using the router-provided authorization;
   - sends the router enough ETH to satisfy the route’s `min_out`;
   - calls `WALLET.transfer(victim, attacker, wallet_balance)`.
4. Attacker constructs a `StrategyPayload` with:
   - `assets[0] = USDC`;
   - `assets[1] = ETH`;
   - `assets[2] = RoguePool`;
   - `amounts[0] = min_eth_out`;
   - one Phoenix swap instruction using `mode = All`, `idx_a = 2`, `idx_b = 0`, `idx_c = 1`.
5. The victim submits:
   - `swap_collateral(caller = victim, account_id, current = USDC_market, amount = swap_amount, new = ETH_market, swap = payload)`.
6. Simulation records `WALLET.transfer(victim, attacker, wallet_balance)` as a child of the victim’s `swap_collateral` authorization. If that simulated tree is signed, the host accepts the nested transfer, the rogue pool pays the expected ETH output, and the strategy finalizes.
7. Result: the victim receives the expected ETH collateral, but loses the unrelated `WALLET` balance to the attacker.

The harness demonstrates this authorization-tree behavior explicitly: recording mode nests the rogue transfer under `swap_collateral`, and enforcement succeeds when that recorded child is signed. [6](#0-5) [8](#0-7)

### Citations

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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L11-25)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let args: Vec<Val> = vec![
        ctx.env,
        ctx.router.into_val(ctx.env),
        ctx.hop.token_in.into_val(ctx.env),
        ctx.amount_in.into_val(ctx.env),
        Option::<i128>::None.into_val(ctx.env),
        Option::<i64>::None.into_val(ctx.env),
        Option::<u64>::None.into_val(ctx.env),
        Option::<i64>::None.into_val(ctx.env),
    ];
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L30-55)
```rust
    let ctx = HopContext::new(env, router, hop, amount_in);
    let before_in = ctx.input_balance();
    let before_out = ctx.output_balance();

    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };

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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-226)
```rust
#[test]
fn simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry() {
    let s = Scene::new();
    let route = s.route_through_pool_stealing(WALLET_BALANCE);

    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
    std::println!("recorded auth tree = {recorded:#?}");

    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
        sub_invocations: std::vec![],
    };
    let poisoned_root = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.t.controller.clone(),
            Symbol::new(&s.t.env, "swap_collateral"),
            s.swap_args(&route),
        )),
        sub_invocations: std::vec![stolen_transfer],
    };
    assert_eq!(recorded, std::vec![(s.alice.clone(), poisoned_root)]);

    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-268)
```rust
    // Rogue pool, honest tree: the host refuses the transfer and the whole call rolls back.
    s.t.env.mock_all_auths_allowing_non_root_auth();
    let rogue = s.route_through_pool_stealing(WALLET_BALANCE);
    let usdc_before = s.t.supply_balance_raw(ALICE, "USDC");
    let refused = s
        .try_swap_with_signed_tree(&rogue, &[])
        .expect_err("a transfer outside the signed tree is unauthorized");
    std::println!("rogue transfer under the honest tree = {refused:?}");
    assert!(
        refused.is_type(ScErrorType::Auth) || refused.is_type(ScErrorType::Context),
        "expected a host auth failure, got {refused:?}"
    );
    assert!(s
        .diagnostics()
        .contains("Unauthorized function call for address"));
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);
    assert_eq!(s.wallet(&s.attacker), 0);
    assert_eq!(s.t.supply_balance_raw(ALICE, "USDC"), usdc_before);

    // Same route, with the tree that simulation returned.
    let stolen_transfer = MockAuthInvoke {
        contract: &s.wallet_token,
        fn_name: "transfer",
        args: (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        sub_invokes: &[],
    };
    s.try_swap_with_signed_tree(&rogue, core::slice::from_ref(&stolen_transfer))
        .expect("the poisoned tree authorizes the rogue transfer");
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
```
