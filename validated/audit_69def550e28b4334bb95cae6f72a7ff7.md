### Title
Attacker with sufficient pre-seed capital overpowers the graduation rebalance's budget cap and forces the HyperSwap LP to open materially off the curve-close price - (File: packages/contracts/src/Bonding.sol)

### Summary
The FaultDisputeGame report describes an attacker whose only real resource advantage — more available funds — lets it overpower a defense mechanism whose corrective power is bounded, producing an incorrect outcome despite an honest party's participation. Alt.fun's two-phase graduation LP-seeding defense (`_seedRebalancing` / `_pairRebalance` / `_swapBudget` in [1](#0-0) ) has the same shape: its corrective rebalance swap is capped at a fixed budget derived from the protocol's own curve-raised inventory, while the attacker's hostile pre-seed size is unbounded by anything except the attacker's own capital. A well-funded attacker can therefore pre-seed the pair with a ratio the bounded rebalance cannot fully correct, and `finalizeGraduation` seeds the locked LP materially away from the curve-close price.

### Finding Description
`finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` handles the case where an attacker front-runs graduation by creating the HyperSwap `TOKEN/LT` pair and calling `pair.mint` against a self-funded, ratio-skewed deposit ( [2](#0-1) ). To fix the ratio, `_pairRebalance` computes the no-fee swap input needed to move the pool back to the curve-close ratio, but that swap is capped via `_swapBudget`, which reserves only 99% of `Bonding`'s own LT or token inventory for the correction ( [3](#0-2) ):

```solidity
function _swapBudget(uint256 budget) internal pure returns (uint256) {
    return (budget * 99) / 100;
}
```

This budget is fixed by the size of the graduation's own `tokensForLP` / `ltFromPair` (the curve-raised liquidity), which is *not* attacker-controlled. The attacker's pre-seed ratio and magnitude, by contrast, are bounded only by how much LT and TOKEN the attacker is willing to buy/hold and transfer into the pair (`IERC20(token).transfer(pair, X)` + `lt.transfer(pair, Y)` + `pair.mint(attacker)`, all permissionless operations reachable by any wallet). When the required rebalance swap exceeds the fixed budget, `_pairRebalance` clamps to the budget and the residual skew is left uncorrected, so `_routerDepositAndDispose`'s deposit lands at a materially off-ratio price.

This is exactly the same "resource asymmetry beats correctness" bug class as the FaultDisputeGame report: the defensive mechanism's corrective capacity is fixed by the protocol's own funds, while the attacking party's leverage scales with its own capital, so a sufficiently funded attacker can force an outcome (an LP opened away from the honest curve-close price) that a resource-unconstrained defense would have prevented.

The codebase itself documents and quantifies this exact regime as "M-02": [4](#0-3) , where a 1:200 pre-seed ratio (`reserveToken = tokensForLP / 100`, `reserveLt = ltFromPair * 200`) causes the optimal rebalance swap to exceed the 99%-of-budget cap, and the assertion confirms the pool opens more than 20% off curve-close price:

```solidity
assertGt(
    _poolPriceLtPerToken(hyperPair, tokenAddr),
    (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
    "M-02 regime: pool opens materially off curve-close"
);
```

The fuzz test `testFuzz_hostilePreSeed_neverProfitable_neverBricks` ( [5](#0-4) ) sweeps `seedMultiple` up to 1000x and only asserts brick-resistance and attacker-P&L bounds — it does not assert any bound on how far the opening price can drift from curve-close, confirming the price-deviation magnitude scales with attacker-supplied capital and is left unbounded by design.

### Impact Explanation
The graduation LP is the price-discovery venue every post-graduation trader interacts with via `Zap`. An LP seeded materially off the curve-close price (documented as >20% in the existing regression, and unbounded in the fuzz sweep as the pre-seed multiple grows) directly harms every subsequent trader and the locked LP position itself: the locked LP (held by `LPLock`, which has no withdraw path in v1 — [6](#0-5) ) is permanently pinned to a mispriced reserve ratio, and arbitrageurs extract the gap from the protocol/LP-lock side rather than the price gap being zero as the zero-gap invariant promises. This matches the explicitly accepted impact category "an LP seeded away from the curve close price."

### Likelihood Explanation
Every step is permissionless and reachable by any unprivileged wallet: creating the HyperSwap pair (`factory.createPair`), transferring TOKEN/LT into it, and calling `pair.mint` are all standard ERC20/UniswapV2 operations requiring no special role. The only constraint is capital — the attacker needs enough LT and TOKEN to build a sufficiently skewed pre-seed relative to the target graduation's own `tokensForLP`/`ltFromPair` size, which for smaller or newly-graduating tokens can be a modest amount. The window is the entire `Graduating` phase (`_enterGraduating` → `finalizeGraduation`), during which the pre-seed can be built before the (keeper-driven, ~60s) permissionless finalize call lands.

### Recommendation
Do not cap the rebalance purely as a fixed fraction of the protocol's own inventory. Either (a) size the per-side swap budget dynamically against the attacker's actual pre-seed magnitude so the correction always fully re-prices the pool regardless of pre-seed size (accepting a larger burn/sweep of the excess side), or (b) reject/quarantine hostile mint pre-seeds whose implied price deviation would exceed an acceptable bound by minting the protocol's LP into a *fresh* pair address (if feasible) rather than the front-run one, or (c) explicitly bound and document the maximum acceptable price deviation and have `finalizeGraduation` fall back to a defensive path (e.g., routing the entire curve-raised liquidity to a rescue/manual-intervention flow) when the pre-existing skew exceeds that bound, rather than silently minting an off-price LP.

### Proof of Concept
Using the existing test harness pattern (`test/TwoPhaseGraduation.t.sol`):
1. Launch a token and drive it into `Lifecycle.Graduating` (`_enterGraduating`), fixing `tokensForLP` and `ltFromPair`.
2. As `griefer` (any unprivileged wallet), call `hsFactory.createPair(tokenAddr, address(lt))`.
3. Fund and transfer `reserveToken = tokensForLP / 100` and `reserveLt = ltFromPair * 200` into the pair, then call `pair.mint(griefer)` — a 1:200 skew relative to the honest curve-close ratio.
4. Call `bonding.finalizeGraduation(tokenAddr)` (permissionless).
5. Observe (as asserted in `testFuzz_hostilePreSeed_neverProfitable_neverBricks` / the M-02 regime test) that the resulting pool price is more than 20% off the curve-close ratio `ltFromPair / tokensForLP`, because `_swapBudget` capped the corrective swap at 99% of `Bonding`'s own LT inventory, which was too small to fully correct a 200x skew. [7](#0-6)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1275-1354)
```text
    /// @dev Hostile-mint-pre-seed branch of `_seedUniswapV2Direct`. Split
    ///      out because (a) it's the cold path (~99% of graduations hit
    ///      the empty-pair branch above) and (b) the local-variable density
    ///      would otherwise blow stack-too-deep.
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

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L860-917)
```text
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

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L926-960)
```text
    function testFuzz_hostilePreSeed_neverProfitable_neverBricks(
        uint256 seedMultiple,
        bool ltRich
    ) public {
        seedMultiple = bound(seedMultiple, 1, 1000);

        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);
        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);

        // One side held at its LP target, the other over-funded by
        // `seedMultiple`. Small multiples reach the cached ratio within budget;
        // large ones exhaust it and exercise the M-02 residual. Both rich
        // directions are covered by `ltRich`.
        (uint256 reserveToken, uint256 reserveLt) =
            ltRich ? (tokensForLP, ltFromPair * seedMultiple) : (tokensForLP * seedMultiple, ltFromPair);

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);

        // Brick-resistance: must succeed for every shape, and lock non-zero LP.
        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed for every pre-seed shape");
        assertGt(
            MockHyperswapPair(hyperPair).balanceOf(address(lpLockContract)), 0, "lpLock must hold non-zero protocol LP"
        );

        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        // Strict P&L bound; the small absolute slack only absorbs integer
        // rounding in the LP-claim arithmetic (sub-wei-relative), far below any
        // economically-meaningful subsidy.
        assertLe(claimValue, depositValue + 1e9, "pre-seeder LP claim must not exceed deposit (P&L <= 0)");
    }
```

**File:** packages/contracts/AGENTS.md (L66-66)
```markdown
| `LPLock.sol` | Graduation LP lock (UUPS, no withdraw in v1) |
```
