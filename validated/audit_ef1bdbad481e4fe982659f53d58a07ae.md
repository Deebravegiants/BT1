### Title
Reachable revert in `Router._computeBuy`'s overflow cap can DoS the closing curve buy - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` reverts with `OverflowCapDegenerate()` whenever the K-invariant back-calculation for a capped buy produces `cappedReserveToken == 0`, i.e. when the requested buy would consume tokens equal to (or attempt to exceed) the pair's entire real token balance (`pair.tokenBalance()`) relative to the stored virtual `reserveToken`. This mirrors CVE-2017-12960's bug class — a reachable "assertion" (here, a `revert`) inside a data-processing function that an ordinary external actor can trigger deterministically, causing denial of service on that call path.

### Finding Description
`_computeBuy` computes the unconstrained curve output, then caps it at `realBalance = pair.tokenBalance()` if it would exceed real supply: [1](#0-0) 

When `tokensOut` is capped to `realBalance` and `tokensOut == reserveToken` (i.e. `realBalance >= reserveToken`, the entire virtual token reserve), `cappedReserveToken = reserveToken - tokensOut` becomes `0`, and the function unconditionally reverts with `OverflowCapDegenerate()` instead of returning a valid (even if smaller) `amountInUsed`/`tokensOut` pair. This function is reached from `Router.buy` — called by `Bonding.buy`, which is called by any unprivileged trader through `Zap.buy` / `Zap.buyWithPermit` / `Zap.createToken`'s mandatory seed buy: [2](#0-1) [3](#0-2) 

Any trader submitting a buy large enough to attempt to consume the remaining full real token balance of the curve (which is a state any large single buy or a sequence of buys naturally approaches as the curve nears exhaustion) will hit this degenerate branch and have the transaction revert, rather than being served with a smaller, correctly capped fill. Since `Zap`'s `_executeBuy` pre-sizes the LT mint via `Bonding.previewLtUntilGraduation`/`Router.previewBuy` (which calls the same `_computeBuy`), the revert can surface at quote time as well as execution time: [4](#0-3) 

### Impact Explanation
The impact is a denial of service on the closing leg of the bonding curve: a trader attempting to buy out the last of the sellable supply (the exact trade that is supposed to exhaust the curve and trigger graduation via `tokenBalance() == 0`) can be forced to revert instead of completing. This blocks the natural "supply exhausted" graduation trigger path documented in the codebase's own invariant suite (`GraduationInvariantsTest`, invariant #5 "Supply trigger — Exhausting curve supply graduates even below $9K", and #7 "Overflow cap — Buy capped at real balance; excess LT refunded to buyer"), meaning the overflow-cap mechanism that is explicitly designed to always succeed and refund excess LT can instead degenerate into an outright revert at the exact boundary condition it was built to handle. This is a functional/availability impact on trading and graduation liveness rather than direct fund theft, keeping severity at Medium under the report's rules (permanent freezing/DoS class), though it does not on its own cause fund loss — no LT or USDC leaves any account when the revert fires (the `SafeERC20` transfer and `swap` calls never execute).

### Likelihood Explanation
Reachable by any unprivileged buyer with no special permissions, in a single transaction, whenever the pre-cap `tokensOut` computation would exactly zero out the remaining virtual/real reserve gap (`realBalance == reserveToken`). This is precisely the last-buy/curve-exhaustion boundary, which is a state the protocol's own design intends to reach on every graduation via the supply trigger, making the degenerate branch a realistically reachable edge condition rather than a purely theoretical one.

### Recommendation
In `Router._computeBuy`, handle the `cappedReserveToken == 0` case by returning the maximum valid fill (i.e., cap `tokensOut` at `realBalance - 1` or otherwise compute `amountInUsed` from the full-exhaustion K identity without dividing by zero) rather than reverting, so the last buy on a curve always completes and the supply-exhaustion graduation trigger cannot be griefed into failure.

### Proof of Concept
1. Launch a token via `Zap.createToken`, letting the curve accumulate buys until `pair.tokenBalance()` (real token balance) is close to `reserveToken` (the virtual token reserve tracked by `Pair`/`Router`).
2. As any trader, call `Zap.buy(tokenAddress, usdcAmount, minTokensOut, referrer)` with `usdcAmount` sized (via `Router.previewBuy`/`getAmountOut`) so that the unconstrained curve output `tokensOut` would equal exactly `reserveToken` before capping.
3. `Router._computeBuy` computes `tokensOut = realBalance` after capping, then `cappedReserveToken = reserveToken - tokensOut == 0`, and the call reverts with `Router.OverflowCapDegenerate()` inside `Router.buy`, propagating up through `Bonding.buy` and `Zap._executeBuy`, denying the trade that would otherwise exhaust the curve and trigger graduation. [5](#0-4)

### Citations

**File:** packages/contracts/src/Router.sol (L92-108)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }
```

**File:** packages/contracts/src/Router.sol (L110-123)
```text
    /// @notice External view of `_computeBuy`. Returns `(amountInUsed,
    ///         tokensOut)` for a hypothetical LT-in buy of `amountIn`,
    ///         honouring the same overflow cap as `buy()`. Used by `Zap` to
    ///         pre-size the LT mint and by the frontend for buy-quote previews.
    function previewBuy(
        address token,
        uint256 amountIn
    ) external view returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        return _computeBuy(pairAddr, amountIn);
    }
```

**File:** packages/contracts/src/Router.sol (L125-148)
```text
    /// @dev Capped: `amountInUsed` is back-calculated from the K invariant
    ///      (rounded up so the curve never under-charges).
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
