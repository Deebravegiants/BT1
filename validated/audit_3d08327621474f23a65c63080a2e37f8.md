### Title
Unguarded underflow-panic in `Router._computeBuy` / `_computeSell` from K-invariant slack, unlike the graceful pattern used elsewhere - ([File: packages/contracts/src/Router.sol, packages/contracts/src/Pair.sol])

### Summary
`Pair.swap` enforces the curve invariant with a `+1` slack: `(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` reverts, but this permits the *actual* stored product `tokenReserve * assetReserve` to drift slightly below the immutable `k` on every trade. [1](#0-0)  `Router._computeBuy` and `_computeSell` both assume the stored reserves satisfy the curve exactly and perform a bare subtraction against `k / newReserve` with no underflow guard. [2](#0-1) [3](#0-2) 

### Finding Description
`Pair.mint` sets `k = tokenReserve * assetReserve` once at launch and never updates it afterward. [4](#0-3)  Every subsequent `swap` recomputes new reserves and only checks that the *slack-padded* product `(newTokenReserve+1)*(newAssetReserve+1)` is not below `k`, then unconditionally commits `newTokenReserve`/`newAssetReserve` as the new stored reserves. [5](#0-4)  Because the check is padded by `+1` on each side while the *actual* committed reserves are not padded, the real product `tokenReserve * assetReserve` can end up strictly less than `k` after a swap, and this shortfall can accumulate over a sequence of trades on the same pair.

Both AMM math helpers in `Router.sol` derive the counter-reserve straight from `k` divided by the *other* new reserve, then subtract from the *current stored* reserve with plain Solidity arithmetic (checked, so an underflow reverts with a raw `Panic(0x11)` rather than a custom error):
- `_computeBuy`: `tokensOut = reserveToken - (k / newReserveAsset);` [6](#0-5) 
- `_computeSell`: `assetOut = reserveAsset - (k / newReserveToken);` [7](#0-6) 

If accumulated slack ever pushes `k` far enough above the true `reserveToken * reserveAsset` product that `k / newReserve` (for some trade size) exceeds the current stored counter-reserve, these lines underflow and the enclosing call reverts with an unguarded VM `Panic`. Since `Router.buy`/`Router.sell` are the only path `Bonding.buy`/`Bonding.sell` (and therefore `Zap.buy`/`Zap.sell`) use to price every trade on a given curve pair, once a pair's stored reserves drift enough to trip this, every subsequent buy and sell against that pair reverts — there is no fallback venue before graduation, so curve-side users cannot exit or enter, and the token can also become unable to reach a graduation trigger if trading is bricked before `canGraduate` fires.

This is the same bug class as the referenced rust-lightning fix: code that "should remain unreachable" (the codebase explicitly treats a similar saturating-subtract need as necessary defensive coding elsewhere — see `Bonding.finalizeGraduation`'s comment "we keep finalize from bricking on a Panic if any future code path... briefly violates the invariant" and its guarded `ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0`) [8](#0-7)  was never applied to the analogous arithmetic in `Router._computeBuy`/`_computeSell`, leaving a raw Solidity Panic as the sole failure mode for curve-side trades once the `+1` K slack accumulates.

### Impact Explanation
A bricked curve pair means every trader holding the launched token pre-graduation cannot sell (funds stuck in the token, no exit venue since the HyperSwap pair doesn't exist pre-graduation) and no one can buy further, and if this occurs before the graduation threshold is crossed the token can never graduate to get an alternate trading venue. This is a permanent freezing-of-funds condition for a token's curve-side holders, reachable purely through the normal permissionless `Bonding.buy`/`Bonding.sell` (or `Zap.buy`/`Zap.sell`) trade sequence — not any privileged path.

### Likelihood Explanation
The `+1` slack is a fixed per-swap tolerance baked into every `Pair.swap` call, so the drift accumulates deterministically with trade count rather than requiring an unusual state. Triggering the exact underflow requires the accumulated slack to be large enough relative to the reserves at the moment of a given trade size, which for the default 18-decimal, billion-token reserves used at launch may require a very large number of trades or reserves compressed near the tail end of the curve (e.g., late in the curve close to graduation, where `k`, expressed via a much smaller counter-reserve, amplifies rounding sensitivity). The precise trigger conditions were not verified with a concrete numeric trace in this review, so likelihood should be treated as plausible-but-unconfirmed rather than proven-exploitable.

### Recommendation
Apply the same defensive, saturating-subtract pattern already used in `Bonding.finalizeGraduation` (and `_sweepLTToOwner`) to `Router._computeBuy` and `_computeSell`: check that the subtrahend does not exceed the stored reserve before subtracting, and revert with a descriptive custom error (e.g., `reuse OverflowCapDegenerate` or a new `CurveInvariantDrift` error) instead of letting the operation fall through to a raw arithmetic `Panic`. Additionally, consider tightening or removing the `+1`/`+1` slack in `Pair.swap`'s K-invariant check (or re-deriving `k` from the freshly committed reserves periodically) so the stored reserves cannot drift below the value `k` implies over the life of a pair.

### Proof of Concept
Not independently reproduced with a concrete numeric trace in this review; the root cause is structural (unbounded, unguarded slack accumulation feeding un-guarded subtraction) and can be confirmed/refuted by fuzzing `Router._computeBuy`/`_computeSell` against a `Pair` driven through a long sequence of minimum-size swaps and checking whether `tokenReserve * assetReserve` ever falls below `k` by an amount that trips the underflow in a subsequent trade of adversarially chosen size.

### Citations

**File:** packages/contracts/src/Pair.sol (L55-63)
```text
    function mint(
        uint256 tokenReserve,
        uint256 assetReserve
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
        return true;
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

**File:** packages/contracts/src/Bonding.sol (L1014-1020)
```text
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```
