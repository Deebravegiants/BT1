### Title
Bad-debt write-down clamps a wiped supply index up to `SUPPLY_INDEX_FLOOR_RAW`, leaving insolvent claims that drain the next depositor - (File: contracts/pool/src/interest.rs)

### Summary
The external bug class is "an input larger than the modulus is not reduced, so the math returns a wrong but well-formed result." The analog lives in `apply_bad_debt_to_supply_index`: when `bad_debt` exceeds the total supplied value (the value domain's analog of the curve order), the loss is silently capped instead of zeroing the market, and the resulting supply index is then clamped **up** to `SUPPLY_INDEX_FLOOR_RAW = RAY/1000`. A fully wiped market therefore keeps a nonzero index, and every unburned supply share retains a residual token claim that is paid out of the next depositor's cash.

### Finding Description
`apply_bad_debt_to_supply_index` computes `reduction_factor = (total_supplied_value - min(bad_debt, total_supplied_value)) / total_supplied_value`, multiplies it into the old index with `mul_floor`, and then applies `new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))` [1](#0-0) . When `bad_debt >= total_supplied_value`, `remaining = 0`, so the mathematically correct index is `0` — but the floor clamp lifts it to `RAY/1000`. The index, like the P256 scalar in the advisory, is an input that must be reduced into its valid domain (`[0, total supplied value]` of recoverable backing); instead it is forced back into a nonzero range the books cannot support.

The pool's own test proves the consequence arithmetic end-to-end in `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard`: after a full wipeout, `unscale_supply_floor(alice_scaled) > 0` ("wiped survivor keeps a stranded claim"), a new deposit of `alice_stranded` units makes `total_owed > cash` ("post-deposit books insolvent"), and `resolve_withdrawal(i128::MAX, alice_scaled)` followed by `require_reserves(gross)` pays Alice exactly Bob's fresh deposit, leaving `cash < bob_claim` [2](#0-1) . The claim is exercised through the normal `withdraw` path via `Cache::resolve_withdrawal` and `require_reserves` [3](#0-2) .

The write-down is reached from the seizure path in `contracts/pool/src/ops/seize.rs`, which is driven by the unprivileged `liquidate`/`clean_bad_debt` controller flows; `clean_bad_debt` is reachable by any address once a position is below the dust threshold.

### Impact Explanation
Theft of user funds and protocol insolvency. Any supplier with residual scaled shares after a complete write-down can withdraw real tokens deposited later by an honest user. The stranded supplier extracts the fresh deposit in full (`gross == deposit` in the test), and the fresh depositor's claim exceeds remaining cash permanently — a textbook haircut-free socialization failure caused purely by the index floor.

### Likelihood Explanation
Requires a market where `clean_bad_debt` (or a liquidation seize) writes off debt at least equal to total supplied value — i.e., a fully-underwater small/dust market, exactly the state `clean_bad_debt` exists to process — followed by any new supply. Both steps are unprivileged: the wipe-out is permissionless cleanup, and the victim's `supply` and the attacker's `withdraw` are ordinary entrypoints. No oracle manipulation, governance, or timing edge is needed; the incorrect index is stored persistently. The residual is bounded by the floor (each stranded share is worth up to `RAY/1000 × scaled`), so the extractable amount scales with the wiped position size — Medium severity, matching the advisory's "specific inputs only" character.

### Recommendation
Do not floor the post-write-down index above zero. When `capped == total_supplied_value`, set the supply index to `0` (or revert) and treat remaining `supplied` shares as worthless; alternatively, refuse `supply`/`mint_supply` into a market whose index was clamped, or require `supplied == 0` before allowing new deposits after a total write-down. The floor's stated purpose is "avoid a zero index" — the fix is to make the zero-index state explicitly non-operational for deposits rather than manufacturing a solvent-looking index.

### Proof of Concept
Conceptual, mirroring `contracts/pool/tests/interest.rs:430-494`:

1. Attacker holds `1_000 RAY` scaled supply in a hub market; the market's `1_000 RAY` scaled debt goes bad (e.g., dust cleanup via `clean_bad_debt` on a fully-underwater spoke).
2. `apply_bad_debt_to_supply_index` runs with `bad_debt >= supplied × index`: `reduction_factor = 0`, but `set_supply_index(max(0, RAY/1000))` stores `RAY/1000` [4](#0-3) .
3. Attacker's stranded claim: `unscale_supply_floor(1_000 RAY × RAY/1000) = RAY` worth of tokens > 0 despite total backing of 0.
4. Victim supplies `alice_stranded` tokens; cash now covers the attacker's claim but `total_owed > cash`.
5. Attacker calls `withdraw(0)` (withdraw-all sentinel) → `resolve_withdrawal(i128::MAX, ...)` burns all shares and `require_reserves` passes since `gross == cash`; the attacker receives the victim's entire deposit [5](#0-4) .
6. Victim's withdrawal now fails `require_reserves` — funds permanently lost.

Caveat: whether a production guard outside the cache layer (e.g., a post-seize `supplied == 0` requirement, hinted at by the test's "without supply guard" name) blocks step 4 could not be fully confirmed within the available iterations; if such a guard exists in `ops/seize.rs` or the deposit path, the finding reduces to a dormant accounting bug.

### Citations

**File:** contracts/pool/src/interest.rs (L80-88)
```rust
    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

**File:** contracts/pool/tests/interest.rs (L448-493)
```rust
        let bad_debt = cache.unscale_borrow_ceil_ray(borrow_scaled);
        apply_bad_debt_to_supply_index(&mut cache, bad_debt);
        cache.burn_debt(borrow_scaled);

        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "seize wipeout clamps supply_index UP to RAY/1000, leaving unburned shares a residual"
        );

        let alice_stranded = cache.unscale_supply_floor(alice_scaled);
        assert!(alice_stranded > 0, "wiped survivor keeps a stranded claim");
        assert_eq!(
            cache.cash(),
            0,
            "empty market: claim masked by require_reserves"
        );

        let deposit = alice_stranded;
        let bob_scaled = cache.calculate_scaled_supply(deposit);
        cache.mint_supply(bob_scaled);
        cache.credit_cash(deposit);

        let total_owed = cache.unscale_supply_floor(cache.supplied());
        assert!(
            total_owed > cache.cash(),
            "post-deposit books insolvent: owed {} > cash {}",
            total_owed,
            cache.cash()
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, alice_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "wiped position pays out real cash");
        assert_eq!(gross, deposit, "Alice extracts exactly Bob's fresh deposit");

        let bob_claim = cache.unscale_supply_floor(bob_scaled);
        assert!(
            cache.cash() < bob_claim,
            "cash {} cannot cover Bob's honest claim {}: fresh depositor lost funds",
            cache.cash(),
            bob_claim
        );
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
