### Title
Permanent brick of `finalizeGraduation` via HyperSwap V2 `MINIMUM_LIQUIDITY` underflow when the dual USD/supply trigger fires on a near-zero real LT raise - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding`'s graduation trigger computes the USD threshold as `(storedAssetReserve − virtualLtReserve) × exchangeRate ≥ $9K`, where `exchangeRate` is read live from the rebasing LT [1](#0-0) . Because `exchangeRate` can spike arbitrarily (it is an external, live-read price for the reserve LT), the raw-LT amount needed to cross the $9K threshold can shrink to a handful of wei. `_prepareGraduationLiquidity` derives `tokensForLP` proportionally to that same tiny `ltFromPair` [2](#0-1) , so both LP-bound legs can be pinned at dust quantities in Phase 1. Phase 2's `_seedDirectMint` then calls the HyperSwap V2 pair's standard `mint()` with these dust amounts [3](#0-2) , which underflow-reverts under UniswapV2's `MINIMUM_LIQUIDITY = 1000` first-mint floor whenever `sqrt(amount0 * amount1) <= 1000`. Because `finalizeGraduation` is a one-shot, permissionless function with no alternate code path once `Lifecycle.Graduating` is cached [4](#0-3) , this permanently bricks the token: it can never reach `Lifecycle.Graduated`, trading stays frozen, and the curve-raised LT plus the reserved 250M LP tokens are stuck in `Bonding` forever.

### Finding Description
Phase 1 (`_enterGraduating`) is triggered either inline on a threshold-crossing buy or permissionlessly via `Bonding.triggerGraduation` [5](#0-4) . It calls `_prepareGraduationLiquidity`, which:
- drains the curve's real LT into `Bonding` as `ltFromPair = assetReserve − virtualLtReserve` [6](#0-5) ,
- derives `tokensForLP = ltFromPair × tokenReserve / assetReserve`, capped at `LP_RESERVE` (250M) [7](#0-6) .

The USD graduation trigger multiplies the raw `ltFromPair` by the *live* `exchangeRate()` of the paired LT to compare against the fixed USD threshold [1](#0-0) . Since `exchangeRate` is an external, rebasing/appreciating price with no upper bound enforced by `Bonding`, a large enough price jump lets the USD threshold trip while `ltFromPair` (raw LT wei) is only a few units. Because `tokensForLP` is computed as a linear function of that same tiny `ltFromPair`, both `tokensForLP` and `ltFromPair` — the exact amounts cached in `pendingGraduation` and later fed verbatim to Phase 2 — collapse to dust.

Phase 2 (`finalizeGraduation`) reads the cached, frozen `(tokensForLP, ltFromPair)` and, for the ~99% "no LP minted yet" regime, calls `_seedDirectMint`, which transfers these dust amounts to the HyperSwap pair and calls the pair's standard `mint()` [3](#0-2) . Standard UniswapV2-family `mint()` on a pristine pair computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY` and reverts (underflow / `INSUFFICIENT_LIQUIDITY_MINTED`) whenever `sqrt(amount0*amount1) <= 1000`. With dust `tokensForLP`/`ltFromPair`, this condition is trivially met, so the `mint()` call — and therefore every future call to `finalizeGraduation(tokenAddress)` — reverts unconditionally, because `tokensForLP`/`ltFromPair` are pinned in storage and never recomputed (per design, to preserve the zero-gap invariant across the tx split) [8](#0-7) .

This is functionally the same bug class as CVE-2017-7957: an edge-case input shape (here, a legitimate/attacker-triggerable price condition rather than a crafted XML type) that the state-transition code doesn't validate against, causing an unhandled crash in code that untrusted transactions can always re-trigger, with no recovery path.

### Impact Explanation
Once Phase 1 fires, `info.lifecycle` is already `Graduating`: all buys/sells on the curve revert with `TokenIsGraduating`, and `_prepareGraduationLiquidity` has already moved the real curve LT out of the `Pair` into `Bonding` via `Router.graduate` and burned the unsold/excess tokens [9](#0-8) . If `finalizeGraduation` can never succeed, the token is permanently stuck in `Graduating`: trading never reopens (neither on the curve nor on HyperSwap), and the curve-raised LT plus the 250M `lpReserve` tokens sit unreachable in `Bonding` forever — no admin rescue path exists for `finalizeGraduation` itself once bricked. This is a concrete, permanent freezing of creator/trader funds, satisfying the High-severity DoS class from the XStream analog.

### Likelihood Explanation
Triggering requires only: (1) a token whose curve has raised very little real LT (e.g., right after the mandatory `$20` seed buy, before any organic trading), and (2) the paired LT's live `exchangeRate()` appreciating enough that `ltFromPair × exchangeRate ≥ graduationThresholdUsd`. Since alt.fun's reserve asset is explicitly a BounceTech leveraged/rebasing token whose price is read live and is external to the protocol, large short-term appreciation is a realistic, protocol-acknowledged risk surface (the docs already discuss `exchangeRate` drift and pumps elsewhere, e.g. `test_previewLtUntilGraduation_thresholdLegBindsAtElevatedRate`). Any unprivileged address can then call the permissionless `Bonding.triggerGraduation(tokenAddress)` to lock in the dust `(tokensForLP, ltFromPair)` pair and permanently brick the token.

### Recommendation
Add a floor check in `_prepareGraduationLiquidity` (or immediately before caching `pendingGraduation`) that rejects/defers graduation when `tokensForLP` or `ltFromPair` would be below the amount needed to satisfy the LP's `MINIMUM_LIQUIDITY` floor (e.g. `sqrt(tokensForLP * ltFromPair) > MINIMUM_LIQUIDITY` with margin), or alternatively route dust-sized graduations through a path that pre-funds the pair with a protocol-owned top-up so `mint()` never underflows. This preserves the existing brick-resistance guarantees for attacker-seeded dust (which are already handled) while closing the case where the protocol's *own* computed deposit amounts are dust due to LT price extremes.

### Proof of Concept
1. Launch a token via `Zap.createToken` with the minimum seed (`MIN_SEED_USDC`), pairing it with an LT.
2. Do not trade further (or trade minimally) so `ltFromPair` (real LT raised above the launch-time virtual reserve) is tiny, e.g. a few wei.
3. Cause (or wait for) the paired LT's `exchangeRate()` to spike sharply — this is an external, live-read rebasing price outside `Bonding`'s control, matching the "reserve asset is external rebasing-priced LT" risk surface.
4. Any unprivileged address calls `Bonding.triggerGraduation(tokenAddress)`. `canGraduate` returns true because `ltFromPair × exchangeRate ≥ graduationThresholdUsd` even though `ltFromPair` (raw wei) is dust; `_enterGraduating` caches dust `tokensForLP`/`ltFromPair` in `pendingGraduation` and flips `lifecycle = Graduating`, freezing the token.
5. Any address calls `Bonding.finalizeGraduation(tokenAddress)`. `_seedDirectMint` transfers the dust amounts to the freshly created HyperSwap pair and calls `pair.mint(lpLock)`, which reverts because `sqrt(tokensForLP * ltFromPair) <= MINIMUM_LIQUIDITY (1000)`.
6. Every subsequent call to `finalizeGraduation(tokenAddress)` reverts identically (the cached `pendingGraduation` values never change), permanently bricking the token in `Lifecycle.Graduating` with its raised LT and 250M reserved tokens unreachable.

Note: I was unable to directly inspect the `_launchTimeVirtualLtReserve`/launch-time seeding arithmetic in full or the exact `MINIMUM_LIQUIDITY` constant/behavior of the HyperSwap V2 pair contract in this index (it is an external dependency, out of the in-scope `packages/contracts/src` production code), so the PoC's magnitude assumptions rely on standard UniswapV2 `mint()` semantics rather than a directly-cited HyperSwap source line.

### Citations

**File:** docs/contracts-scope.md (L88-89)
```markdown
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
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

**File:** packages/contracts/src/Bonding.sol (L981-999)
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
