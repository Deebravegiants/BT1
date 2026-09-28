### Title
Flash-loan repayment is pulled via `transfer_from` from an initiator-chosen `receiver`, draining any third-party contract's allowance to the pool - (File: contracts/pool/src/ops/flash.rs)

### Summary
The pool's flash loan pays principal to a caller-selected `receiver` and then repays itself with `transfer_from(spender=pool, from=receiver)`, consuming `receiver`'s token allowance to the pool rather than the initiator's funds. Because `initiator` and `receiver` are independent arguments threaded through the permissionless controller `flash_loan` entrypoint, an unprivileged caller can nominate any WASM contract as `receiver`, causing that contract's standing allowance to be spent — the same bug class as the Taiko `AssignmentHook` report, where an attacker-chosen address (Coinbase) was debited via `safeTransferFrom` instead of the actual caller.

### Finding Description
`LiquidityPool::flash_loan` accepts `initiator` and `receiver` as separate parameters and forwards both to `ops::flash::apply` [1](#0-0) . Inside `apply`, the pool transfers `amount` to `receiver` and invokes `receiver.execute_flash_loan(initiator, asset, amount, fee, pool, data)` [2](#0-1) . Repayment is then collected by `collect_repayment`, which only checks `asset.allowance(receiver, pool) >= total_repayment` and executes `asset.transfer_from(pool, receiver, pool, &total_repayment)` — the debit source is the attacker-selected `receiver`, not the `initiator` who authorized the controller call [3](#0-2) .

The controller path confirms the attacker controls both roles independently: `process_flash_loan` only requires `caller.require_auth()` (via `require_authorized_caller`) and that `receiver` be a WASM contract; there is no check tying `receiver` to `caller` or to the initiator's funds [4](#0-3) . The `data` payload passed to the victim's `execute_flash_loan` callback is also fully attacker-controlled [5](#0-4) .

This mirrors the Taiko flaw precisely: a hook pulled fees via `transferFrom` from a user-supplied `coinbase` address, letting a proposer spend any user's allowance to `TaikoL1`; here the pool pulls `principal + fee` from a user-supplied `receiver`, letting anyone spend any contract's allowance to the pool.

### Impact Explanation
Any WASM contract holding a SEP-41 allowance to the pool can be forced to pay for a flash loan it never requested. Concretely, per call the victim receives `amount` and is debited `amount + fee`, a guaranteed unauthorized loss of `fee` that is booked as protocol revenue [6](#0-5) . Worse, if the victim's `execute_flash_loan` implementation does not verify `initiator` and acts on the attacker-supplied `data` (generic flash-receiver/executor contracts do this), the attacker can extract the received principal to himself, turning the victim's allowance into a full principal-plus-fee theft bounded only by `min(allowance, pool cash)`. Repeated calls drain the allowance entirely. This is theft of user funds reachable by a single unprivileged transaction through the allowlisted `flash_loan` path.

### Likelihood Explanation
Exploitation requires a victim contract that (a) has granted a nonzero allowance to the pool, and (b) exposes an `execute_flash_loan` that does not revert when invoked with a foreign `initiator`/`data`. Both conditions are realistic: allowance-based repayment is the protocol's own designed mechanism, so any third-party flash receiver that approves the pool (standing or per-call approvals outside a pending loan) qualifies, and integrator contracts that treat the pool as a trusted caller commonly omit `initiator` validation. The attacker needs nothing privileged — `flash_loan` on the controller is permissionless [7](#0-6) . Severity is Medium: the guaranteed loss is the fee per call, with full-allowance theft conditional on the victim's callback behavior.

### Recommendation
Charge the `initiator`, not an attacker-named `receiver`. Either:
- Require `initiator == receiver` (or derive `receiver` from `initiator`) in `ops::flash::apply` / `process_flash_loan`, so the allowance spent always belongs to the party that authorized the call; or
- Keep the receiver arbitrary but pull repayment from `initiator` (`transfer_from(pool, initiator, pool, total)`), mirroring Taiko's fix of tracking the true proposer/payer.

Additionally, pass the initiator's authorization requirement into the repayment leg so allowance consumption is always attributable to the authenticated caller.

### Proof of Concept
1. Victim contract `V` previously approved the pool for `A` units of token `T` (e.g., a flash-receiver integration that keeps a standing allowance).
2. Attacker calls `controller.flash_loan(caller=attacker, hub_asset={hub,T}, amount=x, receiver=V, data=<attacker-chosen bytes>)` where `x + fee <= A` and `x <= pool reserves`.
3. `process_flash_loan` authenticates only `attacker`, then calls `pool.flash_loan(initiator=attacker, receiver=V, ...)` [8](#0-7) .
4. Pool transfers `x` of `T` to `V`, invokes `V.execute_flash_loan(attacker, T, x, fee, pool, data)`; `V`'s callback does not revert (and if `V` is a generic receiver honoring `data`, it can be made to forward `x` to the attacker).
5. `collect_repayment` checks `allowance(V, pool) >= x + fee` and executes `transfer_from(pool, V, pool, x + fee)` [9](#0-8) .
6. Result: `V`'s allowance is consumed and its balance drops by `fee` (or by `x + fee` net if the principal was extracted via `data`), with no authorization from `V`. Repeat while allowance remains.

### Citations

**File:** contracts/pool/src/lib.rs (L200-210)
```rust
    #[only_owner]
    fn flash_loan(
        env: Env,
        hub_asset: HubAssetKey,
        initiator: Address,
        receiver: Address,
        amount: i128,
        data: Bytes,
    ) -> i128 {
        ops::flash::apply(&env, hub_asset, initiator, receiver, amount, data)
    }
```

**File:** contracts/pool/src/ops/flash.rs (L60-67)
```rust
    asset.transfer(&pool, &receiver, &amount);
    require_balance(env, &asset, &pool, terms.balance_after_payout);
    invoke_receiver(
        env, &cache, &receiver, initiator, amount, terms.fee, &pool, data,
    );

    require_balance(env, &asset, &pool, terms.balance_after_payout);
    collect_repayment(env, &asset, &pool, &receiver, &terms);
```

**File:** contracts/pool/src/ops/flash.rs (L124-135)
```rust
pub(crate) fn book_fee(cache: &mut Cache, fee: i128) {
    let protocol_fee = Ray::from_asset(cache.env(), fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(cache, protocol_fee);
    cache.credit_cash(fee);
}

/// Successful-path tail of [`apply`]: books the fee, commits the market, and emits market state.
///
/// Called only after token balance checks confirm principal+fee returned.
pub(crate) fn finalize(env: &Env, cache: &mut Cache, fee: i128) {
    book_fee(cache, fee);
    events::emit_market_state(env, cache.commit());
```

**File:** contracts/pool/src/ops/flash.rs (L150-162)
```rust
    env.invoke_contract::<()>(
        receiver,
        &Symbol::new(env, "execute_flash_loan"),
        (
            initiator,
            cache.params().asset_id.clone(),
            amount,
            fee,
            pool.clone(),
            data,
        )
            .into_val(env),
    );
```

**File:** contracts/pool/src/ops/flash.rs (L166-180)
```rust
fn collect_repayment(
    env: &Env,
    asset: &token::Client,
    pool: &Address,
    receiver: &Address,
    terms: &FlashTerms,
) {
    assert_with_error!(
        env,
        asset.allowance(receiver, pool) >= terms.total_repayment,
        FlashLoanError::InvalidFlashloanRepay
    );
    asset.transfer_from(pool, receiver, pool, &terms.total_repayment);
    require_balance(env, asset, pool, terms.balance_after_repayment);
}
```

**File:** contracts/controller/src/strategies/flash_loan.rs (L14-33)
```rust
pub(crate) fn process_flash_loan(
    env: &Env,
    caller: &Address,
    hub_asset: &HubAssetKey,
    amount: i128,
    receiver: &Address,
    data: &Bytes,
) {
    require_authorized_caller(env, caller);
    require_positive_amount(env, amount);
    config::require_hub_active(env, hub_asset.hub_id);

    require_wasm_receiver(env, receiver);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();

    let fee = storage::with_flash_guard(env, || {
        pool_flash_loan_call(env, &pool_addr, hub_asset, caller, receiver, amount, data)
    });
```
