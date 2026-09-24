### Title
Rounding-favored-trader curve math + loose `Pair.swap` K-slack lets an underflow permanently brick `Bonding.buy`/`Bonding.sell` for a token - ([File: packages/contracts/src/Pair.sol])

### Summary
CVE-2022-43034 is a heap buffer overflow in Bento4's `AP4_BitReader::SkipBits` caused by insufficient bounds validation before an arithmetic step (skipping past the buffer's real size). The analogous root cause here is a missing bounds/invariant check on the arithmetic that derives `realLtRaised` in `Bonding.canGraduate` / `Bonding.previewLtUntilGraduation`: both do an unchecked subtraction `assetReserve - virtualLtReserve` that assumes `assetReserve` can never drop below the launch-time virtual reserve. That assumption is not actually enforced by `Pair.swap`'s invariant check, which is looser than the amounts `Router._computeBuy` / `Router._computeSell` actually apply, letting the pair's real product drift below `k` on every trade. Because `canGraduate` is called unconditionally inside `Bonding.sell` and after every `Bonding.buy`, an underflow there reverts and permanently bricks both trading directions for the affected token.

### Finding Description
`Pair.swap` enforces the curve invariant with a flat epsilon instead of an exact or fee-adjusted check: [1](#0-0) 

```
uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
```

This accepts any post-trade state whose true product `newTokenReserve * newAssetReserve` is up to `newTokenReserve + newAssetReserve + 1` below `k` — nowhere near "K never decreases".

`Router._computeBuy` and `Router._computeSell` compute the swap amounts by flooring the *other* side's required reserve: [2](#0-1) 

```
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);   // floor(k/newReserveAsset) ⇒ tokensOut rounds UP
...
uint256 newReserveToken = reserveToken + amountIn;
assetOut = reserveAsset - (k / newReserveToken);    // floor(k/newReserveToken) ⇒ assetOut rounds UP
```

Both legs floor-divide `k` by the *known* side to derive the *other* reserve, which always rounds the trader's output **up** relative to the true continuous curve. This means both `buy` and `sell` systematically leak value to the trader, and `Pair.swap`'s loose `+1` check never rejects it. A round-trip (`Zap.buy` then `Zap.sell`, or vice versa) on the same token therefore lets an attacker extract dust LT from the pair's *stored* `assetReserve` beyond what the curve should allow, pushing `assetReserve` down over repeated trades.

`Bonding.canGraduate` and `Bonding.previewLtUntilGraduation` both assume `assetReserve >= virtualLtReserve` (the launch-time virtual seed, recovered via `Pair.k() / Token.TOTAL_SUPPLY()`) and perform an unchecked subtraction with no floor/clamp: [3](#0-2) 

```
(, uint256 assetReserve) = IPair(pair).getReserves();
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
``` [4](#0-3) 

If `assetReserve` is ever driven (even by a single wei) below the recovered `virtualLtReserve`, this subtraction underflows and reverts under Solidity 0.8's checked arithmetic — the exact analog of the CVE's bounds-check omission before an out-of-range arithmetic operation.

`canGraduate` is not an isolated view — it is load-bearing on both trading paths: [5](#0-4) 

```
if (canGraduate(tokenAddress)) revert TokenIsGraduating();   // sell() — reverts if canGraduate reverts
``` [6](#0-5) 

```
(amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);
...
if (canGraduate(tokenAddress)) {                              // buy() — reverts if canGraduate reverts
    _enterGraduating(tokenAddress);
}
```

So a single underflow in `canGraduate` permanently reverts **every subsequent `buy` and `sell`** on that token's curve — nobody can trade in or out again, and the token can never reach the USD/supply graduation trigger either (both paths call `canGraduate`), stranding all LT and tokens already committed to that pair.

### Impact Explanation
Once `assetReserve` drifts to (or below) `virtualLtReserve`, `canGraduate` reverts on every call. Both `Bonding.buy` and `Bonding.sell` unconditionally call `canGraduate` (directly, or via `_executeBuy`), so the entire curve for that token becomes permanently unusable: existing holders cannot sell their tokens back for LT, the creator/other buyers cannot buy, and the token can never graduate (the only two graduation triggers are also gated behind `canGraduate`/its subtraction). This is a permanent freeze of every trader's and creator's funds already deposited in that specific bonding-curve pair — no admin recovery path exists for `Bonding`/`Router`/`Pair` state once bricked this way.

### Likelihood Explanation
Any unprivileged wallet can reach this purely through `Zap.buy` / `Zap.sell` (or their permit variants), which are permissionless. The floor-rounding-in-favor-of-the-trader behavior in `Router._computeBuy`/`_computeSell` is deterministic and reproducible on every call, and `Pair.swap`'s `+1` invariant never blocks it. The magnitude of drift per round trip is sub-wei-level dust, so triggering the underflow in practice requires either (a) an extremely long sequence of round trips concentrating the accumulated rounding loss, or (b) a curve whose `virtualLtReserve` and `assetReserve` are already close (e.g. right after launch, before much LT has been raised, when the gap between `assetReserve` and `virtualLtReserve` is smallest). The bug is real and root-caused in production code, but the number of transactions needed to force the underflow in the general case is high; it is most exploitable against freshly-launched, thinly-traded curves where the buffer between `assetReserve` and `virtualLtReserve` is naturally minimal.

### Recommendation
- Make `Pair.swap`'s invariant check exact/monotonic (no `+1` slack) so no trade can ever leave the real product below `k`, e.g. require `newTokenReserve * newAssetReserve >= k` unless the trade is deliberately rounding in the pool's favor.
- In `Router._computeBuy`/`_computeSell`, round the trader's output **down** (in the pool's favor) rather than rounding the counter-reserve up, consistent with standard AMM practice (Uniswap V2 rounds fee-adjusted balances in favor of the pool).
- Defensively clamp the subtraction in `Bonding.canGraduate` and `Bonding.previewLtUntilGraduation` (`realLtRaised = assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`) so a rounding-driven dip can never revert-brick the curve, mirroring the saturating-subtract pattern already used elsewhere in the codebase (e.g. `finalizeGraduation`'s `protectedLT` computation).

### Proof of Concept
1. Launch a token via `Zap.createToken` with the minimum seed (`Zap.MIN_SEED_USDC`), so `assetReserve` starts only marginally above `virtualLtReserve`.
2. From an unrelated wallet, repeat `Zap.buy(token, smallUsdc, 0, ref)` immediately followed by `Zap.sell(token, tokensJustBought, 0)` many times. Each round trip lets `Router._computeBuy`/`_computeSell`'s floor-division rounding hand the trader marginally more output than the exact curve would, which `Pair.swap`'s loose `(x+1)(y+1) >= k` check does not reject, so the pair's stored `assetReserve` slowly decreases relative to `virtualLtReserve`.
3. Once `assetReserve` dips to/below `_launchTimeVirtualLtReserve(token, pair)` (`Pair.k() / Token.TOTAL_SUPPLY()`), the next call to `Bonding.canGraduate(token)` underflows and reverts.
4. Any subsequent `Zap.buy` or `Zap.sell` on that token now reverts unconditionally (both call `canGraduate` internally), permanently freezing every holder's and the creator's position in that curve with no recovery path.

### Citations

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

**File:** packages/contracts/src/Router.sol (L127-182)
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

    /// @notice Tokens in → LT out.
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }

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

**File:** packages/contracts/src/Bonding.sol (L592-600)
```text
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();

        (, uint256 assetOut) = $.router.sell(amountIn, tokenAddress, msg.sender);
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

**File:** packages/contracts/src/Bonding.sol (L923-931)
```text
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
```
