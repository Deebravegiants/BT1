### Title
Flash-loan repayment is pulled from an arbitrary initiator-chosen `receiver`, letting anyone spend a victim's standing token allowance to the pool - ([File: contracts/pool/src/ops/flash.rs](contracts/pool/src/ops/flash.rs))

### Summary
The incident class is a callback/settlement path that never authenticates the entity being charged, so an attacker aims it at a victim with an existing allowance and drains it via `transfer_from`. The pool's flash loan does exactly this: `collect_repayment` pulls `amount + fee` with `transfer_from(pool, receiver, pool, …)` from whatever `receiver` address the initiator supplied, and the only guard is `allowance(receiver, pool) >= total_repayment`. Nothing ties the `receiver` to the `initiator`, and nothing requires the receiver to have consented to this specific loan. Any contract that keeps a standing (or forgotten long-expiry) allowance to the pool can be named as `receiver` and charged. [1](#0-0) 

### Finding Description
`apply` pays out `amount` to `receiver`, invokes `execute_flash_loan` on it with attacker-controlled `data`, then `collect_repayment` checks only the token allowance and pulls `amount + fee` from `receiver` via `transfer_from`. The pool never authenticates `receiver`, never checks `receiver == initiator`, and never records a per-loan spend intent — the token allowance itself is the entire authorization. The receiver requirement is only `require_wasm_receiver` (it must be a contract). [2](#0-1) 

The reachable path for a single unprivileged attacker is `controller.flash_loan(initiator=attacker, asset, amount, receiver=victim_contract, data)`, which forwards `receiver` verbatim into `pool.flash_loan` → `ops::flash::apply`. A victim is any deployed contract that (a) exposes a callable `execute_flash_loan` (the standard receiver interface — the SDK's own mock/fixture approves `amount + fee` unconditionally and even refreshes the allowance inside the callback) or simply already holds an allowance and whose callback does not reject attacker-supplied `initiator`/`data`, and (b) has `allowance(victim, pool) >= amount + fee`. The pool pushes `amount` to the victim, then pulls `amount + fee` back — the victim net-loses the fee every call, and the attacker repeats until the allowance is exhausted. This mirrors the reported incident: the settlement code authenticates nothing about the payer, so pre-existing allowances become the attack surface. [3](#0-2) 

### Impact Explanation
Theft of user funds: each invocation transfers `fee` out of a victim contract's balance into protocol revenue without the victim initiating or consenting to the loan. With a typical bps-scale fee the per-call loss is small, but it is unprivileged, permissionless, and repeatable against the same allowance, so cumulative loss scales with the victim's allowance and balance. The payout leg lands on the victim, so principal is not stolen — the extractable amount per call is the fee, routed to pool cash/revenue rather than the attacker, which keeps this at Medium rather than High. [4](#0-3) 

### Likelihood Explanation
Medium. Exploitation needs a deployed contract holding a live `receiver → pool` allowance at least `amount + fee`. That state exists naturally: flash receivers approve `amount + fee` to the pool to repay, the canonical repayment helper approves with a next-ledger expiry, and any integration that approves with a longer window (or whose loan reverted after the allowance check was conceptually expected) leaves the allowance standing for its remaining lifetime. Receivers built on the documented mock pattern (`execute_flash_loan` that approves repayment without gating `initiator`/`pool`) satisfy the callback requirement directly — the eval guidance explicitly warns receivers "must gate the caller," confirming unauthenticated receivers are the default failure mode. The attacker only needs a normal `flash_loan` call; no privileged role, no oracle, no route. [5](#0-4) 

### Recommendation
Bind the repayment pull to the loan initiator instead of an arbitrary `receiver`:

- Require `receiver == initiator` (or require `receiver.require_auth()` so the charged party signs each loan), OR
- Record a per-loan obligation keyed to `receiver` written only by the receiver's own callback (e.g., the receiver must explicitly register/approve the repayment in storage during `execute_flash_loan`), and have `collect_repayment` consume that record rather than relying on a free-standing token allowance; or equivalently, have the callback return/pay `amount + fee` to the pool instead of the pool pulling from an allowance it never scoped.

At minimum, pass and enforce an initiator↔receiver binding so one user's standing allowance cannot be spent by an unrelated caller.

### Proof of Concept
1. Victim contract `V` previously took (or was designed for) flash loans and holds `allowance(V, pool) = A` on asset `T`, with `balance(V) ≥ A`. `V` exposes the standard `execute_flash_loan(initiator, asset, amount, fee, pool, data)` that approves repayment without authenticating `initiator` (the documented mock/SDK pattern).
2. Attacker calls `controller.flash_loan(initiator=attacker, asset=T_key, amount=x, receiver=V, data=arbitrary)` with `x + fee(x) ≤ A`.
3. `apply` transfers `x` of `T` from the pool to `V` (line 60), invokes `V.execute_flash_loan` — which succeeds and (for the mock pattern) re-approves `x + fee` to the pool — then `collect_repayment` sees `allowance(V, pool) ≥ x + fee` and executes `transfer_from(pool, V, pool, x + fee)` (lines 173–178).
4. Post-state: `V` is down `fee(x)`, pool cash and protocol revenue are up `fee(x)`, attacker repeats with fresh `x` until `A` (or `V`'s balance) is drained — no signature or role from `V` was ever required.

Root cause: `collect_repayment` treats a standing token allowance as loan consent; `apply`/`invoke_receiver` never authenticate that `receiver` agreed to this loan from this initiator. [6](#0-5)

### Citations

**File:** contracts/pool/src/ops/flash.rs (L40-70)
```rust
pub(crate) fn apply(
    env: &Env,
    hub_asset: HubAssetKey,
    initiator: Address,
    receiver: Address,
    amount: i128,
    data: Bytes,
) -> i128 {
    let mut cache = prepare(env, hub_asset, amount);
    require_wasm_receiver(env, &receiver);

    let pool = env.current_contract_address();
    let asset = token::Client::new(env, &cache.params().asset_id);
    let terms = terms(
        env,
        amount,
        cache.params().flashloan_fee,
        asset.balance(&pool),
    );

    asset.transfer(&pool, &receiver, &amount);
    require_balance(env, &asset, &pool, terms.balance_after_payout);
    invoke_receiver(
        env, &cache, &receiver, initiator, amount, terms.fee, &pool, data,
    );

    require_balance(env, &asset, &pool, terms.balance_after_payout);
    collect_repayment(env, &asset, &pool, &receiver, &terms);

    finalize(env, &mut cache, terms.fee);
    terms.fee
```

**File:** contracts/pool/src/ops/flash.rs (L150-163)
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
}
```

**File:** contracts/pool/src/ops/flash.rs (L165-180)
```rust
/// Pulls principal + fee via `transfer_from` after verifying allowance.
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
