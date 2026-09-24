### Title
Budget-capped hostile-mint pre-seed lets an unrelated wallet force the HyperSwap V2 graduation LP to open materially off the curve-close price, letting anyone arbitrage value out of the protocol-locked LP - (File: packages/contracts/src/Bonding.sol)

### Summary
`finalizeGraduation` (permissionless) seeds the HyperSwap V2 TOKEN/LT pair via `_seedUniswapV2Direct → _seedRebalancing → _pairRebalance → _routerDepositAndDispose`. Any unrelated wallet can front-run phase 2 by creating the HyperSwap pair and calling `pair.mint()` against a self-funded, extremely LT-rich or token-rich deposit. The rebalance swap that is supposed to correct the ratio back to the cached curve-close price (`tokensForLP` / `ltFromPair`) is capped at 99% of the available inventory (`_swapBudget`), so for sufficiently skewed pre-seed ratios the optimal correcting swap exceeds the budget and the pool is deposited materially off the curve-close price. This is the same bug class as the D3X AI incident's `exchange()`-relies-on-manipulable-spot-price root cause, mapped onto alt.fun's own LP-seeding code rather than D3X's own contract.

### Finding Description
`_seedUniswapV2Direct` (`packages/contracts/src/Bonding.sol`, ~lines 1201-1234) branches on the state of the HyperSwap pair at `finalizeGraduation` time:

- Regime 1 (`totalSupply()==0`): direct mint at the cached ratio, price-exact.
- Regime 2: pure donation, skimmed and collapsed into Regime 1.
- Regime 3 (`pair.mint` already called by an attacker): `_seedRebalancing` (lines ~1279-1354) computes which side is rich, and calls `_pairRebalance` with `maxSwap: _swapBudget(...)` where `_swapBudget` (lines ~1374-1378) hard-caps the correcting swap at `(budget * 99) / 100`.

`_pairRebalance` computes the no-fee-optimal swap input via `_noFeeSwapInput` and, when the unconstrained optimum exceeds `maxSwap`, the swap is clamped to the 99% budget rather than reaching the target ratio. The remaining inventory is then deposited via `_routerDepositAndDispose`'s `addLiquidity(..., 1, 1, lpLock_, ...)` at whatever ratio the capped swap left the pool at — which for extreme pre-seeds is materially different from `ltFromPair / tokensForLP`.

The protocol's own regression test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` (`packages/contracts/test/TwoPhaseGraduation.t.sol`, lines 858-917) constructs exactly this scenario (TOKEN side at 1% of target, LT side at 200x target) and asserts:
```
assertGt(
    _poolPriceLtPerToken(hyperPair, tokenAddr),
    (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
    "M-02 regime: pool opens materially off curve-close"
);
```
i.e. the finalized pool price is proven, by the team's own test, to land ≥20% off the curve-close price for this pre-seed shape. The test only asserts that the *pre-seeder's own captured LP share*, valued at the fair price, is not profitable (`claimValue <= depositValue`) — it does not, and cannot, prevent a *third, unrelated* wallet from immediately swapping against the now-mispriced HyperSwap pool to arbitrage the gap, since `finalizeGraduation` is fully permissionless and the resulting pair is a real, unrestricted HyperSwap V2 pool anyone can trade on the instant it exists.

Because the locked LP (`LPLock`) is funded from the curve's real raised LT (`ltFromPair`) and the reserved token allocation (`tokensForLP`) — i.e. protocol/creator/trader-attributable value, not the attacker's — any arbitrage against the mispriced pool is extracted from that LP-owned reserve, not from the pre-seeder's own deposit. This is a distinct loss channel from the "pre-seeder P&L ≤ 0" property the existing test verifies. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
The LP seeded into the HyperSwap TOKEN/LT pair is the curve-raised, trader/creator-attributable value (`ltFromPair` and `tokensForLP`), locked via `LPLock.recordLock`, which `finalizeGraduation` "cannot skip." When the pool is forced open ≥20%+ off the curve-close price by an extreme hostile mint pre-seed, arbitrageurs (which can be the same pre-seeding wallet using a second address, or any third party) can immediately trade against the newly-created, permissionless HyperSwap pool to capture the price gap. Because the mis-seeded reserves belong to the protocol's locked LP rather than the attacker's own deposit, this arbitrage is a direct value transfer out of trader/LP-owned funds — an "LP seeded away from the curve close price" outcome that the validation rules explicitly recognize as an acceptable impact class, independent of whether the pre-seeder's own captured LP share nets positive.

