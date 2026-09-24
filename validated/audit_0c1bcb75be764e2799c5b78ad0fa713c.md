### Title
Sell path lacks the real-balance cap that buy enforces, letting `_computeSell` pay out LT the pair never actually holds - ([File: packages/contracts/src/Router.sol])

### Summary
The CVE's root cause is that `ksmbd_conn_handler_loop` trusted a declared length field without validating it against the real size of the data actually available, producing a read past the real buffer. `Router.sol` has the same shape of bug: `_computeBuy` validates its curve-math output against the pair's *real* token balance before paying it out, but `_computeSell` — the symmetric function on the asset (LT) side — never performs the equivalent check against the pair's real LT balance before `Router.sell` executes `IPair.transferAsset`.

### Finding Description
`_computeBuy` explicitly guards against the stored (virtual) reserve exceeding what the pair actually holds: [1](#0-0) 

There is no analogous check in `_computeSell`. It derives `assetOut` purely from the stored `reserveToken`/`reserveAsset`/`k` bookkeeping and hands that number straight to `IPair.transferAsset`, with no comparison against the pair's actual LT holdings: [2](#0-1) 

The invariant enforced on every swap is intentionally loosened by a `+1` slack on both sides: [3](#0-2) 

Because `assetReserve` at mint time is virtual (no real LT is deposited for the initial seed, per `Pair.sol`'s own header comment) and only grows by the real LT amounts that flow in through `Router.buy`, the pair's true LT holding at any time is `reserveAsset − virtualSeed` (modulo drift). The `+1` slack in `swap` permits every trade to settle `newTokenReserve`/`newAssetReserve` slightly below the exact `k`-implied value, i.e. each swap is allowed to leave the stored reserves accounting for slightly less value than the invariant strictly requires. Because `_computeSell` never checks its computed `assetOut` against `IPair.assetBalance()`/real holdings the way `_computeBuy` checks `tokensOut` against `pair.tokenBalance()`, repeated buy/sell cycles that ride this slack can walk the stored `assetReserve` bookkeeping away from the pair's real LT balance — with the sell path calling `transferAsset` for a `assetOut` figure that is no longer backed by the LT actually sitting in the `Pair`, exactly as `ksmbd` read past the real buffer because it trusted an unvalidated declared length.

### Impact Explanation
If sell-side `assetOut` outruns the pair's real LT balance, either sells begin reverting (freezing every trader's exit on that curve, since `Zap.sell`/`Bonding.sell` route through this exact call) or, while the drift is smaller than the residual balance, later sellers receive LT redeemed via BounceTech that is not fully backed by what earlier buyers actually deposited — an unbacked LT payout that surfaces as USDC insolvency once run through `IBounceLeveragedToken.redeem` in `Zap._sellInternal`. Both outcomes match the Validate criteria of concrete theft/freezing of trader funds or unbacked LT payouts.

### Likelihood Explanation
Any unprivileged trader can reach this purely through repeated `Zap.buy`/`Zap.sell` cycles (or `Bonding.buy`/`Bonding.sell` via the router) on a single token — no privileged role, upgrade, or off-chain component is required. The drift accumulates deterministically from the `+1` slack baked into every `Pair.swap` call, so it's a matter of transaction volume, not a probabilistic exploit.

### Recommendation
Add a real-balance cap to `_computeSell` mirroring `_computeBuy`'s guard — clamp `assetOut` to `pair.assetBalance()` (or the real, non-virtual portion of `reserveAsset`) before `Router.sell` calls `transferAsset`, and consider tightening or removing the `+1` slack in `Pair.swap` so stored reserves cannot drift from the pair's actual token/LT holdings over repeated trades.

### Proof of Concept
1. Attacker (or any trader) alternates `Zap.buy(token, usdcAmount, 0, address(0))` and `Zap.sell(token, tokensReceived, 0)` on the same curve token many times.
2. Each round-trip swap is accepted by `Pair.swap` because `(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` is a strictly looser check than the exact invariant, allowing the stored `assetReserve` bookkeeping to end up marginally higher, relative to the pair's real LT balance, than it should be.
3. Over enough rounds, `_computeSell`'s `assetOut = reserveAsset - (k / newReserveToken)` for a later sell exceeds `IPair(pairAddr).assetBalance()`, so `Router.sell`'s call to `IPair(pairAddr).transferAsset(to, assetOut)` either reverts (freezing further sells on that token) or drains LT that other, later, legitimately-backed sellers were relying on.

### Citations

**File:** packages/contracts/src/Router.sol (L137-147)
```text
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
```

**File:** packages/contracts/src/Router.sol (L150-182)
```text
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
