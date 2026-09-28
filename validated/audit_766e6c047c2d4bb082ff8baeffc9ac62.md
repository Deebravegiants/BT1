### Title
Unbounded swap-route code can add unauthorized wallet-token transfers to the caller’s signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs])

### Summary

High severity: a malicious route venue can execute arbitrary contract code during `multiply`, `swap_debt`, `swap_collateral`, or `repay_debt_with_collateral` and request token transfers from the caller’s wallet. If simulation adds that transfer beneath the caller’s authorization and the caller signs the resulting tree, the venue can steal wallet assets unrelated to the routed amount while returning sufficient swap output for the strategy to succeed. [1](#0-0) [2](#0-1) 

### Finding Description

The strategy entrypoints authenticate only the caller’s top-level action and account ownership, while their `swap` payload is supplied by that caller and forwarded to the configured router. [3](#0-2) [4](#0-3) 

`swap_tokens` explicitly authorizes only one controller-to-router input transfer for `amount_in`, but it then invokes `router.execute_strategy(&controller, &amount_in, swap)` with the caller-controlled route payload. [5](#0-4) 

The controller’s subsequent checks measure only `token_in` spending and positive `token_out` receipt; they do not inspect transfers from the caller’s wallet in unrelated token contracts. [6](#0-5) [7](#0-6) 

Because route venues are not allowlisted, a payload-selected venue can invoke `token.transfer(caller, attacker, amount)`. Soroban records that transfer as a child invocation under the caller’s strategy authorization, and enforcement accepts it if the signed authorization tree includes that child. [2](#0-1) [8](#0-7) 

### Impact Explanation

A malicious route can steal any wallet token for which it adds a signed child `transfer`, independently of the collateral or debt being routed. [9](#0-8) [10](#0-9) 

The attacker can size the theft up to the victim’s full balance and still return sufficient `token_out` to satisfy the controller’s positive-output and final risk checks, so the transaction can complete normally after the theft. [6](#0-5) [11](#0-10) 

This is theft of user funds rather than a routing-quality or slippage issue: the stolen token does not have to be the strategy input, output, listed collateral, or otherwise committed to the protocol. [2](#0-1) 

### Likelihood Explanation

An unprivileged attacker can deploy the malicious venue contract and construct a route that reaches it; no admin role, leaked key, oracle manipulation, protocol upgrade, or privileged entrypoint is required. [1](#0-0) [12](#0-11) 

Exploitation requires a victim to submit a malicious route and sign the simulation-produced authorization tree containing the extra token transfer. That resembles the DLL-redirection primitive: attacker-selected code is placed inside an execution context whose authorization is broader than the code should receive. [13](#0-12) 

The affected entrypoints are user-facing operations, including `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`, so a malicious interface, copied route, or route-generation service can expose ordinary users to the payload. [14](#0-13) [15](#0-14) 

### Recommendation

Restrict swap payloads to a governance-approved set of immutable venue or adapter contracts instead of allowing routes to execute arbitrary contract addresses. [12](#0-11) 

Route decoding should reject venue addresses outside that allowlist before execution, and venue calls should be prevented from introducing token transfers outside the expected router/controller input and output legs. [1](#0-0) [6](#0-5) 

Until route execution is constrained, clients must decode and display the complete authorization tree and reject any child invocation other than the expected controller input transfer or a strictly expected swap-authorization leg. [16](#0-15) 

### Proof of Concept

1. Deploy a malicious venue contract whose route callback executes `token.transfer(victim, attacker, victim_balance)` on a token held by the victim. [17](#0-16) 

2. Construct a `swap` payload that routes through that venue while preserving a normal `token_in`/`token_out` result, then induce the victim to call `swap_collateral(caller=victim, account_id, current, amount, new, swap)`. [18](#0-17) [19](#0-18) 

3. The controller authorizes only its exact input transfer to the configured router, but the router still executes the attacker-selected venue through the opaque payload. [1](#0-0) 

4. During simulation, the venue’s `transfer(victim, attacker, victim_balance)` appears as a child under the victim’s `swap_collateral` authorization. [20](#0-19) 

5. If the victim signs that returned tree, the unrelated wallet token moves to the attacker while the router returns output that satisfies the controller’s measured-output check. [21](#0-20) [13](#0-12)

### Citations

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L67-76)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L20-22)
```rust
const SWAP_IN_USDC: i128 = 50_000_000_000; // 5 000 USDC, 7 decimals
const FAIR_OUT_ETH: i128 = 25_000_000; // 2.5 ETH at $2 000
const WALLET_BALANCE: i128 = 77_770_000_000; // Alice's balance of a token the protocol never listed
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

**File:** contracts/controller/src/lib.rs (L255-321)
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
        close_position: bool,
    ) {
        strategies::repay_debt_with_collateral::process_repay_debt_with_collateral(
```
