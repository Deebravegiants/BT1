### Title
Zero-rounded `tokensForLP` at graduation can permanently revert `finalizeGraduation`, freezing curve-raised LT and the 250M LP reserve - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes a crash triggered by an edge-case empty/malformed input (`OIDCStripCookies` + empty `Cookie`) that the code never defensively checked for, causing a NULL-pointer dereference. The analog in alt.fun is a degenerate value computed by `Bonding._prepareGraduationLiquidity` — `tokensForLP` — that can legitimately round to `0` via integer division under a large `exchangeRate()` pump combined with a small real LT raise, and is never checked to be non-zero before it is fed into HyperSwap V2's `pair.mint`. Because the graduation math is cached once in phase 1 and reused verbatim in phase 2 with no recovery path, a `0`-amount mint permanently reverts `finalizeGraduation` for that token.

### Finding Description
`_prepareGraduationLiquidity` computes the LP-bound token amount purely from stored pair reserves: [1](#0-0) 

`tokensForLP = (ltFromPair * tokenReserve) / assetReserve` is only capped from above (`≤ LP_RESERVE`, proved by the parabola invariant per `docs/contracts-scope.md` and `AGENTS.md`); there is no lower-bound guarantee or explicit non-zero check. `assetReserve` is dominated by the launch-time virtual LT reserve (`_launchTimeVirtualLtReserve`, `Pair.k()/TOTAL_SUPPLY()`), which is a large fixed constant calibrated to open every curve at ~$3K market cap. The USD graduation trigger is `(storedAssetReserve - virtualLtReserve) × exchangeRate() ≥ $9K` — i.e. it is satisfied by the *product* of raw LT raised and the live, externally-controlled `exchangeRate()` of the BounceTech LT (a rebasing/leveraged price feed), documented as read live and un-settled at read time: [2](#0-1) 

If `exchangeRate()` is large enough (a leverage/price spike inherent to the LT design that the protocol explicitly accepts as normal, per the "Exchange-rate freshness" note), the USD trigger fires while the raw `ltFromPair` (numerator input into `tokensForLP`) is still tiny relative to the still-near-virtual `assetReserve` denominator. Integer division then rounds `tokensForLP` down to `0`.

Once `tokensForLP == 0` is cached in `pendingGraduation` at phase 1 (`_enterGraduating`), phase 2's `finalizeGraduation` reads it back unconditionally: [3](#0-2) 

For a fresh HyperSwap pair (the ~99% "empty pair" happy path), `_seedUniswapV2Direct` routes straight to `_seedDirectMint`, which transfers `0` TOKEN and `ltFromPair` LT to the pair and calls `pair.mint`: [4](#0-3) 

A UniswapV2-style `mint` on a pair with zero total supply computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY`; with `amount0 == 0` this is `sqrt(0) - 1000`, which underflows/reverts (`INSUFFICIENT_LIQUIDITY_MINTED` or a Panic, depending on the pair implementation). `finalizeGraduation` therefore reverts on every call, forever — the cached `(tokensForLP, ltFromPair)` never change (the code explicitly documents this as intentional: "Exchange-rate drift ... is accepted by design ... a recompute would return byte-identical values"), so there is no way to retry into success.

The token is permanently stuck in `Lifecycle.Graduating`: trading is frozen (`buy`/`sell` revert with `TokenIsGraduating`), the real LT drained by `Router.graduate` in phase 1 and the (up to) 250M `LP_RESERVE` tokens are already committed to this graduation and sit unusable on `Bonding`, and `LPLock` — by design — has no rescue mechanism for anything that doesn't complete a `recordLock` (per its own natspec: "the only way to retire a locker is a UUPS upgrade"). There is no owner/admin path in v1 to cancel or retry a stuck `Graduating` token or to move funds back to `Curve`.

### Impact Explanation
This is a permanent freeze of trader/creator funds: the LT raised on the curve (drained via `Router.graduate` in phase 1) and up to 250M reserved tokens become permanently unrecoverable, and every holder of the token loses the ability to trade it (curve is frozen in `Graduating`, and it can never reach `Graduated` to open on HyperSwap). This satisfies the "permanent freezing of trader, creator or LP funds" bar for High severity.

### Likelihood Explanation
Reachability depends on the concrete magnitude of the launch-time virtual LT reserve, the $9K USD threshold, and the practical bounds/velocity of the BounceTech LT's `exchangeRate()` — parameters I could not fully pin down from the indexed contract constants/deploy script within the available tool budget. The mechanism itself (integer-division rounding of `tokensForLP` to `0` while `ltFromPair > 0`) is unconditionally reachable in the code as written and requires no privileged role — any unprivileged trader can be the one whose ordinary buy crosses the USD threshold at a moment the LT's price has spiked, which is an externally-controlled, protocol-accepted condition rather than an attacker-crafted one. Given the codebase's extensive, explicit invariant testing around the *upper* bound of `tokensForLP` (`tokensForLP ≤ LP_RESERVE`) and total absence of any lower-bound (`> 0`) guarantee or test, this looks like a genuine gap rather than a defended edge case, but I could not conclusively confirm parameter-level reachability against production constants.

### Recommendation
Add an explicit floor check in `_prepareGraduationLiquidity` (or immediately before the `pair.mint` calls in `_seedDirectMint`/`_seedRebalancing`) that reverts *before* caching `pendingGraduation` if `tokensForLP == 0` (or below UniswapV2's `MINIMUM_LIQUIDITY` requirement), or floors `tokensForLP` to a minimum viable amount so the mint can never structurally fail. Since phase 1 is the only point at which the values are computed and frozen, the check must live there so a degenerate ratio blocks entry into `Graduating` rather than bricking `finalizeGraduation` after the LT has already been drained.

### Proof of Concept
Conceptual (parameter-dependent; not verified against production constants):
1. Launch a token normally via `Bonding.launch` (virtual LT reserve seeded per standard sizing).
2. Have an unprivileged trader submit a small `Zap.buy` that lands while the paired BounceTech LT's `exchangeRate()` is transiently very high (a normal market condition for a leveraged token, not an exploit of BounceTech itself), such that `(assetReserve - virtualLtReserve) × exchangeRate() ≥ $9K` while the raw `ltFromPair = assetReserve - virtualLtReserve` is still small relative to `assetReserve`.
3. This buy triggers `_enterGraduating` → `_prepareGraduationLiquidity`, computing `tokensForLP = (ltFromPair * tokenReserve) / assetReserve == 0` due to integer-division rounding, cached into `pendingGraduation[token]`.
4. Anyone calls `Bonding.finalizeGraduation(token)`; it reaches `_seedDirectMint`, transfers `0` TOKEN / nonzero LT to the fresh HyperSwap pair, and `pair.mint(lpLock)` reverts (`INSUFFICIENT_LIQUIDITY_MINTED`/underflow).
5. Every subsequent call to `finalizeGraduation(token)` reverts identically forever — the token is permanently stuck in `Lifecycle.Graduating`, its drained LT and reserved 250M tokens unrecoverable.

### Citations

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

**File:** docs/contracts-scope.md (L68-76)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

```
