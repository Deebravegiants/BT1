Based on my review of the bonding-curve AMM math, I found a viable analog. The external report's bug class — a missing nil/availability check before a state read that can panic and crash the node — maps onto alt.fun's own unchecked subtractions that assume an invariant (`assetReserve ≥ virtualLtReserve`) that the AMM's own rounding behavior does not actually guarantee.

### Title
Trader-favoring rounding in `Router._computeBuy`/`_computeSell` erodes the pair's real invariant below the virtual seed, causing unchecked-subtraction underflow panics that permanently brick buys/sells and graduation - (File: `packages/contracts/src/Router.sol`, `packages/contracts/src/Bonding.sol`)

### Summary
`Router._computeBuy` and `Router._computeSell` compute trade outputs as `reserve - floor(k / newReserve)` [1](#0-0) [2](#0-1) . Flooring the subtracted term always rounds the *output* up, i.e. every buy and every sell is rounded in the trader's favor, never the pool's. `Pair.swap`'s K check only enforces `(newTokenReserve+1)*(newAssetReserve+1) ≥ k` [3](#0-2) , a slack wide enough to accommodate this drift without ever reverting the swap itself. Over repeated trading (organically, or accelerated by a single unprivileged trader running self-financed buy/sell round trips), the pair's real `tokenReserve*assetReserve` product erodes below the nominal `k`, which lets `assetReserve` drift below the launch-time virtual seed value that `Bonding` assumes it can never fall under.

### Finding Description
`Bonding.canGraduate` and `Bonding._prepareGraduationLiquidity` both perform the unchecked subtraction `assetReserve - _launchTimeVirtualLtReserve(...)` on the assumption that real LT raised is always non-negative: [4](#0-3) [5](#0-4) 

That assumption holds only if the pair's actual invariant never dips below the launch-time `k`. But `_computeBuy`/`_computeSell`'s floor-rounding scheme structurally leaks a small amount of the reserve to the trader on every trade (both buy and sell round the output *up*, not down), and `Pair.swap`'s `(x+1)(y+1) ≥ k` check is loose enough to never catch this drift. Given enough trades on a single curve — which an unprivileged trader can force cheaply by repeatedly buying and selling small amounts back and forth — `assetReserve` can be pushed below the launch-time virtual reserve.

Critically, `canGraduate` is called inline at the end of *every* buy via `_executeBuy`: [6](#0-5) 

Once the drift crosses the threshold, this internal call underflows and panics (`Panic(0x11)`), which reverts the *entire* buy transaction — not just the graduation check. The same unchecked subtraction is also hit by `_prepareGraduationLiquidity` during `_enterGraduating`/`triggerGraduation`, and by `previewLtUntilGraduation`'s off-chain preview path.

### Impact Explanation
Once triggered, every subsequent `Bonding.buy` reverts (because `_executeBuy` unconditionally calls `canGraduate`), and `triggerGraduation` reverts too. The curve becomes permanently un-buyable and un-gradulatable, and depending on whether `Bonding.sell`'s own `_computeSell` underflow is hit first, sells may brick as well — trapping curve-side LT and tokens with no recovery path (no admin rescue for a bricked curve pre-graduation). This is a permanent freeze of trader and creator funds on that token, matching the report's "prevent panic" bug class exactly: a missing defensive check before a subtraction that assumes an invariant the surrounding math does not actually preserve.

### Likelihood Explanation
Reachable purely through `Zap.buy`/`Zap.sell` → `Bonding.buy`/`sell`, both callable by any unprivileged address, no special permissions required. The rounding drift is small per trade, but a determined attacker can force many round trips (buy then sell back the same token amount) cheaply on a token with thin reserves to accelerate the erosion, and organic trading volume on a popular token achieves the same effect over time. Because the vulnerable subtraction sits on the hot path of every single buy (`_executeBuy`'s inline `canGraduate` call), the token only needs to be pushed past the drift threshold once for it to brick permanently.

### Recommendation
Round `_computeBuy`/`_computeSell` output *down* (or input *up*) so every trade rounds in favor of the pool, matching the standard UniswapV2-style safe-rounding convention, eliminating the invariant erosion at its source. As defense in depth, guard the `assetReserve - virtualLtReserve` (and the equivalent in `previewLtUntilGraduation`) with a saturating-subtract or explicit `if (assetReserve <= virtual) return false/0;` check, the same pattern already used defensively elsewhere in the codebase (e.g. `finalizeGraduation`'s saturating LT-balance subtraction) [7](#0-6) , so a drifted invariant degrades gracefully instead of bricking the curve.

### Proof of Concept
1. Launch a token via `Zap.createToken` with a minimal seed.
2. As an unprivileged trader, repeatedly call `Zap.buy` followed by `Zap.sell` for the same small token amount, many times, on the same curve.
3. Each round trip rounds slightly in the trader's favor per `Router._computeBuy`/`_computeSell`'s floor-division output computation, incrementally eroding `assetReserve` below the level `Pair.k()/Token.TOTAL_SUPPLY()` (the launch-time virtual reserve) implies it should be.
4. Once the drift crosses that boundary, the next `Zap.buy` call reverts inside `Bonding._executeBuy`'s inline `canGraduate` check with an arithmetic underflow panic, and `Bonding.triggerGraduation`/`previewLtUntilGraduation` revert identically — the curve is permanently stuck.

### Citations

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
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

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
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

**File:** packages/contracts/src/Bonding.sol (L1015-1020)
```text
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```
