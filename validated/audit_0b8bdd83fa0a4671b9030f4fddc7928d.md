### Title
Hostile HyperSwap pre-seed can force `finalizeGraduation` to open the graduation LP at an off-curve price when the pre-seed exceeds the rebalance swap budget - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` defends against an attacker pre-creating/pre-seeding the HyperSwap V2 TOKEN/LT pair with a hostile ratio, but the defense (a single capped `pair.swap` rebalance) is explicitly capped at `_swapBudget()` (99% of the tokenIn side available to Bonding). When an attacker pre-seeds a ratio extreme enough that the required corrective swap exceeds that cap, the rebalance only partially corrects the ratio, and the subsequent `router.addLiquidity` deposit (`min0=1, min1=1`) mints the graduation LP at a ratio still skewed away from the true curve-close price.

### Finding Description
`_seedRebalancing` ( [1](#0-0) ) rebalances a hostile mint-pre-seeded HyperSwap pair toward the cached curve-close ratio `(tokensForLP, ltFromPair)` via a single `_pairRebalance` swap, then deposits the residual via `_routerDepositAndDispose`'s `addLiquidity(..., 1, 1, lpLock_, ...)` call ( [2](#0-1) ).

The rebalance swap size `s` is computed by `_noFeeSwapInput` under a no-fee constant-product assumption and then explicitly clamped to `maxSwap = _swapBudget(inventory)` (99% of whichever side Bonding holds for *this* graduation) — see `_swapBudget`'s own natspec: "an extreme hostile pre-seed (massively imbalanced reserves) drives the unconstrained `_noFeeSwapInput` past our per-side budget, `_pairRebalance` clamps to the full budget" ( [3](#0-2) ). The clamp exists purely for brick-resistance (so the deposit leg always has non-zero amounts on both sides); it makes no attempt to guarantee the *post-swap ratio* still lands near the target when the required swap is larger than the budget allows. In that case `_pairRebalance` executes the capped, insufficient swap ( [4](#0-3) ), the pool remains materially skewed toward the attacker's chosen ratio, and `_routerDepositAndDispose` then deposits the remaining `(tokensForLP, ltFromPair)`-derived inventory into the pool at that skewed ratio via the router's `quote()`-based optimal split ( [2](#0-1) ), then burns/sweeps the off-ratio remainder.

This is the exact scenario the contract's own comments flag as unresolved: `_swapBudget`'s natspec calls this the "catastrophic pre-seeds beyond our budget capacity, where the alternative is bricking" case, and the `AGENTS.md` notes that the dedicated regression suite proving "wrong-opening-price / LP-capture scenarios, attacker-no-profit... properties" was removed and "are no longer enforced by automated tests" ( [5](#0-4) ). The `_seedRebalancing`/`_seedDirectMint` "overpower with direct mint" fallback only triggers when *both* sides of the pre-seed are small relative to the graduation's own inventory (`DIRECT_MINT_PRESEED_BPS` band, [6](#0-5) ); a pre-seed sized large enough on one side to blow the swap budget, but not small enough to hit that direct-mint band, falls straight into the under-corrected rebalance-then-deposit path described above.

Because HyperSwap V2 pair creation and liquidity provision are fully permissionless, and `finalizeGraduation` itself is permissionless ( [7](#0-6) ), an unprivileged attacker who has accumulated a large TOKEN and/or LT position (e.g. via legitimate curve buys before the token graduates, or simply holding a large amount of the freely tradeable external LT) can pre-create/pre-seed the pair with a ratio deliberately far from the curve-close price and sized so that Bonding's own `tokensForLP`/`ltFromPair` inventory cannot correct it within the 99%-of-budget swap cap.

### Impact Explanation
The result is an "LP seeded away from the curve close price" — one of the explicitly accepted impact classes for this analog. Once the HyperSwap TOKEN/LT pool opens at a materially mispriced ratio, the attacker (who controls both the pre-existing LP share and knowledge of the exact skew) can immediately arbitrage the newly seeded pool against the true curve-close valuation, extracting value that should have accrued to the protocol/creator/token holders through the locked LP. Depending on the attacker's pre-seed size relative to `LP_RESERVE` (up to 250M tokens) and the real LT raised by the curve, the mispricing — and thus extractable value — can be scaled well beyond the sub-percent drift the "normal" fee-slippage case produces, since the correction is capped rather than proportional to the pre-seed's severity. This is a value-extraction vector against LP/creator/protocol funds reachable by any unprivileged address, which is Medium-High severity depending on achievable pre-seed size.

### Likelihood Explanation
Reaching this path requires no special privilege: pre-creating a HyperSwap V2 pair, transferring TOKEN/LT into it, and calling `mint()` are all permissionless actions available to any wallet before `finalizeGraduation` is called (the keeper calls it ~60s after `TokenGraduating`, giving a narrow but real front-running window, and worst case an attacker can call `finalizeGraduation` itself once conditions favor them since it too is permissionless). The main constraint is capital: the attacker needs a pre-seed large enough, relative to the specific token's `tokensForLP`/`ltFromPair` inventory, to exceed the 99% swap-budget cap on at least one side while avoiding the small-pre-seed direct-mint fallback band. For low-liquidity graduations (small `ltFromPair`, e.g. tokens that graduate via the supply trigger in a bear market with a thin LT raise) this bar is low, making the attack practically feasible with moderate capital.

### Recommendation
Do not silently accept a partially-corrected ratio when the rebalance swap is clamped by budget. Either (a) compute the actual achievable post-swap ratio after clamping and compare it against the target ratio with an explicit tolerance, reverting/queuing the graduation (or falling back to the direct-mint "overpower" path unconditionally) whenever the deviation exceeds a safe bound, or (b) size `maxSwap` dynamically so it is guaranteed sufficient to reach the target ratio for the given pre-seed size rather than a fixed 99%-of-inventory cap, and only fall back to accepting an off-ratio deposit under a proven-bounded worst case. Restore/re-add the removed `HostilePreSeed.t.sol` coverage (`test_hostilePreSeed_*`, attacker-no-profit assertions) so this property is regression-tested, since the code comments themselves indicate this guarantee is currently unverified.

### Proof of Concept
1. Creator launches a token whose curve raises a modest amount of LT before graduating (small `ltFromPair`) — e.g. via the supply trigger (`tokenBalance() == 0`) in a low-price LT environment, so `_prepareGraduationLiquidity` caches a small `ltFromPair` and a correspondingly small `tokensForLP` (bounded by the parabola invariant, `tokensForLP ≤ LP_RESERVE`), see [8](#0-7) .
2. Attacker buys a large TOKEN position on the curve before it graduates (legitimate `Zap.buy`/`Bonding.buy`), and separately holds/acquires a large amount of LT (freely mintable/tradeable via BounceTech).
3. As soon as `TokenGraduating` fires (phase 1, `_enterGraduating`), the attacker races the keeper: calls `IUniswapV2Factory.createPair(token, lt)` (or reuses an existing empty pair), transfers a large, deliberately-skewed amount of TOKEN and LT into it, and calls `pair.mint(attacker)` — establishing reserves whose ratio is far from `tokensForLP : ltFromPair` and whose magnitude on at least one side exceeds 99% of Bonding's own inventory for that side.
4. `finalizeGraduation(token)` is called (by the keeper or the attacker itself, permissionless — [9](#0-8) ). Because `totalSupply() != 0`, it takes the `_seedRebalancing` path ( [10](#0-9) ); the pre-seed sizes fall outside the `DIRECT_MINT_PRESEED_BPS` "overpower" band ( [6](#0-5) ), so `_pairRebalance` is invoked; `_noFeeSwapInput`'s desired swap exceeds `maxSwap`, so it is clamped ( [3](#0-2) ) and the pool remains meaningfully off the curve-close ratio after the swap.
5. `_routerDepositAndDispose` deposits the remaining `(tokensForLP, ltFromPair)`-derived inventory at this still-skewed ratio ( [2](#0-1) ), minting graduation LP to `LPLock` at an off-curve price while the attacker's own pre-minted LP (and any follow-on trade) captures the mispricing via arbitrage against the true curve-close valuation.

Note: I was not able to execute Foundry tests against this path (this environment has no filesystem/terminal access), so the exact numeric magnitude of the achievable price deviation for a given pre-seed size was not empirically confirmed — a Devin session with repo access should implement `test_hostilePreSeed_budgetExceeded_opensOffRatio` (extending `test/TwoPhaseGraduation.t.sol`) to quantify the resulting price gap and attacker-extractable value for a range of pre-seed sizes/ratios.

### Citations

**File:** packages/contracts/src/Bonding.sol (L981-1034)
```text
    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
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

**File:** packages/contracts/src/Bonding.sol (L1224-1234)
```text
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
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

**File:** packages/contracts/AGENTS.md (L229-229)
```markdown
The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```
