### Title
Opaque swap routes can attach wallet-draining transfers to the caller's authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept an opaque caller-supplied `swap: Bytes` payload and authenticate the root call with `caller.require_auth()`. [1](#0-0) [2](#0-1)   
For an existing account, `swap_collateral` verifies only that the caller is the owner or an active delegate before routing the withdrawn collateral through the supplied payload. [3](#0-2)   
The controller forwards that payload to the configured router, while its own authorization is restricted to one exact controller-to-router token transfer. [4](#0-3) [5](#0-4)   
A malicious route-selected venue can therefore execute below the caller's root authorization and request an additional `token.transfer(victim, attacker, amount)` from an unrelated wallet asset. [6](#0-5) 

### Finding Description
The vulnerable pattern is the same trust-boundary confusion as hostname-derived service validation: an attacker-selected execution endpoint is reached inside a broader authenticated operation. [6](#0-5)   
`swap_tokens` snapshots only the controller's input and output balances, invokes `execute_strategy(&controller, &amount_in, swap)`, rejects controller overspending, and requires positive controller output. [7](#0-6)   
These checks bound the routed collateral but do not bound other `require_auth` operations performed by contracts reached through the opaque route. [8](#0-7)   
When transaction simulation records that extra wallet transfer as a child of the victim's signed controller invocation, signing the resulting tree authorizes both the intended swap and the unrelated transfer. [2](#0-1) 

### Impact Explanation
A successful attack can steal unrelated tokens directly from the user's wallet while the protocol position remains solvent and the controller's measured swap checks pass. [9](#0-8) [10](#0-9)   
The stolen amount is bounded only by the additional token-transfer sub-invocations that the victim signs, so this is theft of user funds rather than route-quality loss or MEV. [5](#0-4) 

### Likelihood Explanation
The attacker needs the victim to submit an attacker-constructed route and sign the simulated authorization tree, so exploitation requires user interaction but no privileged role or leaked key. [1](#0-0) [11](#0-10)   
The route is opaque bytes at the controller boundary, and a client that presents only the root function arguments rather than every recorded sub-invocation can hide the extra wallet transfer from the victim. [1](#0-0) [6](#0-5) 

### Recommendation
Do not allow opaque strategy payloads to reach arbitrary venue contract addresses beneath an account-owner authorization. [6](#0-5)   
Restrict executable venue/pool addresses to a governance-approved registry of audited contracts, and make clients reject any authorization tree containing sub-invocations other than the explicitly expected token movement. [12](#0-11) 

### Proof of Concept
1. Victim Alice owns a lending account with USDC collateral and separately holds an unrelated TOKEN in her wallet. [3](#0-2) 
2. Attacker deploys a venue-compatible contract whose `get_reserves` or `swap` call invokes `TOKEN.transfer(alice, attacker, alice_balance)` and still returns enough ETH output to satisfy the route. [7](#0-6) 
3. Attacker gives Alice a `swap` payload naming that contract and asks her to call `swap_collateral(alice, account_id, usdc_key, amount, eth_key, malicious_swap_xdr)`. [1](#0-0) 
4. Simulation records the malicious TOKEN transfer beneath Alice's controller authorization; if Alice signs that tree, the route executes, the controller observes bounded collateral spend and positive ETH output, and Alice's unrelated TOKEN balance moves to the attacker. [2](#0-1) [9](#0-8)

### Citations

**File:** interfaces/controller/src/lib.rs (L98-106)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    );
```

**File:** contracts/controller/src/risk/validation.rs (L12-16)
```rust
/// Authenticates `caller` and rejects execution during a flash loan.
pub(crate) fn require_authorized_caller(env: &Env, caller: &Address) {
    caller.require_auth();
    require_not_flash_loaning(env);
}
```

**File:** contracts/controller/src/risk/validation.rs (L29-60)
```rust
pub(crate) fn require_post_pool_risk_gates(env: &Env, cache: &mut Context, account: &Account) {
    if account.debt_free() {
        return;
    }

    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    assert_with_error!(
        env,
        totals.ltv_collateral >= totals.total_debt,
        CollateralError::InsufficientCollateral
    );

    spec_hooks::solvency_gate_checked(account);

    assert_with_error!(
        env,
        totals.health_factor >= Wad::ONE,
        CollateralError::InsufficientCollateral
    );

    let floor = storage::get_min_borrow_collateral_usd_wad(env);
    if floor != 0 && totals.ltv_collateral.raw() < floor {
        panic_with_error!(env, CollateralError::MinBorrowCollateralNotMet);
    }

    require_whole_unit_collateral_floor(env, cache, account);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-55)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L24-55)
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
