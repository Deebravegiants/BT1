### Title
Missing `deadline` parameter on `Zap.buy` / `Zap.sell` (and permit variants) allows stale slippage-bounded trades to be sandwiched by MEV — (File: `packages/contracts/src/Zap.sol`)

### Summary
`Zap.buy`, `Zap.buyWithPermit`, `Zap.sell`, and `Zap.sellWithPermit` accept only a slippage floor (`minTokensOut` / `minUsdcOut`) and never a `deadline`. A signed/broadcast transaction can sit in the mempool indefinitely and still execute at any later block as long as the stale floor is still technically satisfied, exposing the trader to sandwiching by whoever controls block ordering around the eventual inclusion.

### Finding Description
`Zap.buy` forwards straight to `_buyInternal`, whose only check against price movement is `if (tokensOut < minTokensOut) revert SlippageExceeded();` [1](#0-0) . `Zap.sell`/`_sellInternal` is symmetric, checking only `if (usdcOut < minUsdcOut) revert SlippageExceeded();` [2](#0-1) . Neither the public entry points nor the `IZap` interface expose any time-bound parameter [3](#0-2) . The `permit` variants only carry a `deadline` for the ERC-2612 signature itself (`PermitData.deadline`), consumed by `_tryPermit`, which is unrelated to bounding when the swap itself can execute [4](#0-3) .

The trade itself executes against a live constant-product bonding curve in `Router._computeBuy` / `Router._computeSell`, whose price is a pure function of the pair's on-chain reserves at execution time [5](#0-4) . Because this AMM state is entirely on-chain and moves with every buy/sell, a searcher who observes a pending `Zap.buy`/`Zap.sell` can classically sandwich it: push the reserves against the victim just enough that `tokensOut`/`usdcOut` still clears the victim's (now stale) floor, then reverse the move in a back-run, capturing the spread that should have gone to the victim. A transaction that sits pending for an extended period (low gas price, network congestion, or simply a user forgetting about it) is the textbook precondition for this: the floor was chosen against the price at signing time, not at inclusion time, so an old, wide floor becomes a large exploitable slack once the curve has since moved.

This mirrors the referenced report's root cause on `PaprController` — a swap-executing entry point with a slippage bound but no deadline — mapped onto alt.fun's own AMM math and its user-facing `Zap.buy`/`Zap.sell` (and permit variants), which are directly reachable by any unprivileged trader.

### Impact Explanation
A trader's pending `buy`/`sell` can be sandwiched, extracting the "positive slippage" between the fair execution price and the stale floor they set at signing time. This is a direct value-transfer from trader funds to an MEV searcher, on every one of the whitelisted reachable functions (`Zap.buy`, `Zap.buyWithPermit`, `Zap.sell`, `Zap.sellWithPermit`). It does not, by itself, cause protocol insolvency or LP-seeding damage, so it sits at the same severity the original report was judged at: **Medium** (per the C4 judge's ruling on the analogous Papr issue, "stealing of positive slippage" warrants Medium, not High).

### Likelihood Explanation
Likelihood is meaningful but not universal: it requires (a) a transaction that remains pending/unconfirmed for a non-trivial window, and (b) a searcher with block-building or reordering capability willing to run the sandwich. Given alt.fun's bonding-curve pairs are shallow relative to Uniswap-scale liquidity (curve K sized to open new tokens at ~$3K market cap, per `docs/contracts-scope.md`), even modest reserve pushes materially move `_computeBuy`/`_computeSell` output, making sandwiches economically attractive on the frequent case of `minTokensOut = 0` / `minUsdcOut = 0` submissions (seen throughout the test suite, e.g. `zap.buy(tokenAddr, buyAmount, 0, referrer)`) or on any floor set well below the live price.

### Recommendation
Add an explicit `deadline` parameter to `Zap.buy`, `Zap.buyWithPermit`, `Zap.sell`, and `Zap.sellWithPermit` (and to `IZap`), reverting with `block.timestamp > deadline`. This bounds how long a signed slippage floor remains valid, closing the staleness window that MEV searchers rely on, consistent with the standard AMM router pattern the referenced report recommends.

