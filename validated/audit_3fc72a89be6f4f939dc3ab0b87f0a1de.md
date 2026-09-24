## Root Cause Identified: Hostile-Pre-Seed Fallback Escapes the "Empty/Negligible Pool" Invariant [1](#0-0) 

### Title
Hostile HyperSwap V2 pre-seed can force `_seedDirectMint` onto a non-trivial pre-existing LP, donating the graduation's LP-bound tokens to the attacker's pool share - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` seeds the post-graduation HyperSwap V2 pair via `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance`, whose entire purpose is to prevent an attacker-pre-seeded pool from capturing the graduation deposit through Uniswap V2's `mint()` `min()` formula. However, when `_pairRebalance` returns `false` because the pair's fee-charging `getAmountOut` rounds to zero, the code unconditionally falls back to `_seedDirectMint` [2](#0-1) , which was designed and is only safe for the empty-pool / negligible-dust case [3](#0-2) . The `expectedOut == 0` condition depends only on the *swap size* rounding to zero, not on the pool's *absolute reserves* being small — an attacker can pre-seed the pair with substantial reserves at (or extremely near) the eventual curve-close ratio, keeping the required rebalance swap tiny enough that its fee-adjusted output floors to zero, while still holding a large, non-negligible LP position. The fallback then transfers `tokensForLP`/`ltFromPair` straight into that non-empty pool and calls `pair.mint(lpLock)`, hitting Uniswap V2's `min(amount0·S/r0, amount1·S/r1)` formula and donating the off-ratio remainder to the attacker's own outstanding LP shares.

### Finding Description
This is the alt.fun analog of the `caption-download` report's class: an unconfined write into an attacker-influenced destination that bypasses the very boundary check the code believes it enforces. In `yutu`, `os.Create(c.File)` bypassed `pkg.Root` confinement because the guard only existed on *other* code paths. Here, the "confinement" is the Regime-3 rebalance-then-optimal-deposit path (`_pairRebalance` + `_routerDepositAndDispose`), which is supposed to be the only way LP-bound tokens ever touch a pre-seeded, non-empty HyperSwap pair. The guard that is supposed to keep `_seedDirectMint` (the unconfined `mint()` sink) restricted to genuinely negligible reserves only exists at the *first* call site of `_seedDirectMint` — the `DIRECT_MINT_PRESEED_BPS` check at lines 1297-1301, which explicitly bounds `reserveToken`/`reserveLT` to ≤ 1 bp of the target amounts.

The other two call sites, reached when `_pairRebalance` returns `false` (lines 1319-1332 and 1335-1347), have **no such reserve-size bound**. `_pairRebalance` returns `false` purely because `_noFeeSwapInput` computes `s == 0` or the pair's `getAmountOut(s, tokenIn) == 0` [4](#0-3) . Both conditions are about the *magnitude of the required correction*, not the *magnitude of the existing reserves*. An attacker who pre-seeds the pair with a large mint at a ratio extremely close to (but not exactly) the eventual curve-close ratio produces:
- large `reserveToken`/`reserveLT` (so the direct-mint fallback is not "negligible"), and
- a tiny required swap `s` (because the ratio is already almost correct), whose fee-adjusted output rounds to zero.

This forces `finalizeGraduation` down the `_seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair)` path on a pool where `IUniswapV2Pair(pair).totalSupply() != 0` [5](#0-4) . Uniswap V2's `mint()` on a non-empty pool computes `liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)`; whichever side of `(tokensForLP, ltFromPair)` is proportionally larger than the pool's current ratio is not minted as LP to `lpLock` — it simply becomes additional reserve backing the *existing* LP supply, which is 100% attacker-owned. The attacker's un-locked, freely-withdrawable LP shares thus capture value that was meant to open the graduated market at the curve-close price for `lpLock`-held liquidity.

### Impact Explanation
The graduation's `tokensForLP`/`ltFromPair` (up to `LP_RESERVE` tokens = 25% of `TOTAL_SUPPLY`, plus all curve-raised LT) is meant to seed a locked LP position at the exact curve-close price for public benefit (per the extensive natspec on `_seedUniswapV2Direct`). By steering `finalizeGraduation` into the unguarded `_seedDirectMint` fallback against a substantial, near-matched pre-seed, an attacker converts part of that deposit into unminted reserve value backing their own unlocked LP tokens instead of the `LPLock`-held position, then withdraws via ordinary `IUniswapV2Pair.burn`. This is a direct value transfer from the protocol's/traders' LP seed to the attacker and opens the graduated pool at an off-curve-close price for the `lpLock` share — squarely within the report's accepted impact categories ("theft... of trader, creator or LP funds" and "an LP seeded away from the curve close price").

### Likelihood Explanation
Reachable entirely through permissionless, unprivileged actions already enumerated as in-scope: pre-creating/pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation, then letting (or forcing, via `triggerGraduation`) a normal graduation proceed. No privileged role, oracle manipulation, or protocol bug elsewhere is required — only careful sizing of the pre-seed ratio relative to the token's eventual curve-close ratio, which the attacker can predict from public curve state before graduation (`canGraduate`, `_prepareGraduationLiquidity`'s deterministic math). This requires some precision (landing the ratio close enough that the fee-adjusted swap output floors to zero) but is a pure off-chain computation, not an on-chain race.

### Recommendation
Apply the same reserve-negligibility bound used at the `DIRECT_MINT_PRESEED_BPS` call site to *every* `_seedDirectMint` fallback reached from `_seedRebalancing`. If `_pairRebalance` returns `false` but the pool's reserves are not within the negligible band, do not fall back to an unconfined `mint()` — instead force a minimal non-zero swap (e.g. round `s` up to 1 wei of fee-adjusted output) or route through `_routerDepositAndDispose`'s optimal-split deposit directly against the current (unrebalanced) ratio, which never donates via `min()` since the router only pulls the matched-ratio subset.

### Proof of Concept
1. Attacker computes the token's projected `tokensForLP`/`ltFromPair` ratio from public curve state before graduation.
2. Attacker calls `IUniswapV2Factory.createPair(token, lt)` (or lets `_ensureUniswapV2Pair` create it) and self-funds a large `mint()` at a ratio extremely close to, but not exactly, that projected ratio — sized so the corrective swap computed by `_noFeeSwapInput` is small enough that `IUniswapV2Pair.getAmountOut(s, tokenIn)` rounds to `0` [6](#0-5) .
3. Attacker (or anyone) triggers graduation normally; `finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` detects `totalSupply != 0` and a non-negligible reserve size (bypassing the `DIRECT_MINT_PRESEED_BPS` guard), attempts `_pairRebalance`, which returns `false` per step 2.
4. Code falls back to `_seedDirectMint`, transferring the full `tokensForLP`/`ltFromPair` into the still-imbalanced, attacker-dominated pool and calling `pair.mint(lpLock)` [7](#0-6) ; the `min()` formula donates the off-ratio excess to reserves backing the attacker's pre-existing, unlocked LP shares.
5. Attacker calls `IUniswapV2Pair.burn` on their own LP tokens to redeem the inflated reserves, extracting value that should have backed the `LPLock`-held liquidity.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1236-1259)
```text
    /// @dev Transfer the full `(tokensForLP, ltFromPair)` to the pair and
    ///      `mint` the LP to `LPLock`, opening at the exact cached
    ///      curve-close ratio. Used by the empty-pair regime and as the
    ///      dust-pre-seed fallback in `_seedRebalancing` — against dust
    ///      reserves the V2 `min()` formula's donation to any pre-existing
    ///      LP is negligible (see `_seedUniswapV2Direct` natspec). Any TOKEN
    ///      remainder (a skimmed pure-donation pre-seed) is burned; the LT
    ///      remainder is left for `finalizeGraduation`'s `_sweepLTToOwner`
    ///      post-bookend.
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
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
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
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
