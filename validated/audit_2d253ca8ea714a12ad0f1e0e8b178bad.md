### Title
Tokens transferred directly to the `Controller` contract are permanently locked with no recovery path - ([File: contracts/controller/src/payments.rs])

### Summary
The `Controller` contract can hold token balances (it transiently custodies funds during `flash_position`, `multiply`, `swap_*` and `migrate_from_blend` flows), but it exposes no endpoint to credit, refund, or sweep tokens that were sent to it outside those flows. Any unprivileged address can call `token.transfer(user, controller, amount)` — or a flash receiver callback can send an undeclared asset — and those tokens are stranded forever.

### Finding Description
Every controller flow that touches token custody uses measured balance deltas against a snapshot taken inside the same call, and only the *increase* over the snapshot is ever acted on:

- `refund_controller_balance_delta` refunds only `balance_delta_since(..., balance_before)`, i.e. the increase since the in-call baseline: "Refunds only the controller balance increase since `balance_before`, preserving the pre-existing balance" [1](#0-0) 
- `flash_position` snapshots collateral and refund-asset balances *after* minting/forwarding and before the callback (`collateral_before`, `refund_before`), so only callback-time receipts are deposited or refunded [2](#0-1) 
- `migrate_from_blend`'s `reconcile_debt_refunds` explicitly leaves pre-existing controller funds untouched: "Pre-existing controller funds remain untouched" [3](#0-2) 
- `repay_debt_from_controller` similarly snapshots post-funding so only the new delta is refunded [4](#0-3) 

The docs confirm the gap: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint" [5](#0-4) . Unlike the swap-aggregator, which has `sweep_balance` to recover stray tokens [6](#0-5) , the controller has no `sweep`, `recover`, or `rescue` function — a grep across the repo finds such functions only in the swap-aggregator and governance tests.

There is also no donation path: a direct transfer to the controller is not credited to any account's supply (unlike a transfer to the pool, which would at least be absorbed into the supply index). The tokens simply sit on the controller address with zero accounting and zero exit.

### Impact Explanation
Permanent freezing of funds. Any user who sends tokens to the controller address — by mistake, by an uninformed wallet/UX, or via a flash callback returning an asset not declared in `collaterals`/`refund_assets` — loses them permanently. No privileged or unprivileged entrypoint can ever move them: not `withdraw` (only pulls account collateral from the pool), not `claim_revenue` (forwards only measured receipts of the current call), not `liquidate`, not governance `execute` (the controller has no generic arbitrary-call escape for token balances — governance only reaches owner-gated config setters).

### Likelihood Explanation
Medium-low per incident but trivially reachable: `token::transfer(victim, controller_addr, amount)` requires no permissions and no protocol state. The EVM analog (WETH unwrap `receive()`) maps here because Soroban tokens are freely transferable to any contract address, and the controller's design actively guarantees stranded funds are never claimable — every delta-based refund deliberately excludes the pre-existing balance. The loss requires user error rather than an attacker action, matching the original report's medium severity.

### Recommendation
Add an owner-gated (or governance-timelocked) `sweep(asset, to)` on the controller that transfers the *full* token balance minus any amounts owed to in-flight accounting (in practice the controller carries no persistent token liabilities — all custody is intra-transactional — so sweeping the whole balance is safe). Alternatively, route stray controller balances into the pool as protocol revenue via `recapitalize`-style measured deposit, so accidental sends benefit suppliers instead of being burned.

### Proof of Concept
```rust
// Soroban test: a user sends tokens straight to the controller.
let token = token::Client::new(&env, &usdc);
sac_usdc.mint(&user, &1_000);
token.transfer(&user, &controller_addr, &1_000);

// The controller now holds 1_000 USDC. Attempt every possible recovery:
// - no `sweep`/`recover` entrypoint exists on the controller interface
// - `flash_position` refund only returns deltas over the in-call snapshot,
//   taken AFTER the pre-existing 1_000 balance (flash_position.rs:130), so
//   refund_controller_balance_delta sees excess == 0 (payments.rs:48-51)
// - `claim_revenue` forwards only measured receipts of that call
// Result: balance(controller, USDC) == 1_000 forever; no call can move it.
assert_eq!(token.balance(&controller_addr), 1_000);
```

### Citations

**File:** contracts/controller/src/payments.rs (L39-52)
```rust
/// Refunds only the controller balance increase since `balance_before`,
/// preserving the pre-existing balance; no-op for a nonpositive delta.
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

**File:** contracts/controller/src/strategies/flash_position.rs (L120-148)
```rust
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);
```

**File:** contracts/controller/src/strategies/migrate_blend.rs (L232-248)
```rust
/// Repays hub debt using positive balances above the pre-borrow snapshot.
/// Pre-existing controller funds remain untouched.
fn reconcile_debt_refunds(
    env: &Env,
    account: &mut Account,
    cache: &mut Context,
    caller: &Address,
    hub_id: u32,
    debt_caps: &Vec<(Address, i128)>,
    before: &Map<Address, i128>,
) {
    let controller = env.current_contract_address();
    for (debt_asset, _max) in debt_caps.iter() {
        let prev = before.get(debt_asset.clone()).unwrap_or(0);

        let refund = balance_delta_since(env, &debt_asset, &controller, prev);
        if refund > 0 {
```

**File:** contracts/controller/src/strategies/legs.rs (L59-80)
```rust
    // Snapshot after funding so only repayment refunds go to the caller.
    let controller_balance_before_repay = debt_tok.balance(&env.current_contract_address());

    repay_prefunded_position(
        env,
        account,
        &env.current_contract_address(),
        req.action,
        RepaymentRequest {
            hub_asset: req.debt,
            position: req.debt_pos,
            amount: received,
        },
        cache,
    );

    refund_controller_balance_delta(
        env,
        &req.debt.asset,
        controller_balance_before_repay,
        caller,
    );
```

**File:** docs/reference/endpoints.md (L84-86)
```markdown
Refund assets must be unique, listed in the debt hub and account spoke, disjoint from collateral declarations, and bounded by the maximum supply-position count. Refund eligibility requires an active spoke and an existing listing; it does not check collateralizable, borrowable, paused or frozen flags. Only positive balance changes above pre-callback balances return to the caller. The debt token can be a refund asset, but refunding it does not repay the minted debt.

Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint. Refunds produce token transfer events, without a dedicated controller refund event.
```

**File:** contracts/swap-aggregator/src/lib.rs (L1-1)
```rust
#![no_std]
```
