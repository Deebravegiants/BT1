## Analysis

CVE‑2024‑20380 is a DoS caused by an unhandled edge case at a C↔Rust FFI boundary: attacker-supplied input reaches a foreign-interface computation that the caller assumed would never fail, and it crashes the process instead of failing gracefully. The alt.fun analog of "an attacker-controlled value crossing into a boundary computation that the code assumes is always safe, but which can be driven into a revert/crash by adversarial magnitudes" is the `Math.mulDiv` call inside `Bonding._noFeeSwapInput`.

### Title
Attacker-inflated HyperSwap pre-seed reserves can overflow `Math.mulDiv` in `_noFeeSwapInput`, permanently bricking `finalizeGraduation` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`_noFeeSwapInput` computes `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` where `reserveIn`/`reserveOut` are the *live* HyperSwap V2 pair reserves and `targetN`/`targetD` are the graduation's cached `(ltFromPair, tokensForLP)` pair [1](#0-0) . The pair reserves are attacker-controlled up to `uint112` max via the permissionless hostile-pre-seed path (`factory.createPair` + `transfer` + `pair.mint`) documented in the codebase's own pre-seed-defense writeup [2](#0-1) . The natspec on `_noFeeSwapInput` itself acknowledges the overflow can happen and merely asserts it is unreachable because `tokensForLP`/`ltFromPair` are supply-bounded — but that reasoning ignores that either of those two values can be driven *small* (not large) while the pre-seed reserves are driven *large*, which is exactly the regime that triggers `mulDiv`'s revert-on-overflow guard [3](#0-2) .

### Finding Description
`_seedRebalancing` picks the swap direction and passes `(reserveIn, reserveOut, targetN, targetD)` straight from live pair state and the cached graduation amounts into `_pairRebalance` → `_noFeeSwapInput`: [4](#0-3) 

- `reserveToken`/`reserveLT` come from `IUniswapV2Pair(pair).getReserves()` — a `uint112` pair whose owner is whoever front-runs `factory.createPair` + `pair.mint`, i.e. fully attacker-controlled up to `type(uint112).max` (~5.19e33) each, exactly the pre-seed exploit the codebase's own AGENTS.md documents in detail.
- `tokensForLP` is proportional to `sold` on the bonding curve (`tokensForLP(sold) = sold·(S−sold)/S`), and `ltFromPair` is the real LT raised. Both are cached at the *end of phase 1* (`_enterGraduating`) and can be made arbitrarily small: the dual graduation trigger fires on `canGraduate` returning true purely from `exchangeRate()` appreciation of the external LT, with no floor on how little curve `sold` or real LT is required at that moment (see `docs/contracts-scope.md`'s dual-trigger description) [5](#0-4) .

`_noFeeSwapInput`'s own comment concedes the failure mode exists and only "reasons away" the large-numerator case, not the small-denominator / large-reserve case: [6](#0-5) 

When `reserveIn·reserveOut·targetN / targetD` doesn't fit in `uint256`, OZ's `Math.mulDiv` reverts. Because `finalizeGraduation` calls this transitively with no `try/catch`, the revert propagates all the way up and `finalizeGraduation` can never succeed for that token — while the attacker's hostile pre-seed persists on-chain forever (nothing else can reduce those reserves), the brick is permanent, not merely griefed-once.

### Impact Explanation
Once `finalizeGraduation` is permanently unable to complete for a token:
- All curve-raised real LT and the 250M reserved tokens parked in `Bonding` for that graduation (`p.tokensForLP`, `p.ltFromPair`, plus whatever protectedLT/dust is present) are frozen forever — `Bonding` has no owner-level rescue path for a stuck `Graduating` token.
- Every holder is permanently locked out: `Lifecycle.Graduating` blocks both `buy` and `sell` with `TokenIsGraduating` [7](#0-6) , and there is no path back to `Curve` or forward to `Graduated`.
- This directly violates the codebase's own stated top-priority invariant that "`_seedUniswapV2Direct` MUST never revert under any pre-seed shape" and that "a brick locks every holder in `Graduating` forever" [8](#0-7)  — this is a permanent freezing of trader, creator and (implicitly) LP funds, satisfying the "Validate" bar.

### Likelihood Explanation
Both preconditions are independently permissionless and unprivileged:
1. **Pre-seeding with maximal reserves.** `factory.createPair` + `IERC20.transfer(pair, X)` + `pair.mint(attacker)` are all open calls; an attacker can push reserves close to the `uint112` ceiling on both sides at any hostile ratio, exactly the primitive the codebase's own pre-seed-defense document walks through [9](#0-8) .
2. **Shrinking `tokensForLP`/`ltFromPair`.** A token graduating early — with little of the curve `sold` and/or little real LT raised — because the paired LT's `exchangeRate()` appreciated is an explicitly designed, expected path ("LT appreciation pushed the curve past the USD threshold"), reachable by anyone who can move (or wait for) the underlying leveraged token's price, or simply by choosing/awaiting a volatile LT pairing and calling `Bonding.triggerGraduation` at the opportune moment.

Combining the two requires no special privilege, no upgrade, and no bug inside BounceTech or HyperSwap themselves — only ordinary permissionless calls documented as reachable elsewhere in this same file.

### Recommendation
- Bound `reserveIn`/`reserveOut` (or the intermediate product) before calling `Math.mulDiv`, e.g. clamp/cap the pre-seed reserves considered by the rebalance to a sane multiple of `tokensForLP`/`ltFromPair` rather than passing raw `uint112` values straight through.
- Wrap the `_pairRebalance` call (or `_noFeeSwapInput` specifically) in a `try/catch`-style guard (a low-level call, since `_noFeeSwapInput` is `internal pure` this means restructuring it to a bounded-safe formula) so an overflow falls back to `_seedDirectMint` the same way the existing `s == 0` / `expectedOut == 0` cases already do, preserving the brick-resistance contract the file promises.
- Add a fuzz/unit test in `NoFeeSwapInput.t.sol` that exercises `uint112`-max reserves against a *small* `targetD` (not just a small `targetN`), which is the actual overflow-triggering shape, to close the gap the current natspec's reasoning misses.

### Proof of Concept
1. Launch a token and, before any real curve buys accumulate much `sold`, cause `canGraduate` to flip true purely via the paired LT's `exchangeRate()` appreciating (permissionless — this is the documented "rate-pump-only" ripening path), then call `Bonding.triggerGraduation`. This yields a `PendingGraduation` with a very small `tokensForLP` (and/or `ltFromPair`), pinned in `_enterGraduating`.
2. Before `finalizeGraduation` lands, front-run: `factory.createPair(token, lt)`, then `token.transfer(pair, ~type(uint112).max)` and `lt.transfer(pair, small)` (or vice versa, to hit whichever branch divides by the small cached value), then `pair.mint(attacker)`.
3. Anyone calls `finalizeGraduation(tokenAddress)`. `_seedRebalancing` computes `reserveToken * ltFromPair` vs `reserveLT * tokensForLP` to pick a branch, then calls `_pairRebalance` → `_noFeeSwapInput(reserveIn≈2^112, reserveOut≈2^112, targetN, targetD≈tiny, maxSwap)`. `Math.mulDiv(reserveIn*reserveOut, targetN, targetD)` computes an exact result exceeding `2^256` and reverts, which propagates out of `finalizeGraduation` with no fallback — the token is permanently stuck in `Lifecycle.Graduating`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
```text
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
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

**File:** packages/contracts/AGENTS.md (L130-149)
```markdown
### The exploit

A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

When our `pair.mint(lpLock)` runs in phase 2 against this non-empty pair, V2's mint formula picks up the existing reserves:

```
liquidity = min(amount0 · totalSupply / reserve0, amount1 · totalSupply / reserve1)
```

The `min(...)` arm whose denominator is bigger relative to its numerator wins, and the OTHER arm's "excess" deposit is donated pro-rata to existing LP holders — i.e. to the attacker. Two harms:

- **Wrong opening price.** Post-mint reserves are `(R_attacker + T_a, R_attacker + T_b)`, so the LP opens at `(R_a + T_a) / (R_b + T_b)`, NOT at the curve close `T_a / T_b`. A `$15` LT pre-seed at 50% off curve close opens the pool ~454 bps off.
- **LP capture.** The wasted-side excess goes to the attacker's LP claim. A `1 wei + 1 LT` pre-seed (~`$1` attack budget) captures ~34 bps of LP.

A cheaper variant skips step 3 entirely: `transfer(pair, dust) + pair.sync()` forces the stored reserves to the dust ratio without minting any LP, leaving the pair at `reserves > 0 && totalSupply == 0`. Regime 1 below covers both shapes by keying on supply rather than reserves.
```

**File:** packages/contracts/AGENTS.md (L191-193)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:
```

**File:** docs/contracts-scope.md (L68-77)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

**Retired LTs.** The reserve asset is an external BounceTech LT. If BounceTech de-registers it (it redeploys a fresh LT at a new address and flips the old address's `ltExists` to `false`), bonding curves already pointing at the old LT keep trading — `mint` / `redeem` / `exchangeRate` still work — but its `exchangeRate` stops tracking the underlying, so leverage is effectively frozen. The USD trigger above then can't ripen further; the supply trigger still graduates the token, and holders can always exit via `redeem`, so no funds are stranded. `Bonding.launch` rejects new bonding curves against a retired LT (its `ltExists` gate), so only pre-existing bonding curves are affected. See root `AGENTS.md` for the full note.
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L122-152)
```text
    function test_phase1_buy_during_pending_reverts() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        uint256 attempt = _ltGraduationTrigger();
        lt.mintDirect(trader, attempt);
        vm.startPrank(trader);
        lt.approve(address(curveRouter), attempt);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.buy(attempt, tokenAddr, 0, trader);
        vm.stopPrank();
    }

    function test_phase1_sell_during_pending_reverts() public {
        // Seed a holder before graduating so they have something to try to sell.
        (address tokenAddr,) = _launchToken();
        _buyNoFinalize(tokenAddr, trader, _ltStageBeforeGraduation());
        uint256 holderBalance = Token(tokenAddr).balanceOf(trader);
        assertTrue(holderBalance > 0);

        // Now graduate via the standard rate-pump pattern.
        lt.setExchangeRate(_ratePumpForStagedGraduation());
        _buyNoFinalize(tokenAddr, trader2, _ltGraduationTrigger());
        assertTrue(bonding.isGraduating(tokenAddr));

        vm.startPrank(trader);
        Token(tokenAddr).approve(address(curveRouter), holderBalance);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.sell(holderBalance, tokenAddr, 0, trader);
        vm.stopPrank();
    }
```
