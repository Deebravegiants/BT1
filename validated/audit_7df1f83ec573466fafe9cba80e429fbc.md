### Title
Unvalidated route pool can turn a signed swap authorization into arbitrary wallet-token theft - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy routes accept attacker-controlled pool addresses without a trusted-pool registry, allowing a malicious venue contract to request a victim-signed token transfer unrelated to the advertised swap. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` all accept an opaque `swap: Bytes` route while acting for the caller's position. [3](#0-2) 

`swap_tokens` passes that payload to the configured router after authorizing only the controller's exact input transfer. [4](#0-3) 

The router constructs each hop's `pool` directly from the caller-supplied `assets` registry and dispatches it to the selected venue adapter. [5](#0-4) [6](#0-5) 

Program validation checks opcode encoding and registry bounds but does not compare the pool address against a trusted registry or derive it from a canonical venue factory. [7](#0-6) [8](#0-7) 

Consequently, a malicious contract implementing the expected pool ABI can call `token.transfer(victim, attacker, amount)` while nested beneath the user's signed strategy invocation, causing simulation to add that theft as a signed authorization child. [9](#0-8) [10](#0-9) 

### Impact Explanation
An attacker can steal any token balance the victim authorizes in the poisoned invocation tree while still paying enough swap output to satisfy the router and controller's measured-output checks. [11](#0-10) [12](#0-11) 

The stolen asset need not be either swap leg or be held by the lending pool, so the loss can exceed the routed collateral amount and drain an unrelated wallet balance. [13](#0-12) 

### Likelihood Explanation
Exploitation requires the victim to submit an attacker-supplied route and sign the simulated authorization containing the malicious child transfer, but neither the route schema nor the controller rejects the unallowlisted pool before that point. [14](#0-13) [10](#0-9) 

A fair-paying malicious pool makes the economic result look successful, increasing the chance that a route provider can induce users to approve the poisoned authorization. [15](#0-14) 

### Recommendation
Bind each route hop to governance-approved venue/pool addresses or derive the pool from a trusted venue factory instead of accepting an arbitrary `assets` registry entry. [16](#0-15) 

Until pool admission is enforced on-chain, clients should treat any authorization child other than the expected strategy input transfer as fatal, but client-side inspection alone should not be the protocol boundary. [17](#0-16) 

### Proof of Concept
1. Victim supplies USDC through `swap_collateral(caller, account_id, current, amount, new, swap)` and holds an unrelated `wallet_token` balance. [18](#0-17) [19](#0-18) 
2. Attacker deploys a pool contract whose `swap` entrypoint calls `token::Client::new(&wallet_token).transfer(&victim, &attacker, &amount)` and also pays the expected output. [9](#0-8) 
3. Attacker encodes that pool address in the route's `assets` registry and selects a supported `SwapVenue`, causing `dispatch_hop` to invoke the malicious contract. [1](#0-0) 
4. Simulation records `wallet_token.transfer(victim, attacker, WALLET_BALANCE)` as a child of the victim's `swap_collateral` authorization rather than rejecting the foreign transfer. [20](#0-19) 
5. Signing the simulated tree empties the victim's unrelated wallet balance while crediting the expected ETH output. [21](#0-20)

### Citations

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

**File:** interfaces/controller/src/lib.rs (L88-116)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-54)
```rust
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L34-40)
```rust
    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L42-56)
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
```

**File:** contracts/swap-aggregator/src/program.rs (L20-24)
```rust
//!   [2]      idx_a       pool
//!   [3]      idx_b       token_in  | lp share token
//!   [4]      idx_c       token_out | amounts index
//! weights (3 * weight_count bytes)
//!   u24 big-endian parts-per-million, each in 1..=PPM_DENOMINATOR
```

**File:** contracts/swap-aggregator/src/program.rs (L239-249)
```rust
    fn validate(&self, env: &Env, assets_len: u32, amounts_len: u32, weight_count: u32) {
        for i in 0..self.op_count {
            let record = self.raw(i);
            let Some(opcode) = Opcode::from_u8(record[field::OPCODE]) else {
                panic_with_error!(env, Error::InvalidRouteXdr);
            };
            let mode = Mode::from_u8(record[field::MODE]);
            let (idx_a, idx_b, idx_c) = (
                record[field::POOL] as u32,
                record[field::TOKEN_IN] as u32,
                record[field::TOKEN_OUT] as u32,
```

**File:** contracts/swap-aggregator/src/program.rs (L281-291)
```rust
            if idx_a >= assets_len || idx_b >= assets_len {
                panic_with_error!(env, Error::InvalidRouteXdr);
            }
            match opcode {
                Opcode::Swap(_) => {
                    if idx_c >= assets_len {
                        panic_with_error!(env, Error::InvalidRouteXdr);
                    }
                    if idx_b == idx_c {
                        panic_with_error!(env, Error::SameToken);
                    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L82-100)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-226)
```rust
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
