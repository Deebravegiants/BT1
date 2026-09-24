Based on my research, the codebase's own test suite (`test_hostilePreSeed_budgetCappedSwap_isNotProfitable`, aka "M-02") already documents and accepts a residual risk that matches the "LP seeded away from curve close price" impact criterion. While the team's own analysis frames this as "attacker not profitable," the actual harm lands on the protocol's locked LP (and thus its holders), not on the attacker — a distinct victim from the one the mitigation was designed to protect.

### Title
HyperSwap LP graduation can permanently open materially off the curve-close price under a budget-capped hostile pre-seed - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` seeds the HyperSwap V2 TOKEN/LT pair via `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance`/`_routerDepositAndDispose`. When an attacker front-runs the pair with an extreme mint pre-seed whose optimal correcting swap exceeds the protocol's 99%-of-inventory swap budget, the rebalance swap is capped and cannot fully correct the pool ratio before the deposit executes, so the pool permanently opens materially (up to ~2x, by the test's own assertion) off the curve-close price.

### Finding Description
`_seedRebalancing` computes the direction and magnitude of a corrective swap via `_noFeeSwapInput`, then calls `_pairRebalance`, which executes the swap directly against the pair (`pair.swap`) capped at `_swapBudget(inventory) = inventory * 99 / 100`: [1](#0-0) 

The budget cap exists purely to guarantee `_routerDepositAndDispose`'s subsequent `addLiquidity` call always has non-zero amounts on both sides (brick resistance), not to guarantee the pool reaches the curve-close ratio: [2](#0-1) 

When the optimal corrective swap size exceeds this budget (an "LT-rich" pre-seed with a disproportionately large LT reserve relative to a tiny token reserve), the capped swap under-corrects the ratio, and `_routerDepositAndDispose` then deposits the remaining inventory at the router's quote-derived ratio, which is still far from the curve-close ratio: [3](#0-2) 

The protocol's own regression test for this exact regime (labelled "M-02") explicitly asserts the resulting pool price is more than 20% off curve-close, and only checks that the *attacker* who created the pre-seed cannot profit — it does not check, and the code does not defend against, the resulting mispricing harming the protocol's own locked LP position: [4](#0-3) 

### Impact Explanation
Once `finalizeGraduation` completes, `LPLock.recordLock` is called and the mispriced LP is permanently locked with no rescue path (per the codebase's own documentation, `LPLock` has no withdraw/rescue mechanism in v1): [5](#0-4) 

A pool opening materially off the curve-close price is an open invitation for arbitrage bots to trade against it, extracting value from the locked LP position (which ultimately represents value the protocol/community intended to retain in the graduated pool) — the exact harm the "Dynamic LP Seeding (zero price gap)" design is meant to prevent, per the protocol's own docs: [6](#0-5) 
While the pre-seeding attacker's own capital nets negative (per the M-02 test's P&L assertions), the mispricing itself is irreversible and the value drained by third-party arbitrageurs comes out of the permanently-locked protocol LP, not the attacker. This is a real, if bounded and expensive-to-trigger, freezing/loss of LP value.

### Likelihood Explanation
Triggering the M-02 regime requires an attacker to pre-fund a HyperSwap pair with an extreme LT-rich ratio (in the test, LT reserve = 200× `ltFromPair` and TOKEN reserve = 1% of `tokensForLP`) between phase 1 (`_enterGraduating`) and phase 2 (`finalizeGraduation`). This is capital-intensive in absolute USD terms for tokens that graduate via the $9K USD trigger, but the LT amount needed scales with `ltFromPair`, which can be small for tokens that graduate via the supply-exhaustion trigger in a bear market (`IPair.tokenBalance() == 0`) with little real LT raised — making the attack considerably cheaper in that specific scenario. The token side is obtainable via ordinary curve buys before graduation.

### Recommendation
Either (a) widen the swap budget or add a second rebalancing pass/swap direction so the pool can be driven closer to the curve-close ratio even under extreme pre-seed ratios, accepting the mass-conservation tradeoff differently (e.g., burn/dispose more of the off-ratio side rather than depositing at a still-skewed ratio), or (b) explicitly bound how far off curve-close the deposit is allowed to land, and if the budget-capped correction can't reach that bound, defer the deposit (e.g., mint LP into an escrow that can be corrected/topped up in a follow-up permissionless call) rather than locking a materially mispriced position irrevocably via `LPLock.recordLock`.

### Proof of Concept
See `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `test/TwoPhaseGraduation.t.sol` (lines 864-917), which already reproduces the scenario: it pre-seeds a HyperSwap pair with `reserveToken = tokensForLP / 100` and `reserveLt = ltFromPair * 200`, calls `bonding.finalizeGraduation(tokenAddr)`, and asserts: [7](#0-6) 
demonstrating the pool opens at more than 1.2x the curve-close price, which per the code comment is understated ("the pool stays ~2x off curve-close after the swap").

### Citations

**File:** packages/contracts/src/Bonding.sol (L1025-1033)
```text
        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
```

**File:** packages/contracts/src/Bonding.sol (L1316-1353)
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
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
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

**File:** docs/contracts-scope.md (L79-83)
```markdown
### Dynamic LP Seeding (zero price gap)

The problem: the reserve asset (LT) has a varying USD price, so the exact number of LP tokens needed to make the DEX pool open at the last curve price is not known ahead of time. Naively seeding the LP with the full 250M reserve would create a large price gap that arbitrage bots would immediately close, transferring value out of the protocol.

Our approach: compute the exact `tokensForLP` at graduation time so the LP opens at **precisely** the last curve price. Burn whatever is left of the 250M reserve.
```
