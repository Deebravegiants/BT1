### Title
Attacker-Sized HyperSwap Pre-Seed Reserves Can Overflow `Math.mulDiv` in `Bonding._noFeeSwapInput`, Permanently Bricking `finalizeGraduation` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._noFeeSwapInput` computes the closed-form rebalance-swap input as `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` followed by `Math.sqrt`. The reserves fed into this formula are read live from the attacker-controllable HyperSwap V2 pair (`_seedRebalancing`'s `reserveToken`/`reserveLT`, sourced from `pair.getReserves()` after a front-run `pair.mint`), while `targetN`/`targetD` are the protocol-computed `tokensForLP`/`ltFromPair` cached at phase-1 (`_enterGraduating`). The contract's own natspec on `_noFeeSwapInput` admits: *"Constructed adversarial inputs that violate this would revert rather than silently truncate."* Because `reserveIn`/`reserveOut` are attacker-set (via a self-funded `pair.mint` before `finalizeGraduation`), and `targetD` (`tokensForLP` or `ltFromPair`) can be small relative to a maximally-skewed pre-seed, `Math.mulDiv`'s internal division can overflow `uint256`, causing the call to revert.

### Finding Description
The hostile-pre-seed defense in `Bonding._seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput` is explicitly documented as needing to "never revert under any pre-seed shape" [1](#0-0) , because a revert here permanently bricks `finalizeGraduation`, which is the only path out of the `Graduating` lifecycle state.

`_noFeeSwapInput`'s discriminant is `reserveIn * reserveOut * targetN / targetD`, computed via OZ `Math.mulDiv` to survive the intermediate 512-bit product, but the *final* division result must still fit in `uint256` or `Math.mulDiv` reverts [2](#0-1) . The function's own natspec concedes this is caller-dependent: *"Call sites must keep that invariant... Constructed adversarial inputs that violate this would revert rather than silently truncate, which is the correct failure mode."* [3](#0-2) 

`reserveIn`/`reserveOut` come straight from `IUniswapV2Pair(pair).getReserves()` on a pair the attacker front-ran and self-seeded via `pair.mint(attacker)` before phase 2 runs [4](#0-3) . `targetN`/`targetD` are the cached `tokensForLP`/`ltFromPair` — bounded above by `LP_RESERVE` (250M tokens) and by the real LT raised on the curve, which is a fixed multiple of the launch-time virtual LT reserve (`3× virtualLtReserve`, itself `VIRTUAL_LIQUIDITY_USD × 1e18 / exchangeRate`). When the paired LT's `exchangeRate()` is very large (a heavily-appreciated leveraged token, entirely plausible for BounceTech LTs over time), `virtualLtReserve` — and hence `ltFromPair` — becomes small in LT-wei terms, shrinking `targetD` toward the low end while `reserveIn`/`reserveOut` (attacker-funded, bounded only by `Token.TOTAL_SUPPLY()` on the token leg and by the attacker's own LT holdings on the LT leg) can be pushed large. This combination can push the discriminant past `2^256`, causing `Math.mulDiv` to revert instead of returning a value — exactly the "specially crafted input causing an arithmetic operator to crash" bug class in the referenced CVE, mapped onto alt.fun's own graduation-seeding math.

The test suite only validates the "realistic-max" case by deliberately picking `targetD` large enough to keep the discriminant in range (`test_overflowSafety_atRealisticMax` in `test/NoFeeSwapInput.t.sol`, lines 176-183), and never exercises a low-`targetD` / high-`reserveIn·reserveOut` combination — i.e. exactly the regime where the acknowledged revert risk lives.

### Impact Explanation
A reverted `_noFeeSwapInput` propagates unguarded through `_pairRebalance` → `_seedRebalancing` → `_seedUniswapV2Direct` → `finalizeGraduation`, which has no try/catch around this call. Since phase 1 (`_enterGraduating`) has already drained the curve's real LT and burned the curve tokens, and phase 2 (`finalizeGraduation`) is the only path that can flip `Graduating → Graduated`, a permanently-reverting `finalizeGraduation` leaves:
- All curve-raised LT and the 250M `LP_RESERVE` tokens permanently stuck in `Bonding`.
- Every trader/holder of the token permanently unable to exit (trading is frozen in `Graduating`, and there is no path back to `Curve`).
- The LP that should have been locked via `LPLock.recordLock` never created.

This is a permanent freeze of trader, creator, and LP-bound funds for that token — one of the explicitly in-scope high-severity impacts.

### Likelihood Explanation
Reaching the vulnerable state requires only unprivileged, permissionless actions: front-running `factory.createPair(token, lt)`, funding the pair with attacker-owned TOKEN/LT and calling `pair.mint(attacker)` before `finalizeGraduation` runs — a scenario the protocol's own documentation treats as the primary threat model for this code path. The specific numeric conditions needed to trip the `Math.mulDiv` overflow require a token whose paired LT has appreciated enough to shrink `virtualLtReserve`/`ltFromPair`, combined with the attacker funding a sufficiently large pre-seed (bounded above by `Token.TOTAL_SUPPLY()` on the token leg, and by the attacker's own LT capital on the LT leg). This makes it a real but non-trivial-capital attack, and the exact reachable numeric window versus the practical `uint112` V2 reserve cap requires on-chain/fuzzing verification that could not be fully confirmed from static review alone.

### Recommendation
- Wrap the `Math.mulDiv` discriminant computation in `_noFeeSwapInput` with an explicit pre-check (e.g., compare `reserveIn`/`reserveOut`/`targetN`/`targetD` against a safe bound, or use a saturating/capped variant) so that adversarial inputs return a capped `s` (e.g., `maxSwap`) instead of reverting.
- Alternatively, wrap the `_pairRebalance` call in `_seedRebalancing` with a low-level call/try-catch that falls back to `_seedDirectMint` on any revert from the rebalance leg, preserving the "must never revert" brick-resistance property end-to-end.
- Add fuzz coverage in `test/NoFeeSwapInput.t.sol` that sweeps `targetD` down toward small values while `reserveIn`/`reserveOut` are pushed toward realistic attacker-fundable maxima, to confirm the discriminant never actually overflows in production's achievable input space (or to prove it can, motivating the fix above).

### Proof of Concept
1. Launch a token whose paired LT has a very large `exchangeRate()` (e.g., a long-lived, heavily-appreciated BounceTech LT), so `virtualLtReserve = VIRTUAL_LIQUIDITY_USD × 1e18 / exchangeRate` is tiny and `ltFromPair ≈ 3 × virtualLtReserve` is likewise tiny once the curve graduates.
2. Buy enough of the curve to trigger `_enterGraduating` (phase 1), caching a small `ltFromPair` and a `tokensForLP` up to `LP_RESERVE` (250M tokens).
3. Front-run `factory.createPair(token, lt)`, acquire a large TOKEN balance (up to `Token.TOTAL_SUPPLY()`) and a large LT balance, `transfer` both to the pair, and call `pair.mint(attacker)` to set `reserveToken`/`reserveLT` far above the cached `tokensForLP`/`ltFromPair` ratio's safe envelope.
4. Call the permissionless `Bonding.finalizeGraduation(token)`. `_seedRebalancing` computes `reserveToken * ltFromPair` vs `reserveLT * tokensForLP` to pick a rebalance direction and calls `_pairRebalance`, which calls `_noFeeSwapInput(reserveIn, reserveOut, targetN, targetD, maxSwap)` with the attacker-inflated `reserveIn`/`reserveOut` and the small cached `targetD`; `Math.mulDiv` reverts, `finalizeGraduation` reverts, and the token is permanently stuck in `Graduating`.

Confirming the exact numeric feasibility (i.e., whether realistic `uint112`-bounded reserves and achievable `ltFromPair` values actually cross the `2^256` boundary in practice) requires on-chain fuzzing/execution beyond static review; this should be validated with a Foundry fuzz test extending `test/NoFeeSwapInput.t.sol` before remediation is scoped.

### Citations

**File:** packages/contracts/AGENTS.md (L191-193)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:
```

**File:** packages/contracts/src/Bonding.sol (L1279-1289)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
```

**File:** packages/contracts/src/Bonding.sol (L1488-1522)
```text
    /// @dev Smallest swap input that drives the pool's reserve ratio
    ///      `(reserveIn + s) / (reserveOut - out)` to `targetN/targetD`
    ///      under the no-fee constant-product model:
    ///        `(reserveIn + s)² = reserveIn * reserveOut * targetN/targetD`
    ///      ⇒ `s = sqrt(reserveIn * reserveOut * targetN/targetD) - reserveIn`,
    ///      capped at `maxSwap`. The actual swap is fee-charging (the pair's
    ///      live fee), so the post-swap ratio drifts from the target by the
    ///      fee; the balanced-subset deposit absorbs the residual without
    ///      donating.
    ///
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```
