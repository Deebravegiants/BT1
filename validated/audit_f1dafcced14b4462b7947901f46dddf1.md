### Title
Zero-liquidity rebalance-deposit residue reverts `LPLock.recordLock`, permanently bricking `finalizeGraduation` on a small-`tokensForLP` graduation with a sized hostile pre-seed - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The Envoy advisory is a null-pointer dereference that fires only under a narrow, specific combination of conditions (body-less non-GET/HEAD request + a 303 response on a route configured for internal redirects) where code unconditionally uses a resource that was never allocated, crashing the whole process. The alt.fun analog is the hostile-pre-seed defense in `Bonding._seedUniswapV2Direct` / `_seedRebalancing` / `_routerDepositAndDispose`, which under a narrow combination of conditions (a graduation with a very small `tokensForLP`, combined with an attacker-sized `pair.mint` pre-seed that is large enough to escape the dust-fallback band but small enough that the 99%-capped rebalance swap still exhausts nearly all of one side) can leave `remToken == 0` or `remLT == 0` so `addLiquidity` is skipped and `liquidity = 0` is returned to `finalizeGraduation`, which unconditionally calls `LPLock.recordLock(tokenAddress, lpPair, liquidity)`. `LPLock.recordLock` reverts with `ZeroAmount` when `amount == 0` [1](#0-0) , which unconditionally reverts the entire `finalizeGraduation` transaction, and since the underlying pre-seed condition and the tiny `tokensForLP` are both persistent on-chain state, every retry hits the same revert - a permanent brick of a token stuck forever in `Lifecycle.Graduating`.

### Finding Description
`finalizeGraduation` reads the cached phase-1 amounts and unconditionally forwards whatever `_seedUniswapV2Direct` returns to `LPLock.recordLock`, with no zero-check of its own: [2](#0-1) 

`_seedUniswapV2Direct` branches into three regimes; the hostile mint-pre-seed regime (`_seedRebalancing`) rebalances the pool toward the cached curve-close ratio via a direct `pair.swap`, then deposits the remaining balanced subset via `router.addLiquidity`: [3](#0-2) 

The rebalance swap input is deliberately capped at 99% of the available side's balance via `_swapBudget`, specifically to prevent the swap from consuming 100% of one side (which would leave nothing to deposit). The code's own natspec documents the exact failure mode this is meant to prevent — that without the cap, `_routerDepositAndDispose` would skip `addLiquidity` (`remToken == 0` or `remLT == 0`), `finalizeGraduation` would return `liquidity = 0`, and `LPLock.recordLock(...)` would record — in the comment's own words — "a zero-sized lock": [4](#0-3) 

But `LPLock.recordLock` does not silently record a zero-sized lock — it explicitly reverts on `amount == 0`: [1](#0-0) 

This is the root-cause mismatch: the `_swapBudget` mitigation only guarantees the swap doesn't consume literally 100% of the budget — it guarantees a nominal 1% remainder of the *budget*, not a nonzero remainder of the *deposit*. Because `_swapBudget` operates on a percentage (`(budget * 99) / 100`), integer division floors, and for a small enough budget (e.g. a `tokensForLP`/`ltFromPair` in the single- or double-digit-wei range — reachable in production because the LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` is near zero whenever graduation is triggered with very little curve supply sold, e.g. the USD trigger fires almost immediately after a minimal seed buy due to LT price appreciation) the 1% "reserved" remainder can itself round down to 0. When that happens, `_routerDepositAndDispose`'s `remToken > 0 && remLT > 0` guard is false, `addLiquidity` is skipped, `liquidity` stays 0, and the unconditional `LPLock.recordLock(tokenAddress, lpPair, 0)` call reverts with `ZeroAmount`.

Because `finalizeGraduation` is a single atomic transaction, this revert rolls back all its state changes (the pair skim/mint/swap, the token burns, the `lifecycle` flip) — nothing is persisted, so the token remains in `Lifecycle.Graduating` and the same hostile pre-seed persists on the still-existing HyperSwap pair. Every subsequent call to the permissionless `finalizeGraduation` recomputes the exact same reserves and the exact same rounding-to-zero outcome, so the revert is deterministic and permanent. The token can never reach `Lifecycle.Graduated`; the curve's `ltFromPair` raised LT, the `tokensForLP` locked-target tokens, and any post-graduation trading are frozen forever, since `Zap.buy`/`Zap.sell` gate on `isGraduating(tokenAddress)` and revert with `TokenIsGraduating` [5](#0-4) .

### Impact Explanation
This is a permanent freeze of funds for every trader who bought into the curve before graduation and every future holder: `ltFromPair` (the curve-raised LT reserve asset) is trapped inside `Bonding`/the HyperSwap pair with no withdraw path, and the launched `Token`'s curve-side liquidity can never open on HyperSwap V2, meaning holders can never exit via `Zap.sell` (which routes to `Bonding.sell` only while `Curve`, and to Uniswap only while `Graduated` — the token is stuck in neither valid state permanently). This satisfies the "permanent freezing of trader ... funds" bar for a High-severity finding, directly analogous to Envoy's crash-the-whole-process DoS: a narrow trigger condition causes a persistent, unrecoverable failure of the load-bearing graduation path.

### Likelihood Explanation
Reachable by an unprivileged attacker with no special role: front-run `factory.createPair(token, lt)` (permissionless) and `pair.mint(attacker, ...)` with a self-funded seed sized to sit just outside the `DIRECT_MINT_PRESEED_BPS` dust-fallback band but small enough, relative to a `tokensForLP`/`ltFromPair` that is itself very small (achievable by graduating a token whose curve supply sold is near zero, e.g. an LT-appreciation-driven USD-trigger graduation shortly after the mandatory seed buy), that the 99%-capped rebalance swap's 1% reserved remainder still rounds to zero in integer arithmetic. This requires the attacker to control the pre-seed size and to time it against a graduation with a small `tokensForLP`, which is a realistic and repeatable griefing setup (an attacker can watch for or even induce small-`tokensForLP` graduations via LT price manipulation/appreciation) rather than a purely theoretical edge case, given the code's own natspec acknowledges the exact zero-remainder failure mode it is trying to avoid.

### Recommendation
In `_routerDepositAndDispose` (or in `finalizeGraduation` before calling `LPLock.recordLock`), add an explicit fallback when `remToken == 0 || remLT == 0` after the rebalance to force the `_seedDirectMint` path (mint whatever nonzero inventory remains directly at the cached ratio) instead of silently returning `liquidity = 0`, so `finalizeGraduation` never calls `LPLock.recordLock` with a zero amount. Alternatively, harden `_swapBudget`'s rounding so the reserved remainder is guaranteed to be at least 1 wei (e.g. `budget - (budget * 99)/100` computed as a minimum-of-1 floor) rather than relying on percentage math that can floor to zero for small budgets, and add a regression test that graduates a token with a single-digit-wei `tokensForLP`/`ltFromPair` against a sized hostile pre-seed to confirm `finalizeGraduation` never reverts.

### Proof of Concept
1. Launch a token with the minimum allowed seed buy (`Zap.MIN_SEED_USDC`), leaving curve supply sold near zero so `tokensForLP(sold) = sold·(S−sold)/S` and the corresponding `ltFromPair` are both tiny (single/double-digit wei-scale).
2. Pump the paired LT's `exchangeRate()` so the USD trigger fires (`canGraduate` true) without any further meaningful buy, and call the permissionless `Bonding.triggerGraduation(tokenAddress)` to run phase 1 (`_enterGraduating`), caching the tiny `(tokensForLP, ltFromPair)` in `pendingGraduation[tokenAddress]`.
3. Before anyone calls `finalizeGraduation`, front-run: call `factory.createPair(tokenAddress, lt)` (or use `_ensureUniswapV2Pair`'s auto-creation) then `transfer` a small (TOKEN, LT) pre-seed to the pair and call `pair.mint(attacker)`, sizing the pre-seed just above the `DIRECT_MINT_PRESEED_BPS` dust-fallback threshold relative to the tiny cached `(tokensForLP, ltFromPair)`.
4. Call the permissionless `Bonding.finalizeGraduation(tokenAddress)`. `_seedRebalancing` takes the rebalance branch, `_pairRebalance` executes a swap capped at 99% of the tiny available balance via `_swapBudget`, and the 1% reserved remainder rounds to 0 in integer division; `_routerDepositAndDispose` skips `addLiquidity` (`remToken == 0` or `remLT == 0`), returning `liquidity = 0`.
5. `finalizeGraduation` calls `LPLock.recordLock(tokenAddress, lpPair, 0)`, which reverts with `LPLock.ZeroAmount`, reverting the whole `finalizeGraduation` call.
6. Any subsequent call to `finalizeGraduation` recomputes identical state and reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, and `Zap.buy`/`Zap.sell` permanently revert with `TokenIsGraduating`, freezing all curve-raised LT and the token's tradability forever.

### Citations

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1033)
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

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
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

**File:** packages/contracts/src/Zap.sol (L248-251)
```text
        Bonding bonding_ = _s().bonding;
        if (bonding_.creatorOf(tokenAddress) == address(0)) revert TokenNotTrading();
        if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();

```
