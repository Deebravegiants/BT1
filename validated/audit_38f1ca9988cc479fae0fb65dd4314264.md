### Title
LP seeded materially off curve-close price via budget-capped rebalance swap in `Bonding._seedRebalancing` - ([File: packages/contracts/src/Bonding.sol])

### Summary
Any unprivileged wallet can permissionlessly create the HyperSwap V2 TOKEN/LT pair for a curve that is about to graduate and mint a sufficiently lopsided LP position into it before `Bonding.finalizeGraduation` runs. The protocol's own pre-seed defense (`_seedRebalancing` → `_pairRebalance`) is designed to arb the pool back to the curve-close ratio, but the rebalance swap is intentionally capped at 99% of the available side's inventory (`_swapBudget`, [1](#0-0) ). When the pre-seed skew is large enough that the closed-form no-fee correction (`_noFeeSwapInput`) exceeds that cap, the swap only partially corrects the ratio and the subsequently deposited LP opens at a price that is materially different (the protocol's own regression test measures >20% deviation) from the curve's actual closing price — a direct analog to the DOLA-price-manipulation-driven mispricing in the Inverse Finance incident, here applied to alt.fun's own AMM-seeding step.

### Finding Description
`finalizeGraduation` is permissionless and callable by anyone once a token enters `Lifecycle.Graduating` ( [2](#0-1) ). Between phase 1 (`_enterGraduating`, which pins `tokensForLP`/`ltFromPair` at the last curve price) and phase 2, `_ensureUniswapV2Pair` will create the pair if it doesn't already exist, and anyone can pre-fund and `pair.mint()` into it at an arbitrary ratio ( [3](#0-2) ).

`_seedUniswapV2Direct`/`_seedRebalancing` detect this non-empty, non-zero-supply pre-seed and try to correct it via a direct `pair.swap` sized by `_noFeeSwapInput`, then deposit the remainder through the router's `addLiquidity` ( [4](#0-3) ). The swap input is deliberately clamped to `_swapBudget` = 99% of the swap-side's available balance so that `addLiquidity` never sees a fully-drained side ( [5](#0-4) ). For an extreme enough pre-seed ratio, the ideal correcting swap size computed by `_noFeeSwapInput` exceeds this budget, so `_pairRebalance` only moves the pool part of the way to the cached curve-close ratio ( [6](#0-5) ). The remaining inventory is then deposited via `router.addLiquidity` at that still-skewed post-swap ratio, so the LP that `LPLock.recordLock` locks in for token holders/creator/protocol opens meaningfully away from the true curve-close price.

The protocol's own tests confirm and quantify this residual: `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` constructs a 200x LT-rich mint pre-seed, verifies the ideal correction exceeds the 99% budget, and asserts the resulting pool price is `> 1.2×` the curve-close price — i.e., the graduation LP opens materially mispriced by design ( [7](#0-6) ).

### Impact Explanation
The mispriced pool is exactly the "LP seeded away from the curve close price" harm class this scan is validating against. Once graduation finalizes at a skewed price, the first arbitrageurs to trade against the newly-opened HyperSwap pool extract the price gap from the locked LP — value that should have accrued to the protocol/creator-owned locked liquidity (and, transitively, to holders relying on that liquidity depth) is instead transferred to arbitrage bots. Because `LPLock` in v1 has no rescue/rebalance path (per `AGENTS.md`), this mispricing and its associated value leakage is permanent and unrecoverable once locked. This is a concrete, protocol-level economic loss distinct from the attacker's own (non-profitable) P&L, so it satisfies the "LP seeded away from curve close price" acceptance bar even though the pre-seeder personally nets negative.

### Likelihood Explanation
The precondition — a single unprivileged wallet permissionlessly creating the HyperSwap pair and minting an extreme-ratio dust/mint pre-seed before `finalizeGraduation` lands — is directly reachable by any address with a small amount of capital (the mint pre-seed budget scales with `tokensForLP`/`ltFromPair`, both of which are small at typical launch sizes). No privileged role, upgrade, or off-chain assumption is required; the flow is racing a public mempool transaction (`finalizeGraduation`), which is the same threat model the codebase's own `AGENTS.md` and `TwoPhaseGraduation.t.sol` already anticipate and partially, but not fully, mitigate.

### Recommendation
Either (a) remove the fixed 99% swap-budget cap and instead allow `_pairRebalance` to consume up to 100% of available inventory while still guaranteeing a non-zero deposit through a smarter split (e.g., reserving a fixed minimal absolute amount rather than a fixed percentage), or (b) detect when the required correction exceeds the safely-swappable budget and fall back to a widened "wait and retry" / permissioned recovery path rather than depositing at a still-skewed ratio, or (c) enforce a maximum acceptable post-rebalance price deviation from the cached curve-close ratio and, if exceeded, route the excess LT/TOKEN into a compensating mechanism (e.g., additional protocol-funded rebalancing) instead of silently locking a mispriced LP.

### Proof of Concept
The existing regression test demonstrates the vulnerable path end-to-end: [8](#0-7) 
1. Launch a token and drive it into `Graduating` (`_enterGraduating`).
2. Attacker calls `hsFactory.createPair(tokenAddr, lt)`, funds the pair with `reserveToken = tokensForLP/100` and `reserveLt = ltFromPair*200`, and calls `pair.mint(attacker)` — a purely permissionless sequence.
3. Anyone calls `bonding.finalizeGraduation(tokenAddr)`. `_pairRebalance`'s ideal correction exceeds `_swapBudget`, so the swap is capped and the deposited LP opens at `> 1.2×` the true curve-close LT-per-token price, confirmed by the test's own assertion on `_poolPriceLtPerToken`.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1279-1353)
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

**File:** packages/contracts/src/Bonding.sol (L1414-1430)
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
