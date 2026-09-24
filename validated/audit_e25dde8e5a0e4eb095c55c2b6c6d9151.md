### Title
Budget-Capped Hostile Pre-Seed Rebalance Lets a Griefer Force `finalizeGraduation` to Lock LP at a Materially Off-Curve-Close Price - (`packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` is permissionless, and the HyperSwap V2 TOKEN/LT pair it seeds can be pre-created and pre-seeded by anyone before phase 2 runs, exactly the "attacker plants content at a location the trusted path will act on" bug class in CVE-2019-9642 (unauthenticated actor stages malicious content that a subsequent trusted operation executes/consumes without adequate validation). Here the "content" is a hostile-ratio LP mint into the graduation pair, and the "trusted operation" is `_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`, which is supposed to always deposit the locked LP at the curve-close price. The rebalance swap that is meant to neutralize the hostile ratio is capped at 99% of the available per-side inventory (`_swapBudget`), so a large enough pre-seed makes the required corrective swap exceed the cap, and the protocol-owned LP — locked forever in `LPLock` with no rescue path — gets minted at a price materially away from the curve's true close price.

### Finding Description
`finalizeGraduation` reuses whatever HyperSwap pair exists for `(token, lt)`, including one an attacker created and seeded ahead of time via `pair.mint`: [1](#0-0) 

When `totalSupply() > 0` (an attacker minted dust LP at a hostile ratio), `_seedRebalancing` computes the swap needed to correct the ratio and caps it via `_swapBudget`, which reserves only 1% of the available inventory: [2](#0-1) 

The cap exists specifically to avoid a total-DoS (consuming 100% of one side would zero the deposit), but the documented consequence is that for large-enough imbalances the corrective swap cannot fully close the gap, and the pool opens materially off curve-close: [3](#0-2) 

This exact residual is exercised and explicitly accepted in the test suite: [4](#0-3) 

The AGENTS.md notes this is intentional/known ("mass conservation prevents fixing both the price and the deposit... 50 bps is well inside 'exploit denied'") for *typical* pre-seed sizes, but the M-02 regression above shows the ceiling is not 50 bps for sufficiently large pre-seeds — it can be >20% off curve-close (`(((ltFromPair * 1e18) / tokensForLP) * 12) / 10` bound), and the pool opens at whatever residual the capped swap leaves behind: [5](#0-4) 

The LP minted from this deposit goes straight to `LPLock.recordLock`, which has no withdraw/rescue path in v1 — the mispriced position is permanent, not something the protocol can later rebalance: [6](#0-5) 

### Impact Explanation
Once the pool opens off the curve's true close price, third-party arbitrageurs will immediately trade against the mispriced pool to pull it back to fair value. Because the mispriced side of the reserve is the protocol/creator-locked LP (not the attacker's own capital, which the rebalance swap already confiscates toward the owner per the M-02 test: `assertGt(lt.balanceOf(bonding.owner()) - ownerLtBefore, reserveLt / 2, "the over-funded LT side must be confiscated to the owner")`), the arbitrage profit is extracted from the protocol-owned, permanently-locked LP position rather than from the attacker. This is a real, quantifiable value leak from `LPLock`'s locked liquidity — meeting the "LP seeded away from the curve close price" impact bar — even though the attacker's own residual LP claim is engineered to be non-profitable (P&L ≤ 0 for the attacker specifically, not for the protocol's locked LP value).

### Likelihood Explanation
Triggering the extreme (>20% off-price) regime requires the griefer to source and donate LT/token amounts on the order of hundreds of times `ltFromPair`/`tokensForLP` (per the test, `reserveLt = ltFromPair * 200`), which is a substantial capital outlay proportional to the size of the graduating token's raise. This bounds likelihood to well-capitalized adversaries or situations where `ltFromPair`/`tokensForLP` are small (early/low-cap graduations), where the capital needed to skew the open price is modest in absolute terms. The team is aware of and has load-bearing tests for this exact residual, indicating it is a known, accepted trade-off rather than an unknown defect — but the trade-off still leaves a concrete, reachable path for value extraction from protocol-locked LP, which is why it is reported here as a Medium-severity analog rather than dismissed as no-impact.

### Recommendation
Consider tightening the residual: instead of a flat 99% cap that guarantees only "non-zero deposit," size the cap so the deposit-side minimum satisfies both the brick-resistance property (both sides > 0) and a maximum acceptable curve-close deviation (e.g., dynamically choose the largest swap that keeps `s ≤ maxSwap` while re-checking that the resulting post-swap/post-deposit price gap stays within a fixed bps ceiling; if it can't, consider routing the excess to a defensive burn/skim rather than depositing into `LPLock` at a bad price), and/or add a hard revert-free "abort deposit, escrow-only" fallback specifically for pre-seeds so large that the 1% cap would otherwise leave a >X bps gap, sweeping the leftover LT to the owner (as already done) and additionally minting the corresponding LP at the *reduced* size that keeps price gap bounded rather than committing the full locked inventory at a skewed ratio.

### Proof of Concept
Based on the existing regression `test_M02_...` pattern in `test/TwoPhaseGraduation.t.sol` (lines 871-917):
1. Launch a token and drive it to `Graduating` via `_enterGraduating` (phase 1), caching `tokensForLP` / `ltFromPair`.
2. Before anyone calls `finalizeGraduation`, the griefer front-runs: creates the HyperSwap pair `hsFactory.createPair(tokenAddr, address(lt))`, funds it with `reserveToken = tokensForLP/100` and `reserveLt = ltFromPair * 200`, and calls `pair.mint(griefer)` — establishing a wildly LT-rich pool.
3. Anyone (or the keeper) calls `bonding.finalizeGraduation(tokenAddr)`. `_pairRebalance`'s required corrective swap exceeds `_swapBudget`'s 99% cap, so the swap is clamped and the subsequent `router.addLiquidity` deposit locks LP at a price >20% away from the curve-close ratio (`_poolPriceLtPerToken(hyperPair, tokenAddr) > ((ltFromPair*1e18/tokensForLP) * 12)/10`), while the griefer's own residual LP claim is confiscated to a net loss — the loss instead lands on the value of the permanently-locked protocol LP in `LPLock`, which third-party arbitrageurs can subsequently capture.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1023-1031)
```text
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);
```

**File:** packages/contracts/src/Bonding.sol (L1121-1130)
```text
    function _ensureUniswapV2Pair(
        address tokenA,
        address tokenB
    ) internal returns (address pair) {
        IUniswapV2Factory v2Factory = IUniswapV2Factory(_s().uniswapV2Factory);
        pair = v2Factory.getPair(tokenA, tokenB);
        if (pair == address(0)) {
            pair = v2Factory.createPair(tokenA, tokenB);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1304-1354)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1356-1378)
```text
    /// @dev Cap the rebalance swap at 99% of the available side's budget,
    ///      so the subsequent `addLiquidity` always has a non-zero amount
    ///      of BOTH sides to deposit. Without this, an extreme hostile
    ///      pre-seed (massively imbalanced reserves) drives the
    ///      unconstrained `_noFeeSwapInput` past our per-side budget,
    ///      `_pairRebalance` clamps to the full budget, and the swap
    ///      consumes 100% of one side. `_routerDepositAndDispose` then
    ///      skips `addLiquidity` (`remToken == 0` or `remLT == 0`),
    ///      `finalizeGraduation` returns `liquidity = 0`, and
    ///      `LPLock.recordLock(...)` records a zero-sized lock — the
    ///      attacker's pre-existing LP becomes 100% of the pool. Reserving
    ///      1% guarantees the deposit leg always lands AND mints non-zero
    ///      LP at the post-swap ratio. The 1% comes off the swap, not the
    ///      deposit — for any realistic pre-seed `s_unconstrained` is
    ///      orders of magnitude below `maxSwap`, so the cap doesn't bind
    ///      and behaviour is unchanged. It only kicks in for catastrophic
    ///      pre-seeds beyond our budget capacity, where the alternative
    ///      is bricking.
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L871-917)
```text
        // The optimal TOKEN-in swap to reach the cached ratio is ~1.4x
        // `tokensForLP`, so the 99%-of-`tokensForLP` budget cap binds and the
        // pool stays ~2x off curve-close after the swap.
        uint256 reserveToken = tokensForLP / 100;
        uint256 reserveLt = ltFromPair * 200;

        // M-02 precondition: the optimal swap exceeds the budget (this is the
        // budget-capped regime, distinct from the swap-rounds-to-zero fallback
        // covered by the dust tests above).
        assertGt(
            _noFeeSwapInputUncapped(reserveToken, reserveLt, tokensForLP, ltFromPair),
            (tokensForLP * 99) / 100,
            "setup: optimal rebalance swap must exceed the per-side budget (M-02 regime)"
        );

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);
        uint256 ownerLtBefore = lt.balanceOf(bonding.owner());

        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed despite an unrecoverable pre-seed");

        // The accepted residual: no bounded swap can correct a 200x LT-rich
        // pre-seed, so the pool opens materially off curve-close.
        assertGt(
            _poolPriceLtPerToken(hyperPair, tokenAddr),
            (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
            "M-02 regime: pool opens materially off curve-close"
        );

        // The over-funded LT side is arbed out by the rebalance swap and swept
        // to the owner — the pre-seeder cannot recover it.
        assertGt(
            lt.balanceOf(bonding.owner()) - ownerLtBefore,
            reserveLt / 2,
            "the over-funded LT side must be confiscated to the owner"
        );

        // P&L: the pre-seeder's residual LP, valued at the fair (curve-close)
        // price, is worth a fraction of what they deposited — the attack is
        // cost-negative.
        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        assertLe(claimValue, depositValue, "pre-seeder must not profit (P&L <= 0)");
        assertLt(claimValue * 2, depositValue, "pre-seeder must lose materially, not merely break even");
    }
```

**File:** packages/contracts/AGENTS.md (L202-208)
```markdown
### Attacker P&L outcome

After the fix, the attacker holds LP at the curve-close ratio. The arbitrage-back-to-true-price step that the attacker wanted to extract from is gone (we already arb'd it during the rebalance, paying the V2 0.3% fee back to ourselves as ~99% LP holder via the pair's K-invariant accounting). Attacker's LP claim ≈ what they put in, modulo the `MINIMUM_LIQUIDITY` lock and a tiny share of the fee they paid. **Net P&L ≤ 0** — the attack is cost-negative. This property was previously asserted directly but is no longer guarded by an automated test; future protocol changes that touch the rebalance / deposit path should re-derive it manually.

### Pool-open precision

Honest graduations open at 0 bps gap (Regime 1, exact direct mint). Dust mint pre-seeds also open at ~0 bps — they take the `_seedDirectMint` fallback, which deposits at the cached ratio with only a vanishing skew from the dust reserves. Larger mint pre-seeds (where the rebalance swap fires) open within ~50 bps — the structural ceiling is the V2 fee landing between rebalance and deposit (~30 bps) plus integer rounding in the router's `quote()`-based split (~10 bps). 50 bps is well inside "exploit denied" — arbitrage closes the gap within blocks and the attacker still loses pre-seed value.
```
