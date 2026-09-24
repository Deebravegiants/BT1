Based on the evidence gathered, this bug class already has a documented, tested, and explicitly *accepted* residual in alt.fun — the M-02 hostile-mint-pre-seed defense — which is the direct analog to the "restoring the vault" report.

### Title
LP seeded away from curve-close price under extreme hostile mint pre-seed, permanently mispricing the locked LP - ([File: packages/contracts/src/Bonding.sol])

### Summary
`finalizeGraduation` deposits the cached `(tokensForLP, ltFromPair)` inventory into the HyperSwap V2 pair using whatever reserve ratio is present at call time, applying only a *budget-capped* rebalance swap (`_pairRebalance`, capped at 99% of one side via `_swapBudget`) before depositing via `_routerDepositAndDispose`. When an attacker front-runs `finalizeGraduation` with an extreme `pair.mint` pre-seed ratio, the optimal rebalance input exceeds the per-side budget, and the swap cannot fully correct the ratio before deposit — exactly mirroring the reported Notional pattern where restoring liquidity at "whatever the current pool balances happen to be" produces a worse LP position than the actual value deposited.

### Finding Description
`_seedRebalancing`/`_pairRebalance` compute a no-fee closed-form swap input (`_noFeeSwapInput`) intended to drive the HyperSwap pair back to the `tokensForLP / ltFromPair` curve-close ratio before `_routerDepositAndDispose` calls `router.addLiquidity`. [1](#0-0)  The swap input is deliberately capped at 99% of the available side's inventory via `_swapBudget`, specifically to avoid bricking `finalizeGraduation` when a pre-seed is extreme. [2](#0-1)  When the optimal correction exceeds this budget (an attacker mints a sufficiently lopsided ratio, e.g. TOKEN reserve at 1% of `tokensForLP` and LT reserve at 200x `ltFromPair`), the swap only partially corrects the ratio and `_routerDepositAndDispose` deposits the remaining inventory at a price that is materially off the curve-close price. [3](#0-2)  The protocol's own repo test explicitly demonstrates and accepts this: `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` asserts the pool "opens materially off curve-close" and only checks that the *attacker* doesn't profit — it does not check that the community's locked LP (`LPLock`, non-recoverable in v1) opens at fair value. [4](#0-3)  The LP tokens are minted straight to `LPLock`, which has no withdraw/rescue path in v1, so a mispriced LP position is permanently locked. [5](#0-4) 

### Impact Explanation
The attack is triggerable by an unprivileged wallet that simply front-runs `finalizeGraduation` with `factory.createPair` + `transfer` + `pair.mint(attacker)` using an extreme reserve ratio (any wallet can hold TOKEN from a small curve buy and any LT amount). This causes the protocol's fixed, curve-priced LP inventory (`tokensForLP`, `ltFromPair`, cached at phase 1 and never re-priced) to be deposited into HyperSwap at a materially skewed ratio, opening the token's post-graduation trading price away from its true curve-close price. Because the deposit is a one-shot, non-reversible `LPLock.recordLock` with no rescue path, this is a permanent mispricing/value loss to the protocol-owned LP position (and, transitively, to the community/creator claim represented by `LP_RESERVE`) — directly matching the accepted-impact category "an LP seeded away from the curve close price."

### Likelihood Explanation
This requires no privileged role and no market conditions beyond acquiring some TOKEN via a normal curve buy and some LT (freely tradable/mintable via `Zap`). `finalizeGraduation` is explicitly permissionless and designed to be callable "even under any pre-seed shape," so an attacker choosing an extreme ratio is a foreseeable and directly reachable griefing path, and the repository's own test suite already reproduces the exact off-ratio outcome (`test_hostilePreSeed_budgetCappedSwap_isNotProfitable`, `testFuzz_hostilePreSeed_neverProfitable_neverBricks`) — confirming the scenario is real and currently only mitigated for attacker profitability, not for LP-price fidelity.

### Recommendation
Extend the M-02 defense so it also bounds the *LP-opening-price deviation*, not just attacker profitability: e.g., increase the rebalance budget dynamically based on pre-seed severity, split the correction across more than one swap leg, or (mirroring the original report's own recommendation) allow the protocol owner/keeper to inject an external-market top-up trade before `_routerDepositAndDispose` so that catastrophic ratio pre-seeds no longer force a materially off-ratio deposit into the permanently-locked LP.

### Proof of Concept
Use the existing repository test as the concrete reproduction: `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `test/TwoPhaseGraduation.t.sol` sets `reserveToken = tokensForLP / 100` and `reserveLt = ltFromPair * 200` via `_grieferMintPreSeed`, then calls `bonding.finalizeGraduation(tokenAddr)` and asserts the resulting pool price is more than 1.2x the curve-close target (`_poolPriceLtPerToken(hyperPair, tokenAddr) > (((ltFromPair * 1e18) / tokensForLP) * 12) / 10`), demonstrating the LP is seeded materially away from curve-close price and permanently locked in `LPLock`. [6](#0-5)

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

**File:** packages/contracts/AGENTS.md (L1152-1154)
```markdown

```
