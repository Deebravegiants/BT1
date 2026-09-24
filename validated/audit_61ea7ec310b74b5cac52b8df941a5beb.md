### Title
Missing deadline parameter on `Zap.buy`/`Zap.sell` (and permit variants) allows stale-price sandwiching - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap.buy`, `Zap.buyWithPermit`, `Zap.sell`, and `Zap.sellWithPermit` accept only a slippage floor (`minTokensOut` / `minUsdcOut`) and never check `block.timestamp` against a caller-supplied deadline, exactly the bug class reported for Arrakis's `ArrakisV2Router.sol`.

### Finding Description
`Zap.buy`/`_buyInternal` and `Zap.sell`/`_sellInternal` enforce only a post-trade slippage floor: [1](#0-0) [2](#0-1) 

There is no `deadline` field anywhere in the call signature — `buy(tokenAddress, usdcAmount, minTokensOut, referrer)` and `sell(tokenAddress, tokenAmount, minUsdcOut)` — nor in the `IZap` interface or `PermitData` struct used by the permit variants: [3](#0-2) 

`minTokensOut`/`minUsdcOut` are computed off-chain by the caller against the *current* on-curve price via `Router.getAmountOut`/`previewBuy` (`Router.sol`, `_computeBuy`/`_computeSell`, lines 127–182). If the signed transaction sits in the mempool for a period (e.g., gas-price spike, low-gas submission) and the curve price moves, the trade can still clear the stale slippage floor while a searcher sandwiches it — buying/selling ahead to push the curve price to just inside the floor, and reversing right after, extracting the price delta between the tx's original quote time and its actual mining time. This is precisely the class in the referenced report: slippage-only protection without a deadline lets stale-priced transactions execute long after the user intended, converting normal slippage protection into a sandwichable floor rather than a freshness guarantee.

### Impact Explanation
A trader's `Zap.buy`/`Zap.sell` (or their permit variants) can be executed at a materially worse price than intended once mined, with the difference captured by an MEV searcher — concrete theft of trader funds bounded only by the width of the `minTokensOut`/`minUsdcOut` band the user chose, which users commonly set loosely (or leave at `0`, as shown throughout `Zap.t.sol`) since the flow provides no separate freshness guarantee.

### Likelihood Explanation
Every call to `Zap.buy`/`buyWithPermit`/`sell`/`sellWithPermit` is affected; the only precondition is a transaction that lingers in the mempool (gas spikes, RPC delay, or a searcher deliberately delaying inclusion via priority fee manipulation) combined with observable price movement on the curve pair, both of which are routine on any public chain.

### Recommendation
Add a `deadline` parameter to `Zap.buy`, `Zap.sell`, and their `WithPermit` variants (and to `IZap`), and revert with a clear error when `block.timestamp > deadline`, mirroring the standard Uniswap-style safeguard the original report recommends.

### Proof of Concept
1. Trader calls `zap.buy(token, usdcAmount, minTokensOut, referrer)` with `minTokensOut` computed from `Router.getAmountOut` at time T.
2. Due to gas-price volatility the tx sits unmined until T+Δ, during which the curve price drifts (organic trading or a searcher priming the curve).
3. A searcher observes the pending tx, front-runs it to push the price to just inside `minTokensOut`, lets the trader's tx execute (still passing the `tokensOut < minTokensOut` check in `_buyInternal`, line 256), then back-runs to restore price, pocketing the difference.
4. No code path in `Zap.sol` or `IZap.sol` rejects the trade based on staleness — only the slippage floor is checked, confirming the missing deadline guard.

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

**File:** packages/contracts/src/Zap.sol (L412-460)
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

**File:** packages/contracts/src/interfaces/IZap.sol (L8-28)
```text
interface IZap {
    struct PermitData {
        uint256 value;
        uint256 deadline;
        uint8 v;
        bytes32 r;
        bytes32 s;
    }

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
