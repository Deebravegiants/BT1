### Title
Attacker-controlled route venue can smuggle a signed wallet-token transfer into a swap authorization tree - ([File: contracts/swap-aggregator/src/venues/soroswap.rs](contracts/swap-aggregator/src/venues/soroswap.rs))

### Summary
A route supplied to `execute_strategy` selects pool contracts from the caller-controlled `assets` registry, and the venue adapters invoke those addresses without an allowlist. [1](#0-0) [2](#0-1) 

During a Soroswap hop, the router calls `get_reserves` and `swap` on that caller-selected pool. [3](#0-2) [4](#0-3) 

A malicious pool can use that callback to request `victim.require_auth()` through an unrelated token transfer; Soroban records it as a child beneath the victim’s root authorization, so a wallet that signs the simulated tree also authorizes the unrelated transfer. [5](#0-4) [6](#0-5) 

This is analogous to the Ghostscript flaw because untrusted route code obtains a hidden privileged operation that escapes the operation the user intended to authorize.

### Finding Description
`execute_strategy` authenticates only the supplied `sender`, decodes the payload, and then executes every instruction. [7](#0-6) 

Each swap instruction constructs a `SwapHop` whose `pool`, `token_in`, and `token_out` fields come from the payload’s indexed address registry. [8](#0-7) [1](#0-0) 

`dispatch_hop` dispatches the venue implementation but performs only balance-delta accounting around that venue call. [9](#0-8) [10](#0-9) 

Those checks ensure that the router spent the requested input and received positive output, but they do not restrict what additional authorization requests the selected pool makes while it is on the call stack. [11](#0-10) 

For a controller-routed strategy, the controller’s own router grant is narrowly scoped to one exact input transfer and measured output. [12](#0-11) [13](#0-12) 

That scoping protects only the controller’s `token_in.transfer`; it does not remove the account owner’s root authorization from the call tree under which the pool executes. [12](#0-11) [4](#0-3) 

### Impact Explanation
An attacker can steal arbitrary token balances from a user who signs a poisoned route simulation, including assets that are unrelated to the lending position and never passed as route inputs. [14](#0-13) 

The malicious hop can still satisfy every economic check by consuming the exact routed input and paying sufficient output from prefunded inventory, so the swap completes while the hidden transfer also executes. [10](#0-9) [15](#0-14) 

The impact is theft of user funds, and severity is Medium because exploitation requires the victim to submit a malicious route and sign the resulting authorization tree rather than being executable against an arbitrary user without interaction. [16](#0-15) 

### Likelihood Explanation
Any unprivileged address can deploy a compatible malicious pool contract and place its address in the route’s `assets` registry because route validation checks indices and instruction structure rather than pool identity. [2](#0-1) [1](#0-0) 

The same exposure exists through direct `execute_strategy` calls and controller entrypoints that forward route bytes, such as `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply`. [7](#0-6) [12](#0-11) 

The attack is not unconditional: enforcing authorization rejects the rogue transfer when the signed tree omits it, and succeeds only when the victim signs the poisoned tree produced by simulation. [17](#0-16) 

### Recommendation
Do not invoke pool addresses supplied by route data without binding them to a trusted venue registry or pool factory/implementation identifier.

At minimum, maintain an on-chain allowlist of acceptable pool contracts for each venue and reject any hop whose `pool` address is absent before executing it.

Additionally, expose the complete simulated authorization tree to users and require wallets or route builders to reject any child invocation other than the expected protocol token pull before signing.

If arbitrary third-party pools must remain supported, isolate the venue call from user-authorization scope or add a host-supported authorization boundary that prevents venue code from adding unrelated child authorizations to the caller’s root entry.

### Proof of Concept
1. Alice owns a lending account and holds an unrelated wallet token `T`.

2. The attacker deploys `RoguePool` implementing the Soroswap-facing calls `get_reserves` and `swap`.

3. The route payload places `RoguePool` in `assets` and encodes a `Soroswap` instruction for `USDC -> ETH`; that instruction survives structural validation because the pool is just an indexed address. [18](#0-17) [2](#0-1) 

4. The router measures input and output balances, calls the attacker-selected pool, and receives a valid prefunded ETH output, so the venue accounting succeeds. [19](#0-18) [10](#0-9) 

5. Inside `RoguePool::swap`, the attacker invokes `T.transfer(Alice, attacker, Alice_balance)`; simulation records that token transfer as a child of Alice’s `swap_collateral` authorization. [5](#0-4) [20](#0-19) 

6. If Alice signs the simulated tree, the unrelated wallet token moves to the attacker while the nominal `USDC -> ETH` position swap still completes. [6](#0-5)

### Citations

**File:** contracts/swap-aggregator/src/types.rs (L21-30)
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
```

**File:** contracts/swap-aggregator/src/types.rs (L38-44)
```rust
pub struct StrategyPayload {
    /// Amount registry: min-out, fixed inputs, burn floors, mint min-shares.
    pub amounts: Vec<i128>,
    /// Address registry: tokens, pools, and LP share tokens.
    pub assets: Vec<Address>,
    /// Packed program: header, instruction records, split weights.
    pub ops: Bytes,
```

**File:** contracts/swap-aggregator/src/program.rs (L96-104)
```rust
    /// Swap through `venue`: `idx_a` pool, `idx_b` token in, `idx_c` token out.
    Swap(SwapVenue),
    /// Aquarius withdraw: `idx_a` pool, `idx_b` share token, `idx_c` first
    /// index of the per-constituent floor run in `amounts`.
    Burn,
    /// Aquarius deposit: `idx_a` pool, `idx_b` share token, `idx_c` index of
    /// the minimum share count in `amounts`.
    Mint,
}
```

**File:** contracts/swap-aggregator/src/program.rs (L237-250)
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
            );
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L51-58)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let token_in_is_0 = ctx.hop.token_in < ctx.hop.token_out;

    let no_args: Vec<Val> = vec![ctx.env];
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L66-87)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L230-268)
```rust
fn enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer() {
    let s = Scene::new();

    // Control: a pool that touches nothing passes with the honest root-only tree.
    let benign = s.route_through_pool_stealing(0);
    s.try_swap_with_signed_tree(&benign, &[])
        .expect("the honest tree authorizes an honest route");
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);

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
