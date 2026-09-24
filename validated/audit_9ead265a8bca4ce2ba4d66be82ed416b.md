### Title
Unbounded K-invariant slack in `Pair.swap` lets floor-rounding in `Router._computeBuy` / `_computeSell` permanently underflow `assetReserve - _launchTimeVirtualLtReserve`, bricking the curve - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Pair.sol], [File: packages/contracts/src/Router.sol])

### Summary
The CVE describes a parser that reads fixed-size fields out of an externally supplied buffer without validating that the buffer is actually large enough to contain them, producing an out-of-bounds read used downstream. The alt.fun analog is `Bonding._launchTimeVirtualLtReserve`, a value that is *derived* once at launch time and then subtracted from the pair's *live* `assetReserve` on every graduation check, without ever re-validating that the live reserve is still large enough to contain that derived quantity. Because `Pair.swap`'s K-invariant check only enforces a loose lower bound (the `+1` slack), and `Router._computeBuy`/`_computeSell` use floor division to derive the new reserves, every trade leaks a small amount of the curve's true invariant downward. Enough buy/sell round trips push the live `assetReserve` below the fixed `_launchTimeVirtualLtReserve`, causing an arithmetic underflow that permanently bricks the token's curve.

### Finding Description
`Bonding._launchTimeVirtualLtReserve` recovers the launch-time virtual LT reserve as an immutable identity: [1](#0-0) 

This value is subtracted from the pair's live `assetReserve` in three places that are all reachable by an unprivileged trader: `canGraduate` (called on every `buy()`), `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` (called from `_enterGraduating`/`triggerGraduation`): [2](#0-1) [3](#0-2) 

The subtraction assumes `assetReserve` can never fall below the launch-time virtual reserve. But `assetReserve` is mutated purely by `Pair.swap`, whose invariant check only enforces a *loose* floor via the `+1` slack: [4](#0-3) 

`Router._computeBuy` and `_computeSell` derive the trade output with floor division against `k`, so each individual trade lands the pool's *true* product strictly ≤ `k` (never re-normalized upward), and the `+1` slack in `Pair.swap` never rejects this monotonic decay: [5](#0-4) [6](#0-5) 

Because `tokenReserve` is bounded above by the initial virtual `totalSupply` (the curve can never sell/buy back more than the `curveSupply` that was ever removed), repeated buy-then-sell round trips return `tokenReserve` toward its initial ceiling while each round trip leaks a small amount of true reserve value from `assetReserve` due to the floor-rounding described above. This lets `assetReserve` drift strictly below the fixed `_launchTimeVirtualLtReserve` while `_pool.k` (and thus `_launchTimeVirtualLtReserve`) never changes (`Pair.swap` never modifies `_pool.k`). Once that happens, `assetReserve - _launchTimeVirtualLtReserve(...)` underflows and reverts with a `Panic(0x11)`.

### Impact Explanation
Every reachable entry point that could recover from this state calls the same vulnerable subtraction:
- `Bonding.buy` → `_executeBuy` → `canGraduate` (line 689-694) — every future buy reverts.
- `Bonding.sell` → `canGraduate` (line 598) — every future sell reverts.
- `Bonding.triggerGraduation` → `canGraduate` — cannot be used to force graduation either.
- `previewLtUntilGraduation` and `_prepareGraduationLiquidity`/`_enterGraduating` also underflow, so even a manual attempt to push the token to graduation reverts.

Since the underflow reverts the entire transaction (including the trade that caused it), the token's curve becomes permanently un-tradeable and un-graduatable: all LT and tokens already held by the `Pair` are frozen with no recovery path in the current contracts (no admin rescue function targets this state). This is a permanent freezing of trader and creator funds, satisfying the Validate criteria.

### Likelihood Explanation
The root cause is a purely mechanical, fee-less AMM leak: `Pair.swap`'s `+1` invariant slack combined with floor-division outputs in `Router._computeBuy`/`_computeSell` means **every single trade** loses a small amount of true `k` (this is normal/expected AMM slack, but here nothing ever re-derives or bounds `_launchTimeVirtualLtReserve` against the drifted state). An unprivileged trader can drive this by simply performing many small buy/sell round trips (or targeted extreme-ratio trades) on their own token, with no special privileges, no cross-contract dependency, and no reliance on the LT's or HyperSwap's internal behavior — only `Zap.buy`/`Zap.sell` (or direct `Bonding.buy`/`sell` via an allow-listed router) are needed.

### Recommendation
Make the graduation-threshold subtraction saturating (as already done defensively in `finalizeGraduation`'s `protectedLT` computation) or clamp `_launchTimeVirtualLtReserve` to at most the live `assetReserve` before subtracting, e.g.:
```solidity
uint256 virtualLt = _launchTimeVirtualLtReserve(token_, pair);
uint256 realLtRaised = assetReserve > virtualLt ? assetReserve - virtualLt : 0;
```
Apply the same guard in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity`. Separately, consider tightening `Pair.swap`'s invariant check (removing or shrinking the `+1` slack, or re-normalizing `_pool.k` periodically) to stop the underlying reserve leak from accumulating in the first place.

### Proof of Concept
1. Launch a token via `Zap.createToken`, establishing `_pool.k = totalSupply * virtualLtReserve` in `Pair.mint`.
2. Repeatedly call `Zap.buy` then `Zap.sell` for small amounts on the same token (any unprivileged wallet). Each round trip: `Router._computeBuy` sets `tokenReserve_new = floor(k / (assetReserve + amountIn))`, and `Router._computeSell` similarly floors `assetReserve_new = floor(k*... )`; `Pair.swap`'s check `(newTokenReserve+1)*(newAssetReserve+1) >= k` permits the actual stored product to end up below `k` on every iteration.
3. After enough round trips, `tokenReserve` returns to its original virtual ceiling (`totalSupply`) while `assetReserve` has drifted to a value strictly less than `_launchTimeVirtualLtReserve(token, pair) = k_initial / totalSupply` (which is fixed and unaffected by trading).
4. The next call to `Bonding.buy`/`sell`/`triggerGraduation` (or any view like `previewLtUntilGraduation`) executes `assetReserve - _launchTimeVirtualLtReserve(...)` and reverts with an arithmetic underflow `Panic(0x11)`, permanently bricking the token's curve and freezing any LT/tokens already deposited in the `Pair`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
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
