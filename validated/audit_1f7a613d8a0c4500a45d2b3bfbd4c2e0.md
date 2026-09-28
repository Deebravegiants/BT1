### Title
Flash-loan repayment is pulled from an attacker-selected `receiver`, so any contract exposing `execute_flash_loan` can be forced to pay fees for loans it never initiated - (File: contracts/pool/src/ops/flash.rs)

### Summary
The Vaultka bug class is "callback fires on a handler that never validated it was the initiator of the request". The XOXNO analog lives in the pool flash loan: `LiquidityPool::flash_loan` accepts a caller-chosen `receiver`, pays the principal to it, invokes `execute_flash_loan` on it, and then collects `amount + fee` via `transfer_from` **from the receiver** (`contracts/pool/src/ops/flash.rs:166-180`), not from the authenticated initiator. Neither the controller path (`contracts/controller/src/strategies/flash_loan.rs:14-33`) nor the pool binds `receiver` to `initiator` or obtains any opt-in from the receiver. Any WASM contract that exports `execute_flash_loan` and approves repayment when the `pool` argument is the real pool — the documented integration gate — can be charged flash fees by an arbitrary caller without its consent.

### Finding Description
`pool_flash_loan_call` forwards the authenticated `caller` as `initiator` and the user-supplied `receiver` to the pool (`contracts/controller/src/external/pool.rs:96-107`). In `apply` the pool:

1. `asset.transfer(&pool, &receiver, &amount)` — principal goes to `receiver` (`flash.rs:60`)
2. `invoke_receiver(...)` calls `execute_flash_loan(initiator, asset, amount, fee, pool, data)` on `receiver` (`flash.rs:150-162`)
3. `collect_repayment` requires `allowance(receiver, pool) >= total_repayment` and executes `transfer_from(pool, receiver, pool, &terms.total_repayment)` (`flash.rs:173-179`)

The repayment source is `receiver`, an address the caller picked freely (`require_wasm_receiver` only checks it is a contract). A receiver whose callback validates `pool` and approves `amount + fee` — exactly the pattern the SDK skill documents, where the "trusted-invoker gate" is `pool == cfg.pool` plus an optional `initiator` check — will have `fee` pulled from it on every call initiated by anyone. The `initiator` argument is delivered to the callback, but the protocol never enforces that the initiator is the receiver or that the receiver consented; a receiver that omits the `initiator == cfg.operator` check (or uses a permissive operator) is drained at the fee rate. Each call is unprivileged: any address can invoke `controller.flash_loan(hub_asset, amount, receiver, data)` since `process_flash_loan` only requires `require_authorized_caller(caller)` and `require_wasm_receiver(receiver)`.

### Impact Explanation
Theft of user funds. Each invocation charges the victim receiver the flash fee on a principal size chosen by the attacker, bounded only by `cache.require_reserves(amount)`. The attacker can loop the call, extracting `fee` per iteration from the victim's token balance into protocol revenue, until the victim's balance or remaining allowance is exhausted. The attacker does not need the victim's auth at any point — only a callable `execute_flash_loan` entry point on the victim contract.

### Likelihood Explanation
Medium-high feasibility, per-call impact bounded by the fee. It requires a deployed receiver contract that approves repayment in its callback without binding `initiator`, which is realistic because (a) the documented minimum gate is "gate the caller to the trusted pool" (`mock/flash-loan-receiver/README.md:4-5`), and (b) the `initiator` check is presented as optional hardening in the skill docs. Because the fee is a fraction of principal, draining a victim takes repeated calls; severity is Medium.

### Recommendation
Bind repayment to the initiator, not the callback target: pull `amount + fee` via `transfer_from` from `initiator` (the address the controller authenticated), or require `receiver == initiator`. Alternatively, require the receiver's pre-existing allowance to be checked *before* paying out and treat the callback as informational only. Concretely, change `collect_repayment` in `contracts/pool/src/ops/flash.rs` to debit `initiator`, and have the initiator forward/approve rather than making the receiver the default payer.

### Proof of Concept
```rust
// Victim: a production receiver that gates only on the pool address.
#[contractimpl]
impl FlashLoanReceiver for VictimReceiver {
    fn execute_flash_loan(env: Env, _initiator: Address, asset: Address,
                          amount: i128, fee: i128, pool: Address, _data: Bytes) {
        assert!(pool == cfg(&env).pool, "untrusted pool");
        // approves repayment as documented; never checks _initiator
        token::Client::new(&env, &asset)
            .approve(&env.current_contract_address(), &pool,
                     &(amount + fee), &(env.ledger().sequence() + 1));
    }
}

// Attacker (any account):
for _ in 0..n {
    controller.flash_loan(&hub_asset, &pool_balance, &victim_addr, &data);
    // pool pays `amount` to victim, victim approves,
    // pool pulls `amount + fee` from victim -> victim loses `fee` per call
}
```
Each iteration nets the pool `fee` booked as protocol revenue (`book_fee`, `flash.rs:124-128`) while the victim pays it, solely because the attacker could name the victim as `receiver`.