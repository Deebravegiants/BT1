### Title
Post-graduation traders bypass Zap's 0.75% fee by swapping directly on the public HyperSwap pair and redeeming the LT directly - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap` is described as the sole fee layer of the protocol: "**fee layer**... No fees live on `Bonding`, `Router`, or `Factory`." Once a token graduates, trading moves to a real, permissionless HyperSwap V2 `TOKEN/LT` pair and the reserve asset is redeemable through the external BounceTech `IBounceLeveragedToken` contract — neither of which is gated to only accept calls from `Zap`. A trader can therefore swap TOKEN↔LT directly on the pair and call `redeem`/`mint` directly on the LT, completely skipping `Zap._executeBuy` / `Zap._sellInternal` and the 0.75% Alt Fun fee that is supposed to apply "on every buy/sell (curve **and** post-grad)."

### Finding Description
`Zap._sellInternal` is the only place the sell-side fee is charged: [1](#0-0) 
For a graduated token it routes through `_sellOnUniswapV2` → `_swapOnUniswapV2`, which does a **plain, unauthenticated** `pair.swap(...)` call: [2](#0-1) 
That `IUniswapV2Pair.swap` call carries no access control that restricts it to `Zap` — it is a real HyperSwap V2 pool, and the protocol's own docs confirm any LT holder can already interact with it directly: "Post-graduation, anyone holding LT directly can also still buy by swapping on the HyperSwap TOKEN/LT pair, bypassing `Zap`." [3](#0-2) 

Likewise, the sell path's only remaining step after acquiring LT is a direct call to the external LT's public `redeem`: [4](#0-3) 
That function is declared on the public interface with no caller restriction: [5](#0-4) 

Because both the HyperSwap pair and the BounceTech LT are freestanding, permissionless contracts that `Zap` merely calls into (not proxies that gate access), any unprivileged trader holding a graduated `TOKEN` can, in a single transaction, without going through `Zap` at all:
1. `transfer(pair, tokenAmount)` then call `pair.swap(0, amountOut, msg.sender, "")` directly on the graduated `TOKEN/LT` pair to receive LT (paying only HyperSwap's 0.3% LP fee, no Alt Fun fee).
2. Call `IBounceLeveragedToken(lt).redeem(msg.sender, ltAmount, 0)` directly to convert the LT into USDC.

This is functionally identical to the bug class in the reference report: a fee that is supposed to be charged uniformly on a value-exit path (`withdrawLend()` / `Zap.sell()`) can be bypassed entirely by using an alternate, un-fee-gated code path (`liquidate()` / direct pair-and-LT interaction) that reaches the same economic outcome (USDC out) without the fee deduction. The buy side is symmetric — a trader can `mint` LT directly on the LT contract and swap it into TOKEN directly on the pair, bypassing `Zap.buy`'s 0.75% fee as well.

### Impact Explanation
Every post-graduation trader can permanently avoid the 0.75% Alt Fun fee (split 0.5% protocol / 0.25% creator) on both buys and sells simply by not using the `Zap` UI/contract and instead calling the pair and LT directly — something the protocol's own code comments acknowledge is possible ("anyone holding LT directly can also still buy by swapping on the HyperSwap TOKEN/LT pair, bypassing `Zap`"). Since post-graduation is the terminal, long-term trading venue for every launched token, this results in an ongoing, unbounded loss of protocol and creator fee revenue for the lifetime of every graduated token — a systemic, permanent value leak rather than a one-off exploit, matching the "financial loss for BlueBerryBank" impact class of the analog report.

### Likelihood Explanation
High. No special privileges, timing, or capital are required — any address holding the graduated `TOKEN` or LT can perform the two direct calls. The protocol's own natspec already documents that this bypass path exists for buys ("anyone holding LT directly can also still buy by swapping on the HyperSwap TOKEN/LT pair, bypassing `Zap`"), and the identical mechanism is available symmetrically for the sell/exit side via a direct `redeem` call on the LT. Sophisticated traders, arbitrage bots, and MEV searchers have a strong ongoing incentive to always trade this way post-graduation to save the fee.

### Recommendation
Move fee enforcement to a layer the trader cannot route around, e.g.:
- Charge the Alt Fun fee inside a hook the graduated pair itself calls (not achievable with a stock HyperSwap V2 pair) — or accept that a stock V2 pair cannot be fee-gated and instead recapture equivalent value at redemption time.
- Alternatively, since the LT's `redeem`/`mint` functions are external BounceTech infrastructure that alt.fun does not control, consider whether the fee model should instead be levied as a protocol-side spread built into the curve/LP pricing rather than relying on all trades to route through `Zap`, since post-graduation `Zap` is optional infrastructure, not an enforced chokepoint.
- At minimum, document this as an accepted trade-off (similar to the existing buy-side note) rather than an implicit assumption, since it means the “0.75% on every buy/sell — curve **and** post-grad” guarantee in `docs/contracts-scope.md` does not hold once a token graduates.

### Proof of Concept
1. Launch and graduate a token via the normal flow (`Zap.createToken` → buys → `Bonding.triggerGraduation`/`finalizeGraduation`), so `bonding.isGraduated(tokenAddress) == true` and `bonding.graduatedPair(tokenAddress)` is a live HyperSwap V2 `TOKEN/LT` pair.
2. A trader acquires `TOKEN` (e.g., via a normal `Zap.buy`) and wants to exit.
3. Instead of calling `Zap.sell`, the trader:
   - `IERC20(tokenAddress).transfer(pair, tokenAmount)`
   - Computes `amountOut` via `IUniswapV2Pair(pair).getAmountOut(tokenAmount, tokenAddress)` (mirroring `Zap._swapOnUniswapV2`, `packages/contracts/src/Zap.sol:556`)
   - Calls `IUniswapV2Pair(pair).swap(0, amountOut, trader, "")` directly, receiving LT with only the pair's 0.3% fee deducted — no Alt Fun fee.
4. The trader then calls `IBounceLeveragedToken(lt).redeem(trader, ltAmount, 0)` directly (`packages/contracts/src/interfaces/IBounceLeveragedToken.sol:19-23`), receiving gross USDC with zero deduction for the 0.75% Alt Fun sell fee that `Zap._sellInternal` (`packages/contracts/src/Zap.sol:457-458`) would otherwise have charged.
5. Compare to a trader using `Zap.sell` for the same `tokenAmount`: they receive `usdcOut = grossUsdc - fee` where `fee = Math.mulDiv(grossUsdc, sellFeeBps, BPS_DENOM, Ceil)` — strictly less than the direct-path trader's payout, with `FeeVault` receiving nothing for this trade.

### Citations

**File:** packages/contracts/src/Zap.sol (L304-314)
```text
        // BounceTech LTs are mint-pausable (but NOT redeem-pausable). When
        // the LT operator pauses minting, this call reverts, so every buy
        // through Zap — bonding curve and post-graduation alike — DoSes for
        // that token while sells keep working (sells go through `redeem`,
        // not `mint`). This is an accepted v1 tradeoff: a sell-only market
        // is preferable to freezing both sides, since holders can still
        // exit to USDC. Post-graduation, anyone holding LT directly can
        // also still buy by swapping on the HyperSwap TOKEN/LT pair,
        // bypassing Zap. We do not mirror BounceTech's pause flag in
        // `Zap` (it would couple our pausing surface to theirs and add
        // storage with no security gain).
```

**File:** packages/contracts/src/Zap.sol (L440-466)
```text
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

        $.usdc.safeTransfer(msg.sender, usdcOut);

        if (fee > 0) {
            _accrueFee(tokenAddress, bonding_.creatorOf(tokenAddress), fee, false);
        }
```

**File:** packages/contracts/src/Zap.sol (L542-562)
```text
    function _swapOnUniswapV2(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        Bonding bonding_ = _s().bonding;
        // `graduatedPair` is keyed by the launched token only; check `tokenIn`
        // first (sell direction) then fall back to `tokenOut` (buy direction).
        address pair = bonding_.graduatedPair(tokenIn);
        if (pair == address(0)) pair = bonding_.graduatedPair(tokenOut);

        bool inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn;
        // Quote from the pair so the output tracks its live fee instead of a
        // hardcoded rate, keeping `amountOut` consistent with the K-check.
        amountOut = IUniswapV2Pair(pair).getAmountOut(amountIn, tokenIn);

        IERC20(tokenIn).safeTransfer(pair, amountIn);

        (uint256 amount0Out, uint256 amount1Out) = inIsToken0 ? (uint256(0), amountOut) : (amountOut, uint256(0));
        IUniswapV2Pair(pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
    }
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L18-23)
```text
    /// @notice LT → USDC. Reverts if the computed USDC output exceeds `baseAssetBalance()`.
    function redeem(
        address to,
        uint256 ltAmount,
        uint256 minBase
    ) external returns (uint256 baseAmount);
```
