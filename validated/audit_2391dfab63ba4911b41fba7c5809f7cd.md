### Title
Tokens pushed to the controller during `flash_position` are never returned when the asset is undeclared or unlistable — ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary
The external report describes excess funds sent with a call being locked in the contract instead of refunded. In XOXNO Lending, `repay` and `recapitalize` do refund overpayments, but `flash_position` has a structural gap: tokens delivered to the controller inside the receiver callback are only credited if declared in `collaterals` or returned if listed in `refund_assets`, and `refund_assets` entries must be markets listed in the debt hub and the account's spoke. Any other token the receiver pushes to the controller is neither credited nor refundable, and the controller exposes no sweep/recovery endpoint, so those funds are frozen permanently.

### Finding Description
`flash_position(caller, account_id, spoke_id, mode, debt, amount, receiver, data, collaterals, refund_assets)` mints debt, forwards the measured receipt to `receiver`, and invokes `execute_flash_position`. After the callback returns, the controller only handles two lists: `collect_collateral_deposits` measures deltas for declared `collaterals` and deposits them, and `refund_listed_assets` iterates `refund_assets` and calls `refund_controller_balance_delta` for each. [1](#0-0) [2](#0-1) 

`refund_controller_balance_delta` is the only outbound leg, and it runs solely for the caller-supplied `refund_assets` list. [3](#0-2)  Per the documented validation, refund assets must be unique, listed in the debt hub and the account spoke, disjoint from `collaterals`, and bounded by `max_supply_positions`. [4](#0-3)  Consequences:

1. A token that is not a listed market in the debt hub and account spoke cannot appear in `refund_assets` at all — validation reverts (`#307`/`#16`). If the receiver pushes such a token to the controller, there is no parameterization of the call that returns it.
2. Even a listable token pushed but not declared in either list is retained: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint." [4](#0-3) 
3. The invariant doc confirms retained debt tokens "remain uncredited if in neither list." [5](#0-4) 

This is not the user's own sloppy direct transfer being unrecoverable (a generic donation caveat): the token reaches the controller inside a protocol-driven callback where the caller's only recovery mechanism — `refund_assets` — is artificially restricted to hub/spoke-listed markets and disjoint from collateral declarations.

### Impact Explanation
Permanent freezing of user funds. Any token the receiver delivers to the controller that cannot be (or is not) declared is locked in the controller contract forever; no endpoint can move arbitrary token balances out, and `claim_revenue` only handles pool-side revenue, not controller-held stray balances. The loss scales with whatever value the receiver pushes — e.g., swap output dust in a token not listed under the debt hub, fee-on-transfer over-delivery, or a misbehaving/ compromised route contract attached to a user's receiver. Accepted impact class: permanent freezing of funds.

### Likelihood Explanation
Medium-low. The flash-receiver is the caller's own contract (in-scope: "own flash receiver"), and a correctly implemented receiver only pushes declared collateral. However, the freeze requires no privileged action and no attacker — any over-delivery by the receiver (rounding surplus, an extra token leg a multi-output swap produces, a listed token in a different hub, or a token delisted between simulation and execution) is unrecoverable, and the call offers no way to declare such a token for refund when it fails the hub/spoke listing check. Reachable via the unprivileged `flash_position` entrypoint for any account owner/delegate.

### Recommendation
Remove the market-listing requirement on `refund_assets` (uniqueness and disjointness from `collaterals` are sufficient; `refund_controller_balance_delta` only moves measured positive deltas of the caller's own pushed tokens), and/or refund every positive post-callback balance delta that is not consumed by declared collateral deposits. Alternatively, add an admin/claimable sweep for non-booked controller balances so stray tokens are recoverable instead of permanently locked.

### Proof of Concept
1. Alice owns a Multiply-mode account (or uses `account_id = 0` with sufficient declared collateral) and deploys a `FlashPositionReceiver`.
2. Alice calls `controller.flash_position(caller=Alice, debt=(hub0, USDC), amount, receiver, collaterals=[(hub0, XLM, min)], refund_assets=[XLM? — rejected: refund assets must be disjoint from collaterals and listed in the debt hub/spoke])`.
3. Inside `execute_flash_position`, the receiver transfers `min` XLM collateral plus `E` units of a token `T` that is not a listed market in `debt.hub_id`/`spoke_id` (e.g., a stray output token from the swap route) to the controller.
4. After the callback, `collect_collateral_deposits` deposits only the XLM delta; `refund_listed_assets` iterates only `refund_assets`, which cannot contain `T` (validation `#307`/`#16` would have reverted the whole call if it did).
5. The call succeeds; the `E` units of `T` remain on the controller balance. No controller endpoint can transfer them out — `refund_controller_balance_delta` is only invoked for listed `refund_assets`, and there is no sweep function — so `T` is frozen permanently.

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L145-153)
```rust
    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L372-384)
```rust
fn refund_listed_assets(
    env: &Env,
    caller: &Address,
    refund_assets: &Vec<Address>,
    before: &Map<Address, i128>,
) {
    for asset in refund_assets.iter() {
        let baseline = before
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError));
        refund_controller_balance_delta(env, &asset, baseline, caller);
    }
}
```

**File:** contracts/controller/src/payments.rs (L41-52)
```rust
pub(crate) fn refund_controller_balance_delta(
    env: &Env,
    asset: &Address,
    balance_before: i128,
    refund_to: &Address,
) {
    let controller = env.current_contract_address();
    let excess = balance_delta_since(env, asset, &controller, balance_before);
    if excess > 0 {
        token::Client::new(env, asset).transfer(&controller, refund_to, &excess);
    }
}
```

**File:** docs/reference/endpoints.md (L84-86)
```markdown
Refund assets must be unique, listed in the debt hub and account spoke, disjoint from collateral declarations, and bounded by the maximum supply-position count. Refund eligibility requires an active spoke and an existing listing; it does not check collateralizable, borrowable, paused or frozen flags. Only positive balance changes above pre-callback balances return to the caller. The debt token can be a refund asset, but refunding it does not repay the minted debt.

Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint. Refunds produce token transfer events, without a dedicated controller refund event.
```

**File:** docs/reference/invariants.md (L685-689)
```markdown
Before and after account finalization, the borrowed market must retain positive
scaled debt and the account must retain supply. Returned debt becomes
collateral if declared, returns to the caller if refund-listed, or remains
uncredited if in neither list. Refunds cover only positive callback balance
changes.
```
