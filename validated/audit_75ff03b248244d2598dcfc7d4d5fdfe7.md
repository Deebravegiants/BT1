### Title
Bad-debt supply-index floor resurrecting wiped supply claims drains later depositors — use-after-free of socialized positions - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes bad debt by scaling the supply index down, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (`RAY / 1000`) instead of driving supplier claims to zero. When bad debt meets or exceeds total supplied value, the wipeout is "freed" economically but the scaled share balances survive with a positive floor index — a stale, already-written-down claim that still unscales to real token value. Any subsequent deposit recapitalizes those dead claims, letting the wiped-out holders withdraw cash contributed by new suppliers.

### Finding Description
- `apply_bad_debt_to_supply_index` computes `new_supply_index = supply_index * (1 - capped_bad_debt / total_supplied_value)` and applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))` (contracts/pool/src/interest.rs:73-89). When `bad_debt >= total_supplied_value`, `remaining == 0`, so the factor is zero — but the floor forces the index to `RAY/1000`, not zero.
- Crucially, `supplied` (total scaled shares, including the wiped positions' shares) is unchanged. Every pre-wipeout position's `scaled_amount` still unscales via `unscale_supply_floor`/`resolve_withdrawal` to `scaled * RAY/1000` — a positive claim.
- The repo's own unit test demonstrates the hole: `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (contracts/pool/tests/interest.rs:372-427) shows `stranded > 0`, a fresh deposit minted at the floored index, then the stale position's `resolve_withdrawal(i128::MAX, old_scaled)` paying `gross == fresh_cash`, draining exactly the fresh deposit. The test explicitly notes the invariant is "only masked by require_reserves" — i.e., nothing caps the claim, only available cash does.
- Reachability: an unprivileged account accumulates debt that becomes bad debt (price move or dust positions), `clean_bad_debt` / liquidation bad-debt path calls the pool write-down, index clamps at the floor. The wiped suppliers (any unprivileged address holding pre-wipeout shares) later call `withdraw` on the controller, which reaches `ops::withdraw::accounting` → `resolve_withdrawal` → `require_reserves` → `debit_cash`/`transfer_out`. As soon as any new supplier deposits into the same (hub, asset) market, cash exists and the dead claims pay out first-come-first-served.

### Impact Explanation
Theft of user funds / protocol insolvency. A total bad-debt wipeout should zero supplier claims; instead every wiped position retains `scaled * RAY/1000` of claim. The first wiped holder to withdraw after fresh liquidity enters the market walks away with up to the entire new deposit, while the fresh supplier's own claim (minted at the same floored index for exactly its deposit) becomes unbacked — `cash < fresh_claim`. This is direct value transfer from later depositors to earlier wiped positions, unbounded except by `supplied_total * RAY/1000`.

### Likelihood Explanation
Requires a full (or near-full) bad-debt wipeout in a market — achievable via `clean_bad_debt` on a deeply underwater position, which the protocol explicitly supports as a permissionless cleanup path. After the wipeout, only one new supply is needed to arm the drain; any wiped holder (or the attacker who owns them) can withdraw immediately. Ordering is attacker-controllable: the same actor can hold the wiped shares, trigger cleanup, watch for fresh deposits, and withdraw.

### Recommendation
In `apply_bad_debt_to_supply_index`, when `capped == total_supplied_value` (full wipeout), reset the market consistently: either set `supply_index` to a true zero-claim representation and burn/zero `supplied`, or mint no resurrection value — e.g., track an explicit `wiped` flag and treat remaining `supplied` shares as claimless. At minimum, gate withdrawals on `supply_index > floor` or reconcile `supplied` so that `supplied * floor_index` cannot exceed accounted cash obligations. Alternatively, remove the `SUPPLY_INDEX_FLOOR_RAW` clamp on the write-down path and handle the zero-index case in share math (reject new supply until re-seeded).

### Proof of Concept
The shipped unit test is the PoC: `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (contracts/pool/tests/interest.rs:372-427):

```rust
apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY));
// supply_index clamps UP to RAY/1000; old_scaled still unscales to > 0
let stranded = cache.unscale_supply_floor(old_scaled); // stranded > 0

// fresh victim deposits
let fresh_scaled = cache.calculate_scaled_supply(fresh_cash);
cache.mint_supply(fresh_scaled);
cache.credit_cash(fresh_cash);

// wiped holder withdraws: passes require_reserves because fresh cash exists
let (burn, gross) = cache.resolve_withdrawal(i128::MAX, old_scaled);
cache.require_reserves(gross);
cache.burn_supply(burn);
cache.debit_cash(gross);
// gross == fresh_cash; cache.cash() < fresh_claim → victim's deposit stolen
```

Production path: `controller.clean_bad_debt` → pool seize/settle → `apply_bad_debt_to_supply_index`; then victim calls `supply`; then attacker calls `withdraw(amount = i128::MAX)` → `ops::withdraw::accounting` → `gate_and_debit` → `transfer_out`.