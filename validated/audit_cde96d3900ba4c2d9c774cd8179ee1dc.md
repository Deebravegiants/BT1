## Finding [1](#0-0) , alt.fun explicitly documents that post-graduation trades can bypass `Zap` entirely by going direct to the HyperSwap `Pair`, which is exactly the same bug class as the reported "Collect Fee Can Be Avoided" issue (fee logic lives on one entry point, but a different function achieves the identical economic transfer for free).

### Title
Alt Fun's 0.75% Buy/Sell Fee Is Fully Avoidable by Trading Directly on the Graduated HyperSwap TOKEN/LT Pair - (File: packages/contracts/src/Zap.sol)

### Summary
All of Alt Fun's protocol + creator revenue is collected exclusively inside `Zap._executeBuy` / `Zap._sellInternal`, which skim 0.75% before routing the trade to the curve (`Bonding.buy`/`sell`) or, post-graduation, to the HyperSwap V2 `Pair`. `Bonding.buy`/`sell` are protected by `onlyRouter`, so the fee can't be bypassed pre-graduation. But once a token graduates, trading moves onto an independent, permissionless UniswapV2-style `Pair` contract that has no fee logic and no access control of its own — anyone can transfer LT/Token to the pair and call `swap()` directly, exactly mirroring the original report's "call a different function that performs the same transfer without the fee" pattern.

### Finding Description
`Zap._swapOnUniswapV2` performs post-graduation trades by transferring the input asset straight to the pair and calling the pair's own `swap()`: [2](#0-1) 

This is only possible because HyperSwap's TOKEN/LT `Pair` is a standard, permissionless UniswapV2 pair — `swap()` carries no caller restriction. The code's own comment confirms the consequence generally, not just for the mint-pause edge case it was written for:

> "Post-graduation, anyone holding LT directly can also still buy by swapping on the HyperSwap TOKEN/LT pair, bypassing Zap." [3](#0-2) 

Because the 0.75% Alt Fun fee is charged only inside `Zap` (`_executeBuy` / `_executeSell`) and forwarded to `FeeVault` via `_accrueFee`, and `Router`/`Pair` "hold no fee state" by design: [4](#0-3) 

any wallet holding LT (obtained via BounceTech `mint`, via a prior legitimate `Zap.buy`, or by any other means) can acquire the graduated Token or LT and swap directly against the pair, in either direction, completely skipping `Zap` and its fee deduction — the same class of bug as the original report, where `decreaseLiquidity` bypassed `UNCX`'s `collect`-fee logic.

### Impact Explanation
Every post-graduation trade routed directly to the pair instead of through `Zap` costs `FeeVault` its full 0.75% cut (0.5% protocol / 0.25% creator) on that trade. Since graduation is permanent (`Lifecycle.Graduated`) and all subsequent trading for that token happens on the pair, this is not a one-off leak but a standing, permanent bypass available to every trader on every graduated token for the life of the pool — a systemic, unbounded loss of protocol and creator revenue (fee-vault under-accrual), not a bounded or rare edge case.

### Likelihood Explanation
High. No special privileges are required — any EOA can call the standard `IUniswapV2Pair.swap()` function once it holds LT or the launched Token, and the pattern is a copy of a well-known technique (skip the "nice" wrapper contract, interact with the raw AMM pool). The protocol's own comments acknowledge this pathway exists and is used deliberately by `Zap` itself for its own post-grad trades, confirming it is trivially reachable by any external caller as well.

### Recommendation
Enforce the fee at the AMM layer for graduated pools rather than only at the `Zap` wrapper — e.g., restrict direct `swap()` calls on the graduated pair to the allowlisted `Zap`/router (mirroring `Bonding`'s `onlyRouter` gating), or move a portion of the fee into the pool itself (e.g., a modified pair fee split going to `FeeVault`) so it cannot be dodged by interacting with the pair directly.

### Proof of Concept
1. Wait for a token to graduate (`Bonding.isGraduated(token) == true`), so trading has moved to the HyperSwap `Pair` (`Bonding.graduatedPair(token)`).
2. As any unrelated wallet, acquire LT directly (e.g., via BounceTech's own `mint`, unrelated to Alt Fun).
3. `IERC20(lt).transfer(pair, ltAmount)` then call `IUniswapV2Pair(pair).swap(amount0Out, amount1Out, to, "")` directly, computing `amountXOut` from `pair.getAmountOut`.
4. Receive `Token` output with zero Alt Fun fee deducted and no call ever reaching `Zap._executeBuy` / `FeeVault.accrue` — compare against the equivalent `Zap.buy` call, which would have deducted 0.75% per [5](#0-4) .

### Citations

**File:** packages/contracts/src/Zap.sol (L292-300)
```text
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
        // The LT floor applies to the post-fee amount forwarded to `mint`, not
        // the gross input — `_buyInternal`'s pre-check on `usdcAmount` leaves a
        // ~5-cent dirty band (`[MIN, MIN / (1 − buyFeeBps/BPS_DENOM)]`) where
        // the gross passes but `mint` reverts with the undecodable
        // `0x05eb05ac` selector that the pre-check exists to suppress.
        if (netUsdc < minUsdcAmount()) revert BelowMinAmount();
```

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

**File:** packages/contracts/src/Router.sol (L11-18)
```text
/// @title Router
/// @notice AMM math for bonding-curve pairs. No fees here — `Zap` handles fees.
/// @dev Supports virtual token reserves (curve extends beyond sellable supply,
///      enabling zero-gap LP seeding at graduation).
///
///      No reentrancy guard: all entry points are gated by `BONDING_ROLE`, and
///      `Bonding` wraps every trade in `nonReentrant`. Granting `BONDING_ROLE`
///      to any caller that doesn't enforce non-reentrancy would be unsafe.
```
