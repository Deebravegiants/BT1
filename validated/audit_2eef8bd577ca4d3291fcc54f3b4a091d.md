### Title
Payload-selected route contract can hijack caller authorization and drain unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
A user-supplied swap route can place attacker-controlled code below the caller’s `swap_collateral` authorization. That code can request unrelated token transfers from the caller; transaction simulation records those transfers as children of the caller’s authorization entry, and they execute if the caller signs the resulting tree. The controller’s bounded router authorization protects only the controller-held swap input, not arbitrary wallet assets touched by route-selected code. [1](#0-0) [2](#0-1) 

### Finding Description
`process_swap_collateral` authorizes the account owner or delegate and forwards the caller-provided `StrategySwap` bytes into `withdraw_and_swap_from_supply`. [3](#0-2) 

`swap_tokens` sends those opaque bytes to the configured router without identifying or constraining the contracts that the route will execute. [4](#0-3) 

The controller creates one exact invoker-contract authorization for `token_in.transfer(controller, router, amount_in)`, but that narrow authorization only protects the controller’s input transfer. [1](#0-0) [5](#0-4) 

Because venue addresses are route-controlled and unallowlisted, a route can execute an attacker-deployed contract while the victim’s top-level authorization is active. [6](#0-5) 

The malicious contract can invoke `transfer(victim, attacker, amount)` on an unrelated token; simulation records it as a child invocation under the victim’s `swap_collateral` authorization, and enforcement accepts it when the victim signs that poisoned tree. [7](#0-6) 

The controller’s post-swap checks measure only `token_in` spending and `token_out` receipt, so a fair-looking swap can satisfy every protocol check while unrelated wallet assets are stolen in parallel. [8](#0-7) [9](#0-8) 

### Impact Explanation
An attacker can steal arbitrary token balances from a user who signs a malicious swap authorization tree, including assets unrelated to the lending position and outside the swapped input amount. [2](#0-1) 

The attacker does not need protocol privileges or control of the configured router: they only need the victim to execute a route naming attacker-controlled venue code. [4](#0-3) [2](#0-1) 

The protocol can still receive positive measured output, refund unused input, and finish with a solvent account, so the theft is not bounded by the route minimum, measured input spend, output receipt, or final health checks. [8](#0-7) [10](#0-9) [7](#0-6) 

This is theft of user funds and therefore a valid in-scope impact. [7](#0-6) 

### Likelihood Explanation
Likelihood is Medium. The attack requires user interaction: the victim must sign the poisoned authorization tree produced by simulation or otherwise explicitly include the malicious child transfer. [7](#0-6) 

However, the malicious venue can make the swap economically normal by spending exactly the authorized input and returning sufficient output, so users and integrating clients that only validate token amounts, minimum output, and final simulation success may not notice the extra authorization child. [8](#0-7) [9](#0-8) 

The same pattern is reachable through any caller-supplied `StrategySwap` routed via `multiply`, `swap_debt`, `swap_collateral`, or `repay_debt_with_collateral`; `swap_collateral` is the representative path. [11](#0-10) [12](#0-11) [13](#0-12) [14](#0-13) 

### Recommendation
Do not expose arbitrary venue contract addresses inside caller-provided routes. Store venue or pool identifiers in a governance-approved registry and make route instructions select registered entries rather than raw executable addresses. [4](#0-3) 

If arbitrary routes remain supported, the protocol cannot fully distinguish a route-requested wallet transfer inside contract code, so transaction construction must decode the route and reject any simulated authorization tree containing children beyond the expected swap-input authorization. [7](#0-6) 

A defense-in-depth design should also separate user-facing swap execution from position-management calls by requiring routes to reference protocol-curated route plans, limiting executable calls to known venue adapters and approved pool IDs, and rejecting payload fields that provide arbitrary executable addresses. [4](#0-3) [15](#0-14) 

### Proof of Concept
1. Deploy `RogueVenue` with a `swap` implementation that calls `token::Client::new(wallet_token).transfer(victim, attacker, wallet_balance)` while also returning enough output for the route to satisfy its minimum. [2](#0-1) 

2. Construct a `StrategySwap` route whose hop address is `RogueVenue`, using the victim’s USDC collateral as input and ETH as output. [4](#0-3) 

3. Have the victim call:
   `swap_collateral(caller = victim, account_id = victim_account, current = USDC, from_amount = 5_000_USDC, new = ETH, swap = malicious_route)`. [16](#0-15) 

4. The controller withdraws the collateral, authorizes only `USDC.transfer(controller, router, 5_000_USDC)`, and calls the configured router with the malicious route bytes. [17](#0-16) 

5. During route execution, `RogueVenue` requests `wallet_token.transfer(victim, attacker, wallet_balance)` under the victim’s active authorization context. [18](#0-17) 

6. Simulation records the unrelated wallet transfer as a child of the victim’s `swap_collateral` invocation. If the victim signs that returned tree, the wallet transfer executes alongside an otherwise successful collateral swap. [7](#0-6) 

7. The controller then observes no excessive input spend and a positive ETH balance increase, deposits the received collateral, and completes its normal account checks even though the unrelated `wallet_token` balance was transferred to the attacker. [8](#0-7) [10](#0-9)

### Citations

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

**File:** contracts/controller/src/strategies/swap.rs (L74-84)
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
}
```

**File:** docs/explanation/threat-model.md (L144-164)
```markdown
Router swaps settle measured input/output changes. The controller grants
one exact input-transfer invocation, not a token allowance, and refunds
unspent input still held by the controller. The router checks its payload
minimum against output after fees but before payout; its own residuals
follow a capped admin-revenue policy. The controller requires positive
measured output and final account risk, not an independent slippage bound.
A compromised router may consume authorized input for dust output while the
final account passes its risk gates. Exposure is bounded by routed funds and
those gates, not by an independent controller slippage limit.

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L17-65)
```rust
pub(crate) struct SwapCollateralParams<'a> {
    pub account_id: u64,
    pub current: &'a HubAssetKey,
    pub from_amount: i128,
    pub new: &'a HubAssetKey,
    pub swap: &'a StrategySwap,
}

/// Withdraws current collateral, swaps into the new asset, then deposits and
/// checks the account's final risk. Matching assets across hubs pass through.
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
    let mut cache = Context::new(env);
    // Check the destination before withdrawing existing collateral.
    require_can_supply(env, &mut cache, account.spoke_id, new);

    let extra_assets = vec![env, current.asset.clone(), new.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L67-77)
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
}
```

**File:** common/src/token.rs (L33-52)
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
}
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L18-28)
```rust
pub(crate) struct SwapDebtParams<'a> {
    pub account_id: u64,
    pub existing_debt: &'a HubAssetKey,
    pub new_debt_amount: i128,
    pub new_debt: &'a HubAssetKey,
    pub swap: &'a StrategySwap,
}

/// Refinances existing debt by borrowing the new asset and swapping into the
/// old asset for repayment. Matching assets across hubs pass through.
pub(crate) fn process_swap_debt(env: &Env, caller: &Address, params: SwapDebtParams<'_>) {
```

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L18-30)
```rust
pub(crate) struct RepayWithCollateralParams<'a> {
    pub account_id: u64,
    pub collateral: &'a HubAssetKey,
    pub collateral_amount: i128,
    pub debt: &'a HubAssetKey,
    pub swap: &'a StrategySwap,
    pub close_position: bool,
}

/// Repays from collateral: nets same-market balances or withdraws and swaps.
/// Closing requires all debt cleared before returning collateral to `caller`;
/// every path ends with the standard risk checks and finalization.
pub(crate) fn process_repay_debt_with_collateral(
```

**File:** contracts/controller/src/strategies/multiply.rs (L19-33)
```rust
pub(crate) struct MultiplyParams<'a> {
    pub account_id: u64,
    pub spoke_id: u32,
    pub collateral: &'a HubAssetKey,
    pub debt_to_flash_loan: i128,
    pub debt: &'a HubAssetKey,
    pub mode: PositionMode,
    pub swap: &'a StrategySwap,
    pub initial_payment: Option<(HubAssetKey, i128)>,
    pub convert_swap: Option<StrategySwap>,
}

/// Borrows and swaps into collateral to open or extend a leveraged position.
/// Includes optional initial funds and returns the account id after risk checks.
pub(crate) fn process_multiply(env: &Env, caller: &Address, params: MultiplyParams<'_>) -> u64 {
```
