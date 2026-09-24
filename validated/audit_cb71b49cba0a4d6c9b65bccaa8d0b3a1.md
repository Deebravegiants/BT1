### Title
Rounding a tiny `ltFromPair` to a zero `tokensForLP` (or vice versa) permanently bricks `finalizeGraduation`, freezing all curve-raised LT and the LP reserve forever - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`_prepareGraduationLiquidity` computes `tokensForLP = (ltFromPair * tokenReserve) / assetReserve` with plain integer division and no floor/zero check. When the USD-value graduation trigger fires on a curve that has raised very little real LT relative to the (potentially very large) launch-time virtual LT reserve, this division can truncate to `0` while `ltFromPair` is still positive (or the symmetric case where `ltFromPair` itself is negligible). The zero value is cached in `pendingGraduation` and carried unchanged into phase 2, where `_seedDirectMint` calls the HyperSwap pair's `mint()` with one side equal to `0`. A vanilla UniswapV2-style `mint()` reverts when the computed liquidity is zero, so `finalizeGraduation` reverts every time it is called — deterministically and forever, since the cached `pendingGraduation` values never change while the token is `Lifecycle.Graduating`.

### Finding Description
`_prepareGraduationLiquidity` derives the LP-bound token amount from the LP-bound LT amount: [1](#0-0) 

`ltFromPair = assetReserve - virtualLtReserve` is the *real* LT raised by the curve. Because the launch-time virtual LT reserve (`Pair.k() / TOTAL_SUPPLY()`) can be large relative to a curve that has raised only a small amount of real LT, `tokensForLP = ltFromPair * tokenReserve / assetReserve` can floor to `0` even when `ltFromPair > 0`.

The USD-value graduation trigger is driven by `exchangeRate`, an externally-controlled, rebasing price feed on the LT (documented in `AGENTS.md` as read live via `exchangeRate`). Pushing `exchangeRate` up (via ordinary buys, or LT appreciation as exercised by the repo's own test helper `_ratePumpForStagedGraduation`) lets a curve with a tiny real LT raise satisfy `(storedAssetReserve − virtualLtReserve) × exchangeRate ≥ $9K` while `ltFromPair` (in raw LT units) stays small relative to `assetReserve` (dominated by the virtual component). This is exactly the condition under which `tokensForLP` rounds to `0`.

`_enterGraduating` caches this degenerate pair verbatim: [2](#0-1) 

`finalizeGraduation` then reads the frozen cache and drives phase-2 seeding with `tokensForLP = 0`: [3](#0-2) 

For a fresh pair (`totalSupply() == 0`, the ~99% case), `_seedUniswapV2Direct` routes straight to `_seedDirectMint`: [4](#0-3) 

`_seedDirectMint` calls `IUniswapV2Pair(pair).mint(lpLock)` after transferring `tokensForLP = 0` tokens and `ltFromPair` LT to the pair. A standard V2 pair's `mint()` computes `liquidity = sqrt(amount0*amount1)` on first mint, which is `0` whenever either transferred amount is `0`, and reverts with `INSUFFICIENT_LIQUIDITY_MINTED`. This causes the entire `finalizeGraduation` transaction — including the `Lifecycle.Graduating → Graduated` flip and `LPLock.recordLock` — to revert and roll back.

Because `pendingGraduation[tokenAddress]` is byte-identical on every subsequent call (the whole design intentionally freezes these values while `Lifecycle.Graduating`, per the contract's own natspec: "a recompute would return byte-identical values... re-pricing... would break the zero-gap-in-LT-units invariant"), every future call to permissionless `finalizeGraduation` reverts identically. There is no owner override, no recovery function, and `triggerGraduation`/`buy`/`sell` are all gated to revert for a token stuck in `Lifecycle.Graduating` (`TokenIsGraduating`). The `LPLock.recordLock` one-shot guard and its `ZeroAmount` check reinforce that a zero-liquidity path was anticipated for the *deposit-skip* branch of `_routerDepositAndDispose`, but not for the `_seedDirectMint` first-mint branch, which has no analogous zero-guard or fallback: [5](#0-4) 

This is the direct analog of the CVE's root cause: a code path that assumes a non-degenerate input (a non-null `bp` in the kernel case; a non-zero `tokensForLP`/`ltFromPair` here) is reachable from an unprivileged, externally-influenceable state (a corrupted xfs image; an LT-appreciation-driven graduation with a near-zero real raise) and the missing check turns into an unrecoverable, permanent failure of the finalize/cleanup path rather than a contained error.

### Impact Explanation
Once triggered, the token is permanently stuck in `Lifecycle.Graduating`: trading (`buy`/`sell`) is frozen (`TokenIsGraduating`), no HyperSwap LP is ever created, and all curve-raised LT plus the 250M `LP_RESERVE` tokens (already burned down by `lpBurned = LP_RESERVE - tokensForLP` in phase 1, which already executed and is not rolled back) sit unusable in `Bonding` forever. This is a permanent freeze of trader/creator funds with no on-chain recovery path — a High/Medium-severity denial-of-funds condition matching the "permanent freezing of trader, creator or LP funds" acceptance criterion.

### Likelihood Explanation
Reachable by any unprivileged party through ordinary permissionless calls: buys that push the curve's LT holdings up combined with the reserve-asset's own `exchangeRate` appreciation (or a large legitimate/attacker buy that pumps the USD-denominated trigger while the real LT raise stays numerically small relative to the virtual reserve), followed by a call to permissionless `triggerGraduation` / the inline trigger inside `buy`, and finally `finalizeGraduation`. No special privileges, roles, or upgrade access are required — only the ordinary `Zap.buy`/`Bonding.triggerGraduation`/`Bonding.finalizeGraduation` entry points named in the rules.

### Recommendation
In `_prepareGraduationLiquidity`, explicitly guard the degenerate case where `tokensForLP` (or `ltFromPair`) rounds to `0` — e.g. revert `NotGraduatable`-style before entering `Graduating`, or floor `tokensForLP` to a minimum non-zero amount consistent with the parabola invariant — so that `_enterGraduating` can never cache a pair that will deterministically brick `_seedDirectMint`'s first `mint()`. Additionally, add a defensive fallback/guard in `_seedDirectMint` for a zero-amount side (mirroring the `ZeroAmount` protection already present in `LPLock.recordLock`) so a degenerate cache cannot deadlock phase 2 irrecoverably.

### Proof of Concept
1. Launch a token via `Bonding.launch` (virtual LT reserve fixed at `Pair.k() / TOTAL_SUPPLY()`, large relative to a small real raise).
2. Buy a small amount of curve tokens with LT so that `assetReserve` grows only slightly above the virtual reserve (`ltFromPair` stays numerically tiny relative to `assetReserve`).
3. Pump `exchangeRate` on the mock/real LT (as done in the repo's own `_ratePumpForStagedGraduation` helper) until `(storedAssetReserve − virtualLtReserve) × exchangeRate ≥ $9K`, satisfying `canGraduate` via the USD trigger while `ltFromPair` (raw LT units) remains small enough that `tokensForLP = ltFromPair * tokenReserve / assetReserve` floors to `0`.
4. Call permissionless `bonding.triggerGraduation(tokenAddress)` — phase 1 caches `pendingGraduation.tokensForLP = 0`.
5. Call permissionless `bonding.finalizeGraduation(tokenAddress)` — `_seedDirectMint` transfers `0` tokens / `ltFromPair` LT to the fresh pair and calls `pair.mint(lpLock)`, which reverts with `INSUFFICIENT_LIQUIDITY_MINTED`.
6. Every subsequent call to `finalizeGraduation` reverts identically because `pendingGraduation` is frozen; the token is permanently stuck in `Lifecycle.Graduating` with trading disabled and all raised LT/LP_RESERVE tokens locked in `Bonding`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
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
