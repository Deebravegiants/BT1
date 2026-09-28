### Title
Malicious swap routes can inject unrelated token transfers into the caller’s authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept caller-supplied opaque swap payloads and delegate them to the configured router. `swap_tokens` validates only that the payload is non-empty, authorizes the controller’s exact input transfer, invokes the router, and then checks the controller’s measured input/output balances. [1](#0-0)  A malicious route-selected venue can place an unrelated `token.transfer(victim, attacker, amount)` beneath the victim’s authorized controller call; simulation records that transfer as a child authorization, and signing the returned tree permits the theft even though the strategy’s measured token settlement remains valid. [2](#0-1) [3](#0-2) 

### Finding Description
`swap_collateral` exposes the vulnerable pattern to an account owner or delegate through a caller-controlled `swap: Bytes` argument. [4](#0-3)  The common helper tightly bounds only the controller-to-router input transfer; it does not restrict authorization requests made by contracts reached through the route. [5](#0-4)  After the router returns, the controller checks that its own input did not increase, that measured spending did not exceed `amount_in`, that unused controller-held input is refunded, and that output increased. [3](#0-2)  These measurements do not detect an unrelated wallet-token transfer authorized elsewhere in the call tree. [6](#0-5) 

### Impact Explanation
A victim can lose arbitrary wallet assets unrelated to the swapped collateral while still receiving a positive, correctly measured strategy output. [3](#0-2)  Because the rogue transfer is represented in the signed authorization tree rather than performed without authorization, the transaction is valid and the strategy state transition can complete normally. [6](#0-5) 

### Likelihood Explanation
Exploitation requires the victim to execute an attacker-supplied route and sign the poisoned authorization tree, so the attack has a user-interaction prerequisite rather than being directly callable against an arbitrary account. [4](#0-3)  The barrier is nevertheless material because routes are opaque bytes and normal output and solvency checks can still pass. [1](#0-0) 

### Recommendation
Do not allow route payloads to reach arbitrary venue contracts under an authenticated strategy call; require governance- or protocol-approved venue and pool addresses before dispatching route-selected code. [7](#0-6)  Until such an allowlist exists, clients must simulate every route and reject any authorization tree containing calls other than the expected strategy root and exact input transfer. [5](#0-4) 

### Proof of Concept
1. The victim owns a lending account with supplied USDC and also holds an unrelated token never listed by the protocol. [4](#0-3) 
2. The attacker supplies a route whose venue is attacker-controlled and whose callback invokes `unrelated_token.transfer(victim, attacker, victim_balance)`. [7](#0-6) 
3. The victim calls `swap_collateral(victim, account_id, usdc_hub_asset, amount, eth_hub_asset, malicious_route)`. [8](#0-7) 
4. The controller authorizes only its exact input transfer, but the nested venue request is recorded as another child beneath the victim’s strategy authorization. [2](#0-1) 
5. Signing the simulated tree permits both the expected swap and the unrelated token transfer; the controller’s balance-delta output check still succeeds. [3](#0-2) 
6. The transaction completes with the victim’s unrelated token moved to the attacker while the swapped ETH is credited normally. [6](#0-5)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L17-38)
```rust
    amount_in: i128,
    token_out: &Address,
    swap: &StrategySwap,
) -> i128 {
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

**File:** contracts/controller/src/lib.rs (L280-302)
```rust
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
