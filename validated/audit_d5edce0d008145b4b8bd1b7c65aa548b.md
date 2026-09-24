No vulnerability found for this question.

The reported bug class relies on a concentration-based tax model where fee calculation reads a stale "current concentration" across an array of duplicate deposit/withdraw entries in a single call — this requires (1) an array-of-assets interface for deposit/withdraw and (2) a fee formula that is non-linear in trade size (concentration deviation), making it exploitable by splitting.

alt.fun has neither property. `Zap.buy`/`Zap.sell` operate on a single `tokenAddress` per call with no array parameter, and the fee is a flat basis-points rate applied linearly to the traded amount (`feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM` and `fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, ...)`), [1](#0-0) [2](#0-1)  so splitting a trade into many small ones changes nothing — the sum of fees on N parts equals the fee on the whole, with no concentration/deviation term to under-value. The AMM math in `Router._computeBuy`/`_computeSell` is a standard constant-product curve with no tax component at all. [3](#0-2)  None of the in-scope reachable functions (`Bonding.triggerGraduation`, `finalizeGraduation`, `FeeVault.claim`/`claimProtocol`, LP seeding) take asset arrays or compute fees from a stored "current concentration" that could go stale across duplicate entries either.

Since the root-cause mechanism (array-of-duplicates + concentration-delta tax formula) has no counterpart in alt.fun's architecture, there is no valid analog to report.

### Citations

**File:** packages/contracts/src/Zap.sol (L292-294)
```text
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
```

**File:** packages/contracts/src/Zap.sol (L456-458)
```text
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;
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
