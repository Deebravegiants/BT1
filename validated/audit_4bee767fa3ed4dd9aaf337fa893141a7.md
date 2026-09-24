### Title
Vanishing-liquidity graduation permanently bricks `finalizeGraduation` and freezes curve-raised LT/tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2021-1093 describes a driver `assert()`/similar invariant check that an attacker can trigger to force an application exit — turning a recoverable condition into an unrecoverable crash. alt.fun's two-phase graduation has the same shape: `Bonding._seedUniswapV2Direct`'s Regime-1 fast path (`_seedDirectMint`) calls the real HyperSwap V2 pair's `mint()`, which enforces UniswapV2's own hard invariant `require(liquidity > 0)` (implemented as `sqrt(amount0*amount1) - MINIMUM_LIQUIDITY`, i.e., a Solidity `Panic`-on-underflow when the product is too small). If the cached `tokensForLP`/`ltFromPair` amounts computed at phase-1 close are small enough, this check/underflow always reverts — and because `Bonding`'s two-phase design has no way to unwind phase 1, the token is permanently stuck in `Lifecycle.Graduating`.

### Finding Description
`triggerGraduation` is explicitly permissionless and designed to fire phase 1 purely from LT price appreciation, without requiring any buy: [1](#0-0) 

The USD graduation trigger is `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K`, i.e., it only cares about the USD *value* of the raw LT raised (`ltFromPair`), not its raw token quantity: [2](#0-1) 

`_prepareGraduationLiquidity`, run at phase-1 close (`_enterGraduating`), derives the LP-seed amounts purely from the pair's raw reserves:
```
ltFromPair = assetReserve - virtualLtReserve
tokensForLP = ltFromPair * tokenReserve / assetReserve
``` [3](#0-2) 

If the LT's `exchangeRate()` has appreciated enough (an externally-driven, unprivileged-observable event — BounceTech LT price movement, not gated by any protocol permission), a vanishingly small raw `ltFromPair` (a handful of wei) is sufficient to cross the fixed $9K USD threshold. Since `virtualLtReserve` dominates `assetReserve` in this regime, `tokensForLP = ltFromPair * tokenReserve / assetReserve` rounds down toward zero. `triggerGraduation` (callable by any unprivileged address) then locks in these tiny cached values in `pendingGraduation[token]` and flips `lifecycle → Graduating`, a transition that is irreversible (subsequent `triggerGraduation` calls revert with `TokenIsGraduating`): [4](#0-3) 

Phase 2, `finalizeGraduation`, is also permissionless, and for a pristine/empty pair (the ~99% common case) routes straight to `_seedDirectMint`, calling the real HyperSwap pair's `mint(lpLock)` with these tiny cached amounts: [5](#0-4) [6](#0-5) 

Any canonical UniswapV2-fork pair's `mint()` enforces `liquidity = sqrt(amount0*amount1) - MINIMUM_LIQUIDITY` (`MINIMUM_LIQUIDITY = 1000`) on the first mint and reverts if that computation underflows or the resulting `liquidity` is `0` — the project's own mock mirrors this exact real-V2 behavior: [7](#0-6) 

This is precisely the CVE's bug class: a hard invariant check/assertion (here, UniswapV2's `require(liquidity > 0)`, or the underflow `Panic` feeding it) that is unconditionally reachable from unprivileged input and, once triggered, terminates the call with no graceful degradation. Unlike Regime 3 (hostile mint pre-seed), which was explicitly hardened with a `_swapBudget` 99%-cap specifically to avoid `LPLock.recordLock` ever seeing a zero-sized lock, Regime 1's direct-mint fast path has no analogous floor on `tokensForLP`/`ltFromPair` before calling `pair.mint`.

### Impact Explanation
Once `_enterGraduating` fires, `Router.graduate` has already drained the curve's real raised LT out of the `Pair` and into `Bonding` (via phase 1), and the token's `Lifecycle` is permanently `Graduating` — there is no code path back to `Curve`. If the cached `(tokensForLP, ltFromPair)` are small enough to make `pair.mint` revert, `finalizeGraduation` can never succeed for that token, ever (every future call reverts identically since the cached values are fixed at phase-1 close). This permanently freezes:
- all real LT raised by curve buyers for that token, now stuck inside `Bonding` with no rescue function that can move it into a locked LP or back to traders,
- the `250M`-token LP reserve normally destined for `tokensForLP`/`lpBurned`,
- the token itself, which can never reach `Lifecycle.Graduated` and therefore never trades on HyperSwap via `Zap`.

This is a concrete, permanent freeze of trader funds — squarely in the accepted impact category.

### Likelihood Explanation
Reachability requires only that an unprivileged party observe the LT's `exchangeRate()` crossing a level where `ltFromPair` (raw LT, in wei) needed to hit the fixed $9K threshold rounds `tokensForLP` down to (or near) zero, then call the fully permissionless `triggerGraduation`, followed by the fully permissionless `finalizeGraduation` — both explicitly documented as callable by "anyone" / "a random EOA." No special capital or privilege is required; the LT's price is an external, rebasing/leveraged asset whose exchange rate is outside the protocol's control, and `triggerGraduation` exists specifically to catch this "LT appreciation alone" scenario. The precise numeric window needed to force `tokensForLP` to zero-or-near-zero depends on decimals/rounding and the specific LT's exchange-rate trajectory, which is why this is rated Medium rather than High/Critical — it requires a specific (but plausible and externally-influenceable) price condition rather than being trivially triggerable at will by an attacker with arbitrary capital.

### Recommendation
Add an explicit, revert-free floor check in `_prepareGraduationLiquidity` / `_seedDirectMint`: if `tokensForLP` or `ltFromPair` would fall below the pair's `MINIMUM_LIQUIDITY` product floor, either (a) defer graduation (don't let `canGraduate`/`triggerGraduation` fire until the resulting LP-seed amounts are guaranteed non-degenerate), or (b) top up the LP-seed side from the `LP_RESERVE`/protocol treasury so `sqrt(tokensForLP * ltFromPair) > MINIMUM_LIQUIDITY` is guaranteed by construction, mirroring the brick-resistance guarantee already built for Regime 3 via `_swapBudget`.

### Proof of Concept
1. A token is launched normally via `Zap.createToken`, and some curve buys occur, raising a small amount of real LT (`ltFromPair`) in the `Pair`.
2. The LT's `exchangeRate()` appreciates sharply (external BounceTech LT event, outside protocol control) such that `ltFromPair_raw × exchangeRate ≥ $9K` while `ltFromPair_raw` itself is only a few wei — this is exactly the scenario `triggerGraduation`'s natspec calls out ("LT appreciation pushed the curve past the USD threshold").
3. Any unprivileged address calls `Bonding.triggerGraduation(token)`. `canGraduate` is true, so `_enterGraduating` fires: `_prepareGraduationLiquidity` computes `tokensForLP = ltFromPair_raw * tokenReserve / assetReserve`, which rounds to `0` (or a value whose product with `ltFromPair_raw` is below `MINIMUM_LIQUIDITY²`) because `assetReserve` is dominated by the large `virtualLtReserve`. Lifecycle flips to `Graduating`; these values are cached in `pendingGraduation[token]`.
4. Any unprivileged address calls `Bonding.finalizeGraduation(token)`. The pair is pristine (`totalSupply() == 0`), so `_seedUniswapV2Direct` takes the Regime-1 `_seedDirectMint` path and calls the real HyperSwap V2 pair's `mint(lpLock)` with the tiny cached amounts.
5. UniswapV2's `mint()` computes `liquidity = sqrt(tokensForLP * ltFromPair_raw) - MINIMUM_LIQUIDITY`; since the product is at or near zero, this underflows/reverts (`Panic` or `require(liquidity > 0)` per the mirrored mock behavior at `test/mocks/MockHyperswapRouter.sol:58-65`).
6. `finalizeGraduation` reverts every time it is called (the cached values never change), and `triggerGraduation` cannot be re-run (`TokenIsGraduating`). The token is permanently stuck; the LT already drained into `Bonding` by phase 1, and the 250M reserved LP tokens, are permanently unreachable.

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

**File:** packages/contracts/src/Bonding.sol (L955-979)
```text
    /// @notice Permissionless trigger for phase 1 of graduation. Same flow as
    ///         the inline post-buy trigger inside `_executeBuy`, but callable
    ///         without any buy. Closes the case where `canGraduate` is true
    ///         (LT appreciation pushed the curve past the USD threshold) but
    ///         the closing buy on the curve would mint below the BounceTech
    ///         LT mint floor and revert with `BelowMinTransactionSize`,
    ///         making the token un-graduatable via `Zap.buy`.
    /// @dev    `_enterGraduating` reads pair reserves and the launch-time
    ///         virtual reserve only — it does not depend on a buy having
    ///         just landed, so the same logic is safe to expose as a
    ///         standalone entry point. The lifecycle pre-checks mirror
    ///         `Bonding.buy`; the launch trading delay is intentionally
    ///         not enforced because `canGraduate` already requires either
    ///         the USD threshold or full curve sellout, both of which are
    ///         unreachable from a fresh launch within the delay window.
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
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

**File:** packages/contracts/src/Bonding.sol (L1217-1226)
```text
        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }
```

**File:** docs/contracts-scope.md (L68-71)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-65)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");
```