### Likelihood Explanation
`finalizeGraduation` is permissionless and must run against whatever HyperSwap pair state exists at call time; `factory.createPair` and `pair.mint` on the underlying HyperSwap V2 factory/pair are also permissionless, so any unrelated wallet can pre-seed the pair between phase 1 (`_enterGraduating`) and phase 2 (`finalizeGraduation`) with an arbitrarily skewed ratio at the cost of the pre-seed capital only (per `_seedRebalancing`'s reserve-vs-target comparison, the more extreme the ratio, the larger the residual gap survives the 99%-budget-capped rebalance swap). The team's own fuzz/regression suite already demonstrates this "M-02" regime is reachable and produces a materially off-ratio pool, confirming the mechanism is not merely theoretical.

### Recommendation
- Do not treat "pre-seeder P&L ≤ 0" as sufficient mitigation; separately bound or eliminate the residual pool-price gap itself, e.g. by widening the swap budget dynamically (using more of the protocol's own idle LT/token inventory) or by depositing a symmetric "make-whole" amount from Bonding's own reserves when the pre-swap ratio cannot be corrected within budget.
- Consider disincentivizing the pre-seed race entirely (e.g., an atomic create-and-seed path that removes the window between phase 1 and phase 2 during which a hostile pre-seed can be planted), or add a minimum lock/cool-down before external LPs can arbitrage a freshly-finalized graduation pool, giving the protocol (or a keeper) a chance to correct the ratio first.
- At minimum, monitor/alert on `finalizeGraduation` calls that hit the `_swapBudget`-capped branch so the resulting price gap can be corrected off-chain quickly, and document the residual value-leak (distinct from pre-seeder profitability) so it's tracked rather than assumed already fixed.

### Proof of Concept
This is directly reproduced by the protocol's own test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable`:
1. Launch a token and drive it to `Lifecycle.Graduating` (`_enterGraduating`), caching `tokensForLP` / `ltFromPair`.
2. Before `finalizeGraduation` is called, an unrelated wallet ("griefer") creates the HyperSwap TOKEN/LT pair and calls `pair.mint()` against a self-funded deposit sized at `reserveToken = tokensForLP / 100`, `reserveLt = ltFromPair * 200` (a 200x LT-rich, 1%-token pre-seed).
3. Anyone calls `bonding.finalizeGraduation(tokenAddr)` (permissionless). `_seedRebalancing` detects the pool is LT-rich, computes the optimal correcting swap via `_noFeeSwapInput`, finds it exceeds the 99%-of-budget cap (`_swapBudget`), and executes the capped swap anyway via `_pairRebalance`, then deposits the remainder via `_routerDepositAndDispose`.
4. Post-finalize, `_poolPriceLtPerToken(hyperPair, tokenAddr) > 1.2 × (ltFromPair * 1e18 / tokensForLP)` — the pool is proven, by the test's own assertion, to open ≥20% off the curve-close price.
5. Any third-party wallet can now submit a normal swap against `hyperPair` to arbitrage this gap, extracting value from the LP that `LPLock` holds on behalf of the protocol/creator/traders — a loss distinct from, and not precluded by, the existing "pre-seeder P&L ≤ 0" test. [4](#0-3)

### Citations

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

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L858-917)
```text
    /// @notice M-02 reproducer. An LT-rich mint pre-seed so lopsided that the
    ///         TOKEN-side rebalance swap exhausts its full budget (~99% of
    ///         `tokensForLP`) without reaching the cached ratio, so the pool
    ///         deposits materially off curve-close. Finalize must still succeed
    ///         (no brick), the over-funded LT side must be confiscated to the
    ///         owner, and the pre-seeder must end net-negative.
    function test_hostilePreSeed_budgetCappedSwap_isNotProfitable() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);

        // Extreme LT-rich shape: TOKEN side at 1% of target, LT side at 200x.
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
