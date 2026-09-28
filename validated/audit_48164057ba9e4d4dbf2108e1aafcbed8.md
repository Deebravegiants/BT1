### Title
Bad-debt write-down clamps the supply index to a nonzero floor, leaving wiped-out suppliers a "phantom" share claim that drains future depositors' cash - ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary

`apply_bad_debt_to_supply_index` socializes bad debt by scaling `supply_index` down in proportion to the unrecovered loss, but then clamps the result **up** to `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`) instead of letting it reach zero. When a market's bad debt equals or exceeds the total supplied value, every supplier's `scaled_amount` still unscales to a positive claim at the floored index. Those stale claims survive the wipeout and can later be withdrawn against cash deposited by *new* suppliers — a classic use-after-free analogue: a written-down-to-zero resource (the supply index / the value backing the shares) continues to be dereferenced by the old share balances. [1](#0-0) [2](#0-1) 

### Finding Description

In `contracts/pool/src/interest.rs::apply_bad_debt_to_supply_index` (lines 73–89):

```rust
let capped = bad_debt.min(total_supplied_value);
let remaining = total_supplied_value.checked_sub(cache.env(), capped);
let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
let new_supply_index = cache.supply_index().mul_floor(cache.env(), reduction_factor);
cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

When `bad_debt >= total_supplied_value`, `capped == total_supplied_value`, `remaining == 0`, `reduction_factor == 0`, and `new_supply_index == 0` — but `.max(SUPPLY_INDEX_FLOOR_RAW)` resurrects the index to `RAY/1000`. Every existing `scaled_amount` then still unscales to `scaled * 1e24 / RAY` > 0 units of claim.

The pool's own regression test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-427`) proves the exploit mechanics end-to-end on the raw cache: after the clamp, `unscale_supply_floor(old_scaled) > 0`, a fresh deposit of exactly that amount is credited, and `resolve_withdrawal(i128::MAX, old_scaled)` pays the wiped-out holder `gross == fresh_cash`, leaving `cash < fresh_claim` — the new supplier can no longer be made whole.

The path is reachable in production:

