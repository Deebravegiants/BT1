### Title
Budget-Capped Rebalance in Graduation LP Seeding Allows a Hostile HyperSwap V2 Pre-Seed to Lock the Curve-Close LP at an Off-Market Price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
CVE-2023-27604's root cause is that Airflow's Sqoop provider trusted attacker-suppliable connection parameters and fed them, only partially sanitized, into a security-critical operation (a shell-level import), letting the attacker's input dominate the outcome. The same class — an attacker-controlled input that a "correction" routine only *partially* neutralizes before it is baked into a critical, fund-affecting operation — recurs in `Bonding`'s graduation LP seeding. `finalizeGraduation` is permissionless [1](#0-0) , and the HyperSwap V2 TOKEN/LT pair it seeds into can be pre-created and pre-minted by anyone before graduation, since `_ensureUniswapV2Pair`/the underlying V2 factory's `createPair` is unauthenticated [2](#0-1) . The hostile-pre-seed defense in `_seedRebalancing`/`_pairRebalance` only corrects the pool ratio up to a *fixed, self-referential budget* — `99%` of Bonding's own graduation-time inventory — regardless of how large or skewed the attacker's own pre-seed is.

### Finding Description
When a mint pre-seed (Regime 3) is detected, `_seedRebalancing` computes the swap needed to move the pool to the curve-close ratio via `_noFeeSwapInput`, but caps it at `_swapBudget(...)`, which is hard-coded to 99% of Bonding's *own* curve-raised LT or token inventory for that graduation — not scaled to the size of the attacker's pre-seed reserves: [3](#0-2) [4](#0-3) 

The docstring on `_swapBudget` explicitly acknowledges this cap exists because "an extreme hostile pre-seed... drives the unconstrained `_noFeeSwapInput` past our per-side budget" and that the 1% reservation "only kicks in for catastrophic pre-seeds beyond our budget capacity" [5](#0-4) . When the swap is capped short of the amount needed to reach the true curve-close ratio, `_pairRebalance` still executes at the capped size [6](#0-5) , and `_routerDepositAndDispose` then unconditionally deposits Bonding's entire remaining TOKEN/LT balance into `addLiquidity` at *whatever ratio the pool sits at after the partial swap* — not the intended curve-close ratio — with `min0=1, min1=1` guarding only against a degenerate zero deposit, not against a skewed one: [7](#0-6) 

Because the attacker sizes their own pre-seed reserves (bounded only by their own capital, not by Bonding's inventory which is capped at `LP_RESERVE` = 25% of 1B tokens and the curve-raised LT for that launch), an attacker can trivially make their pre-seed dominate the fixed budget, guaranteeing the corrective swap cannot reach the target ratio. The resulting LP — the one permanently locked via `LPLock.recordLock` [8](#0-7)  — is minted/deposited at a price divorced from the bonding curve's true close price.

### Impact Explanation
This is a concrete "LP seeded away from the curve close price," one of the explicitly accepted impact classes. Post-graduation, `Zap._buyOnUniswapV2`/`_sellOnUniswapV2` swap directly against this mispriced pair [9](#0-8) , so every trader entering the graduated market is transacting off a price the attacker engineered rather than the fair curve-close price, and the value gap between the "true" curve price and the actually-seeded pool price is captured by the attacker's pre-existing LP position (minted for free from their pre-seed) and/or by arbitrageurs snapping the pool back to fair value at the expense of the locked LP's composition. This is a fund-affecting mispricing of the permanently-locked LP, not a cosmetic issue.

### Likelihood Explanation
Medium. The attack requires: (1) permissionlessly creating the V2 pair ahead of a specific token's graduation (trivial — no gating on `IUniswapV2Factory.createPair`); (2) self-funding a mint pre-seed sized to dominate that launch's `LP_RESERVE`/curve-raised-LT budget (bounded, observable numbers an attacker can size against in advance since `LP_RESERVE` is a protocol constant and the curve-raised LT is visible on-chain before the threshold trips); (3) calling or waiting for the permissionless `finalizeGraduation` once phase 1 fires. No privileged role, no upgrade, and no reliance on BounceTech LT or HyperSwap V2 internals being broken — only on alt.fun's own fixed-budget correction logic being out-sized by attacker capital.

### Recommendation
Do not let `_routerDepositAndDispose` deposit unconditionally once the rebalance swap is budget-capped. When `_pairRebalance` returns having hit the `maxSwap` ceiling (rather than reaching the computed ideal `s`), fall back to the `_seedDirectMint` path (which accepts a bounded subsidy to the pre-seeder instead of an unbounded price divergence) rather than depositing at the still-skewed post-swap ratio. Alternatively, size `maxSwap` dynamically against the attacker's pre-seed reserves (not solely Bonding's own inventory) so the correction can always fully reach the curve-close ratio regardless of pre-seed size, and/or add an explicit post-swap ratio-deviation check before calling `addLiquidity` that reverts or reroutes to direct-mint if the deviation exceeds a small tolerance.

### Proof of Concept
1. Creator launches token `T` against LT `L` via `Zap.createToken`; curve begins trading.
2. Before `T` graduates, attacker calls the well-known HyperSwap V2 factory's `createPair(T, L)` directly (bypassing `Bonding._ensureUniswapV2Pair`, which just fetches/creates the same pair later) and then `pair.mint(attacker)` after transferring a large, heavily LT-skewed deposit (e.g., a large amount of `L` and a tiny amount of `T`) sized to be many multiples of what `T`'s eventual `tokensForLP`/`ltFromPair` will be at graduation.
3. Attacker (or anyone, or a normal buy) drives `T` past `canGraduate`, firing `_enterGraduating`, which pins `tokensForLP`/`ltFromPair` at the curve-close ratio.
4. Anyone calls `Bonding.finalizeGraduation(T)`. `_seedUniswapV2Direct` sees `totalSupply() != 0` on the pair (attacker already holds LP), routes to `_seedRebalancing`; the required corrective swap (computed by `_noFeeSwapInput`) exceeds `_swapBudget(bonding's own inventory)`, so the swap executes only at the capped amount, leaving the pool still LT-rich relative to the curve-close ratio.
5. `_routerDepositAndDispose` deposits Bonding's remaining `T`/`L` balance into `addLiquidity` at this still-skewed ratio; `LPLock.recordLock` permanently locks the resulting LP.
6. The graduated pool's spot price now differs materially from the bonding curve's last traded price; the attacker's pre-existing LP tokens (minted for a self-chosen off-market ratio) are worth more than their contributed capital at the true price, and/or subsequent traders swap through `Zap` at the mispriced rate before arbitrage fully corrects it — realizing the value transfer at the expense of the locked LP and post-graduation traders.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1005)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();
```

**File:** packages/contracts/src/Bonding.sol (L1031-1031)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1316-1332)
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
```

**File:** packages/contracts/src/Bonding.sol (L1356-1373)
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
```

**File:** packages/contracts/src/Bonding.sol (L1374-1378)
```text
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

**File:** packages/contracts/src/Zap.sol (L542-562)
```text
    function _swapOnUniswapV2(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        Bonding bonding_ = _s().bonding;
        // `graduatedPair` is keyed by the launched token only; check `tokenIn`
        // first (sell direction) then fall back to `tokenOut` (buy direction).
        address pair = bonding_.graduatedPair(tokenIn);
        if (pair == address(0)) pair = bonding_.graduatedPair(tokenOut);

        bool inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn;
        // Quote from the pair so the output tracks its live fee instead of a
        // hardcoded rate, keeping `amountOut` consistent with the K-check.
        amountOut = IUniswapV2Pair(pair).getAmountOut(amountIn, tokenIn);

        IERC20(tokenIn).safeTransfer(pair, amountIn);

        (uint256 amount0Out, uint256 amount1Out) = inIsToken0 ? (uint256(0), amountOut) : (amountOut, uint256(0));
        IUniswapV2Pair(pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
    }
```
