## Title
Budget-capped hostile-pre-seed rebalance permanently opens the graduation LP off curve-close price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding._seedUniswapV2Direct`'s Regime 3 defense (mint-pre-seed rebalance) caps the corrective swap at 99% of the available inventory via `_swapBudget`. When an attacker pre-seeds the HyperSwap pair at a sufficiently extreme ratio, the capped swap cannot fully correct the pool back to the curve-close price before `_routerDepositAndDispose` deposits the remaining inventory. The protocol's own LP — the position locked forever in `LPLock` — is then permanently seeded at a materially wrong price, and the resulting arbitrage is captured by whoever races to correct it, not by the protocol or by token holders.

### Finding Description
`_seedUniswapV2Direct` branches into `_seedRebalancing` when the HyperSwap pair already has non-zero-supply LP (Regime 3, "mint pre-seed"). This path computes a no-fee swap input to move the pool toward the cached curve-close ratio via `_pairRebalance`, but the swap amount is deliberately capped: [1](#0-0) 

The cap is 99% of the smaller-side inventory (`_ltSwapInventory` / `IERC20(tokenAddress).balanceOf(address(this))`), chosen purely to guarantee the subsequent `addLiquidity` call has non-zero amounts on both sides — not to guarantee price correctness: [2](#0-1) 

`_pairRebalance` executes the (possibly-capped) swap directly against the pair and returns, regardless of whether the resulting ratio actually reached the target: [3](#0-2) 

`_routerDepositAndDispose` then deposits whatever remains at whatever ratio the pool landed at, and this deposit becomes the LP that is permanently locked in `LPLock` with no withdraw path: [4](#0-3) 

The protocol's own natspec and design notes acknowledge this residual explicitly: the team rejected a revert-on-skew check because it reintroduces brick risk, accepting instead that "larger mint pre-seeds ... open within ~50 bps" as normal — but this bound assumes the rebalance swap isn't budget-capped. When it is (extreme pre-seed ratios), the gap can be far larger, as directly demonstrated by the repository's own fuzz/regression tests: [5](#0-4) 

The test explicitly measures the resulting price as more than 20% off curve-close and only asserts that the *attacker's* P&L is non-positive — it does not (and by construction cannot) assert that the LP opened near the curve-close price: [6](#0-5) 

### Impact Explanation
The "zero price gap" property is documented as invariant #1 of graduation and is the core economic guarantee of the LP-seeding design (`docs/contracts-scope.md` invariants table). This invariant is broken whenever a pre-seed's imbalance exceeds the 99%-of-inventory swap budget. Because the LP is minted directly to `LPLock`, which has no withdraw/rescue path in v1, the mispriced position is permanent — any first-hitting third-party arbitrageur profits at the expense of the token's LP (i.e., the protocol/creator/holders' locked liquidity), not the attacker who set up the pre-seed. This is a real, unbacked-value transfer out of the protocol-controlled LP position — squarely inside the "LP seeded away from the curve close price" impact category, reachable by any unprivileged address pre-seeding the pair between phase 1 (`_enterGraduating`) and the permissionless phase 2 (`finalizeGraduation`).

### Likelihood Explanation
Any unprivileged address can trigger this: watch for a `TokenGraduating` event (phase 1), then call `factory.createPair` (if not already created), `transfer` both TOKEN and LT to the pair at an extreme ratio, and `pair.mint(attacker)` before the permissionless `finalizeGraduation` lands. The attack requires no privileged role, no upgrade, and no off-chain dependency — only capital proportional to `tokensForLP`/`ltFromPair` (which are public via `pendingGraduation(token)`) and speed to front-run the keeper (the repo notes keeper finalize lands within ~60s, giving an attacker a real window on a contested/valuable graduation).

### Recommendation
Bound the acceptable pool skew independent of "does the deposit succeed": either (a) size the swap budget dynamically so it's always sufficient to fully correct any pre-seed magnitude (mass-conservation permitting, e.g., by disposing more of the off-ratio side rather than depositing it), or (b) after the capped rebalance, measure the resulting price gap and route any excess deviation into `_sweepLTToOwner`/burn rather than into `LPLock`'s deposit, so the locked LP never opens beyond a fixed bps tolerance from curve-close, at the cost of a smaller (but correctly-priced) locked LP position.

### Proof of Concept
The repository's own `testFuzz_hostilePreSeed_neverProfitable_neverBricks` and `test_hostilePreSeed_M02_*`-style tests in `packages/contracts/test/TwoPhaseGraduation.t.sol` (lines 871-917) already construct this exactly: pre-seed the pair with `reserveToken = tokensForLP/100` and `reserveLt = ltFromPair*200` via `_grieferMintPreSeed`, then call `bonding.finalizeGraduation(tokenAddr)`. The assertion at lines 896-900 confirms the resulting pool price is more than 20% off the curve-close price, with the LP permanently locked in `LPLock` at that off-market price. [5](#0-4)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1310-1354)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1449-1471)
```text
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L871-900)
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
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L910-917)
```text
        // P&L: the pre-seeder's residual LP, valued at the fair (curve-close)
        // price, is worth a fraction of what they deposited — the attack is
        // cost-negative.
        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        assertLe(claimValue, depositValue, "pre-seeder must not profit (P&L <= 0)");
        assertLt(claimValue * 2, depositValue, "pre-seeder must lose materially, not merely break even");
    }
```
