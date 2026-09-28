### Title
Tokens transferred to the Controller outside measured flows are permanently stranded — there is no sweep or recovery path - ([File: contracts/controller/src/payments.rs])

### Summary
The XChainController issue class — a contract that can receive value but exposes no way to send it back out — maps directly onto XOXNO Lending's controller and pool. Both contracts hold token balances (the controller transiently, the pool as custody), and neither exposes any sweep, rescue, or admin withdrawal entrypoint. An unprivileged address can push any listed token into the controller with a plain `token::transfer`, and no reachable code path can ever move it out: every outbound controller transfer is a strictly bounded *balance-delta* refund measured against a snapshot taken inside the same transaction.

### Finding Description
The controller only ever sends tokens out through `refund_controller_balance_delta` (contracts/controller/src/payments.rs:41-52), which snapshots `balance_before` at the start of a repayment leg and refunds **only the increase since that snapshot**, explicitly "preserving the pre-existing balance". The same pattern holds across all unprivileged-reachable flows:

- `repay_debt_from_controller` snapshots after funding so only that call's repayment excess returns to the caller (contracts/controller/src/strategies/legs.rs:59-80).
- `flash_position` declares per-asset collateral/refund legs; per `docs` and `skills/xoxno-lending-contracts/flash-loans.md`, "an undeclared token left on the controller is neither deposited nor refunded."
- `migrate_from_blend` deliberately ignores pre-existing controller balances — the harness test `test_migrate_refund_ignores_preexisting_controller_balance` pins that stranded tokens minted to the controller remain untouched and are never swept (tests/test-harness/tests/strategy/migrate_blend.rs:496-537).
- Borrow/withdraw payouts go through the pool, which debits tracked `cash` — a bookkeeping number donations never increase (INV-ACCT-02, docs/reference/invariants.md). Pool `repay`/`recapitalize` refunds are bounded by the caller's measured receipt (`pool_trust_repay_refunds_only_payer_surplus`, certora/pool/spec/guard_rules.rs:365-411), so stray pool custody is likewise never claimable.
- Withdraw/borrow *to* the pool or controller are rejected with `InvalidFlashloanReceiver` precisely because "the controller holds funds no balance-delta measurement can ever claim" (tests/test-harness/tests/controller/recipient_is_protocol_contract.rs:1-5) — but that guard only covers protocol entrypoints, not direct token transfers.

Unlike the swap-aggregator (out of scope), which has `sweep_balance`, the controller and pool ABIs contain no recovery function at all — `upgrade` is governance-timelocked and is the only theoretical escape.

### Impact Explanation
Any tokens an unprivileged address sends to the controller address — by mistake, by a buggy integrator, or as an undeclared asset pushed by a `flash_position` receiver during its callback — are **permanently frozen**. They belong to no cash book, are excluded from every measured-delta refund by design, and cannot be claimed by anyone, including governance, without a contract upgrade. This is the same permanent-loss-of-value impact as the Derby finding.

### Likelihood Explanation
Requires a user or integrating contract to transfer tokens to the controller (or undeclared tokens during a flash callback) rather than through a crediting entrypoint. Low-frequency but non-trivial: the codebase itself contains multiple regression tests showing developers anticipated exactly this confusion (stray mints to the controller, flash receivers over-pushing collateral), and SAC `transfer` to a contract address needs no contract cooperation. Impact is permanent loss of whatever is sent; consistent with Medium.

### Recommendation
Add a governance-routed (timelocked) recovery operation that transfers controller token balances *above* any in-flight obligations to an accumulator/treasury address, and/or a documented policy for undeclared `flash_position` receipts (e.g., credit them to protocol revenue via `seize_positions`-style reclassification rather than stranding them). On the pool side, document that donations above tracked `cash` are unrecoverable, or add an owner-only sweep that can only touch `balance - Σ cash` across sibling markets on the same asset.

### Proof of Concept
```rust
// Any unprivileged address strands tokens on the controller forever:
let token = token::Client::new(&env, &usdc);
token.transfer(&attacker, &controller_address, &1_000_000_000);

// No controller entrypoint can move it:
// - refund_controller_balance_delta refunds only delta-since-snapshot,
//   so the pre-existing 1_000_000_000 is excluded (payments.rs:48-51)
// - migrate_from_blend refund ignores it (migrate_blend.rs test pins this)
// - flash_position only refunds declared refund assets
// - pool-bound paths measure receipts, never the controller's balance
// There is no sweep_balance / rescue_tokens on controller or pool.
assert_eq!(token.balance(&controller_address), 1_000_000_000); // stuck
```
The harness test `test_migrate_refund_ignores_preexisting_controller_balance` is itself the executable proof: it mints 0.25 ETH to the controller and asserts the balance remains after the operation with no path to claim it.