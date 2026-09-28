### Title

Unvalidated swap routes can attach arbitrary caller-authorized token transfers to controller strategies - (File: `contracts/controller/src/strategies/swap.rs`)

### Summary

Medium. A malicious route submitted through `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` can execute a route-named contract that requests an unrelated token transfer from the caller; if the caller signs the poisoned authorization tree, the strategy can complete normally while stealing unrelated wallet funds. [1](#0-0) [2](#0-1) 

### Finding Description

`swap_tokens` loads the configured router, authorizes one exact controller-to-router input transfer, and then passes the caller-controlled `swap` bytes to `execute_strategy`. [3](#0-2) [1](#0-0) 

After the router returns, the controller only bounds the controller's input spend and requires a positive output delta; it does not inspect route-selected contracts or prevent them from requesting the original caller's authorization. [4](#0-3) [5](#0-4) [6](#0-5) 

The router boundary explicitly permits payload-named pool and token addresses without a venue allowlist, so route code can run below the user's authorization context. [2](#0-1)  A `token.transfer(caller, attacker, amount)` issued by that code is recorded as a child of the caller's authorization and executes when the caller signs that tree. [7](#0-6) 

`swap_collateral(caller, account_id, current, amount, new, swap)` exposes this path directly to an account owner or delegate. [8](#0-7) 

### Impact Explanation

The stolen asset and amount are not limited to the strategy input: a route-invoked contract can request a transfer of any unrelated token held by the caller. [9](#0-8) [10](#0-9) 

The malicious venue can still allow the router to return a valid-looking output, so the controller's balance-delta and account-risk checks do not detect the unauthorized side transfer. [5](#0-4) [11](#0-10) 

This permits theft of user funds beyond the routed amount, analogous to loading attacker-controlled startup variables into a privileged child process. [7](#0-6) 

### Likelihood Explanation

Exploitation requires the victim to submit a malicious route and sign an authorization tree containing the unexpected transfer. [12](#0-11) [13](#0-12) 

An honest simulation records the injected child invocation, so a careful wallet or client can reject it; this user-interaction requirement keeps the issue at medium severity. [14](#0-13) [15](#0-14) 

### Recommendation

Do not let route payloads select arbitrary executable pool, token, or venue contracts under user authorization. [2](#0-1)  Restrict route execution to governance-approved immutable venue adapters or an explicitly allowlisted set of callee contracts, rather than only allowlisting fee tokens. [2](#0-1) 

Until the router enforces that boundary, clients must decode the route and reject any simulated authorization tree containing an unexpected user-authorized child invocation; `swap_collateral` should normally require no child transfer from the account owner. [16](#0-15) [17](#0-16) 

### Proof of Concept

The victim submits:

```text
swap_collateral(
    caller = victim,
    account_id = victim_account,
    current = HubAssetKey { hub_id, asset = USDC },
    amount = strategy_input,
    new = HubAssetKey { hub_id, asset = ETH },
    swap = attacker_supplied_route,
)
```

The route names an attacker-deployed `hop_pool`; the router invokes that pool while processing the strategy input and then pays the expected output. [18](#0-17) 

Inside `swap`, the malicious pool calls an unrelated token's `transfer` with `victim` as sender and `attacker` as recipient. [10](#0-9) 

Simulation records that unrelated transfer as a child of the victim's `swap_collateral` authorization entry. [19](#0-18) [16](#0-15) 

After the victim signs that recorded tree, the unrelated wallet balance is drained while the collateral swap still completes and credits the victim's account. [11](#0-10)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L24-27)
```rust
    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);
```

**File:** contracts/controller/src/strategies/swap.rs (L33-37)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
```

**File:** contracts/controller/src/strategies/swap.rs (L40-44)
```rust
    // Reject input gains or overspending; refund only this swap's unused input.
    let in_after = token_in_client.balance(&controller);
    assert_with_error!(env, in_after <= in_before, StrategyError::RouterOverspend);
    let actual_spent = in_before - in_after;
    assert_with_error!(
```

**File:** contracts/controller/src/strategies/swap.rs (L45-47)
```rust
        env,
        actual_spent <= amount_in,
        StrategyError::RouterOverspend
```

**File:** contracts/controller/src/strategies/swap.rs (L54-55)
```rust
    verify_router_output(env, token_out, out_before)
}
```

**File:** docs/explanation/threat-model.md (L154-158)
```markdown
That bound covers the controller's own grant only. The router calls the pool
and token addresses its payload names and keeps no allowlist of them, so a
route can put third-party code on the call stack below the caller's
authorization. A token transfer that such code makes from the caller is
recorded by an honest simulation as a child of the caller's authorization
```

**File:** docs/explanation/threat-model.md (L159-163)
```markdown
entry, and it executes if the caller signs that tree. The loss is then the
caller's wallet, not the routed amount, and neither the payload minimum nor the
final risk gate bounds it. An honest swap strategy gives the caller no child
entry, and a direct router swap gives exactly one input transfer. A client must
decode the route it signs and refuse an authorization tree with any other
```

**File:** docs/reference/endpoints.md (L34-34)
```markdown
| `swap_collateral(caller: Address, account_id: u64, current: HubAssetKey, amount: i128, new: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Withdraw, convert and redeposit collateral. |
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L43-45)
```rust
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-64)
```rust
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L68-70)
```rust
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L172-176)
```rust
        let root = MockAuthInvoke {
            contract: &self.t.controller,
            fn_name: "swap_collateral",
            args: self.swap_args(route),
            sub_invokes: children,
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L178-182)
```rust
        self.t.env.mock_auths(&[MockAuth {
            address: &self.alice,
            invoke: &root,
        }]);
        self.try_swap(route)
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L199-203)
```rust
    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-210)
```rust
    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L214-218)
```rust
    let poisoned_root = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.t.controller.clone(),
            Symbol::new(&s.t.env, "swap_collateral"),
            s.swap_args(&route),
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L219-222)
```rust
        )),
        sub_invocations: std::vec![stolen_transfer],
    };
    assert_eq!(recorded, std::vec![(s.alice.clone(), poisoned_root)]);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L224-226)
```rust
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```
