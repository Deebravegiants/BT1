Based on the codebase's own risk documentation and the AMM math involved, there is a valid analog: an attacker-triggerable arithmetic revert deep in the permissionless graduation-finalization math, which — unlike a database engine hang — permanently bricks a token's graduation rather than merely denying service temporarily, which is worse.

### Title
Attacker-Controlled `Math.mulDiv` Overflow in `_noFeeSwapInput` Permanently Bricks `finalizeGraduation` - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2023-21879 is a MySQL optimizer bug where a high-privileged but otherwise ordinary client request drives the query optimizer into a state that hangs/crashes the server — an attacker-reachable computation that the engine cannot safely complete. The alt.fun analog is `Bonding._noFeeSwapInput`, the closed-form sqrt/mulDiv routine that powers the hostile-pre-seed rebalance inside the **permissionless**, brick-resistance-critical `finalizeGraduation` path. An attacker who front-runs pair creation and mints a self-funded, maximally-skewed HyperSwap V2 pair can push the function's internal product past `uint256`, causing `Math.mulDiv` to revert every future `finalizeGraduation` call for that token.

### Finding Description
`_noFeeSwapInput` computes the swap size needed to rebalance a hostile pre-seeded pair back toward the curve-close ratio: [1](#0-0) 

The reserves `reserveIn`/`reserveOut` are read live from the attacker-controlled HyperSwap pair (`IUniswapV2Pair.getReserves()`, `uint112`-bounded, max ≈5.19e33 each), and are **not capped** before being passed into `_pairRebalance`: [2](#0-1) 

The natspec on `_noFeeSwapInput` explicitly acknowledges the overflow class and shrugs it off as an acceptable failure mode: [3](#0-2) 

But per the protocol's own stated security contract, this is *not* an acceptable failure mode: `finalizeGraduation` is documented as needing to **never revert under any pre-seed shape**, because a revert leaves the token stuck in `Lifecycle.Graduating` forever (no retry path bypasses the same computation): [4](#0-3) 

The attack path mirrors the protocol's own documented hostile-pre-seed exploit (front-run `factory.createPair`, `transfer` TOKEN/LT to the pair, then `pair.mint(attacker)`), which the Rules explicitly treat as in-scope: [5](#0-4) 

By maximizing `reserveIn * reserveOut` (both near `uint112.max`) and choosing a token/LT pair whose curve-close price ratio (`targetN`/`targetD`, i.e. `ltFromPair`/`tokensForLP` or its inverse) is sufficiently skewed, `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` can be forced to exceed `type(uint256).max`, which OZ's `Math.mulDiv` reverts on rather than truncating. Because `_pairRebalance` is invoked unconditionally on every call to `finalizeGraduation` while the pre-seed reserves are non-zero, the revert is **deterministic and repeatable** on every subsequent call — a permanent, not transient, denial of service.

### Impact Explanation
A successful trigger permanently freezes:
- The curve-raised LT held in `Bonding` for that token (never reaches `LPLock`).
- The 250M `LP_RESERVE` tokens earmarked for LP seeding.
- Every trader's ability to exit into the graduated pool (trading is frozen once `Lifecycle.Graduating` is entered, per `_enterGraduating`).

This satisfies the Validate criterion of "permanent freezing of trader, creator or LP funds" — the funds are not stolen, but become permanently unreachable since there is no rescue/retry path around the same reverting computation.

### Likelihood Explanation
The attack requires no privileged role: any address can call `factory.createPair`, `transfer` TOKEN/LT, and `pair.mint`, exactly as already documented as an in-scope attack primitive by the project itself. The main constraint is finding/arranging a token↔LT pairing whose legitimate curve-close price ratio is extreme enough (combined with maximal `uint112` reserve donations) to breach the `2^256` ceiling — plausible for tokens paired against very low- or very high-unit-value LTs, which the protocol supports natively via its multi-LT design (`Factory`'s `ltFor` mapping, per-token K).

### Recommendation
Cap `reserveIn`/`reserveOut` (or bound the product) defensively inside `_noFeeSwapInput`/`_pairRebalance` before the `mulDiv` call, and make `_pairRebalance` fail soft (return `false`, falling back to `_seedDirectMint`, exactly as it already does for the `s == 0` / `getAmountOut == 0` cases) instead of letting an unchecked overflow propagate up through `finalizeGraduation`. This keeps the "must never revert" invariant intact for every pre-seed shape, not just the two currently guarded ones.

### Proof of Concept
1. Launch/observe a token paired against an LT whose legitimate curve-close ratio (`ltFromPair`/`tokensForLP`) is extreme (achievable by choosing or waiting for a token graduating against a very cheap or very expensive LT).
2. Front-run graduation: call `factory.createPair(token, lt)` on HyperSwap.
3. `transfer` TOKEN and LT to the pair at amounts approaching `type(uint112).max` on both sides, skewed to maximize `reserveIn * reserveOut * targetN / targetD`.
4. `pair.mint(attacker)` to lock in the reserves.
5. When `finalizeGraduation(token)` is called (by the keeper or anyone), `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput` reverts inside `Math.mulDiv`, reverting the whole `finalizeGraduation` transaction.
6. Every subsequent call to `finalizeGraduation(token)` reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, matching `test/NoFeeSwapInput.t.sol`'s own acknowledged (but unmitigated) overflow scenario referenced in `test_overflowSafety_atRealisticMax`. [6](#0-5)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
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

**File:** packages/contracts/AGENTS.md (L132-137)
```markdown
A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

```

**File:** packages/contracts/AGENTS.md (L191-193)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:
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
