### Title
Hostile mint pre-seed can force the HyperSwap graduation LP to open materially off curve-close price when the rebalance swap is budget-capped - ([File: packages/contracts/src/Bonding.sol])

### Summary
The Skipper advisory (GHSA-mxxc-p822-2hx9) is about an unprivileged actor pointing an externally-resolved target (a K8s `ExternalName` Service) so that a privileged component's network access reaches somewhere the operator never intended, with no allowlist on the resolvable target. The alt.fun analog explicitly called out in scope is the HyperSwap V2 `TOKEN/LT` pair, which is permissionlessly creatable/seedable by any address before `Bonding.finalizeGraduation` runs (`_ensureUniswapV2Pair`, `packages/contracts/src/Bonding.sol:1121`). alt.fun has built extensive defenses against this (`_seedUniswapV2Direct`'s three-regime logic), but the documented "budget-capped swap" residual case (M-02) means the protocol's own defense can still be driven to open the graduated LP at a price materially different from the bonding-curve close price by an unprivileged attacker.

### Finding Description
`_seedRebalancing` (`packages/contracts/src/Bonding.sol:1279-1354`) rebalances a hostile mint pre-seed toward the curve-close ratio via a direct `pair.swap`, capped at 99% of the available inventory side (`_swapBudget`, `Bonding.sol:1374-1378`). This cap exists specifically to prevent the deposit leg (`_routerDepositAndDispose`) from being starved to zero and bricking `finalizeGraduation`. However, the natspec on `_swapBudget` (`Bonding.sol:1356-1378`) and the codebase's own regression test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` (`packages/contracts/test/TwoPhaseGraduation.t.sol:864-900`) both confirm that when an attacker pre-seeds the pair with a sufficiently extreme ratio (e.g. LT reserve ≈200x the TOKEN reserve relative to the curve-close target), the optimal no-fee rebalance swap exceeds the per-side budget, the swap is clamped, and the pool is left "~2x off curve-close" after `finalizeGraduation` completes — i.e., the LP that `LPLock` permanently holds opens at a price that diverges materially (well beyond the ~50 bps ceiling of the normal swap-path case documented in `packages/contracts/AGENTS.md`) from the bonding-curve's final trade price.

This is reachable by any unprivileged address: create the `TOKEN`/`LT` pair via the public HyperSwap V2 factory (`factory.createPair(token, lt)` is permissionless on a real UniswapV2 factory), transfer TOKEN/LT to it at a hostile ratio, and call `pair.mint(attacker)` — exactly the front-run sequence already modeled in `_grieferMintPreSeed` (`packages/contracts/test/TwoPhaseGraduation.t.sol:501-516`). No special permission or timing race against the keeper is required beyond getting the pre-seed in before `finalizeGraduation` executes, which for any freshly-`Graduating` token is an open window.

### Impact Explanation
The mispriced pool that results is permanent: `finalizeGraduation` locks the resulting LP tokens into `LPLock`, which "has no withdraw / rescue path in v1" (per `Bonding.sol` comments at lines 1152-1154 and 1211-1213), so the protocol/LP position cannot be corrected after the fact. A pool opening materially off the curve-close price is immediately arbitrageable by anyone: post-graduation traders (and the protocol's own locked LP) absorb the loss as arbitrageurs trade the pool back toward fair value, extracting value from the LP's reserves. This matches the explicitly accepted impact category in scope: "an LP seeded away from the curve close price." While the documentation frames the *attacker's own P&L* as non-profitable in this specific regime (their pre-existing dust LP claim is worth less than what they put in), the LP itself — funded by curve-raised trader/creator funds — is still seeded at a bad price and that value is transferred out via arbitrage, which is a loss to the protocol's locked LP position (funded by `Bonding`'s curve proceeds), not the attacker's problem.

### Likelihood Explanation
This requires the attacker to fund an unusually extreme skew (e.g. ~200x the target ratio on one side) so the optimal no-fee rebalance input exceeds the per-side budget — a deliberate, capital-committing action rather than a cheap dust attack. It is more expensive than the "cheap" dust variants the codebase's Regime 1–3 logic fully neutralizes, but it is still executable by any address with modest capital (only one side needs to be large; the other can be tiny), it requires no privileged role, and the codebase's own test suite explicitly reproduces and accepts this exact scenario as a known residual rather than a fixed one (see the `AGENTS.md` note that the P&L≤0 property is "no longer guarded by an automated test" and the M-02 test's docstring acknowledging "the pool opens materially off curve-close" as expected behavior).

### Recommendation
Either (a) widen the per-side rebalance budget or use the LP-locked `lpReserveTotal`/full-graduation inventory (not just the graduation's earmarked `tokensForLP`/`ltFromPair`) so the swap can fully correct even extreme skews before the 99% cap binds, or (b) detect the budget-capped case explicitly and reject/queue that specific graduation for an admin-assisted repricing path instead of silently accepting a mispriced LP lock, or (c) size the per-graduation LT/token inventory dynamically so the swap budget scales with the actual pre-seed size rather than a fixed graduation-time reserve. At minimum, restore automated regression coverage asserting attacker P&L ≤ 0 *and* bound the maximum acceptable price deviation for the budget-capped path, failing closed (revert/park) rather than silently locking a severely mispriced LP.

### Proof of Concept
Adapted directly from the repo's own regression test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` (`packages/contracts/test/TwoPhaseGraduation.t.sol:864-900`):

1. Launch a token and buy it up into `Graduating` (`_enterGraduating`).
2. Read `(tokensForLP, ltFromPair)` from `bonding.pendingGraduation(tokenAddr)`.
3. As an unprivileged griefer, call the real HyperSwap V2 factory's permissionless `createPair(tokenAddr, address(lt))`.
4. Fund the pair with `reserveToken = tokensForLP / 100` and `reserveLt = ltFromPair * 200` (confirmed in the test to make the optimal no-fee rebalance swap exceed 99% of the swap budget).
5. Call `pair.mint(griefer)` to lock in this hostile ratio.
6. Anyone calls `bonding.finalizeGraduation(tokenAddr)` — it succeeds (no brick), but the pool's final price (`_poolPriceLtPerToken`) is verified to be >20% above the curve-close target, i.e. the LP is permanently locked in `LPLock` at a materially mispriced ratio. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L858-900)
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
```
