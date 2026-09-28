### Title
Unrestricted swap-route execution can add unauthorized wallet token transfers beneath the caller’s signed authorization - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The controller forwards caller-supplied swap bytes to the configured router while only constraining the controller’s own token input transfer and measured token balances. Because the router may invoke route-selected venues below the caller’s authorization, a malicious route can place an unrelated `token.transfer(caller, attacker, amount)` inside the authorization tree returned by simulation. If the caller signs that complete tree, the route venue can transfer wallet tokens that are entirely unrelated to the lending operation.

### Finding Description
`swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral` accept opaque `Bytes` swap payloads and route them through `swap_tokens_or_passthrough` or `swap_tokens`. [1](#0-0) [2](#0-1) [3](#0-2) 

`swap_tokens` loads the configured router, authorizes exactly one controller-to-router input transfer with no sub-invocations, and calls `execute_strategy` with the caller-supplied payload. [4](#0-3)  The transfer authorization helper correctly permits only that exact token transfer on the controller’s behalf. [5](#0-4) 

The post-call checks only compare the controller’s input and output balances: input must not increase, spent input must not exceed `amount_in`, leftover input is refunded, and output must be positive. [6](#0-5)  They do not inspect the payload’s invoked venues or prevent code reached through the route from requesting a separate transfer authorization from the caller. The threat model confirms that the router does not keep a venue allowlist and that third-party route code can add a child token transfer beneath the caller’s authorization. [7](#0-6) 

### Impact Explanation
This is theft of user wallet funds. A malicious venue selected by the swap payload can request `token.transfer(victim, attacker, amount)` while still paying a valid output so the controller’s measured output and account-risk checks succeed. The unrelated wallet-token transfer is attached as a sub-invocation of the caller’s `swap_collateral` authorization during simulation, and executes when the caller signs the resulting complete authorization tree. [7](#0-6)  The controller’s own authorization remains narrow, so the loss bypasses its input-spend, output-receipt, and final-solvency checks rather than violating them. [6](#0-5) 

### Likelihood Explanation
An unprivileged attacker can deploy a venue contract and cause a victim’s quoting interface or route source to include it in the opaque `swap` bytes for `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral`. The victim must sign the authorization tree that contains the additional transfer; therefore, exploitation depends on the wallet or client presenting the tree incompletely or on the victim signing a route-specific tree without decoding all child invocations. This requirement limits but does not remove the exposure, because opaque route bytes are intentionally caller-controlled. [1](#0-0) [8](#0-7) 

### Recommendation
Restrict strategy execution to an allowlisted set of venue contracts or otherwise cryptographically bind the signed route to a validated venue set. Independently require wallets and route builders to decode the complete Soroban authorization tree and reject any non-root or child invocation other than the expected protocol calls. At minimum, prominently enforce that a strategy transaction must contain no user token transfer as a child of `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral`; the controller’s own exact transfer grant is already generated through `authorize_transfer_as_current`. [5](#0-4) 

### Proof of Concept
1. Deploy a malicious contract `RogueHopPool` whose route callback performs `unrelated_token.transfer(victim, attacker, victim_balance)`.
2. Construct a swap route that calls `RogueHopPool` but still pays enough `token_out` for `verify_router_output` to pass.
3. Have the victim invoke `Controller::swap_collateral(caller=victim, account_id, current=USDC_key, amount, new=ETH_key, swap=route)`.
4. The controller withdraws the collateral and calls the configured router through `swap_tokens`, authorizing only the expected controller-to-router `USDC.transfer`. [8](#0-7) 
5. During simulation, the rogue hop’s unrelated wallet transfer is attached beneath the victim’s root `swap_collateral` authorization. [7](#0-6) 
6. If the victim signs that returned tree, the unrelated wallet token transfers to the attacker while the swap output and final account state remain valid. [6](#0-5)

### Citations

**File:** contracts/controller/src/lib.rs (L283-290)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
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

**File:** contracts/controller/src/strategies/swap_debt.rs (L65-72)
```rust
    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
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

**File:** common/src/token.rs (L36-51)
```rust
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
