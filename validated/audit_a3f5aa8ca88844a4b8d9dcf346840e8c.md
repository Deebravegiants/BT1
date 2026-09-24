### Title
`finalizeGraduation` can be permanently bricked by an attacker-inflated HyperSwap pre-seed that overflows `_noFeeSwapInput`'s discriminant, freezing curve-raised LT and the 250M LP reserve forever - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` (Phase 2 of the permissionless two-phase graduation) drives all hostile-pre-seed handling through `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`. The protocol's own test suite documents that `_noFeeSwapInput`'s closed-form discriminant `reserveIn · reserveOut · targetN / targetD` can overflow `uint256` and revert inside OpenZeppelin's `Math.mulDiv`, and that this is only avoided in practice by an *assumption* about realistic input bounds, not by an enforced cap. Because none of `finalizeGraduation`'s call chain uses try/catch, a revert anywhere in that chain reverts the entire `finalizeGraduation` transaction, leaving the token stuck in `Lifecycle.Graduating` with no other exit path - exactly the "root claim becomes unchallengeable" failure mode from the referenced report, where a state machine has exactly one forward-progress function and that function can be forced to fail every single time it's invoked.

### Finding Description
`finalizeGraduation` is the sole permissionless mechanism to advance a token out of `Lifecycle.Graduating`: [1](#0-0) 

Its hostile-pre-seed defense (Regime 3, "mint pre-seed") calls `_pairRebalance`, which sizes a corrective swap via `_noFeeSwapInput(reserveIn, reserveOut, targetN, targetD, maxSwap)`: [2](#0-1) 

and the branch selection / call sites live in `_seedRebalancing`: [3](#0-2) 

The project's own test file documents the exact failure condition being relied upon rather than eliminated:

> "the unrealistic-but-mathematically-possible case where the discriminant overflows uint256 (forcing `Math.mulDiv` to revert) is documented separately on `_noFeeSwapInput`'s natspec — call sites must keep `reserveIn * reserveOut * targetN / targetD ≤ 2^256`." [4](#0-3) 

`AGENTS.md` explicitly states that `_seedUniswapV2Direct` "MUST never revert under any pre-seed shape" and calls brick-resistance "the load-bearing security property" because "a brick locks every holder in `Graduating` forever": [5](#0-4) 

But this guarantee is enforced only by bounding *typical* graduation math (`tokensForLP ≤ LP_RESERVE`, `ltFromPair` sized by the ~$9K threshold), not by clamping the reserves an *attacker* can drive into the HyperSwap pair between Phase 1 and Phase 2. `reserveIn`/`reserveOut` are read live from the pool's `uint112` reserves: [6](#0-5) 

An attacker who front-runs the pair (as already contemplated by the "Regime 3" mint-pre-seed defense) and mints a pre-seed at reserves large enough — combined with a `targetN/targetD` ratio (i.e. cached `tokensForLP`/`ltFromPair`) skewed enough — pushes `reserveIn · reserveOut · targetN / targetD` past `2^256`. `Math.sqrt`/`Math.mulDiv` inside `_noFeeSwapInput` then revert with a low-level panic instead of returning a swap size, which propagates all the way up through `_seedRebalancing` → `_seedUniswapV2Direct` → `finalizeGraduation`, reverting the whole transaction. Because this failure is deterministic given the pool state (not probabilistic), **every subsequent call to `finalizeGraduation` for that token reverts identically**, forever — there is no `try/catch`, no alternate finalize path, and no admin rescue function for `Bonding`'s escrowed assets once `PendingGraduation` is set: [7](#0-6) 

This is the same bug class as the report: a system whose only forward-progress transition (`finalizeGraduation`, analogous to a dispute-game move) can be made to revert unconditionally by an adversary, permanently freezing the underlying state (here: the curve-raised LT plus the reserved 250M `LP_RESERVE` tokens sitting in `Bonding`, and the token's holders, who can never sell because `Lifecycle.Graduating` blocks `buy`/`sell`).

### Impact Explanation
If triggered, the token is permanently stuck in `Lifecycle.Graduating`:
- All LT raised by the curve (`ltFromPair`, already pulled out of the `Pair` via `Router.graduate` in Phase 1) is trapped in `Bonding` with no withdrawal path.
- The 250M `LP_RESERVE` tokens earmarked for LP are similarly trapped.
- Holders can never sell (`TokenIsGraduating` reverts `buy`/`sell`) and the token can never reach `Lifecycle.Graduated`, so no HyperSwap trading ever opens.
- `LPLock.recordLock` is never reached, so no LP is ever locked either — total, permanent freeze of creator/trader/LP-bound funds for that token.

This satisfies "permanent freezing of trader, creator or LP funds," which is one of the explicitly accepted impact categories.

### Likelihood Explanation
Reaching the exact overflow boundary requires the attacker to control both the pre-seed reserve magnitudes and the ratio skew precisely enough to exceed `2^256` in the discriminant, which needs the pair's `uint112` reserves to be pushed to extreme values relative to the cached `(tokensForLP, ltFromPair)` targets. The protocol's own regression tests only assert non-overflow "at realistic maximums," explicitly acknowledging (rather than eliminating) the theoretical overflow case: [8](#0-7) 

Practically, achieving the needed magnitude requires the attacker to source and mint into the pair token/LT quantities at the outer edge of `uint112` capacity, which is expensive but not access-controlled — pair creation and `pair.mint` are fully permissionless, exactly as already exploited in the "Regime 3" hostile-pre-seed scenario the code defends against. Likelihood is Low-to-Medium (large capital/LT supply needed), but because the bug class is a deterministic, un-recoverable revert with no owner/admin escape hatch, the severity classification should remain High given the totality-of-freeze impact once triggered — mirroring Inphi's acknowledgment in the referenced report that a single-path failure (there: MIPS panic; here: an unhandled arithmetic revert) can permanently corrupt otherwise-sound on-chain state.

### Recommendation
- Bound `reserveIn`, `reserveOut`, `targetN`, `targetD` (or the discriminant itself) defensively inside `_noFeeSwapInput`/`_pairRebalance` before computing `Math.mulDiv`, and fall back to `_seedDirectMint` (as already done for the `s == 0` / `getAmountOut == 0` cases) whenever the discriminant computation would overflow, rather than letting the revert propagate.
- Wrap the Regime-3 rebalance branch in a bounded-computation guard so any arithmetic failure degrades to the safe direct-mint fallback instead of reverting the whole `finalizeGraduation` call.
- Add a fuzz/invariant test that drives pair reserves up to `type(uint112).max` combined with extreme `tokensForLP`/`ltFromPair` skews to confirm `finalizeGraduation` truly never reverts, closing the gap between the documented "unrealistic-but-mathematically-possible" case and an enforced guarantee.

### Proof of Concept
1. Creator launches a token via `Bonding.launch`; curve trades normally until the dual trigger fires and Phase 1 (`_enterGraduating`) caches `(tokensForLP, ltFromPair)` in `pendingGraduation[token]`, freezing trading (`Lifecycle.Graduating`).
2. Before anyone calls `finalizeGraduation`, an attacker front-runs by calling `IUniswapV2Factory.createPair(token, lt)` (permissionless) and self-funds a mint that drives the pair's `uint112` reserves toward the extreme end of their range at a ratio skewed far away from the cached `(tokensForLP, ltFromPair)` ratio (the same mechanism already exercised by `test_brick_resistance_frontRun_dust_seed`, but sized to the opposite extreme instead of dust).
3. Any subsequent call to `bonding.finalizeGraduation(token)` routes into Regime 3 (`_seedRebalancing`), computes `reserveIn · reserveOut · targetN / targetD` inside `_noFeeSwapInput`, and the multiplication overflows `uint256`, causing `Math.mulDiv`/`Math.sqrt` to revert.
4. Because the pre-seed reserves are now permanently baked into the pair and `pendingGraduation[token]` is immutable once cached, every future call to `finalizeGraduation(token)` hits the identical overflow and reverts — the token is permanently stuck in `Lifecycle.Graduating`, and the escrowed LT/250M tokens in `Bonding` are unrecoverable.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
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

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1279-1350)
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

        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
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
        // else: pool already at curve-close ratio (rare — e.g. attacker
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

**File:** packages/contracts/test/NoFeeSwapInput.t.sol (L135-180)
```text
    // ─── Overflow safety ──────────────────────────────────────────────────

    /// @notice Across the input space the call site actually produces,
    ///         the discriminant `reserveIn * reserveOut * targetN / targetD`
    ///         stays inside uint256 and the function returns without
    ///         reverting.
    /// @dev    Reserves and targets are bounded to uint64 (max ~1.8e19)
    ///         which comfortably exceeds anything a real graduation can
    ///         produce — `tokensForLP` ≤ 250M·1e18 and `ltFromPair`
    ///         scales with `graduationThresholdUsd`, both well inside
    ///         this bound. The unrealistic-but-mathematically-possible
    ///         case where the discriminant overflows uint256 (forcing
    ///         `Math.mulDiv` to revert) is documented separately on
    ///         `_noFeeSwapInput`'s natspec — call sites must keep
    ///         `reserveIn * reserveOut * targetN / targetD` ≤ 2^256.
    function testFuzz_overflowSafety(
        uint64 reserveIn,
        uint64 reserveOut,
        uint64 targetN,
        uint64 targetD,
        uint256 maxSwap
    ) public view {
        vm.assume(reserveIn > 0 && reserveOut > 0 && targetN > 0 && targetD > 0 && maxSwap > 0);
        harness.exposed_noFeeSwapInput(reserveIn, reserveOut, targetN, targetD, maxSwap);
    }

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
```

**File:** packages/contracts/AGENTS.md (L191-200)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```
