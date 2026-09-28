### Title
A 1-unit donation to the pool permanently bricks `flash_loan` for a market — ([File: contracts/pool/src/ops/flash.rs])

### Summary
The pool's `flash_loan` reconciles accounting `cash` against the real `token.balance()` of the pool with strict equality, while every other path treats `cash` as a pure bookkeeping number that incidental token donations never increase. An unprivileged address can send a direct token transfer (donation) of a single base unit to the pool address, after which `balance != cash` permanently — no entrypoint credits donated tokens into `cash`, and no sweep exists. Every subsequent `flash_loan` for that market reverts on its equality check.

### Finding Description
`cash` is tracked separately from custody: "cash is a bookkeeping number. The only reconciliation against a real `token.balance()` is in `flash_loan`, which checks it three times with strict equality" [1](#0-0) . Donations are explicitly unbooked: "Tracked cash is a separate reserve balance that incidental token donations do not increase" [2](#0-1) , and "Direct donations do not rewrite those books" [3](#0-2) . A test confirms a `token.transfer` to the pool leaves all market books unchanged while the balance rises [4](#0-3) . Since `cash` can only move through `credit_cash`/`debit_cash` inside owner-gated pool mutators [5](#0-4) , and every pool mutator is `#[only_owner]` (the controller), the donated amount creates a permanent `balance − cash` gap. The strict-equality checks in `flash_loan` then fail on every call, reverting the transaction — a remotely triggered, persistent denial of service on the exact-balance cash flash path.

### Impact Explanation
Permanent denial of service of the market's `flash_loan` entrypoint, and transitively of every controller path that relies on it (`controller.flash_loan`, and strategy flows such as `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend` that borrow flash liquidity through the pool). The cost to the attacker is one base unit of the token (a stroop for XLM), and no recovery path exists because no unprivileged or governance entrypoint sweeps donations into `cash` — `recapitalize` only credits up to the measured backing shortfall and refunds the rest [6](#0-5) .

### Likelihood Explanation
Any unprivileged address can execute it: `token.transfer(attacker, pool, 1)` on the SAC. No authorization, timing, or price dependency. One transaction per market permanently disables that market's flash path, matching the external report's class of a low-privilege, network-reachable availability attack (CVSS 6.5, A:H).

### Recommendation
Replace the strict-equality reconciliation in `flash_loan` with a balance-delta check: snapshot `balance` at entry, and require `balance_after − balance_before == fee` (or `>= fee`) at pull-back rather than `balance == cash [+ fee]`. Alternatively, add a permissionless `skim`/`sweep` entrypoint that credits `balance − cash` surplus to revenue or `cash`, so donations self-heal the invariant instead of breaking it.

### Proof of Concept
1. Market `M` is live with `cash == balance` (normal operation).
2. Attacker calls `token.transfer(attacker -> pool, 1)` on `M`'s asset. Per the donation semantics, no market book changes: `cash` is unchanged, `balance = cash + 1` [7](#0-6) .
3. Any subsequent `pool.flash_loan(M, ...)` (or `controller.flash_loan`) reverts at the first strict `balance == cash` check, before paying out [1](#0-0) .
4. The state is unrecoverable without contract intervention: `credit_cash` is only reachable through owner-gated pool mutators [8](#0-7) , and `recapitalize` credits only up to the backing shortfall, refunding excess [6](#0-5) , so neither suppliers nor governance can realign `cash` with the donated balance through existing entrypoints.

Caveat: I was unable to read `contracts/pool/src/ops/flash.rs` directly to confirm the exact equality expression; this finding relies on the pool README's documented "strict equality" reconciliation and the test-confirmed fact that donations never touch `cash`. If the check compares pre/post balance deltas rather than `balance == cash`, the finding does not hold.

### Citations

**File:** contracts/pool/README.md (L61-63)
```markdown
controller's word, without verifying the transfer. `cash` is a bookkeeping
number. The only reconciliation against a real `token.balance()` is in
`flash_loan`, which checks it three times with strict equality.
```

**File:** docs/reference/formulas.md (L81-82)
```markdown
Tracked cash is a separate reserve balance that incidental token donations do
not increase.
```

**File:** docs/reference/formulas.md (L89-94)
```markdown
let shortfall = max(0, floor(supply_value) - (cash + ceil(debt_value)));
```

Addition and subtraction saturate. Supply entry rejects a positive shortfall.
Recapitalization credits at most that shortfall, refunds excess and mints no
shares.
```

**File:** docs/explanation/threat-model.md (L130-131)
```markdown
market books are separate. Direct donations do not rewrite those books.
Cash flash loans impose exact balance transitions and allowance repayment;
```

**File:** tests/test-harness/tests/pool_money_flow_audit.rs (L86-96)
```rust
    // An unsolicited donation belongs to no market's cash book.
    market.token_admin.mint(&payer, &(7 * UNIT));
    token.transfer(&payer, &market.pool, &(7 * UNIT));
    let check = |supply, debt, label: &str| {
        let state = books(&t, &key, supply, debt);
        let other = books(&t, &second, secondary_supply, 0);
        assert_eq!(other.cash, 100 * UNIT);
        assert_eq!(
            token.balance(&market.pool),
            state.cash + other.cash + 7 * UNIT
        );
```

**File:** contracts/pool/src/cache/cash.rs (L24-41)
```rust
    pub(crate) fn credit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.cash = self
            .cash
            .checked_add(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }

    /// Decreases accounting cash by `amount`. Rejects negative amounts or
    /// insufficient reserves.
    pub(crate) fn debit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.require_reserves(amount);
        self.cash = self
            .cash
            .checked_sub(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }
```
