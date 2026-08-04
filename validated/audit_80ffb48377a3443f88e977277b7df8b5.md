### Title
Existential-deposit top-up during contract value transfers is charged to the transaction `origin` instead of the immediate caller, allowing a malicious contract to drain the origin's balance via repeated dust transfers to fresh accounts - (File: substrate/frame/revive/src/exec.rs)

### Summary
`Stack::transfer`/`Stack::transfer_from_origin` in `pallet-revive` implements EVM-style "dust transfer" semantics: when a `CALL` sends `value` to a nonexistent (or sub-ED-balance) account, Substrate's `Currency::transfer` would normally fail because the destination can't reach the existential deposit. To emulate Ethereum behavior, `pallet-revive` tops up the shortfall to `T::Currency::minimum_balance()` by transferring it from the transaction **origin** (`Preservation::Preserve`) rather than from the contract account (`from`) that logically initiated the transfer. Because the `origin` reference is retained across the entire call stack regardless of call depth, any contract invoked (directly or transitively) by that origin can repeatedly trigger fresh-account transfers to drain the origin's free balance in ED-sized increments, independent of the value the origin explicitly authorized for the top-level call.

### Finding Description
`substrate/frame/revive/src/exec.rs` [1](#0-0)  contains the `transfer_from_origin` logic which is reached via `Stack::transfer` whenever a `CALL`/transfer targets an account that does not hold enough balance to satisfy the existential deposit after receiving `value`. Instead of requiring the calling account (`from`, i.e. the immediate `msg.sender` contract in EVM terms) to fund the ED shortfall, the code pulls the ED top-up from the `origin` field of the `Stack`, which represents the original transaction signer, not the immediate caller.

Because `origin` is a property of the whole call stack (set once at the top-level dispatch and carried through every nested `Ext::call`/`Ext::instantiate`), any contract reachable from that origin - even several call frames deep - can invoke this path. An attacker-controlled contract can:
1. Loop internally (bounded only by available gas/weight), and
2. On each iteration call a freshly-derived, never-before-seen address with a tiny `value` (below ED),

forcing `Stack::transfer` to hit the "destination doesn't exist / below ED" branch and pull a full existential deposit from `origin`'s free balance on every iteration - without ever debiting the contract's own account for that ED portion.

This breaks the expected authorization boundary: the top-level extrinsic only commits the `origin` to the `value` explicitly specified for the outer call (plus gas/weight fees); it does not commit the origin to funding an arbitrary number of ED top-ups determined by nested contract logic that the origin does not control. None of the existing protections (gas/weight metering, storage deposit limits) constrain this specific balance flow, because the ED top-up is accounted as a currency transfer from `origin`, not as part of the contract's storage deposit meter, so `storage_deposit_limit` does not bound it, and the value moved is invisible to weight-based fee accounting.

### Impact Explanation
An attacker deploying a contract that is called by (or that calls back to) the real transaction `origin` can cause repeated, uninvited debits of `origin`'s free balance in ED increments, each sent to attacker-chosen addresses that the origin never authorized. This is a direct, unauthorized balance drain of the `origin` account that is not bounded by the `value` field of the top-level call and is not attributable to `from` (the contract that actually performed the transfer) as EVM `msg.sender`/balance semantics would dictate. The number of ED top-ups extractable in a single transaction is bounded only by the gas/weight limit set for that transaction, not by any deliberate value/ED budget the origin approved.

### Likelihood Explanation
This is triggerable with only unprivileged capabilities: any user calling an attacker-deployed (or attacker-influenced) contract via the normal `pallet-revive` dispatch path is exposed. No special privileges, governance, or leaked keys are required - only that the victim's account is the `origin` of a transaction that ends up executing a malicious contract performing repeated dust sends to fresh addresses. The attack is fully repeatable across transactions and scales with the number of fresh addresses the attacker is willing to generate and the gas budget available.

### Recommendation
Charge the existential-deposit top-up from the immediate caller (`from`) rather than the transaction `origin`, matching normal Substrate transfer semantics where the sender of a transfer bears its full cost. If sponsoring dust transfers from the origin is intentional (to preserve EVM `CALL` semantics for legitimately small values), it should be: (a) capped to a small, explicitly bounded total per transaction, (b) accounted through the existing storage/deposit meter so it is visible and limited by `storage_deposit_limit`, and (c) restricted to the top-level call only rather than any nested call reachable from that origin, so nested contract logic cannot repeatedly draw on the origin's balance.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/exec/tests.rs` or `substrate/frame/revive/src/tests.rs`:
1. Deploy a contract `Drainer` that, when called, loops `N` times, each time calling `Ext::call`/`seal_call` with `value = 1` wei-equivalent (below `T::Currency::minimum_balance()`) to a freshly-derived address (e.g., `derive_address(seed_counter)`).
2. Fund `origin` with `N * ED + margin`; fund `Drainer`'s own contract account with only enough balance to cover its own storage deposit (no extra for EDs).
3. Have `origin` call `Drainer` once (top-level call, `value = 0` or minimal).
4. Assert: `get_balance(origin)` decreases by approximately `N * T::Currency::minimum_balance()`.
5. Assert: `get_balance(Drainer's account)` is unaffected by the ED portion (only reflects the `value` amounts, if any, actually specified as own funds).
6. Assert this holds even though `msg.sender` for each nested call is `Drainer`, not `origin`, demonstrating the origin bears costs it did not directly authorize via the top-level call's `value` field.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1-1)
```rust
// This file is part of Substrate.
```
