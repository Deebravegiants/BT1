Confirmed: the codebase's own natspec explicitly documents this exact bypass at [1](#0-0) , and the HyperSwap V2 TOKEN/LT pair has no access control tying it to `Zap` — `pair.swap()` is a standard, permissionless public function [2](#0-1) .

### Title
Post-graduation trades executed directly against the HyperSwap V2 TOKEN/LT pair permanently bypass the 0.75% Alt Fun protocol/creator fee - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap` is the only contract that charges Alt Fun's 0.75% fee, and it charges it unconditionally "on EVERY buy — bonding curve AND post-graduation" [3](#0-2) . But once a token graduates, trading moves to a standard HyperSwap V2 pair whose `swap()` function is public and permissionless — exactly like a stock UniswapV2 pair — with no gate requiring callers to route through `Zap`. Any unrelated wallet holding LT or the launched Token can call `pair.swap(...)` directly (the same call pattern `Zap._swapOnUniswapV2` itself uses) and trade with zero Alt Fun fee, paying only HyperSwap's own 0.3% LP fee.

### Finding Description
`Zap._executeBuy` and `Zap.sell` are the sole fee-enforcement points in the protocol; `Bonding.buy`/`sell` are gated `onlyRouter` so the curve itself can't be reached directly [4](#0-3) , and `Router.sol` gates its functions to `BONDING_ROLE` [5](#0-4) . This access control fully protects the pre-graduation curve.

Post-graduation, though, trading venue switches to a real HyperSwap V2 `pair`, which is intentionally treated by the codebase as a standard, unrestricted AMM: `Zap._swapOnUniswapV2` itself trades on it by doing nothing more than `IERC20(tokenIn).safeTransfer(pair, amountIn)` followed by `pair.swap(amount0Out, amount1Out, address(this), "")` [6](#0-5) . Nothing distinguishes this call as privileged — any address can perform the identical sequence: transfer LT (or Token) to the pair, then call `pair.swap()` for the counter-asset. The pair's own K-invariant is the only check (mirrored by the mock at [7](#0-6) ), and it has no allowlist for `msg.sender` or `to`.

The protocol's own documentation acknowledges the reachability of this exact path: "Post-graduation, anyone holding LT directly can also still buy by swapping on the HyperSwap TOKEN/LT pair, bypassing Zap. We do not mirror BounceTech's pause flag in `Zap`..." [8](#0-7) . That comment is written to justify a *pause*-bypass tradeoff, but the same bypass equally defeats *fee* collection — `FeeAccrued`/`accrue` are only invoked from inside `Zap._accrueFee`, which is never reached on this path [9](#0-8) .

This is directly analogous to the referenced Gitcoin/Allo finding: fee collection is enforced at one layer (a `matchAmount`-driven wrapper / `Zap`) while the underlying value-transfer primitive (round payout / HyperSwap pair) can be reached directly, letting the actor skip the fee entirely.

### Impact Explanation
Every post-graduation trade routed directly to the pair permanently avoids the 0.75% Alt Fun fee (0.5% protocol / 0.25% creator split, per `docs/contracts-scope.md` lines 112-121). Since `docs/contracts-scope.md` states the fee applies "on every buy — curve **and** post-graduation — not just curve trades," and graduation is the terminal, permanent state for a token, this is a standing, indefinite loss of protocol and creator revenue on all trading volume for graduated tokens that goes direct-to-pair (e.g., via aggregators, MEV bots, or any trader who simply reads `Bonding.graduatedPair(token)` and calls the pair themselves). This is a Medium-severity, unbounded fee-avoidance path affecting `FeeVault` insolvency-adjacent revenue (protocol and creator fee income), reachable by any unprivileged wallet with no special conditions.

### Likelihood Explanation
High likelihood of exploitation for any economically-motivated trader/bot: no privileged role, no timing constraints, and no protocol-level obstacle. The pair address is discoverable via `Bonding.graduatedPair(token)` (a public view), and the transfer+`swap()` sequence is trivial to replicate — it is literally the exact sequence `Zap` itself performs internally, just without the fee-deduction step that happens before `Zap` mints/redeems LT.

### Recommendation
Fees cannot be enforced on a standard, permissionless AMM pair after the fact. Recommended mitigations (mutually compatible):
1. Do not treat the "protocol fee is always collected" invariant as true post-graduation; update `docs/contracts-scope.md` and any revenue projections accordingly, since it is fundamentally unenforceable once value moves to a vanilla HyperSwap V2 pool.
2. Consider capturing fee revenue structurally at the pool level instead of at `Zap`, e.g. by using a fee-on-transfer/hook-enabled pair, or accepting that post-graduation "protocol fee" can only be an LP-fee share (via protocol-owned LP or `feeTo` mechanics on the DEX), not a per-trade skim enforced by `Zap`.
3. If per-trade fee enforcement is a hard product requirement post-graduation, the launched `Token` itself would need transfer-fee logic (since the pair cannot be gated), which is a significant architecture change and was apparently deliberately rejected in favor of using "real HyperSwap pairs" (see `packages/contracts/AGENTS.md` line 159 rationale for rejecting a custom pair).

### Proof of Concept
1. Graduate a token normally via `Bonding.triggerGraduation` + `finalizeGraduation`, creating the `Bonding.graduatedPair(token)` HyperSwap V2 pool.
2. An unrelated wallet acquires LT (e.g., by minting via BounceTech's LT `mint()` directly, entirely outside `Zap`).
3. The wallet calls `graduatedPair.getAmountOut(amountIn, ltAddress)` to quote, then:
   - `IERC20(lt).transfer(pairAddress, amountIn)`
   - `pair.swap(0, amountOut, walletAddress, "")` (or the reverse ordering depending on `token0`)
4. The wallet receives the launched `Token` at the pool's price, paying only HyperSwap's embedded LP fee. `FeeVault.accrue` is never called; no `FeeAccrued` event is emitted; `feeVault.protocolBalance()`/`creatorBalance(creator)` are unchanged for this trade, versus the equivalent `Zap.buy` call which would have deducted 0.75% via `_executeBuy`/`_accrueFee` (`packages/contracts/src/Zap.sol` lines 279-360, 476-487).
5. Repeat for sells (`Token` → LT) in the same manner — no `Zap.sell` call, no fee, no `FeeAccrued`.

### Citations

**File:** packages/contracts/src/Zap.sol (L286-291)
```text
        // Fee is charged on EVERY buy — bonding curve AND post-graduation.
        // This is intentional. Lifting the fee post-grad would silently
        // halve protocol+creator revenue the moment a token graduates and is
        // the opposite of what we want. The `if (isGraduated) ...` branch
        // below selects the venue (HyperSwap V2 vs. internal AMM `Router.sol`),
        // not the fee policy.
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

