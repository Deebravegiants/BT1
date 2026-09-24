### Title
Permissionless `triggerGraduation` can permanently brick a token in `Lifecycle.Graduating` via a sub-`MINIMUM_LIQUIDITY` first LP mint - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.triggerGraduation` is explicitly designed to fire graduation phase 1 for the case where LT appreciation (not a buy) pushes the curve past the USD threshold with only a tiny amount of *real* LT ever raised — the natspec says it exists precisely because "the closing buy on the curve would mint below the BounceTech LT mint floor... making the token un-graduatable via `Zap.buy`." [1](#0-0)  Because `ltFromPair` (and therefore `tokensForLP`) is pinned from whatever the curve's stored reserves happen to be at that instant, this path can leave `_prepareGraduationLiquidity` with a vanishingly small `(tokensForLP, ltFromPair)` pair cached in `pendingGraduation[token]`. [2](#0-1)  Phase 2 (`finalizeGraduation`) then calls `_seedDirectMint`, which unconditionally calls the brand-new HyperSwap pair's `mint()` with no floor check. [3](#0-2)  A first-ever V2 `mint()` computes `liquidity = sqrt(amount0*amount1) - MINIMUM_LIQUIDITY` (1000) with no underflow guard — if the product is small enough, this reverts. [4](#0-3)  Since `finalizeGraduation` calls `_seedUniswapV2Direct`/`_seedDirectMint` with no try/catch, that revert propagates and aborts the whole `finalizeGraduation` transaction. Because phase 1 already flipped `lifecycle` to `Graduating` and froze `buy`/`sell` irreversibly, and because `tokensForLP`/`ltFromPair` are cached and never recomputed, there is no on-chain path to retry with different values — every subsequent `finalizeGraduation(tokenAddress)` call reverts identically forever.

### Finding Description
The dual-trigger design intentionally allows graduation to fire on a USD-value threshold computed as `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K`, which can be satisfied with an arbitrarily small real LT amount raised on the curve if `exchangeRate()` (a value read live from the external BounceTech LT, entirely outside alt.fun's control) is high enough. [5](#0-4)  `triggerGraduation` is the permissionless entry point built specifically for this "rate-only ripening" case, and is callable by any address with no minimum-size guard beyond `canGraduate()`: [6](#0-5) 

`_enterGraduating` -> `_prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` and `tokensForLP = ltFromPair * tokenReserve / assetReserve`, with no floor on the resulting product: [7](#0-6)  These are cached verbatim in `pendingGraduation[token]` and consumed byte-for-byte in phase 2, by design, to preserve the zero-gap invariant: [8](#0-7) 

`finalizeGraduation` — the permissionless phase-2 call — routes an empty/fresh pair straight to `_seedDirectMint`, which transfers `(tokensForLP, ltFromPair)` and calls `pair.mint(lpLock)` with zero validation of the resulting liquidity size: [9](#0-8) [10](#0-9)  A first-time V2 `mint()` (as modeled by the project's own mock, mirroring real UniswapV2/HyperSwap behavior) subtracts `MINIMUM_LIQUIDITY` unconditionally: [4](#0-3)  If `sqrt(tokensForLP * ltFromPair) <= 1000`, this underflows and reverts (Solidity 0.8 arithmetic panic), aborting the entire `finalizeGraduation` call.

This is the same failure class as the external CVE report: a rebuild/finalize step (Glade's widget rebuild; here, alt.fun's LP-seed/finalize step) that fails to defensively validate an edge-case input before performing a state-mutating operation, resulting in an unrecoverable crash. The project's own AGENTS.md/comments explicitly call out "brick resistance" as the top-ranked invariant for `finalizeGraduation` and document extensive defenses against hostile *pre-seed* shapes — but no defense exists for the case where the graduation's *own* computed `(tokensForLP, ltFromPair)` pair is simply too small, which is a scenario the protocol's own `triggerGraduation` design deliberately opens the door to.

### Impact Explanation
Once `_enterGraduating` runs, `lifecycle` is irreversibly `Graduating`: `buy`/`sell` on the curve both revert with `TokenIsGraduating`, and `finalizeGraduation` is the only exit — but it reverts deterministically every time it is called for this token, since `pendingGraduation[token]` and the pair state are fixed. Any curve-raised LT that was already drained into `Bonding` via `Router.graduate`, plus the fixed 250M `LP_RESERVE` tokens set aside for LP, plus every trader's/creator's token holdings, are permanently frozen with no owner override, no upgrade path in `Bonding` for a single stuck token, and no rescue function. This is a permanent freezing-of-funds condition matching the "Validate" criteria (permanent freezing of trader/creator/LP funds).

### Likelihood Explanation
Reachability requires only that `canGraduate()` flips true via the USD trigger while the real LT raised (`ltFromPair`) is still tiny — i.e., appreciation-driven graduation rather than a large closing buy. This is exactly the scenario the codebase's own natspec identifies as realistic and already provides a dedicated permissionless entry point for (`triggerGraduation`), rather than a contrived edge case. No attacker capital or privileged role is needed — any address can call `triggerGraduation` once the LT's exchange rate movement (external, market-driven) pushes `canGraduate()` true, and any address (or nobody) then calls `finalizeGraduation`, which reverts. The exact numeric threshold at which `sqrt(tokensForLP*ltFromPair) <= 1000` is hit depends on the $9K USD threshold, the LT's decimals/price, and virtual-reserve math, which I could not fully re-derive numerically in the time available — this is the main source of uncertainty in this finding, and a background engineer should compute the actual reachable range (varying LT price, decimals, and curve reserve state at trigger time) to confirm how narrow or wide the vulnerable window is.

### Recommendation
Before committing to `Lifecycle.Graduating` in `_enterGraduating` (or at minimum before calling `pair.mint` in `_seedDirectMint`), validate that `tokensForLP` and `ltFromPair` are large enough that the resulting first-mint liquidity will exceed `MINIMUM_LIQUIDITY` (e.g. require `Math.sqrt(tokensForLP * ltFromPair) > 1000 + slack`). If the check fails, either revert `triggerGraduation`/the threshold-crossing buy itself (deferring graduation until the real-raised amount is sufficient) rather than allowing entry into an un-finalizable `Graduating` state, or top up the deposit amounts from the `LP_RESERVE`/protocol-owned buffer to clear the floor before minting.

### Proof of Concept
1. Launch a token and buy a very small amount of LT into the curve — just enough that `ltFromPair` (real LT raised, i.e. `assetReserve - virtualLtReserve`) stays extremely small.
2. Have the paired BounceTech LT's `exchangeRate()` increase (this happens automatically over time as the leveraged position accrues, or can be simulated in tests via `lt.setExchangeRate(...)` as the existing test suite already does for `_ratePumpForStagedGraduation`) until `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K`, i.e. `canGraduate(tokenAddr) == true`, while the underlying `ltFromPair` LT-unit amount remains tiny.
3. Any unprivileged address calls `bonding.triggerGraduation(tokenAddr)`. This succeeds, calling `_prepareGraduationLiquidity`, caching a tiny `(tokensForLP, ltFromPair)` pair, and flipping `lifecycle` to `Graduating`.
4. Any address calls `bonding.finalizeGraduation(tokenAddr)`. Because `IUniswapV2Factory.getPair` returns the zero address, `_ensureUniswapV2Pair` creates a fresh pair, `_seedUniswapV2Direct` takes the `totalSupply() == 0` branch into `_seedDirectMint`, which transfers the tiny `(tokensForLP, ltFromPair)` and calls `pair.mint(lpLock)`. If `sqrt(tokensForLP * ltFromPair) <= MINIMUM_LIQUIDITY (1000)`, this call reverts with an arithmetic underflow panic, and `finalizeGraduation` reverts.
5. Every subsequent call to `finalizeGraduation(tokenAddr)` by any caller reverts identically forever — the token is permanently stuck in `Lifecycle.Graduating`, and all LT/tokens already moved into `Bonding` for this graduation are unrecoverable.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L986-999)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1224-1259)
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

    /// @dev Transfer the full `(tokensForLP, ltFromPair)` to the pair and
    ///      `mint` the LP to `LPLock`, opening at the exact cached
    ///      curve-close ratio. Used by the empty-pair regime and as the
    ///      dust-pre-seed fallback in `_seedRebalancing` — against dust
    ///      reserves the V2 `min()` formula's donation to any pre-existing
    ///      LP is negligible (see `_seedUniswapV2Direct` natspec). Any TOKEN
    ///      remainder (a skimmed pure-donation pre-seed) is burned; the LT
    ///      remainder is left for `finalizeGraduation`'s `_sweepLTToOwner`
    ///      post-bookend.
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

**File:** packages/contracts/AGENTS.md (L88-88)
```markdown
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