- `clean_bad_debt` / `check_bad_debt_after_liquidation` (permissionless keeper surface per the threat model) drives `apply_bad_debt_to_supply_index` through the pool.
- `withdraw` is gated by `require_reserves` (cash ≥ payout), not by `require_backed_market` — `require_backed_market` only fires on `supply` (`contracts/pool/README.md` guards table: `require_backed_market` fires on `supply` only; `require_reserves` fires on `withdraw`). Once any later depositor (or a `recapitalize` injection, or fee revenue) puts cash into the wiped market, the phantom claim passes `require_reserves` and pays out real tokens. [3](#0-2) [4](#0-3) 

Notably, `supply_index` is documented as non-monotone precisely because of this write-down, and the floor exists only "to avoid a zero index" — but zeroing the index is the *correct* terminal state for a fully wiped market; the floor converts a correct zero into a live residual claim.

### Impact Explanation

**Theft of user funds / protocol insolvency.** Holders of supply shares in a market that suffered a ≥100% bad-debt write-down retain a positive claim valued at `scaled × 10^24 / 10^27 = scaled/1000` RAY-units. Any subsequent cash entering the market — new supplier deposits, `recapitalize` (which is permissionless and adds cash without minting shares), interest-bearing inflows, or accidental direct token transfers to the pool — becomes withdrawable by the wiped-out shareholders ahead of the new suppliers' claims. The new suppliers are left with shares whose backing was consumed by the phantom claims: a direct transfer of value from future depositors to former (economically zeroed) ones.

An attacker can also be the wiped-out shareholder themself: supply and borrow in a thin/hub market they dominate, let the position go to bad debt (e.g., via a price move on a volatile collateral they supplied), trigger `clean_bad_debt`, and keep the floored-index shares as a salvage claim against anyone who later touches that market.

### Likelihood Explanation

Requires a market to hit a full write-down (bad debt ≥ total supplied value), which is an extreme but real state — it is precisely the state `apply_bad_debt_to_supply_index` exists to handle, and the code path, the floor clamp, and the payout mechanics are all in production code and exercised by the dedicated test. Once reached, no privileged action is needed to harvest the residual claim: `withdraw` is permissionless for the position owner and only needs `cash ≥ payout`. Attacker positioning requires being a supplier in a market that goes fully insolvent — feasible in thin or newly listed markets, or for the attacker who is both the dominant supplier and the defaulting borrower. Severity is bounded by `1/1000` of the original supply value and by how much fresh cash enters the dead market afterward, so the practical ceiling is moderate — Medium/High depending on market size.

### Recommendation

When `bad_debt >= total_supplied_value`, the market's supply side is economically dead and the index should be allowed to reach zero (or the market should be explicitly halted). Options:

- Remove the `.max(SUPPLY_INDEX_FLOOR_RAW)` clamp when `remaining == 0`, or clamp only the *non-zero* case (`if remaining > 0 { max(floor) } else { 0 }`), accepting that `scaled × 0` correctly unscales to zero.
- Alternatively, on a ≥100% write-down, burn/void all outstanding supply shares (or mark the market seized-for-bad-debt) so no residual `scaled_amount` can later unscale.
- If the floor must be kept for numerical reasons, gate withdrawals on the market not being in a wiped state (e.g., a flag set when `reduction_factor == 0`), rather than relying on `require_reserves` to accidentally mask it.

### Proof of Concept

The protocol's own test demonstrates the mechanics verbatim (`contracts/pool/tests/interest.rs:372-427`):

```rust
// 1. Supplier holds old_scaled = 1000 RAY shares at supply_index = RAY.
// 2. Bad debt of 5000 RAY (>= total supplied value) is applied.
apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY));
assert_eq!(cache.supply_index().raw(), SUPPLY_INDEX_FLOOR_RAW); // clamped UP, not zeroed

// 3. The wiped position still has a positive claim.
let stranded = cache.unscale_supply_floor(old_scaled);
assert!(stranded > 0); // phantom claim

// 4. A fresh supplier deposits `stranded` tokens -> cash credited.
cache.mint_supply(cache.calculate_scaled_supply(stranded));
cache.credit_cash(stranded);

// 5. Old (wiped) supplier withdraws; require_reserves passes because cash exists.
let (burn, gross) = cache.resolve_withdrawal(i128::MAX, old_scaled);
cache.require_reserves(gross);
cache.burn_supply(burn);
cache.debit_cash(gross);
// gross == fresh deposit; pool can no longer cover the fresh supplier's claim.
```

On-chain sequence for an unprivileged attacker:

1. Supply `S` of token T in a thin market; borrow against other collateral (or be the borrower whose collateral crashes).
2. Let the debt become bad debt (price move or abandoned position), then call the permissionless `clean_bad_debt`/liquidation path so `apply_bad_debt_to_supply_index` runs with `bad_debt >= supplied × supply_index` — the index is clamped to `SUPPLY_INDEX_FLOOR_RAW` and the attacker's `scaled_amount` is untouched.
3. Wait for any new `supply` (or donate/recapitalize cash) into the market.
4. Call `withdraw` on the dust-valued but nonzero position; `require_reserves` is satisfied by the fresh cash and the phantom claim pays out real tokens, stealing from the new supplier.

### Citations

**File:** contracts/pool/src/interest.rs (L73-89)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
}
```

**File:** contracts/pool/tests/interest.rs (L372-427)
```rust
#[test]
fn test_raw_cache_floor_clamp_strands_claim_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let old_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: old_scaled_raw,
            borrowed: 0,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let old_scaled = Ray::from(old_scaled_raw);

        apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout clamps supply_index UP to RAY/1000 instead of resetting shares to 0",
        );

        let stranded = cache.unscale_supply_floor(old_scaled);
        assert!(stranded > 0, "floor clamp leaves S_old a phantom claim");
        assert_eq!(
            cache.cash(),
            0,
            "no cash yet: invariant only masked by require_reserves"
        );

        let fresh_cash = stranded;
        let fresh_scaled = cache.calculate_scaled_supply(fresh_cash);
        cache.mint_supply(fresh_scaled);
        cache.credit_cash(fresh_cash);

        let fresh_claim = cache.unscale_supply_floor(fresh_scaled);
        assert_eq!(
            fresh_claim, fresh_cash,
            "fresh supplier's claim equals deposit"
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, old_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded wiped position pays out real tokens");
        assert_eq!(gross, fresh_cash, "S_old drains exactly the fresh deposit");
        assert!(
            cache.cash() < fresh_claim,
            "pool cash ({}) can no longer cover fresh supplier claim ({}): funds lost",
            cache.cash(),
            fresh_claim,
        );
    });
```

**File:** contracts/pool/src/cache/scale.rs (L97-105)
```rust
    pub(crate) fn resolve_withdrawal(&self, amount: i128, pos_scaled: Ray) -> (Ray, i128) {
        resolve_withdrawal(
            &self.env,
            amount,
            pos_scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/pool/README.md (L186-205)
```markdown

`borrow_index` only ever grows — `update_borrow_index` is its sole writer.
`supply_index` is **not** monotone: `apply_bad_debt_to_supply_index` scales it
down to socialize a loss across suppliers, floored at `SUPPLY_INDEX_FLOOR_RAW`
(`RAY/1000`). Anything caching an index must tolerate a decrease.

**`revenue <= supplied`** — asserted in
`cache/shares.rs::require_revenue_backed`.

Protocol revenue is not a side pot; it is supply shares the protocol owns. Two
paths exist and the distinction is load-bearing:

| Path | Effect | Used by |
| --- | --- | --- |
| `accrue_revenue` | `revenue += s` **and** `supplied += s` — **mints** shares | interest, flash, liquidation and strategy fees |
| `absorb_supply_as_revenue` | `revenue += s` only — **reassigns** existing shares | `seize_positions`, deposit side |

Seizing a deposit moves ownership of shares already counted in `supplied`, so
`supplied` must not change. Minting for interest creates new claims, so it must.
Swapping these corrupts the accounting silently.
```
