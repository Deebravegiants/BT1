### Title
Permanent freeze via zero-liquidity graduation mint — `Bonding._prepareGraduationLiquidity` / `_seedDirectMint` ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE-2020-23872 class is "a code path that dereferences/derives a value assuming a non-degenerate state, and when that assumption breaks, the call unconditionally reverts/crashes with no recovery path, causing denial of service." The same class exists in alt.fun's two-phase graduation: `_prepareGraduationLiquidity` can compute `tokensForLP == 0` (or a value too small for HyperSwap V2's first-mint formula), and because that value is cached once in `pendingGraduation[token]` and never recomputed, `finalizeGraduation` reverts identically on every future call — the token is permanently stuck in `Lifecycle.Graduating`, with the curve's raised LT and the 250M reserved tokens unrecoverable (no rescue path exists in v1).

### Finding Description
Phase 1 (`Bonding._enterGraduating` → `_prepareGraduationLiquidity`) computes: [1](#0-0) 

`tokensForLP = (ltFromPair × tokenReserve) / assetReserve`, where `ltFromPair` is the *real* LT raised by the curve above the launch-time virtual reserve, i.e. `assetReserve - virtualLtReserve`: [2](#0-1) 

The USD graduation trigger fires as soon as `realLtRaised × exchangeRate ≥ graduationThresholdUsd`. If the LT's `exchangeRate()` has appreciated a lot before the trigger fires (a market condition external to the protocol, reachable by any unprivileged caller simply calling `Bonding.triggerGraduation` or `Zap.sell` once `canGraduate` is true), `realLtRaised` (i.e. `ltFromPair`) needed to cross the USD threshold can be extremely small in raw LT units, while `assetReserve` is dominated by the much larger launch-time `virtualLtReserve`. This drives `tokensForLP = ltFromPair × tokenReserve / assetReserve` toward zero via integer division rounding.

This cached pair `(tokensForLP, ltFromPair)` is stored verbatim in `PendingGraduation` and used byte-for-byte in Phase 2: [3](#0-2) 

Phase 2's happy path (≈99% of graduations, per the code's own comments) goes to `_seedDirectMint` when the HyperSwap pair has `totalSupply() == 0`: [4](#0-3) 

`_seedDirectMint` transfers `(tokensForLP, ltFromPair)` to the pair and calls the standard UniswapV2-style `pair.mint(lpLock)`. On a first mint (`totalSupply == 0`), V2's formula computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY` and reverts with `INSUFFICIENT_LIQUIDITY_MINTED` if that value is `≤ 0`. When `tokensForLP` rounds down to `0` (or is otherwise too small relative to `MINIMUM_LIQUIDITY = 1000`), `sqrt(0 * ltFromPair) = 0`, and the mint unconditionally reverts.

Because `finalizeGraduation` is `nonReentrant` and permissionless but recomputes nothing — it strictly replays the Phase-1-cached `p.tokensForLP` / `p.ltFromPair` — every subsequent call by the keeper or by "anyone" hits the exact same degenerate mint and reverts identically. There is no retry, no fallback, and no on-chain path to unstick the token: `info.lifecycle` stays `Graduating` forever, trading stays frozen (`Zap.buy`/`Zap.sell` both gate on `TokenIsGraduating`), and `ltFromPair` (already drained out of the curve pair into `Bonding` via `Router.graduate` in Phase 1) plus the `LP_RESERVE` token allocation are permanently stranded inside `Bonding` with no owner rescue function for this specific case (the LT rescue functions only sweep amounts *above* `p.ltFromPair`, which by design never releases the earmarked funds).

### Impact Explanation
This is a permanent freeze of protocol funds: the curve's entire raised LT balance and the 250M token LP allocation for the affected token become permanently locked with no possible recovery, and the token can never graduate, permanently blocking creator/trader exit via the graduated pool. This satisfies the "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
The trigger condition — LT price appreciating enough before the USD threshold is crossed that `realLtRaised` in raw LT units is tiny relative to the launch-time virtual reserve — is a normal market condition for a leveraged reserve asset, not an exotic attack. Any unprivileged holder can proactively call the permissionless `Bonding.triggerGraduation` (or trigger it via `Zap.sell`) the moment `canGraduate` becomes true, deliberately locking in a degenerate `tokensForLP` snapshot before a bigger real-LT raise could occur. No special role or contract interaction beyond a single transaction from an ordinary wallet is required.

### Recommendation
- Enforce a minimum viable `tokensForLP` (and/or `ltFromPair`) in `_prepareGraduationLiquidity`, e.g. reject or defer entering `Graduating` if `tokensForLP` would be below the HyperSwap V2 `MINIMUM_LIQUIDITY` threshold, or floor `tokensForLP` to a safe minimum while adjusting `lpBurned` accordingly.
- Add a rescue/retry path in `finalizeGraduation` for the degenerate case (e.g., allow Phase 2 to recompute or fall back to a minimum-liquidity floor rather than reverting unconditionally against a fixed cached value).
- Add a regression test that stages a large `exchangeRate` pump right at the USD-trigger boundary so `ltFromPair` is minimal, and assert `finalizeGraduation` still succeeds.

### Proof of Concept
1. Launch a token normally via `Zap.createToken` (curve opens with the standard virtual LT reserve).
2. Wait for (or, in a test, simulate) a large appreciation of the paired LT's `exchangeRate()` — plausible for a leveraged token tracking a volatile underlying.
3. As soon as `Bonding.canGraduate(token)` becomes `true` via the USD leg while `realLtRaised` is still very small in raw LT units (this is exactly the scenario the codebase's own `previewLtUntilGraduation`/`_ratePumpForStagedGraduation` test helpers stage), call `Bonding.triggerGraduation(token)` from any unprivileged EOA.
4. `_enterGraduating` computes and caches `tokensForLP = (ltFromPair * tokenReserve) / assetReserve`, which rounds to `0` (or near-`0`) because `assetReserve` is dominated by the large `virtualLtReserve` while `ltFromPair` is minimal.
5. Call the permissionless `Bonding.finalizeGraduation(token)`. `_seedDirectMint` calls `pair.mint(lpLock)` with `tokensForLP ≈ 0`, and the standard V2 `require(liquidity > 0, "INSUFFICIENT_LIQUIDITY_MINTED")` check reverts.
6. Any further call to `finalizeGraduation` replays the same cached `(tokensForLP, ltFromPair)` and reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, and the LT already drained into `Bonding` in step 4 can never be deposited into the LP or otherwise recovered.

### Citations

**File:** packages/contracts/src/Bonding.sol (L691-695)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
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

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1217-1259)
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
