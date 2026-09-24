### Title
Unvalidated `assetReserve - virtualLtReserve` subtraction can underflow and permanently brick graduation and trading - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2016-2328 is a class of bug where a size/dimension value that feeds into pointer/array arithmetic is never validated against the data it is applied to, producing out-of-bounds access. The on-chain analog in alt.fun is `Bonding.canGraduate` / `previewLtUntilGraduation` / `_prepareGraduationLiquidity`, which all compute `realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token, pair)` without ever validating that the stored `assetReserve` is actually ≥ the recovered launch-time virtual reserve. Solidity 0.8's checked arithmetic turns an out-of-bounds read into a `Panic(0x11)` revert instead of silently returning garbage, but the root cause is identical: a derived "size" value (`virtualLtReserve`, recovered from `Pair.k() / TOTAL_SUPPLY()`) is subtracted from a live, attacker-influenceable counter (`assetReserve`) whose lower bound is never independently enforced on-chain — it is only assumed to hold by curve-invariant reasoning.

### Finding Description
`Bonding._launchTimeVirtualLtReserve` recovers the launch-time virtual LT reserve as `Pair.k() / Token.TOTAL_SUPPLY()`: [1](#0-0) 

This value is subtracted from the pair's live `assetReserve` in three places without any `>=` check: [2](#0-1) [3](#0-2) [4](#0-3) 

The invariant the code relies on ("assetReserve can never fall below virtualLtReserve because K is fixed and tokenReserve can never exceed TOTAL_SUPPLY") is enforced only loosely by `Pair.swap`'s K-invariant check, which itself has an off-by-one slack on **both** reserve terms: [5](#0-4) 

`Router._computeSell` derives the post-sell `newReserveAsset` as a **floor** division `k / newReserveToken`, and the only gate that a sell must pass is `(newTokenReserve + 1) * (newAssetReserve + 1) >= k` — not the exact `newTokenReserve * newAssetReserve >= k`: [6](#0-5) 

Because `virtualLtReserve` (bounded up to `type(uint112).max/4`, i.e. up to ≈2^108) can be many orders of magnitude larger than `TOTAL_SUPPLY` (a fixed constant, ≈2^90), the `+1` slack on the token side of the K-check is not negligible relative to `virtualLtReserve`: when the pool is driven back toward `tokenReserve == TOTAL_SUPPLY` (i.e., a trader who bought sells the tokens back, tokenBalance returning toward the curve max), the loosened inequality permits `newAssetReserve` to land measurably below the exact ratio implied by `k`, and specifically below `virtualLtReserve` itself once the accumulated floor-rounding across repeated buy/sell round-trips (each pass through `_computeSell`'s `k / newReserveToken` floor) erodes `assetReserve` under the true curve value. No code path re-checks or clamps `assetReserve` against `virtualLtReserve` after a swap — `Pair.swap` only asserts the loosened K bound, and the subtraction sites simply assume `assetReserve >= virtualLtReserve` always holds.

Because `Bonding.buy` and `Bonding.sell` unconditionally invoke `canGraduate` at the end of every trade (via `_executeBuy`) and at entry (via `sell`'s `canGraduate` gate), an underflow inside `canGraduate` (or `previewLtUntilGraduation`, called by `Zap._executeBuy` on every non-graduated buy) reverts the whole transaction with an unrecoverable Solidity Panic: [7](#0-6) [8](#0-7) 

Once this state is reached, every future `buy`, `sell`, and `triggerGraduation` call on that token reverts unconditionally (there is no owner or user recovery path — the subtraction is unconditional in all three call sites), permanently freezing all LT and tokens already parked in the `Pair` for that token.

### Impact Explanation
This is a permanent freeze of trader/LP funds: once `assetReserve` drifts below the recovered `virtualLtReserve`, `canGraduate` (and by extension `buy`, `sell`, `triggerGraduation`, and `previewLtUntilGraduation`/`Zap.buy`) permanently revert for that token. The LT raised on the curve and the tokens held in the `Pair` become unrecoverable — trading is bricked and graduation can never be triggered, satisfying the "permanent freezing of trader, creator, or LP funds" bar from an unprivileged, permissionless entry point (`Zap.buy`/`Zap.sell` → `Bonding.buy`/`Bonding.sell`/`triggerGraduation`).

### Likelihood Explanation
Triggering requires driving `tokenReserve` back up toward `TOTAL_SUPPLY` (i.e., selling back most/all curve-bought tokens) while accumulating enough floor-rounding drift across many small buy/sell round trips, or a single large round-trip near the top of the curve, to erode `assetReserve` below `virtualLtReserve`. This is reachable purely through the public `Zap.buy`/`Zap.sell` interface by any unprivileged trader and does not require any privileged role, but the magnitude of drift needed depends on how large `virtualLtReserve` is relative to `TOTAL_SUPPLY` for a given LT's `exchangeRate()` at launch (larger drift potential for LTs with very low exchange rates, since `virtualLtReserve = VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate` grows as `exchangeRate` shrinks, up to the `type(uint112).max/4` cap). I was not able to fully simulate the exact number of round trips or rounding steps required to cross the threshold within this review — that requires a Foundry fuzzing/invariant run against `_computeSell`/`Pair.swap` with an adversarial choice of `exchangeRate` near the `ExchangeRateTooLow` boundary, which I could not execute here.

### Recommendation
- Replace every unguarded `assetReserve - virtualLtReserve` (and the equivalent in `previewLtUntilGraduation` and `_prepareGraduationLiquidity`) with a saturating subtraction (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`), mirroring the saturating pattern already used elsewhere in `Bonding.sol` (e.g. `finalizeGraduation`'s `ltBalance > p.ltFromPair ? ... : 0`).
- Tighten `Pair.swap`'s K-invariant check to remove the `+1` slack on the side whose reserve is large relative to `TOTAL_SUPPLY`, or explicitly bound the allowed downward drift of `assetReserve` relative to the recovered `virtualLtReserve`.

### Proof of Concept
Conceptual (not executed):
1. Launch a token against an LT with a very low `exchangeRate()` such that `virtualLtReserve = VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate` is close to the `type(uint112).max/4` cap, maximizing the ratio `virtualLtReserve / TOTAL_SUPPLY`.
2. As an unprivileged trader, repeatedly call `Zap.buy` then `Zap.sell` (round-tripping small amounts) to drive `Pair`'s `tokenReserve` back toward `TOTAL_SUPPLY`, relying on `Router._computeSell`'s floor division and `Pair.swap`'s loosened `(x+1)*(y+1) >= k` check to shave `assetReserve` down below the exact curve ratio on each pass.
3. Once accumulated drift pushes `assetReserve` below `_launchTimeVirtualLtReserve(token, pair)`, any subsequent call to `Bonding.canGraduate` (invoked internally by `buy`, `sell`, and `triggerGraduation`) reverts with an arithmetic underflow panic, permanently freezing further trading and graduation for that token.

### Citations

**File:** packages/contracts/src/Bonding.sol (L588-606)
```text
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

        (, uint256 assetOut) = $.router.sell(amountIn, tokenAddress, msg.sender);
        if (assetOut < amountOutMin) revert SlippageExceeded();

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, false, assetOut, amountIn, newCurveSupply, newLtReserve);
        return assetOut;
    }
```

**File:** packages/contracts/src/Bonding.sol (L689-694)
```text
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L717-726)
```text
        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Bonding.sol (L918-932)
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
```

**File:** packages/contracts/src/Bonding.sol (L1084-1084)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
```

**File:** packages/contracts/src/Bonding.sol (L1114-1119)
```text
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/src/Router.sol (L172-182)
```text
    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }
```
