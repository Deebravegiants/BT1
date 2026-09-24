### Title
Two-phase graduation permanently strands raised LT and 250M tokens if `finalizeGraduation` reverts after `_enterGraduating` commits `Lifecycle.Graduating` - (File: packages/contracts/src/Bonding.sol)

### Summary
The Noise advisory's core bug class is a state-machine that advances irreversible counter/session state even when the paired operation can subsequently fail, permanently desynchronizing the two sides and bricking all future operations (denial of service). `alt.fun`'s bonding-curve graduation is architected the same way: `_enterGraduating` (triggered permissionlessly by any buy that crosses the threshold, or directly via `triggerGraduation`) irreversibly commits `Lifecycle.Graduating`, drains the curve's real LT via `Router.graduate`, and burns down to `tokensForLP`/`lpBurned` — all before the paired step, `finalizeGraduation`, which seeds the HyperSwap V2 LP and calls the one-shot `LPLock.recordLock`, ever runs.

### Finding Description
`_enterGraduating` [1](#0-0)  flips `info.lifecycle = Lifecycle.Graduating` and calls `_prepareGraduationLiquidity`, which drains the curve's raised LT out of the `Pair` via `Router.graduate` and burns curve tokens down to the cached `tokensForLP` [2](#0-1) . This is a separate, already-mined transaction from `finalizeGraduation`, which later performs `_ensureUniswapV2Pair`, `_seedUniswapV2Direct`, and `LPLock.recordLock` [3](#0-2) . Once `Lifecycle.Graduating` is set there is no code path back to `Lifecycle.Curve` — `buy`/`sell` both revert with `TokenIsGraduating` for any lifecycle other than `Curve` [4](#0-3) , and `triggerGraduation` also rejects a token already in `Graduating` [5](#0-4) .

If `finalizeGraduation` cannot be driven to completion for a given token, that token is permanently stuck: all curve trading is dead (`TokenIsGraduating` forever), and the LT already pulled out of the `Pair` by `graduate()` plus the 250M (LP_RESERVE-share) `tokensForLP` sit unrecoverable inside `Bonding` — this is precisely the "state advances even though the paired step can fail, causing an unrecoverable desync" bug class from the Noise advisory (nonce increments on failed `Decrypt`, permanently desynchronizing peers).

The comments in the code establish that this exact class of failure was considered and partially hardened against: `LPLock.isLocker` is explicitly add-only because "a live revoke would brick every in-flight `Bonding.finalizeGraduation`" [6](#0-5) , and `_swapBudget`'s 1% reservation exists specifically "the alternative is bricking" [7](#0-6) . However, these mitigations only cover the *hostile-LP-pre-seed* and *locker-revocation* vectors. They do not cover external dependency failure: `_ensureUniswapV2Pair`/`_seedUniswapV2Direct` call into `IUniswapV2Factory`/`IUniswapV2Pair`/`IUniswapV2Router02` (HyperSwap V2, an external, unaudited-by-this-repo dependency) [8](#0-7) [9](#0-8) , and `LPLock.recordLock` itself can revert with `InsufficientLPBalance` or `AlreadyLocked` on any state the contract doesn't anticipate [10](#0-9) . There is no retry-with-fallback, no permissioned recovery/rescue path, and no ability to unwind `Lifecycle.Graduating` back to `Curve` if `finalizeGraduation` is permanently unexecutable for any reason outside the specific pre-seed shapes the natspec anticipated.

### Impact Explanation
If `finalizeGraduation` permanently reverts for a token (e.g., due to an unanticipated HyperSwap V2 pair/router behavior, or any other un-hardened failure the natspec doesn't enumerate), the impact is:
- All curve trading for that token is permanently frozen (denial of service to every trader/holder of that token).
- The real LT raised by the curve (`ltFromPair`, already pulled via `Router.graduate`) and the `tokensForLP` (up to `LP_RESERVE` = 250M tokens) are permanently stranded inside `Bonding` with no recovery function.
- This is a permanent freezing of trader/creator funds, matching the "Accept only concrete theft or permanent freezing" validation bar.

### Likelihood Explanation
Reaching `Lifecycle.Graduating` requires no privilege — it's triggered by an ordinary threshold-crossing `Zap.buy` or the permissionless `triggerGraduation(tokenAddress)` [5](#0-4) . The system's own commentary demonstrates that the developers anticipated multiple concrete ways `finalizeGraduation` could brick (hostile pre-seeds, locker revocation) and had to add targeted, narrow defenses for each; this indicates the *general* class — an unanticipated revert path permanently stranding a Graduating-state token — is a real, previously-triaged risk rather than a theoretical one, even though I could not enumerate a fully concrete unhardened trigger from the available code alone.

### Recommendation
Add a permissioned (or time-boxed permissionless) recovery path that can unwind `Lifecycle.Graduating` back to a safe state (or retry `finalizeGraduation` with alternate parameters) if phase 2 cannot complete after a bounded number of attempts/blocks, so that a single unanticipated revert in the HyperSwap V2 integration or `LPLock.recordLock` cannot permanently strand curve-raised LT and reserved tokens.

### Proof of Concept
Conceptual (exact external trigger not fully enumerable from `packages/contracts/src` alone, per the "no privileged/off-chain/mocked-only path" scoping):
1. Attacker or ordinary trader executes a buy that crosses `graduationThresholdUsd`, causing `_executeBuy` → `_enterGraduating` to fire, setting `Lifecycle.Graduating` and draining curve LT/tokens via `_prepareGraduationLiquidity` [11](#0-10) .
2. Before/during the keeper's `finalizeGraduation(tokenAddress)` call, an interaction with the HyperSwap V2 pair/router or `LPLock.recordLock` causes a revert that is not covered by the existing hostile-pre-seed hardening (e.g., `InsufficientLPBalance`/`AlreadyLocked` in `LPLock.recordLock` [12](#0-11) ).
3. Every subsequent call to `finalizeGraduation` hits the same revert deterministically; `buy`/`sell`/`triggerGraduation` all reject the token because `lifecycle != Curve`.
4. The token's curve LT and `tokensForLP` remain locked in `Bonding` indefinitely, with no owner or permissionless rescue function to move them.

### Citations

**File:** packages/contracts/src/Bonding.sol (L573-598)
```text
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
    }

    /// @notice Sell tokens on the curve. Router-only.
    function sell(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();
```

**File:** packages/contracts/src/Bonding.sol (L918-953)
```text
    function _executeBuy(
        address tokenHolder,
        address trader,
        uint256 amountIn,
        address tokenAddress
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
    }

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

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1449-1486)
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

        // Burn off-ratio TOKEN remainder (`Bonding` is the Token owner).
        // Hostile pre-seeds reduce circulating supply by the attacker's
        // wasted-side share, net positive for honest holders.
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
        // LT remainder is third-party — we cannot burn it. It stays in
        // this contract until `finalizeGraduation`'s post-bookend sweeps
        // it to the owner. Honest graduations never reach this code path,
        // so the residue is zero outside attack scenarios.
    }
```

**File:** packages/contracts/src/LPLock.sol (L29-36)
```text
        /// @dev Locker allowlist for `recordLock`. Add-only via `addLocker` —
        ///      there is no removal path. A live revoke would brick every
        ///      in-flight `Bonding.finalizeGraduation` (token permanently
        ///      stuck in `Lifecycle.Graduating`, no on-chain recovery), so
        ///      the only way to retire a locker is a UUPS upgrade — which
        ///      surfaces on-chain ahead of time instead of as a one-tx kill
        ///      switch.
        mapping(address account => bool) isLocker;
```

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
