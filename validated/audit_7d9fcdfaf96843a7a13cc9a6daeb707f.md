### Title
Blacklisted/deauthorized debt-token receiver cannot fully repay or close a position — forced overpayment refund in `repay` reverts the whole call - (File: contracts/pool/src/ops/repay.rs)

### Summary
The pool's `repay` op unconditionally pushes any overpayment back to `payer` via `transfer_out`. Since accrued debt can never be paid back to the exact base unit at execution time, any caller repaying a full debt inevitably triggers an outbound token transfer to themselves. If that caller's address is blacklisted/deauthorized in the debt token (e.g., a USDC-style token with authorization controls on Stellar), the entire `repay` invocation reverts, so the account owner cannot unilaterally close their debt position — the same class as `_closetrade` reverting on a push-transfer to a blacklisted `_USER`.

### Finding Description
`ops::repay::apply` computes `overpayment = amount − net_repay` in `accounting` and then calls `outcome.cache.transfer_out(payer, outcome.overpayment)` unconditionally: [1](#0-0) 

The controller passes the repay caller straight through as `payer` via `pool_repay_call` → `apply_repay_batch`: [2](#0-1) [3](#0-2) 

Because interest accrues per elapsed time inside `load_leg`/`resolve_repay` at execution, a payer cannot know the exact ceiled debt in advance. The documented integration pattern is precisely to overpay and rely on the refund ("relies on the documented refund of excess payment to the caller rather than pre-computing the exact debt to the base unit"): [4](#0-3) 

Therefore a payer whose address cannot receive the debt token (SAC `authorized` revoked / clawback-enabled trustline deauthorized, the Stellar analogue of a USDC blacklist) has every full-repayment attempt revert inside `transfer_out`, rolling back the entire transaction including the burned debt shares. Underpaying avoids the refund but leaves residual dust debt; the position can never reach zero through their own call.

Contrast with `withdraw`, which takes a user-chosen `to` receiver (`to = None` pays the caller), so a blacklisted user can route collateral to any other address — the repay path offers no such escape: `payer` is hard-bound to the authorizing caller.

### Impact Explanation
Temporary freezing of funds / inability to close a position. A borrower blacklisted in the debt token cannot unilaterally clear their debt, so they cannot fully unwind the account, and any collateral withdrawal remains gated by the residual debt's risk checks. Recovery requires an uninvolved third party to act as `payer` (repay is permissionless and the refund goes to the payer, not the debtor), which the affected user may not be able to arrange — mirroring the original report's "user should be able to close his trade in all conditions." If the token's send-side restriction also blocks them, they cannot even partially deleverage.

### Likelihood Explanation
Reachable by any unprivileged account via `repay(caller, account_id, payments)` with `payments` exceeding current debt. The trigger condition (token-admin deauthorization of a holder) is external but realistic for regulated SAC assets; it requires no protocol misconfiguration. The revert path is deterministic whenever a positive `overpayment` exists and the token rejects the transfer to `payer`.

### Recommendation
Don't push the refund to `payer` inside `repay`. Either (a) credit the overpayment to the payer's controller-side claimable balance and let them withdraw it to an address of their choice, (b) add a `refund_to`/`to` parameter so the payer can designate any receiver, or (c) cap the pulled amount to the measured debt and never custody the excess (pull `min(amount, debt)` instead of refunding).

### Proof of Concept
1. BOB supplies ETH collateral and borrows 1_000 USDC; the account holds a USDC debt position.
2. The USDC SAC admin deauthorizes BOB's trustline (BOB can arrange this deliberately, as in the original griefing scenario).
3. BOB calls `repay(BOB, account_id, [(hub_asset, 2_000 USDC)])` to fully close. The controller pulls 2_000 USDC to the pool, `ops::repay::accounting` computes `overpayment ≈ 1_000 USDC`, and `transfer_out(BOB, overpayment)` invokes `token.transfer(pool, BOB, …)` which panics on the deauthorized receiver.
4. The whole transaction reverts — the debt burn rolls back. Retrying with the exact simulated debt underpays after accrual (dust remains); any overpay reverts on the refund. BOB's position cannot be fully closed by BOB; only a third-party `repay` payer (who would receive the refund) can close it.

### Citations

**File:** contracts/pool/src/ops/repay.rs (L25-34)
```rust
pub(crate) fn apply(
    env: &Env,
    payer: &Address,
    action: &PoolAction,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, action);

    outcome.cache.transfer_out(payer, outcome.overpayment);
    (outcome.mutation, outcome.snapshot)
}
```

**File:** contracts/controller/src/external/pool.rs (L64-72)
```rust
/// Burns debt against prefunded payments and refunds overpayment to `payer`.
pub(crate) fn pool_repay_call(
    env: &Env,
    pool_addr: &Address,
    payer: &Address,
    actions: &Vec<PoolAction>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).repay(payer, actions)
}
```

**File:** contracts/controller/src/positions/debt.rs (L207-218)
```rust
/// Repays prefunded actions and merges the pool results. The pool refunds
/// excess to `payer`; returns the mutations.
pub(crate) fn apply_repay_batch(
    env: &Env,
    account: &mut Account,
    payer: &Address,
    action: events::PositionAction,
    actions: &Vec<PoolAction>,
    cache: &mut Context,
) -> Vec<PoolPositionMutation> {
    let pool_addr = cache.cached_pool_address();
    let results = pool_repay_call(env, &pool_addr, payer, actions);
```

**File:** skills/evals/scenarios/xoxno-lending-contracts/07-unwind-repay-withdraw-all.json (L7-11)
```json
    "Withdraws the full position by passing amount 0 in withdrawals: Vec<(HubAssetKey, i128)> (zero means the asset's whole position; `lending::constants::WITHDRAW_ALL` and `XoxnoLending::withdraw_all` pass it); does not pass i128::MAX or a value read moments earlier that interest accrual can make stale",
    "Uses the Vec<(HubAssetKey, i128)> returned by withdraw (or `Withdrawal::amount` from `XoxnoLending::withdraw`/`withdraw_all`) as the actual asset-unit amounts received instead of assuming the requested amounts landed, and clears the stored account id only on `Withdrawal::account_closed` or an explicit `account_exists == false`",
    "Repays with `XoxnoLending::repay`, which creates the transfer authorization, or with ControllerClient::repay(caller, account_id, payments) after `authorize_transfer_as_current(&env, &asset, &vault, &pool, amount)` for the exact token.transfer(vault -> pool, amount) sub-invocation immediately before the call; relies on the documented refund of excess payment to the caller rather than pre-computing the exact debt to the base unit",
    "Leaves to as None (or the vault's own address) on withdraw; never sets to to the pool or controller address, which reverts InvalidFlashloanReceiver #412 and would strand tokens",
    "Notes that withdraw and repay carry no when_not_paused gate (unlike supply and borrow), so an unwind still works while the controller is paused"
```
