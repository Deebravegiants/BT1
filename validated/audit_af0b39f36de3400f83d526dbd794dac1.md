### Title
Dust `no_seize` collateral leg vetoes the entire pro-rata liquidation, letting a borrower make an underwater account unliquidatable — (File: contracts/controller/src/positions/liquidation/apply.rs)

### Summary
The analog of the autoscaler bug — "entries that can never satisfy the condition are counted in the check, so the condition never fires" — maps onto the liquidation seizure plan: the plan is built pro-rata over **every** nonzero collateral leg of the account, and the `no_seize` listing flag is then enforced across those legs. A single nonzero `no_seize` leg aborts the whole multi-leg liquidation, exactly as a pool with `max_replicas=0` can never produce an error yet still counted toward the failure threshold. A borrower can exploit this by supplying a dust amount of a `no_seize`-flagged collateral asset, making their position permanently unliquidatable.

### Finding Description
Liquidation distributes seizure pro-rata across all of the account's collateral positions. Per INV-HALT-02, listing flags gate different legs: "ordinary liquidation seizure rejects only `no_seize`" and "nonzero `no_seize` collateral can block the whole proportional liquidation, even if supplied after the flag is set. Zero-token planned seizure legs are omitted before that check" (`docs/reference/invariants.md`, INV-HALT-02) [1](#0-0) .

Two facts combine into the flaw:

1. `no_seize` does **not** gate entry — supply rejects only `paused` and `frozen`, so an account can acquire a nonzero balance of a `no_seize` asset through `supply` (or inherit one through a `SeizeMode::Credit` liquidation into a receiver). [2](#0-1) 
2. The seizure check treats every nonzero planned leg identically. A dust leg that contributes a negligible fraction of collateral — economically irrelevant, the "disabled pool" of the plan — still triggers the veto and aborts the entire liquidation, including all healthy legs.

So a borrower holding real collateral can `supply` 1 base unit of any `no_seize`-listed spoke asset. Every subsequent `liquidate` call plans a nonzero seizure on that leg, hits the flag check, and reverts — the account is unliquidatable at any health factor. The permissionless fallback `clean_bad_debt` does not help: it requires `total_collateral <= BAD_DEBT_USD_THRESHOLD` ($5), which a real-collateral account never satisfies — mirroring the original bug where disabled pools made the aggressive-mode threshold unreachable in practice. [3](#0-2) [4](#0-3) 

### Impact Explanation
Medium/High: an underwater account becomes immune to liquidation by holding one dust `no_seize` leg. Its debt keeps accruing while no liquidator can act, and the account sits permanently above the $5 permissionless `clean_bad_debt` dust cap, so the only escape is the owner-gated `force_socialize_bad_debt` runbook. Until governance intervenes, interest accrues into unbacked debt and the position converts into protocol bad debt written off against the market's supply index — i.e., supplier losses / protocol insolvency. [5](#0-4) 

### Likelihood Explanation
Requires a spoke asset listed with `no_seize = true` (an incident-response flag governance can set on any listed collateral while leaving supply open) and a borrower who holds or acquires a dust amount of it. Once set, every `liquidate` against that account reverts deterministically; liquidators cannot work around it because the plan is always computed over all nonzero legs, and `clean_bad_debt` is blocked by the dust cap on any account with meaningful collateral. The trigger condition (a `no_seize` listing) is precisely the scenario in which liquidations matter most.

### Recommendation
Skip `no_seize` legs from the seizure plan instead of aborting the whole liquidation — seize only the seizable legs pro-rata (the flag then converts a leg into "excluded from the denominator"), or apply the veto only when the flagged leg exceeds a materiality threshold rather than any nonzero amount. Alternatively, gate `supply`/credit of `no_seize` assets so a borrower cannot add the poison leg after the flag is set.

### Proof of Concept
1. Governance sets `no_seize = true` on a listed collateral asset (e.g., during an incident on asset `X`); supply remains open because entry rejects only `paused`/`frozen`.
2. Alice has collateral `C` and debt `D` approaching `HF < 1`. She calls `supply(X, 1 base unit)` — one supply slot of a permitted asset; `POSITION_LIMIT_MAX = 5` leaves room.
3. X's price falls / C's price falls; Alice's account crosses `HF < 1`.
4. Any liquidator calls `liquidate(liquidator, alice_account, payments, SeizeMode::Transfer)`. The plan distributes seizure over all nonzero collateral legs, including the dust X leg; the `no_seize` check on that leg reverts the whole call (documented in INV-HALT-02 and the `no_seize` revert scenario `skills/evals/scenarios/xoxno-lending-liquidations/03-revert-318-no-seize.json`).
5. `clean_bad_debt(caller, alice_account)` reverts with `CannotCleanBadDebt` because `total_collateral > $5` while `total_debt > total_collateral` eventually holds — the account is stuck until owner-only `force_socialize_bad_debt`, with debt and interest accruing unbacked in the interim.

### Citations

**File:** docs/reference/invariants.md (L495-504)
```markdown
### INV-HALT-02 — Frozen, paused, and no_seize gate different legs

Listing flags act independently: entry rejects `paused` and `frozen`; user
exits and liquidation repayment reject `paused`; ordinary liquidation seizure
rejects only `no_seize`. Missing listings pass the flag helper, while entry and
new Credit receiver assets separately require a listing.

Nonzero `no_seize` collateral can block the whole proportional liquidation,
even if supplied after the flag is set. Zero-token planned seizure legs are
omitted before that check. Standalone bad-debt cleanup bypasses these flags.
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-235)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L245-249)
```rust
/// Socializes debt exceeding collateral without a dust cap, outside flash loans.
pub(crate) fn process_force_socialize_bad_debt(env: &Env, account_id: u64) {
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```
