### Title
Attacker-controlled swap routes can inject wallet-draining token transfers into the caller’s authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
`swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral` accept caller-supplied route bytes and pass them to the configured router after only token-level output checks. The router executes payload-selected pool addresses, allowing a malicious route to invoke contract code below the caller’s authorization context. That code can add an unrelated `token.transfer(caller, attacker, amount)` child invocation; if the victim signs the authorization tree produced by simulation, the unrelated wallet tokens are transferred to the attacker. This is analogous to the Apache flaw because attacker-controlled data contributes an unintended command/argument to an operation already carrying authority.

### Finding Description
`swap_collateral` authenticates `caller`, verifies ownership or delegation, withdraws collateral, and forwards the caller-controlled `swap` bytes into the shared swap path. [1](#0-0) [2](#0-1) 

The shared swap path authorizes exactly the controller’s expected input transfer, but it does not constrain the route’s external calls; it invokes `router.execute_strategy` and afterward checks only that the controller did not overspend and received positive output. [3](#0-2) [4](#0-3) 

The router requires sender authorization and then decodes a route whose swap instructions select a `pool`, `token_in`, and `token_out` from caller-supplied `assets`. [5](#0-4) [6](#0-5) 

There is no production-code check in the controller that the encoded pool is a recognized liquidity venue. Consequently, an arbitrary contract can run inside the route. Contract code running below the caller’s `swap_collateral` authorization can cause simulation to record an additional token transfer as a child of that authorization, and enforcing mode executes it only if that child appears in the signed tree. [7](#0-6) [8](#0-7) 

The same route boundary is reachable through `swap_debt`, `repay_debt_with_collateral`, and both `multiply` swap fields, all of which accept route bytes and invoke `swap_tokens_or_passthrough` or `swap_tokens`. [9](#0-8) [10](#0-9) [11](#0-10) 

### Impact Explanation
A malicious route can steal tokens unrelated to the lending position or routed input. The hidden transfer can name any token held by the victim, the attacker’s destination, and any amount covered by the victim’s balance; the route can still return enough output to satisfy the controller’s positive-receipt and account-risk checks. [4](#0-3) [12](#0-11) 

The transaction cannot steal the extra tokens without a signed authorization tree containing that transfer, so this does not bypass Soroban authorization directly. The vulnerability is that the protocol accepts an opaque route capable of injecting an extra authorization requirement during simulation; clients that sign the generated tree without validating every child authorize the theft. [8](#0-7) 

### Likelihood Explanation
The victim must submit or accept a malicious route and sign an authorization tree containing the extra transfer. This is plausible when routes are obtained from an off-chain quote service, constructed by another party, or displayed without decoding nested venue calls, but it is less likely when the client explicitly rejects unexpected authorization children. [13](#0-12) 

### Recommendation
Use a governance-maintained allowlist of audited venue pool addresses before dispatching route hops, or otherwise restrict route targets to contracts that cannot issue caller-token transfers. Independently, wallets and route-building clients must decode the simulated authorization tree and reject any child invocation other than the expected router input transfer; this client-side check should be treated as mandatory until route targets are constrained on-chain. [13](#0-12) 

### Proof of Concept
1. Victim owns an account with withdrawable `USDC` collateral and holds an unrelated wallet token.
2. Attacker deploys a contract exposing the venue interface expected by a route hop. Its handler invokes `wallet_token.transfer(victim, attacker, victim_balance)`.
3. Attacker supplies a route naming that contract as a pool while arranging for the route to return a positive amount of the requested output token.
4. Victim calls:
   `swap_collateral(victim, account_id, usdc_hub_asset, amount, eth_hub_asset, malicious_route)`.
5. The controller withdraws `USDC`, grants only the expected controller-to-router input transfer, and invokes the router. [14](#0-13) 
6. During simulation, the malicious pool’s unrelated transfer is recorded as a child of the victim’s `swap_collateral` authorization. [15](#0-14) 
7. If the victim signs that tree, enforcing mode completes the swap and transfers the unrelated wallet token balance to the attacker. [16](#0-15)

### Citations

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-64)
```rust
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

**File:** contracts/controller/src/strategies/swap_debt.rs (L65-72)
```rust
    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L108-117)
```rust
    let debt_available = withdraw_and_swap_from_supply(
        env,
        account,
        cache,
        caller,
        collateral,
        collateral_amount,
        &debt.asset,
        swap,
        events::PositionAction::RpColWd,
```

**File:** contracts/controller/src/strategies/multiply.rs (L187-194)
```rust
        let collateral_amount = swap_tokens(
            env,
            caller,
            &payment.asset,
            received,
            &collateral.asset,
            convert,
        );
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
