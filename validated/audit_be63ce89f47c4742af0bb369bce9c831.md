Based on my investigation, I found a valid analog. The `Bonding._noFeeSwapInput` overflow-safety property is explicitly *assumed* by comment but not code-enforced, and it sits directly inside the one code path (`finalizeGraduation`) that the protocol's own documentation states "MUST never revert under any pre-seed shape."

### Title
Unhandled arithmetic-overflow Panic in `_noFeeSwapInput` can permanently brick `finalizeGraduation` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._noFeeSwapInput` computes `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` and then `Math.sqrt`, as the core of the hostile-pre-seed rebalance defense used inside `_pairRebalance` → `_seedRebalancing` → `_seedUniswapV2Direct`, which `finalizeGraduation` calls unconditionally. `reserveIn`/`reserveOut` come from the HyperSwap V2 pair's live, attacker-influenceable reserves (an attacker can front-run and mint LP against a pair they seed at any ratio, up to circulating token supply / whatever LT they buy), while `targetN`/`targetD` come from the graduation's `tokensForLP`/`ltFromPair`, whose *ratio* is itself a function of the paired LT's live, externally-controlled `exchangeRate()`. When `reserveIn * reserveOut * targetN / targetD` exceeds `type(uint256).max`, OZ `Math.mulDiv`'s internal 512-bit-intermediate guard calls `Panic.panic(Panic.UNDER_OVERFLOW)` [1](#0-0) , which is an unhandled revert that propagates all the way up through `finalizeGraduation`.

### Finding Description
`_noFeeSwapInput`'s own natspec acknowledges the risk but relies on an un-enforced assumption rather than a code-level guard: [2](#0-1) 

The comment states: *"Constructed adversarial inputs that violate this would `revert` rather than silently truncate, which is the correct failure mode."* This treats the revert as acceptable, but it directly conflicts with the protocol's own stated invariant for this call path: [3](#0-2) 

`_pairRebalance` (which calls `_noFeeSwapInput` with no try/catch) is invoked from `_seedUniswapV2Direct`'s Regime-3 handling of a hostile mint pre-seed [4](#0-3) , itself called unconditionally from `finalizeGraduation`: [5](#0-4) 

`reserveIn`/`reserveOut` are read from the HyperSwap pair the attacker pre-seeds (any address can `factory.createPair` + `transfer` + `pair.mint`, as described extensively in `AGENTS.md`'s "HyperSwap Pre-Seed Defense" section) [6](#0-5) . The TOKEN-side reserve an attacker can seed is bounded only by how many of the 750M curve-sellable tokens they can acquire (up to `Router`'s real balance), and the LT-side reserve is bounded only by how much LT they can buy/mint — both economically large but not protocol-capped beyond the uint112 V2 storage width. Meanwhile `targetN/targetD` (`tokensForLP`/`ltFromPair`) are pinned from the curve's close price, and `ltFromPair` in particular can be made arbitrarily small in wei terms if the paired BounceTech LT's `exchangeRate()` is very high when the supply trigger (not the USD trigger) fires graduation — no code path bounds this ratio.

The dedicated overflow-safety test, `test_overflowSafety_atRealisticMax`, only exercises the symmetric case `targetN == targetD` at `uint112.max` reserves, which trivially cancels to a safe `2^224` product; it does **not** cover the asymmetric-ratio case that the natspec itself flags as unguarded [7](#0-6) .

### Impact Explanation
If `_noFeeSwapInput` panics, `finalizeGraduation` reverts entirely — with no fallback, no try/catch, and no alternate code path (the whole design intent of the three-regime defense was to make this call unconditionally non-reverting). Because `finalizeGraduation` is the *only* function that can move a token out of `Lifecycle.Graduating`, a stuck token permanently freezes: all curve-raised LT (`p.ltFromPair`, drained from `Router` already in phase 1) and the 250M reserved tokens (`lpReserve`) held in `Bonding` for that token become permanently inaccessible, and every holder of that token loses the ability to trade or exit. This satisfies "permanent freezing of trader, creator, or LP funds."

### Likelihood Explanation
This requires an attacker to (a) front-run graduation with a self-seeded, mint-pre-seeded HyperSwap pair holding an extreme reserve ratio relative to the curve's close price, and (b) the graduation's `ltFromPair`/`tokensForLP` ratio to be skewed enough (driven by the external LT's live `exchangeRate()`) that the product exceeds `2^256`. This is a narrower, market-condition-dependent trigger than a trivially reachable bug, but it is entirely permissionless, requires no privileged role, and the team's own comments concede the underlying arithmetic invariant is asserted rather than enforced.

### Recommendation
Bound the discriminant explicitly before calling `Math.mulDiv`/`Math.sqrt` in `_noFeeSwapInput` — e.g., cap `reserveIn`/`reserveOut`/`targetN`/`targetD` to a safe combined bit-width, or wrap the computation in a way that degrades to "skip the rebalance swap" (return `0`, same as the existing `s == 0` fallback) rather than reverting when the product would overflow, preserving the documented brick-resistance contract.

### Proof of Concept
1. Launch a token; let curve trading proceed until the supply trigger is about to fire (750M tokens nearly sold) against a BounceTech LT whose `exchangeRate()` has appreciated to a very large value, so that the real LT raised (`ltFromPair`) is tiny in wei terms while `tokensForLP` (bounded up to `LP_RESERVE = 250M * 1e18`) is large — making `tokensForLP / ltFromPair` extremely large.
2. Before the closing buy lands (or before `finalizeGraduation` is called), front-run: `factory.createPair(token, lt)`, transfer a large TOKEN balance (up to the attacker's acquired share of the 750M curve supply) and a correspondingly-shaped LT balance to the pair, then call `pair.mint(attacker)` to seed hostile reserves near the extremes the attacker can afford.
3. Call `finalizeGraduation(token)`. Inside `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` computes a result exceeding `2^256`, and `Math.mulDiv` reverts with `Panic(0x11)`. `finalizeGraduation` reverts, and because no other function can transition `Lifecycle.Graduating → Graduated`, the token, its curve-raised LT, and its 250M token reserve are permanently stuck.

### Citations

**File:** packages/contracts/lib/openzeppelin-contracts/contracts/utils/math/Math.sol (L218-221)
```text
            // Make sure the result is less than 2²⁵⁶. Also prevents denominator == 0.
            if (denominator <= high) {
                Panic.panic(ternary(denominator == 0, Panic.DIVISION_BY_ZERO, Panic.UNDER_OVERFLOW));
            }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1023)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);
```

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

**File:** packages/contracts/src/Bonding.sol (L1498-1522)
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
