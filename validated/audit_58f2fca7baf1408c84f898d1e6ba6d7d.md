The natspec on `Zap._sellInternal` itself already documents this exact analog: sells only use BounceTech's atomic `redeem()` path, and if the LT idle-USDC buffer is depleted, `redeem` reverts. This is a valid, code-confirmed analog to the Balancer-cash DoS.

### Title
Sell/withdraw DoS when LT's idle USDC buffer (`baseAssetBalance`) is insufficient to atomically redeem the trader's LT - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._sellInternal` converts a curve/graduated-pool sell into LT, then calls `IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0)` in the same transaction. `redeem` is documented to revert if the computed USDC output exceeds the LT's `baseAssetBalance()` (its idle-cash buffer), exactly mirroring the Balancer `cash`-vs-`managed` distinction in the original report: the amount a user can withdraw is capped by externally-held liquidity that Zap does not check before committing to the trade.

### Finding Description
`Zap.sell` / `sellWithPermit` route to `_sellInternal` [1](#0-0) 
which pulls the trader's tokens, converts them on the curve or HyperSwap V2 to LT via `_sellOnCurve` / `_sellOnUniswapV2`, and then unconditionally calls `IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0)`. The interface explicitly documents this failure mode: `redeem` "Reverts if the computed USDC output exceeds `baseAssetBalance()`" [2](#0-1) 
and the contract's own comment acknowledges the tradeoff: sells only use BounceTech's atomic `redeem()` path with no fallback/queue, so "If the LT idle-USDC buffer is temporarily depleted, `redeem` reverts and users must retry in smaller chunks" [3](#0-2) 
.

This is the direct analog of the Balancer report: there, `cash` (Vault-held liquidity) could be less than the pool's recorded total balance because part of it was `managed` (withdrawn by an asset manager), causing the withdraw to revert; here, the LT's `baseAssetBalance()` (idle USDC) can be less than what `redeem` needs to pay out because LT capital is deployed into the leveraged strategy, causing `redeem` — and therefore the entire `Zap.sell`/`sellWithPermit` transaction, including the tokens/LT the trader already irreversibly transferred into Zap and converted via the curve/AMM — to revert.

### Impact Explanation
When the LT's idle-cash buffer is insufficient, any trader attempting to sell is fully blocked from exiting to USDC through Zap: their curve/AMM-side conversion (token → LT) already executed state changes (curve reserves updated, AMM swap executed) inside the same transaction before hitting the `redeem` call, so the whole call reverts and they cannot cash out at all via this path — a temporary but complete freeze of the sell/withdraw function for that token, with no built-in fallback (the code explicitly states there is no `prepareRedeem` fallback or queue).

### Likelihood Explanation
This condition depends entirely on BounceTech LT's internal capital deployment (how much of `baseAssetBalance` is idle vs. deployed into the leveraged position), which is external and outside alt.fun's control; it can occur naturally whenever the LT's strategy has deployed most of its base assets, especially during periods of high leverage utilization or after large mints, making it plausible under normal operating conditions rather than requiring an attacker.

### Recommendation
Before calling `redeem`, check `IBounceLeveragedToken(lt).baseAssetBalance()` against the anticipated USDC payout and either revert early with a clear, decodable error, cap/partial-fill the redeem to the available buffer, or support a queued/deferred redemption path so a depleted buffer degrades gracefully instead of reverting the entire sell (including the already-executed curve/AMM leg) in one atomic transaction.

### Proof of Concept
1. A token trades on the curve; LT accrues via curve buys and mints.
2. BounceTech LT deploys most of its base assets into its leveraged strategy, leaving `baseAssetBalance()` low.
3. A trader calls `Zap.sell(tokenAddress, tokenAmount, minUsdcOut)`. `_sellInternal` executes `_sellOnCurve`, converting the trader's tokens into `ltReceived` LT held by Zap.
4. `_sellInternal` calls `IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0)`; because the computed USDC payout exceeds `baseAssetBalance()`, `redeem` reverts.
5. The entire `Zap.sell` transaction reverts, and the trader cannot obtain USDC for their tokens in this transaction; they must retry with smaller `tokenAmount` until the buffer permits it, which may not be possible if the buffer stays depleted.

### Citations

**File:** packages/contracts/src/Zap.sol (L412-452)
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
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L18-26)
```text
    /// @notice LT → USDC. Reverts if the computed USDC output exceeds `baseAssetBalance()`.
    function redeem(
        address to,
        uint256 ltAmount,
        uint256 minBase
    ) external returns (uint256 baseAmount);

    /// @notice Idle USDC available for atomic redeem.
    function baseAssetBalance() external view returns (uint256);
```