**File:** packages/contracts/src/Zap.sol (L476-487)
```text
    function _accrueFee(
        address token,
        address creator,
        uint256 feeAmount,
        bool isBuy
    ) internal {
        ZapStorage storage $ = _s();
        uint256 creatorShare = (feeAmount * $.creatorFeeBps) / BPS_DENOM;
        uint256 protocolShare = feeAmount - creatorShare;
        $.usdc.safeTransfer(address($.feeVault), feeAmount);
        $.feeVault.accrue(token, creator, creatorShare, protocolShare, isBuy);
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

**File:** packages/contracts/src/interfaces/IUniswapV2Pair.sol (L24-29)
```text
    function swap(
        uint256 amount0Out,
        uint256 amount1Out,
        address to,
        bytes calldata data
    ) external;
```

**File:** packages/contracts/src/Bonding.sol (L563-580)
```text
    function buy(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256 tokensOut, uint256 amountInUsed) {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        // `creator == 0` means the slot was never written. `Lifecycle.Curve` is
        // the zero value, so without this an unknown token would fall through
        // and revert deep in `router.buy` with an opaque error.
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
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

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L81-114)
```text
    function swap(
        uint256 amount0Out,
        uint256 amount1Out,
        address to,
        bytes calldata /* data */
    ) external {
        require(amount0Out > 0 || amount1Out > 0, "MockPair: INSUFFICIENT_OUTPUT_AMOUNT");

        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;
        require(amount0Out < reserve0 && amount1Out < reserve1, "MockPair: INSUFFICIENT_LIQUIDITY");

        if (amount0Out > 0) IERC20(token0).transfer(to, amount0Out);
        if (amount1Out > 0) IERC20(token1).transfer(to, amount1Out);

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));

        uint256 amount0In = balance0 > reserve0 - amount0Out ? balance0 - (reserve0 - amount0Out) : 0;
        uint256 amount1In = balance1 > reserve1 - amount1Out ? balance1 - (reserve1 - amount1Out) : 0;
        require(amount0In > 0 || amount1In > 0, "MockPair: INSUFFICIENT_INPUT_AMOUNT");

        // K-invariant check charging each input side its own per-token fee,
        // matching CamelotPair (the fork HyperSwap V2 is based on).
        uint256 balance0Adjusted = (balance0 * FEE_DENOMINATOR) - (amount0In * token0FeePercent);
        uint256 balance1Adjusted = (balance1 * FEE_DENOMINATOR) - (amount1In * token1FeePercent);
        require(
            balance0Adjusted * balance1Adjusted >= uint256(reserve0) * uint256(reserve1) * (FEE_DENOMINATOR ** 2),
            "MockPair: K"
        );

        _reserve0 = uint112(balance0);
        _reserve1 = uint112(balance1);
    }
```
