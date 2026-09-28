### Title
Unvalidated swap routes can smuggle unauthorized token transfers into the caller's signed invocation tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller accepts caller-supplied `Bytes` swap routes and forwards them unchanged to the configured swap aggregator. It narrowly authorizes only the controller's exact input-token transfer to the router, but does not constrain which contracts or token calls the route reaches. A malicious route can invoke attacker-controlled code that initiates an unrelated `token.transfer(caller, attacker, amount)` below the caller-authorized strategy call; Soroban attaches that transfer to the caller's authorization tree, and it executes if the caller signs the simulated tree. This is analogous to CVE-2019-13682's insufficient external-protocol policy enforcement: untrusted external handling can expand a seemingly limited user authorization into unrelated privileged actions.

### Finding Description
`swap_tokens` accepts a `StrategySwap` payload, verifies only that it is non-empty, authorizes exactly `token_in.transfer(controller, router, amount_in)`, and calls `router.execute_strategy(&controller, &amount_in, swap)` without decoding or constraining the route's external contracts. [1](#0-0) 

The authorization helper deliberately creates a leaf authorization for the controller's transfer and no further sub-invocations. [2](#0-1)  However, this protects only the controller's contract-auth entry; it does not constrain calls executed under the strategy caller's required authorization.

The affected public paths include:

- `multiply`, which forwards `swap` and optionally forwards `convert_swap`. [3](#0-2) 
- `swap_debt`, which forwards `swap`. [4](#0-3) 
- `swap_collateral`, which forwards `swap`. [5](#0-4) 
- `repay_debt_with_collateral`, which also accepts a caller route. [6](#0-5) 

All strategy calls require the caller to be authorized and, for an existing account, to be the owner or an active delegate. [7](#0-6)  The account-risk checks occur only after the external route has executed. [8](#0-7) 

### Impact Explanation
An attacker can steal arbitrary token balances from a user who signs the malicious strategy authorization tree. The stolen token does not need to be a listed lending asset: the rogue external contract can name any token contract and transfer `caller -> attacker` during route execution. The controller's post-call measurements only inspect `token_in` and `token_out` balances belonging to the controller; they do not detect unrelated caller-token movement elsewhere in the call tree. [9](#0-8) 

This is theft of user funds and exceeds the intended bounded exposure of the strategy input amount.

### Likelihood Explanation
Exploitation requires the victim to authorize a crafted strategy transaction, similar to the external report's user interaction through a crafted page. No protocol privilege, leaked key, compromised oracle, or account ownership is needed by the attacker. The route bytes are user-controlled on ordinary, unprivileged strategy entrypoints, and the controller performs no route allowlisting or authorization-tree policy check before invoking external route-selected code. [1](#0-0) 

### Recommendation
Do not forward opaque route payloads to code capable of arbitrary external calls under a broadly signed caller authorization. Preferably:

1. Decode and enforce an allowlist of permitted venue/pool contracts before invoking the router.
2. Reject routes containing arbitrary callback or contract invocation operations.
3. Present and verify a bounded authorization policy covering only the expected strategy input transfer.
4. Document and enforce in clients that any additional child invocation under the caller's root authorization must abort signing.
5. Where possible, isolate route execution so external code cannot inherit or extend the caller's authority.

### Proof of Concept
A minimal malicious strategy route names an attacker-deployed contract as a swap venue. During `router.execute_strategy`, that contract executes:

```rust
token::Client::new(&env, &victim_token)
    .transfer(&victim, &attacker, &victim_balance);
```

A concrete route can be submitted through `swap_collateral`:

```text
swap_collateral(
  caller = victim,
  account_id = victim_account,
  current = listed collateral A,
  amount = positive amount,
  new = listed collateral B,
  swap = malicious_route_bytes,
)
```

The controller authorizes only its own input transfer to the router, then invokes the attacker-selected external code. Simulation reports the unrelated `victim_token.transfer(victim, attacker, victim_balance)` as a child of the victim's authorization. If the victim signs that tree, the host permits the transfer in the same transaction while the visible controller swap can still return enough `collateral B` to satisfy `verify_router_output` and final account checks.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L21-54)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);

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

**File:** common/src/token.rs (L33-51)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
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

**File:** contracts/controller/src/lib.rs (L225-251)
```rust
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
        strategies::multiply::process_multiply(
            &env,
            &caller,
            MultiplyParams {
                account_id,
                spoke_id,
                collateral: &collateral,
                debt_to_flash_loan,
                debt: &debt,
                mode,
                swap: &swap,
                initial_payment,
                convert_swap,
            },
```

**File:** contracts/controller/src/lib.rs (L258-276)
```rust
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
```

**File:** contracts/controller/src/lib.rs (L283-301)
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
```

**File:** contracts/controller/src/lib.rs (L311-330)
```rust
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
