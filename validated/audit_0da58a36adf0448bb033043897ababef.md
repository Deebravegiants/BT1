## Title
Attacker-inflated HyperSwap pre-seed reserves can overflow `_noFeeSwapInput`'s `Math.mulDiv` discriminant, permanently reverting `finalizeGraduation` and freezing graduation funds - (File: `packages/contracts/src/Bonding.sol`)

### Summary
CVE-2016-7054 is a DoS class where an oversized/corrupting payload drives an unhandled arithmetic condition that crashes a critical code path. The analogous condition in alt.fun's contracts is in `Bonding._noFeeSwapInput`, the load-bearing math for the hostile-pre-seed defense inside the permissionless `finalizeGraduation` flow, which is contractually required to *never revert*.

### Finding Description
`_noFeeSwapInput` computes the swap needed to rebalance an attacker-pre-seeded HyperSwap pair back to the curve-close ratio: [1](#0-0) 

The natspec itself flags the risk: `Math.mulDiv` keeps `reserveIn * reserveOut * targetN` inside a 512-bit working space, but the *final* result after dividing by `targetD` must still fit in `uint256`, or the call reverts: [2](#0-1) 

`reserveIn`/`reserveOut` come directly from the HyperSwap V2 pair's `uint112` reserves — attacker-controllable up to `type(uint112).max` (~5.19e33) via the documented pre-creation/pre-seed attack (permissionlessly calling `factory.createPair` + `transfer` + `pair.mint`) described in `packages/contracts/AGENTS.md`: [3](#0-2) 

`targetN`/`targetD` are `ltFromPair`/`tokensForLP` (or the reverse), cached from real curve state at graduation: [4](#0-3) 

`tokensForLP` is hard-bounded by the parabola invariant at `LP_RESERVE` (≈2.5e26). `ltFromPair`, however, is `storedAssetReserve - virtualLtReserve` — the real LT raised by the curve, read against the LT's live `exchangeRate`/`baseToLtAmount` conversion. Because the LT is an external, rebasing-priced asset, its wei-denominated raise size for a fixed USD threshold is unbounded from the contract's perspective: a sufficiently depressed `exchangeRate` (an economic property of the external LT, not gated by alt.fun) inflates the LT-wei amount needed to cross the fixed USD graduation threshold, and thus inflates `ltFromPair` in wei terms with no upper clamp anywhere in `_prepareGraduationLiquidity`/`_enterGraduating`.

An attacker who (a) pre-seeds the HyperSwap pair with reserves skewed toward `uint112` scale (achievable with real, but not economically extreme, capital when combined with a low-exchange-rate LT) and (b) waits for/engineers a graduation on an LT whose live rate makes `ltFromPair` large relative to `tokensForLP`, can push `reserveIn * reserveOut * targetN / targetD` past `2^256`. `Math.mulDiv` then reverts unconditionally rather than truncating (this is explicitly documented as the accepted failure mode, but its consequence for `finalizeGraduation`'s brick-resistance contract is not addressed).

Because `_noFeeSwapInput` is called unconditionally from `_pairRebalance` → `_seedRebalancing` → `_seedUniswapV2Direct` → `finalizeGraduation` for any pre-seed above the `DIRECT_MINT_PRESEED_BPS` dust threshold, this revert propagates all the way up and reverts `finalizeGraduation` itself — the exact scenario `AGENTS.md` calls out as unacceptable: *"Phase 2 must never revert under any pre-seed shape... a brick locks every holder in Graduating forever."*

### Impact Explanation
A reverting `finalizeGraduation` permanently freezes the token in `Lifecycle.Graduating`: all curve-raised LT and the 250M `LP_RESERVE` tokens parked on `Bonding` for that token become permanently unreachable (no retry path exists once the discriminant condition recurs on every call, since the cached `pendingGraduation` values and the attacker's pre-seeded reserves are both immutable inputs to the same failing computation). This is a permanent freeze of creator/trader funds, matching the "Validate" bar of concrete permanent freezing of funds.

### Likelihood Explanation
Exploitation requires: (1) permissionlessly pre-seeding a HyperSwap pair with reserves large enough, in combination with (2) a graduation on an LT whose live `exchangeRate` inflates `ltFromPair`'s wei magnitude relative to `tokensForLP`. Both preconditions are reachable by an unprivileged actor (pair creation/pre-seeding is explicitly permissionless, and LT `exchangeRate` is read live and is out of alt.fun's control per the threat model), but the exact reserve magnitudes needed depend on the specific LT's price/decimals, making this a real but resource- and setup-dependent attack rather than a trivial one-transaction griefing vector.

### Recommendation
Bound the `_noFeeSwapInput` discriminant defensively before calling `Math.mulDiv` — e.g., clamp `reserveIn`/`reserveOut`/`targetN`/`targetD` combinations, or wrap the `Math.mulDiv` call in a try/catch (or a manual overflow precheck) inside `_pairRebalance` so an overflow degrades to the existing `_seedDirectMint` fallback (the same fallback already used when the rebalance swap rounds to zero) instead of propagating a revert into `finalizeGraduation`.

### Proof of Concept
1. Attacker permissionlessly calls `factory.createPair(token, lt)` and deposits token/LT amounts sized to push the pair's `uint112` reserves toward the high end of the representable range, then calls `pair.mint(attacker)` (per the documented pre-seed exploit primitive in `AGENTS.md`).
2. Separately/concurrently, the token's bonding curve graduates on an LT whose live `exchangeRate` makes `ltFromPair` large in wei terms relative to `tokensForLP`, both cached by `_enterGraduating`/`_prepareGraduationLiquidity`.
3. Anyone calls the permissionless `finalizeGraduation(token)`. It reaches `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, whose `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` call exceeds `type(uint256).max` and reverts.
4. `finalizeGraduation` reverts on every subsequent call with the same cached state, permanently stranding the curve-raised LT and the 250M `LP_RESERVE` tokens on `Bonding`.

This requires precise reserve/rate magnitudes to trigger reliably; the existing `test_overflowSafety_atRealisticMax` in `packages/contracts/test/NoFeeSwapInput.t.sol` only tests the case where `targetN == targetD` (which cancels out), not the skewed-ratio case that this finding relies on — confirming the coverage gap. [5](#0-4)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1287-1289)
```text
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
```

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

**File:** packages/contracts/src/Bonding.sol (L1498-1506)
```text
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
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

**File:** packages/contracts/test/NoFeeSwapInput.t.sol (L161-183)
```text
    /// @notice Stress at realistic ceiling: V2 uint112 reserves combined
    ///         with the target-ratio bounds the call site actually
    ///         produces. `targetN` and `targetD` come from `tokensForLP`
    ///         and `ltFromPair` (or vice versa), both bounded above by
    ///         `Token.TOTAL_SUPPLY` (1B * 1e18 ≈ 2^90) in any sensible
    ///         BounceTech LT × token combination, so the discriminant
    ///         `reserveIn * reserveOut * targetN / targetD` stays inside
    ///         uint256 even at the extremes that real graduations can
    ///         actually produce.
    ///
    ///         (Note: `_noFeeSwapInput` would revert under the OZ `mulDiv`
    ///         512-bit-intermediate guard if the intermediate result
    ///         exceeded uint256, e.g. with arbitrary uint128 target ratios
    ///         — but no real call site can construct such inputs because
    ///         `tokensForLP` and `ltFromPair` are bounded by token supply.)
    function test_overflowSafety_atRealisticMax() public view {
        uint256 maxReserve = type(uint112).max;
        uint256 totalSupply = 1_000_000_000 ether; // ~2^90, the largest plausible target
        // Discriminant: 2^224 * 2^90 / 1 = 2^314 — overflows uint256, so
        // pin targetD high enough to bring result back within range.
        // 2^224 * 2^90 / 2^90 = 2^224, fits.
        harness.exposed_noFeeSwapInput(maxReserve, maxReserve, totalSupply, totalSupply, type(uint256).max);
    }
```
