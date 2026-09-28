### Title
`Controller::flash_loan` lets an unprivileged caller name an arbitrary `receiver`; the pool then spends that receiver's token allowance via `transfer_from` to collect principal + fee, draining any flash-receiver contract that has approved the pool - (File: contracts/pool/src/ops/flash.rs)

### Summary
`Controller::flash_loan(caller, asset, amount, receiver, data)` only requires authorization from `caller` (`validation::require_authorized_caller` in `strategies/flash_loan.rs`). The `receiver` is a free caller-supplied address. Inside `pool::ops::flash::apply`, the pool pays `amount` to `receiver`, invokes `execute_flash_loan` on it, and then calls `collect_repayment`, which pulls `amount + fee` out of `receiver` using the pool's spender allowance:

```rust
assert_with_error!(
    env,
    asset.allowance(receiver, pool) >= terms.total_repayment,
    FlashLoanError::InvalidFlashloanRepay
);
asset.transfer_from(pool, receiver, pool, &terms.total_repayment);
``` [1](#0-0) 

This is the same bug class as the PerpDepository report: a permissionless entrypoint lets the caller choose *which* account's pre-existing allowance/authorization is consumed, rather than binding the payer to the authorized caller.

### Finding Description
- `flash_loan` is permissionless: `caller.require_auth()` is enforced, but `receiver` is attacker-chosen and is never required to equal `caller` or to authorize the call (contracts cannot `require_auth` retroactively for being named in `transfer_from`; the spender is the pool, which authorizes implicitly as the direct invoker).
- The only constraints on `receiver` are `require_wasm_receiver` (it must be a Wasm contract) and that its `execute_flash_loan` callback does not revert. The callback receives attacker-controlled `initiator` and `data` arguments (`invoke_receiver`, flash.rs:140–163).
- The pool's design *requires* flash-receiver contracts to hold a standing token allowance to the pool so it can collect repayment — exactly the approval precondition of the original bug. Any deployed receiver contract that has approved the pool and whose callback does not hard-reject foreign initiators can be used as `receiver`.
- Each call transfers `amount` to the victim and then pulls `amount + fee` back out of the victim's balance via its allowance, so the victim nets a loss of `fee` per call, repeat-consumed against its remaining allowance until `allowance < total_repayment`.

Net per-call theft is bounded by `fee = flashloan_fee_bps * amount` (flash.rs:107–121), and the attacker can set `amount` up to the market's cash reserves (`cache.require_reserves`), maximizing the fee per call.

### Impact Explanation
Theft of user funds: any flash-receiver contract that approved the pool (the intended integration pattern) loses `fee` of the underlying asset per invocation, with total loss approaching its outstanding allowance. This is unprivileged and repeatable while allowance remains, bounded per call by pool cash reserves and the allowance.

### Likelihood Explanation
Requires a victim: a deployed Wasm contract exposing `execute_flash_loan`, holding an allowance ≥ `amount + fee` to the pool, whose callback doesn't revert for a foreign `initiator`. Receiver contracts are expected to approve the pool precisely so `collect_repayment` works, so such victims plausibly exist; whether a given receiver gates on `initiator`/`data` is contract-specific and unverified here — this is the main uncertainty.

### Recommendation
Bind the payer to the authorized caller, mirroring the report's fix (`msg.sender` instead of `account`):
- In `Controller::flash_loan`, pass `caller` as the repayment source and require `receiver`'s auth, or
- In `pool::ops::flash::collect_repayment`, pull repayment from `initiator`/`caller` (which must also receive the principal), not from the caller-designated `receiver`, so no third party's allowance can be consumed without it initiating the call.

### Proof of Concept
1. Victim contract `V` implements `execute_flash_loan` and has approved the pool for ≥ `A + fee` of asset `X` (required for its own legitimate flash loans).
2. Attacker calls `controller.flash_loan(attacker, X_key, A, V, attacker_data)` with `A` near the market's reserves, authorizing only as `caller`.
3. Pool transfers `A` of `X` to `V`, calls `V.execute_flash_loan(attacker, X, A, fee, pool, data)`. If `V`'s callback does not revert for the foreign initiator, `collect_repayment` executes `X.transfer_from(pool, V, pool, A + fee)` — allowed because `V` approved the pool.
4. `V` ends with `-fee` net; repeat until `allowance(V, pool) < A + fee`.

### Citations

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