### Proof of Concept
1. Trader submits `Zap.buy(tokenAddr, usdcAmount, minTokensOut, referrer)` with `minTokensOut` computed against the current curve price, at a low gas price.
2. Transaction remains pending for an extended period while the curve price (or LT `exchangeRate`) drifts; the originally-tight `minTokensOut` becomes a loose floor relative to the now-current price.
3. When gas conditions make the transaction attractive to include, a searcher front-runs with a buy that pushes `Router`'s stored reserves against the trader (via `Bonding.buy` → `Router._computeBuy`, `packages/contracts/src/Router.sol:127-148`), reducing the trader's `tokensOut` down to just above `minTokensOut` so `_buyInternal`'s check at `packages/contracts/src/Zap.sol:256` still passes.
4. The searcher back-runs with a sell reversing the reserve push, netting the difference between the fair price and the trader's stale floor — value that should have accrued to the trader.
5. No `deadline` check exists anywhere in `Zap.sol` or `IZap.sol` to prevent this transaction from being included arbitrarily late, allowing the above at any time after signing.

### Citations

**File:** packages/contracts/src/Zap.sol (L239-256)
```text
    function _buyInternal(
        address tokenAddress,
        uint256 usdcAmount,
        uint256 minTokensOut,
        address referrer
    ) internal returns (uint256 tokensOut) {
        if (usdcAmount == 0) revert InvalidInput();
        if (tokenAddress == address(0)) revert InvalidInput();
        if (usdcAmount < minUsdcAmount()) revert BelowMinAmount();
        Bonding bonding_ = _s().bonding;
        if (bonding_.creatorOf(tokenAddress) == address(0)) revert TokenNotTrading();
        if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();

        uint256 grossSpent;
        uint256 actualFee;
        (tokensOut, grossSpent, actualFee) = _executeBuy(tokenAddress, usdcAmount);

        if (tokensOut < minTokensOut) revert SlippageExceeded();
```

**File:** packages/contracts/src/Zap.sol (L412-461)
```text
    function _sellInternal(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut
    ) internal returns (uint256 usdcOut) {
        if (tokenAmount == 0) revert InvalidInput();
        if (tokenAddress == address(0)) revert InvalidInput();
        ZapStorage storage $ = _s();
        Bonding bonding_ = $.bonding;
        if (bonding_.creatorOf(tokenAddress) == address(0)) revert TokenNotTrading();
        if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();

        // LT appreciation can push a curve token past the graduation threshold
        // with no buy. Selling now would drag the raised reserve back below it,
        // so graduate the token instead. The holder keeps their tokens and
        // exits on the graduated pool. Nothing is sold, so this fills `0` — only
        // take it when the caller set no floor; a positive `minUsdcOut` reverts
        // so the `usdcOut >= minUsdcOut` guarantee is never silently broken.
        if (bonding_.canGraduate(tokenAddress)) {
            if (minUsdcOut != 0) revert TokenIsGraduating();
            bonding_.triggerGraduation(tokenAddress);
            return 0;
        }

        address lt = bonding_.ltOf(tokenAddress);

        IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), tokenAmount);

        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();

        // Intentional v1 tradeoff: sells only use BounceTech's atomic
        // `redeem()` path (no `prepareRedeem` fallback/queue in Zap). If the
        // LT idle-USDC buffer is temporarily depleted, `redeem` reverts and
        // users must retry in smaller chunks after buffer replenishment.
        // Redeem into this zap (not the user) so we can deduct the fee.
        uint256 grossUsdc = IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0);

        // Symmetric with `_executeBuy`: fee charged on EVERY sell — curve
        // AND post-graduation. The `isGraduated` branch above selects the
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;

        if (usdcOut < minUsdcOut) revert SlippageExceeded();

```

**File:** packages/contracts/src/Zap.sol (L491-503)
```text
    /// @dev Catch swallows reverts to defuse permit-front-run DoS: if an
    ///      attacker submits the same sig first the nonce is consumed but the
    ///      allowance is already set, so the follow-on `transferFrom`
    ///      succeeds. A genuinely bad permit is caught downstream by the
    ///      transfer reverting on insufficient allowance — frontends should
    ///      simulate to surface a permit-specific error pre-flight.
    function _tryPermit(
        address token,
        address owner_,
        PermitData calldata p
    ) internal {
        try IERC20Permit(token).permit(owner_, address(this), p.value, p.deadline, p.v, p.r, p.s) {} catch {}
    }
```

**File:** packages/contracts/src/interfaces/IZap.sol (L17-28)
```text
    function buy(
        address tokenAddress,
        uint256 usdcAmount,
        uint256 minTokensOut,
        address referrer
    ) external returns (uint256 tokensOut);

    function sell(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut
    ) external returns (uint256 usdcOut);
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
