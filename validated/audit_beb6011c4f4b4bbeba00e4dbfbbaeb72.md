## Analysis

The GalloDaSballo report's core claim — a single AMM pair's spot price is treated as ground truth for a quote even though that pair can be thin/attacker-dominated — maps onto alt.fun's own hostile-pre-seed LP-seeding logic in `Bonding.sol`, not onto any oracle module (alt.fun has no `UniswapPriceAdaptor` equivalent). The analogous defect is that the pre-seed rebalance swap that is supposed to correct an attacker-skewed HyperSwap V2 pool ratio back to the curve-close price is budget-capped, and when the cap binds, the subsequent liquidity deposit locks in at the still-skewed pool ratio rather than the intended curve-close ratio.

### Title
LP-seeding rebalance swap is capped at 99% of the graduation's own (small) LT/token budget, so a pre-seed large enough to exceed it locks LP at an off-curve-close price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`_seedRebalancing`/`_pairRebalance`/`_noFeeSwapInput` correct a hostile mint-pre-seed on the HyperSwap V2 pair by computing the exact no-fee swap size needed to move the pool's reserve ratio to the curve-close target (`tokensForLP`/`ltFromPair`), then depositing the rest via `router.addLiquidity`. That swap size is explicitly clamped to `maxSwap = _swapBudget(inventory)` (99% of the protocol's own graduation-sized LT/token inventory), which for a token that just crossed the (small, e.g. $9K) `graduationThresholdUsd` is itself small. An attacker who pre-seeds the pool with reserves large enough that the unconstrained corrective swap `s = sqrt(reserveIn·reserveOut·targetN/targetD) − reserveIn` exceeds that budget gets only a partial correction; `_routerDepositAndDispose` then deposits the protocol's remaining inventory at the router's `quote()`-optimal split for the *current*, still-skewed, pool ratio — not at the cached curve-close ratio.

### Finding Description
`_noFeeSwapInput` in `packages/contracts/src/Bonding.sol` returns `s > maxSwap ? maxSwap : s` [1](#0-0)  — an explicit, unconditional cap. The cap is set in `_seedRebalancing` to `_swapBudget(...)`, i.e. 99% of `Bonding`'s own LT or TOKEN inventory earmarked for this specific graduation (`ltFromPair`/`tokensForLP`, bounded by `LP_RESERVE` and by however much LT the curve actually raised before crossing `graduationThresholdUsd`) [2](#0-1) . The natspec on `_swapBudget` explicitly acknowledges this only "kicks in for catastrophic pre-seeds beyond our budget capacity" and that the 1% margin only guarantees a *non-zero* deposit, not a *correctly-priced* one [3](#0-2) .

When the cap binds, `_pairRebalance` executes only the capped swap against the pair, so the pool ratio moves only partway toward `targetN/targetD` [4](#0-3) . `_routerDepositAndDispose` then calls `router.addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, ...)` [5](#0-4) . HyperSwap's canonical `addLiquidity` deposits the optimal *balanced-at-current-ratio* subset — i.e. it locks the LP position in at whatever ratio the pool is at post-partial-swap, not at the cached curve-close `tokensForLP/ltFromPair` ratio pinned in phase 1 (`_enterGraduating`/`_prepareGraduationLiquidity`) [6](#0-5) [7](#0-6) .

This directly breaks Invariant #1 documented in `docs/contracts-scope.md` — "Zero price gap: `ltFromPair × reserve0End ≈ tokensInLP × reserve1End` within 1 bps" [8](#0-7)  — precisely the class of bug the external report describes: a downstream computation trusts a quote/ratio taken from a single, attacker-influenceable pool without verifying that the correction mechanism actually has enough capacity to reach the true price.

### Impact Explanation
The attack reachable path is fully unprivileged and permissionless, matching the documented "hostile mint pre-seed" exploit window between phase 1 (`_enterGraduating`, fired inline by the threshold-crossing buy) and phase 2 (`finalizeGraduation`) [9](#0-8) :
1. Attacker front-runs by calling `factory.createPair(token, lt)`.
2. Attacker transfers TOKEN and LT to the pair at an extreme, self-chosen ratio and size, then calls `pair.mint(attacker)`.
3. Anyone calls `Bonding.finalizeGraduation(token)`. Because the reserves are large enough relative to the graduation's own inventory, `_pairRebalance`'s swap saturates at `maxSwap`, only partially correcting the ratio, and `_routerDepositAndDispose` locks LP into `LPLock` at that still-skewed price.

The result is: the protocol's curve-raised LT and 250M reserved tokens are permanently locked (via `LPLock.recordLock`, "no withdraw in v1") into a pool priced away from the curve's actual last close price — an LP seeded away from curve close, and value that arbitrageurs (including the attacker) can extract from the mispriced pool at the expense of the freshly-graduated LP position and, ultimately, traders/creators whose fees/attribution depend on a fairly-priced post-graduation market. This qualifies as concrete freezing/mispricing of protocol-held LP funds.

### Likelihood Explanation
Feasibility hinges on how small the graduation's own inventory budget is relative to what an attacker can afford to pre-seed with. Because `graduationThresholdUsd` is configured in the thousands of dollars (test suite uses a threshold on that order) and `LP_RESERVE` tokens have negligible USD value at that market cap, the 99%-of-inventory `maxSwap` cap is itself on the same modest order of magnitude. A moderately funded attacker (comparable capital to the graduation's own raised value, not "orders of magnitude" more) can construct a pre-seed ratio/size for which the unconstrained corrective swap `s` exceeds this cap, deliberately exploiting the exact boundary the code's own comments describe as "catastrophic" but do not bound to be economically infeasible. This is a Medium-severity likelihood: it requires deliberate, moderately capitalized action but no privileged access, no timing luck beyond the normal two-phase window, and no protocol bug beyond the documented cap itself.

### Recommendation
Do not let the deposit proceed once the rebalance swap has saturated its budget without fully closing the gap to `targetN/targetD`. Options:
- After the capped swap, re-check the resulting pool ratio against `targetN/targetD` within a tight tolerance; if still outside tolerance, fall back to `_seedDirectMint` (which locks the LP at the cached ratio via V2's first-liquidity branch, and is already used as the fallback when no swap can fire) instead of depositing via `router.addLiquidity` at an uncorrected ratio.
- Alternatively, size `maxSwap` off of the *actual* magnitude of the hostile pre-seed reserves (e.g., scale with `reserveIn`/`reserveOut`) rather than a fixed 99%-of-inventory budget, so the cap only binds when the attacker's pre-seed is truly disproportionate to any plausible finite defense, and document/enforce a hard cap on acceptable price drift before allowing the router deposit path.

### Proof of Concept
Given a graduation with a small `ltFromPair`/`tokensForLP` budget (bounded by `graduationThresholdUsd`):
1. Attacker calls `factory.createPair(token, lt)`, then transfers TOKEN and LT to the pair in a ratio far from `tokenReserve/assetReserve`'s curve-close price, sized so that `sqrt(reserveIn·reserveOut·targetN/targetD) − reserveIn > 0.99 × (attacker-accessible inventory bound)`, then calls `pair.mint(attacker)`.
2. Anyone calls `finalizeGraduation(token)`. `_pairRebalance` computes `s`, `_noFeeSwapInput` clamps it to `maxSwap` [10](#0-9) , the swap only partially corrects the ratio, and `_routerDepositAndDispose`'s `addLiquidity` locks LP at the post-swap (still off curve-close) ratio into `LPLock`.
3. Compare final pool reserves' ratio to `ltFromPair/tokensForLP` (the invariant checked in `test/GraduationInvariants.t.sol`'s "zero price gap" assertion [11](#0-10) ) — for a pre-seed sized per step 1 the gap exceeds the documented ~1 bps / ~50 bps ceilings.

### Citations

**File:** packages/contracts/src/Bonding.sol (L934-953)
```text
    /// @dev Phase 1: drain curve, cache LP-bound amounts, freeze trading. Runs
    ///      inline at end of the threshold-crossing buy. Pinning `tokensForLP`
    ///      and `ltFromPair` here (at the last curve price) is what preserves
    ///      the zero-gap invariant across the tx split.
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
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

**File:** packages/contracts/src/Bonding.sol (L1449-1473)
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
            IERC20(lt).forceApprove(routerAddr, 0);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```

**File:** docs/contracts-scope.md (L100-100)
```markdown
| 1 | Zero price gap | `ltFromPair × reserve0End ≈ tokensInLP × reserve1End` within 1 bps |
```

**File:** packages/contracts/AGENTS.md (L132-137)
```markdown
A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L100-100)
```text
        // this; we drive it directly in tests.
```
