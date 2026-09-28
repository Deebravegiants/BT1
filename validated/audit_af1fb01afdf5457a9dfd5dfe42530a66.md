### Title
Attacker-initiated `flash_loan` consumes a third-party receiver's standing token allowance to the pool, forcing it to pay fees for loans it never requested - (File: contracts/pool/src/ops/flash.rs)

### Summary
`flash_loan` repayment is collected through the receiver's token allowance, and any caller may name any Wasm contract as `receiver`. An allowance the receiver granted the pool to repay its own flash loan can therefore be consumed by an unrelated initiator's loan. This mirrors the ENS `wrapETH2LD` flaw: permissioning granted for one purpose (repaying the receiver's own borrow) silently extends to assets/uses the approver never intended (anyone's flash loan naming them as receiver).

### Finding Description
The controller's `flash_loan` entrypoint is permissionless in the relevant sense: `process_flash_loan` only calls `require_authorized_caller(env, caller)` (i.e., `caller.require_auth()`), requires `amount` positive, the hub active, and `receiver` a Wasm contract, then forwards `caller` as `initiator` and the attacker-chosen `receiver`/`data` to the pool. [1](#0-0) 

In the pool, `apply` pays `amount` to `receiver`, invokes `execute_flash_loan` on it with the attacker-controlled `initiator` and `data`, then `collect_repayment` merely checks `asset.allowance(receiver, pool) >= amount + fee` and pulls `amount + fee` via `transfer_from`. [2](#0-1) [3](#0-2) 

Two design facts make the allowance over-extended:

1. The allowance check is not bound to the initiator or the loan the receiver intended. Any standing allowance from `receiver` to `pool` — including excess allowance, which ADR-0010 explicitly permits and which `transfer_from` only partially consumes, leaving the remainder live until `live_until_ledger` — satisfies the check for an attacker's loan.
2. Nothing ties `receiver` to `initiator`; the protocol even documents that "the initiator is never the receiver itself," so a foreign initiator is a normal shape, not an anomaly the pool rejects.

### Impact Explanation
Theft of user funds. For each attacker-initiated `flash_loan(caller=attacker, asset, amount, receiver=victim, data)` where the victim's callback does not revert for a foreign initiator (or where standing allowance exists and the callback succeeds), the victim receives `amount` and then has `amount + fee` pulled from its balance — a net loss of `fee` per call, booked as protocol revenue. Repeating with small `amount` lets the attacker drain the victim's outstanding allowance to the pool and beyond it whenever the victim's own callback re-approves repayment. The victim did not request the loan, chose neither the amount, asset, nor `data`, yet pays for it. As in the judged ENS finding, assets are at risk because the user was unaware that approving the pool for repayment also approved arbitrary third parties to spend that allowance.

### Likelihood Explanation
Exploitation requires a Wasm receiver contract whose `execute_flash_loan` does not panic for an unexpected `initiator`/`pool` pair. Receivers that follow the documented hardening (gating `initiator == cfg.operator` and `pool == cfg.pool`, short-lived exact allowance) abort the call, which reverts the loan and costs the attacker nothing but fails. Ungated receivers — including ones that gate only on the pool address, or that carry excess/expired-but-live allowance — are exploitable with a single ordinary `controller::flash_loan` call. This makes the issue conditional on external receiver hardening, consistent with a Medium severity.

### Recommendation
Bind the repayment pull to this loan, not to the receiver's generic allowance. Options:

- Have the pool collect `amount + fee` by requiring the receiver to return/push within the callback under the existing balance-bracket checks (the post-callback balance must equal post-payout already enforced at `flash.rs:66`), removing `transfer_from` entirely; or
- Record per-loan state: store `(receiver, initiator, expected_repayment)` when paying out, and in `collect_repayment` require the allowance was created inside this transaction (e.g., snapshot `allowance(receiver, pool)` before payout and require `allowance_after - allowance_before >= total_repayment`), so stale standing allowance cannot satisfy repayment.

Allowance-before/allowance-after delta checking is the minimal change that preserves the current receiver UX while closing the cross-initiator spend.

### Proof of Concept
Precondition: `Victim` is a deployed Wasm contract implementing `execute_flash_loan` that gates only on `pool == cfg.pool` (a plausible partial hardening), holds token `A`, and has previously run a flash loan where it approved `amount' + fee' + X` to the pool — leaving allowance `X` (explicitly permitted by ADR-0010 / INV-FLASH-01).

1. Attacker calls `controller.flash_loan(caller=attacker, asset=HubAssetKey{hub_id, A}, amount=P, receiver=Victim, data=arbitrary)` with `P + fee(P) <= X`.
2. `process_flash_loan` passes because only `attacker` must auth; `Victim` need not consent.
3. Pool `apply` transfers `P` of `A` to `Victim`, calls `Victim.execute_flash_loan(initiator=attacker, ...)`. `Victim` checks the pool argument, it matches, callback returns.
4. `collect_repayment` sees `allowance(Victim, pool) = X >= P + fee`, pulls `P + fee` from `Victim`.
5. `Victim` ends `+P - (P + fee) = -fee`; the attacker paid nothing and forced `Victim` to fund protocol revenue. The attacker can repeat until `X` is exhausted, choosing `P` to minimize victim-side requirements.

Root cause: `collect_repayment` at `contracts/pool/src/ops/flash.rs:173-179` validates only the allowance magnitude, and `process_flash_loan` at `contracts/controller/src/strategies/flash_loan.rs:22-33` never binds `receiver` to the authorized `caller`, so a repayment approval granted for the receiver's own loans is spendable on loans initiated by anyone.

### Citations

**File:** contracts/controller/src/strategies/flash_loan.rs (L22-33)
```rust
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

**File:** contracts/pool/src/ops/flash.rs (L173-179)
```rust
    assert_with_error!(
        env,
        asset.allowance(receiver, pool) >= terms.total_repayment,
        FlashLoanError::InvalidFlashloanRepay
    );
    asset.transfer_from(pool, receiver, pool, &terms.total_repayment);
    require_balance(env, asset, pool, terms.balance_after_repayment);
```
