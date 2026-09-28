### Title
`flash_loan` pulls principal+fee from an attacker-chosen `receiver`'s allowance, letting anyone spend a victim contract's approval to the pool - (File: contracts/pool/src/ops/flash.rs)

### Summary
`collect_repayment` executes `asset.transfer_from(pool, receiver, pool, total_repayment)` where `receiver` is a caller-supplied argument of `flash_loan`. The `from` of the `transfer_from` is not bound to the caller — any unprivileged address can nominate any WASM contract as the receiver. If that contract has previously granted the pool a token allowance, the attacker can force the pool to debit the victim's balance to cover the flash-loan repayment, net-charging the victim the flash-loan fee without any authorization from the victim.

### Finding Description
The bug class is a `transferFrom` whose `from` argument is not hard-coded as `msg.sender`. In `apply`, the pool:

1. Transfers `amount` to `receiver` (`asset.transfer(&pool, &receiver, &amount)`).
2. Invokes `execute_flash_loan` on `receiver`.
3. Calls `collect_repayment`, which asserts `asset.allowance(receiver, pool) >= terms.total_repayment` and then pulls `amount + fee` from `receiver` via `transfer_from` (`contracts/pool/src/ops/flash.rs:166-180`).

`receiver` is an unconstrained argument: `require_wasm_receiver` only checks that it is a WASM contract, and nothing ties `receiver` to `initiator` or requires `receiver`'s authorization. In Soroban, `transfer_from` requires the *spender* (the pool) to authorize — not `receiver` — so the pool's own auth suffices; the victim never signs anything. The only requirements are that `receiver` is a contract exposing an `execute_flash_loan` entrypoint (so `invoke_receiver` does not revert) and that `receiver` holds a live allowance to the pool of at least `amount + fee`.

Legitimate flash-receiver contracts routinely do exactly this: they implement `execute_flash_loan` and approve the pool for the repayment amount. An attacker can therefore call `flash_loan(caller, asset, amount, victim_receiver, data)` with a large `amount`; the victim receives `amount`, its callback runs (which may be a no-op for a permissive receiver), and the pool then debits `amount + fee` against the victim's allowance. Net effect: the victim's balance decreases by `fee` and its stored allowance is consumed, even though it never initiated or authorized the loan.

### Impact Explanation
Theft of user funds: each invocation transfers value equal to the flash-loan fee from the victim contract to the protocol's revenue accounting (`book_fee` credits the fee as cash and protocol revenue). The attack is repeatable as long as the victim's remaining allowance covers `amount + fee`, so an attacker can drain up to `allowance - amount` in aggregate fees in a single or batched transaction, and can grief any receiver contract that maintains a standing approval to the pool. This mirrors the referenced finding: an allowance granted for the contract's own use is spent by a third party against the owner's will.

### Likelihood Explanation
Exploitation requires a victim contract that (a) implements `execute_flash_loan` and (b) holds a non-consumed allowance to the pool of at least `amount + fee`. Flash receivers that pre-approve or leave residual allowance are the expected integrator pattern, so the precondition is realistic. The attacker needs no privileges, no capital (the principal is supplied by the pool itself), and pays only gas; the attacker does not even profit directly — the damage is forced fee extraction — but the victim's funds are irreversibly taken and booked as protocol revenue. Severity: Medium.

### Recommendation
Bind the repayment source to the initiator or the flash loan session rather than trusting the arbitrary `receiver` argument. Options:

- Pull repayment via `transfer_from` from `initiator` (who must authorize `flash_loan`), or require `receiver.require_auth()` inside `apply` so the nominated contract consents to the draw.
- Alternatively, verify post-callback that `receiver`'s *own* balance increased by `amount` before collecting, and pull only the fee from allowance — or require the receiver to push the repayment with `transfer` from within its own `execute_flash_loan` (auth-bound), rather than the pool pulling `transfer_from` on an arbitrary `from`.

### Proof of Concept
1. Victim contract `V` is a flash receiver: it exposes `execute_flash_loan` and holds `allowance(V, pool) >= amount + fee` (e.g., a standing approval from prior use).
2. Attacker calls `flash_loan(caller: attacker, asset, amount, receiver: V, data: empty)` on the controller/pool with `amount` sized so `fee` is meaningful.
3. Pool transfers `amount` to `V`, invokes `V.execute_flash_loan` (succeeds as a no-op or benign handler), then `collect_repayment` checks `V`'s allowance and executes `transfer_from(pool, V, pool, amount + fee)`.
4. `V` ends the transaction `fee` poorer and with its allowance spent; the fee is credited to protocol revenue and is unrecoverable by `V`. The attacker repeats until `V`'s remaining allowance falls below `amount + fee`.