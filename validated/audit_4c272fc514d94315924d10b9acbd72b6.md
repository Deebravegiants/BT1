### Title
LP-graduation fallback can donate curve-raised value to an attacker-pre-seeded HyperSwap V2 pool - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedRebalancing` / `_pairRebalance` assume that whenever the graduation rebalance swap rounds to zero output, the attacker's pre-existing HyperSwap V2 pool reserves must be "negligible against this graduation's inventory," and therefore falls back to `_seedDirectMint`, which calls the raw, non-empty-pool `IUniswapV2Pair.mint()` path. That assumption is false: the swap can round to zero purely because *this graduation's own* swap budget (`ltFromPair`/`tokensForLP`) is small, independent of how large the attacker's pre-seeded reserves actually are. In that case `_seedDirectMint` deposits the full curve-raised `(tokensForLP, ltFromPair)` into an already non-empty, attacker-controlled-ratio pool, and Uniswap V2's `min(amount0*S/r0, amount1*S/r1)` mint formula donates the higher-value side to the attacker's pre-existing LP position instead of to `LPLock`.

### Finding Description
`finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` handles a "mint pre-seed" (attacker has already called `pair.mint()` against the HyperSwap V2 pair with a self-chosen ratio) by trying to rebalance the pool toward the curve-close ratio via a direct `pair.swap`, then depositing the remainder through the router (`_routerDepositAndDispose`) using `addLiquidity(min0=1, min1=1)`: [1](#0-0) 

The swap leg, `_pairRebalance`, computes the no-fee-equivalent input `s` via `_noFeeSwapInput`, capped at `_swapBudget(...)` (99% of *this graduation's own* available LT/Token inventory), then quotes `getAmountOut(s, tokenIn)` from the pre-seeded pool itself and executes the swap: [2](#0-1) 

If `getAmountOut(s, tokenIn)` rounds to zero, `_pairRebalance` returns `false` and the caller falls back unconditionally to `_seedDirectMint`, which does *not* check whether the V2 pool's `totalSupply()` is zero — it just transfers `(tokensForLP, ltFromPair)` to the pair and calls `mint(lpLock)`: [3](#0-2) 

The natspec justifying this fallback explicitly claims the captured LP share is bounded because a rounds-to-zero swap implies negligible pre-seed reserves: [4](#0-3) 

That inference is the root-cause gap. `getAmountOut` rounding to zero is a function of the swap input `s` **relative to the pre-seeded pool's own reserves** — and `s` is capped by `_swapBudget(_ltSwapInventory(lt, protectedLT))` or `_swapBudget(IERC20(tokenAddress).balanceOf(address(this)))`, i.e. by *this graduation's* own raised inventory, not by the attacker's reserves. A token that graduates with a small real LT raise (the dual trigger fires on `IPair.tokenBalance() == 0` — full curve sellout — independent of the USD leg, per `canGraduate`): [5](#0-4) 
can have a tiny `ltFromPair`/`tokensForLP` inventory even while an attacker has pre-seeded the HyperSwap V2 pair with large, arbitrarily-ratioed reserves (any unrelated wallet can create/pre-seed the pair before `finalizeGraduation` runs, since `_ensureUniswapV2Pair` and V2's `createPair`/`mint` are permissionless). The rebalance swap then rounds to zero against the attacker's oversized reserves, `_pairRebalance` returns `false`, and `_seedDirectMint` mints straight into the existing, attacker-ratio pool — triggering standard Uniswap V2 `min()`-formula donation of the entire curve-raised `(tokensForLP, ltFromPair)` surplus side to the attacker's pre-existing LP shares. `LPLock.recordLock` is then called unconditionally with whatever (possibly tiny) `liquidity` results, and being one-shot it can never be corrected: [6](#0-5) 

### Impact Explanation
This lets an unrelated wallet permanently capture curve-raised LT and/or launched-Token value that was meant to seed the locked LP: the project's real assets are deposited into a pool whose reserve growth accrues to the attacker's own pre-existing LP position, while `LPLock` (and the project) is left holding a locked LP claim worth substantially less than the value actually deposited. This is a concrete, permanent value transfer from the graduating token's LP/creator/trader funds to an attacker — satisfying the "LP seeded away from the curve close price" / theft criterion, and it is irreversible because `finalizeGraduation`/`LPLock.recordLock` cannot be re-run.

### Likelihood Explanation
Reachable by any unprivileged wallet: `_ensureUniswapV2Pair` and Uniswap V2's own `mint` are permissionless, so an attacker can pre-create/pre-seed the TOKEN/LT pair with a skewed ratio and large reserves before `finalizeGraduation` is called (permissionless, keeper-driven but callable by anyone). The attack's practicality depends on the graduating token having a comparatively small `ltFromPair`/`tokensForLP` at graduation (most naturally arising via the supply-sellout trigger, `IPair.tokenBalance()==0`, rather than the USD trigger) relative to the size the attacker seeds — a condition the attacker can select for by monitoring near-sellout curves and racing to pre-seed the V2 pair before phase 2 fires.

### Recommendation
Do not gate the direct-mint fallback purely on "swap rounds to zero." Before falling back to `_seedDirectMint`, check the pre-seeded pool's `totalSupply()`/reserves directly: if `totalSupply() > 0` and the pre-existing reserve values are not actually negligible in absolute (or LP-share) terms relative to `(tokensForLP, ltFromPair)`, refuse the raw `mint()` path (e.g., revert or escalate to a larger, uncapped rebalance) rather than assuming rounding-to-zero implies a harmless pre-seed.

### Proof of Concept
1. Attacker calls `IUniswapV2Factory.createPair(token, lt)` (or lets `_ensureUniswapV2Pair` create it) for a token nearing curve sellout, then directly transfers a large, deliberately skewed amount of `lt`/`token`-equivalent assets into the pair and calls `pair.mint(attacker)`, establishing a large non-empty reserve at an off-curve ratio.
2. Attacker (or anyone) drives the curve to `IPair.tokenBalance() == 0` via normal `Zap.buy` calls, or simply waits for it, triggering `_enterGraduating`/`canGraduate`'s supply leg with a small `ltFromPair` relative to the attacker's pre-seeded pool reserves.
3. `finalizeGraduation(token)` is called (permissionless). `_seedRebalancing` computes a rebalance swap `s` capped by the tiny `ltFromPair`/`tokensForLP` inventory; against the attacker's oversized pool reserves, `getAmountOut(s, tokenIn)` rounds to `0`, so `_pairRebalance` returns `false`.
4. `_seedDirectMint` transfers the full `(tokensForLP, ltFromPair)` into the still-imbalanced, non-empty pool and calls `mint(lpLock)`; Uniswap V2's `min(amount0*S/r0, amount1*S/r1)` formula credits `LPLock` only proportional to the smaller-value side, donating the rest to the attacker's existing LP position.
5. `LPLock.recordLock` is invoked once with the resulting undervalued `liquidity`, permanently locking in the loss.

### Citations

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1022-1033)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
```

**File:** packages/contracts/src/Bonding.sol (L1168-1176)
```text
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

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
