### Title
Precision loss in `Router._computeSell`/`_computeBuy` lets a trade round to zero output while still consuming input, because `Pair.swap` has no minimum-output guard - (File: `packages/contracts/src/Router.sol`, `packages/contracts/src/Pair.sol`)

### Summary
The reported bug class is rounding-down division that silently zeroes out a user's expected shares while their contribution is still consumed. `alt.fun`'s bonding-curve AMM math reproduces the same class: both `_computeBuy` and `_computeSell` derive the output side of a trade via floor division against the pool's constant product `k`, and neither `Router.buy`/`Router.sell` nor `Pair.swap` enforce that the computed output is non-zero before pulling the input asset and mutating reserves.

### Finding Description
`Router._computeSell` computes the LT paid out for a token sell purely by floor division: [1](#0-0) 

`Router.sell` pulls `tokensIn` from the seller into the pair *before* computing `assetOut`, and unconditionally calls `transferAsset`/`swap` with whatever `_computeSell` returned — including `0`: [2](#0-1) 

`Pair.swap` itself has no analog of UniswapV2's `require(amount0Out > 0 || amount1Out > 0, "INSUFFICIENT_OUTPUT_AMOUNT")` — it only checks the K-invariant floor, so a swap with `assetOut == 0` (or `tokensOut == 0` on the buy side) succeeds silently: [3](#0-2) 

The same shape exists on the buy side in `_computeBuy` (`tokensOut = reserveToken - (k / newReserveAsset)`), which can floor to `0` for a small `amountIn` against a large virtual `reserveToken`: [4](#0-3) 

Because `Pair.reserve0` is seeded at the *virtual* full `totalSupply` (up to 1e9 × 1e18) while only 75% is real, `k` is very large, which widens the region of trade sizes for which `k / newReserve` rounds enough to produce a zero-output division result relative to typical LT decimal scales — precisely the "precision loss for small trades" scenario from the report.

Reaching this path requires only an ordinary unprivileged trade through `Zap.sell`/`Zap.buy` (which forward straight into `Bonding.sell`/`Bonding.buy` → `Router.sell`/`Router.buy`). The docs confirm `Zap.sell` explicitly supports a `minUsdcOut == 0` call shape as a first-class path (used for the graduation-trigger case), so a trader (or a naive integrator/bot) invoking a small sell with `minUsdcOut = 0` receives no protective revert:


### Impact Explanation
A trader whose sell (or buy) size falls into the rounding-to-zero region has their `Token` (or LT) irrevocably transferred into the `Pair` while receiving `0` in return — this is a direct, non-recoverable loss of principal for that trade, identical in effect to the H-11 finding where fractions below a precision threshold were lost. Because the check that would normally stop this (`minUsdcOut`/`minTokensOut` in `Zap`) is caller-supplied and can legitimately be `0`, there is no protocol-level backstop; the loss is silent (no revert) rather than a shielded failure.

### Likelihood Explanation
Likelihood is moderate: it requires a trade size small enough relative to the pool's (very large, since it includes the 1B-token virtual reserve) `k` for `k / newReserve` to floor away the entire output. This is more likely early in a token's life (small reserves relative to `k` are not the trigger — rather a *large* `reserveToken` relative to a *small* trade is), and is easily triggered by any unsophisticated trader or bot submitting a dust-sized sell/buy with `minUsdcOut`/`minTokensOut = 0`, which the codebase explicitly treats as a valid, unguarded input.

### Recommendation
Add an explicit non-zero output check in `Router._computeBuy`/`_computeSell` (or in `Router.buy`/`Router.sell` immediately after computing `tokensOut`/`assetOut`) that reverts (e.g., `InsufficientOutputAmount`) rather than allowing a zero-output trade to consume the trader's input, mirroring UniswapV2's `INSUFFICIENT_OUTPUT_AMOUNT` guard in `Pair.swap`.

### Proof of Concept
1. Consider a token pair where the virtual `reserveToken` is large (up to `totalSupply` = 1e9 × 1e18) and `k = reserveToken_init × assetReserve_init`.
2. A trader calls `Zap.sell(tokenAddress, tokenAmount, 0)` with a small `tokenAmount` — a legitimate call shape per the documented `minUsdcOut == 0` path.
3. This reaches `Router.sell` → `_computeSell`: `newReserveToken = reserveToken + tokenAmount`; `assetOut = reserveAsset - (k / newReserveToken)`. For sufficiently large `reserveToken` relative to `tokenAmount`, integer division causes `k / newReserveToken` to equal (or round to) `reserveAsset`, making `assetOut == 0`.
4. `Router.sell` has already executed `IERC20(token).safeTransferFrom(to, pairAddr, amountIn)` before this computation, so the trader's tokens are gone.
5. `IPair(pairAddr).transferAsset(to, 0)` and `IPair(pairAddr).swap(amountIn, 0, 0, 0)` both succeed — no revert anywhere in `Router.sol` or `Pair.sol` — leaving the trader with zero LT/USDC for tokens that are now locked in the pair.

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

**File:** packages/contracts/src/Router.sol (L151-170)
```text
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
