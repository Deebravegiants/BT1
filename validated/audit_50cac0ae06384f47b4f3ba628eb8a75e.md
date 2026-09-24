### Title
Missing `deadline` parameter in `Zap.buy` / `Zap.sell` / `Zap.createToken` (and their `*WithPermit` variants) allows stale trades to execute at a worse price - (File: `packages/contracts/src/Zap.sol`)

### Summary
`Zap.buy`, `Zap.sell`, `Zap.createToken`, and their `buyWithPermit`/`sellWithPermit`/`createTokenWithPermit` counterparts protect only against price movement beyond a caller-supplied floor/ceiling (`minTokensOut` / `minUsdcOut`), but accept no execution deadline. A submitted transaction can sit in the mempool indefinitely and later be included by a block builder at a time far removed from when the user signed it, executing against a materially different bonding-curve or post-graduation HyperSwap price while still nominally satisfying the loose slippage bound the user set when submitting.

### Finding Description
`Zap.buy` [1](#0-0)  and `Zap.sell` [2](#0-1)  take only `minTokensOut`/`minUsdcOut` as execution-price guards, with no `deadline` parameter constraining *when* the trade may execute. The same is true of `createToken`/`createTokenWithPermit`, which perform the mandatory seed buy with `minTokensOut = 0` [3](#0-2) .

Trades on the bonding curve go through `Router._computeBuy`/`_computeSell`, whose output depends on the *live* pair reserves at execution time [4](#0-3) ; post-graduation trades go through `Zap._swapOnUniswapV2`, which similarly quotes off the pair's live reserves at the moment of inclusion [5](#0-4) . Additionally, `_sellInternal`'s USDC-floor check on sells is computed from the LT's live `exchangeRate()` [6](#0-5) , another value that drifts over time and that a stale, unconfirmed tx has no way to bound temporally.

Because none of these entry points take a deadline, a transaction signed against today's curve state (and a slippage bound set relative to that state) remains valid and executable at any future block. A block builder/validator (or simply network congestion) can delay inclusion; by the time it lands, the curve/LT price may have moved substantially in the trader's favor from the *submitter's* perspective at signing time but the transaction still executes at the old, now-stale terms relative to current market conditions — the classic missing-deadline MEV/staleness class described in the referenced report, mapped onto alt.fun's bonding-curve + HyperSwap venues.

### Impact Explanation
Traders lose the ability to bound the time window during which their signed intent can be executed, and the protocol/LT reserve pricing can shift meaningfully between signing and inclusion given the bonding curve's `k`-based repricing on every trade and the LT's live `exchangeRate()`. A stuck-then-late-included buy or sell executes at curve/LT pricing the user never intended to trade against, and — because `minTokensOut`/`minUsdcOut` are typically set relative to the state at signing time with some slippage buffer — the loose bound does not protect against execution at a stale, unfavorable-to-current-market price. This is a direct value-transfer vector out of the trader (and, since fees scale with trade size/price, indirectly affects `FeeVault` accrual accuracy) with no cost to whoever controls the timing of inclusion.

### Likelihood Explanation
Any unprivileged caller submitting `Zap.buy`, `Zap.sell`, `Zap.createToken`, or their permit variants is affected; no special privilege or setup is required, and the class is well-documented as a common MEV pattern in AMM systems with delayed inclusion (PoS proposer visibility windows). The likelihood scales with mempool congestion and gas-price volatility, both of which are outside the trader's control.

### Recommendation
Add an explicit `deadline` parameter to `Zap.buy`, `Zap.sell`, `Zap.createToken`, and their `*WithPermit` variants, and revert with a clear error (e.g. `Expired()`) if `block.timestamp > deadline`, mirroring the pattern already used for the EIP-2612 `PermitData.deadline` [7](#0-6)  but applied to the trade execution itself rather than only the permit signature.

### Proof of Concept
1. Alice calls `zap.buy(token, usdcAmount, minTokensOut, referrer)` with `minTokensOut` computed against the current curve reserves, intending near-immediate inclusion.
2. Due to network congestion or a validator holding the transaction, inclusion is delayed by many blocks/minutes.
3. In the interim, multiple buys/sells shift the curve's `reserveToken`/`reserveAsset` (via `Router._computeBuy`/`_computeSell`) or, post-graduation, the HyperSwap pair's reserves shift via `_swapOnUniswapV2`.
4. Alice's transaction is finally included; it still satisfies `tokensOut >= minTokensOut` [8](#0-7)  because that bound was set loosely, but Alice receives a materially worse price than she would have received had inclusion happened when she signed — and has no on-chain mechanism to invalidate the stale intent because no `deadline` field exists to check.

### Citations

**File:** packages/contracts/src/Zap.sol (L178-196)
```text
    function buy(
        address tokenAddress,
        uint256 usdcAmount,
        uint256 minTokensOut,
        address referrer
    ) external nonReentrant returns (uint256 tokensOut) {
        return _buyInternal(tokenAddress, usdcAmount, minTokensOut, referrer);
    }

    function buyWithPermit(
        address tokenAddress,
        uint256 usdcAmount,
        uint256 minTokensOut,
        address referrer,
        PermitData calldata p
    ) external nonReentrant returns (uint256 tokensOut) {
        _tryPermit(address(_s().usdc), msg.sender, p);
        return _buyInternal(tokenAddress, usdcAmount, minTokensOut, referrer);
    }
```

**File:** packages/contracts/src/Zap.sol (L198-214)
```text
    function sell(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut
    ) external nonReentrant returns (uint256 usdcOut) {
        return _sellInternal(tokenAddress, tokenAmount, minUsdcOut);
    }

    function sellWithPermit(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut,
        PermitData calldata p
    ) external nonReentrant returns (uint256 usdcOut) {
        _tryPermit(tokenAddress, msg.sender, p);
        return _sellInternal(tokenAddress, tokenAmount, minUsdcOut);
    }
```

**File:** packages/contracts/src/Zap.sol (L218-237)
```text
    function _createTokenInternal(
        Bonding.LaunchParams calldata params,
        uint256 seedUsdcAmount
    ) internal returns (address tokenAddr) {
        if (params.ltAddress == address(0)) revert InvalidInput();
        // Mandatory seed buy. See `MIN_SEED_USDC` for the no-cap rationale.
        // Floored at the live mint floor too, so a seed can't pass here and
        // then revert when it's minted (see `minSeedUsdc`).
        if (seedUsdcAmount < minSeedUsdc()) revert BelowMinSeed();

        (tokenAddr,) = _s().bonding.launch(params, msg.sender);
        emit TokenCreated(tokenAddr, msg.sender, params.ltAddress);

        // The seed buy is what arms the bypass into `Bonding`'s launch
        // trading delay — it MUST happen in the same tx as `bonding.launch`,
        // otherwise the transient flag clears and the buy reverts with
        // `TradingNotOpen`. `minTokensOut = 0` is intentional: same-tx as
        // launch, so there's nothing for slippage to protect against.
        _buyInternal(tokenAddr, seedUsdcAmount, 0, address(0));
    }
```

**File:** packages/contracts/src/Zap.sol (L254-256)
```text
        (tokensOut, grossSpent, actualFee) = _executeBuy(tokenAddress, usdcAmount);

        if (tokensOut < minTokensOut) revert SlippageExceeded();
```

**File:** packages/contracts/src/Zap.sol (L440-445)
```text
        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
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

**File:** packages/contracts/src/interfaces/IZap.sol (L8-15)
```text
interface IZap {
    struct PermitData {
        uint256 value;
        uint256 deadline;
        uint8 v;
        bytes32 r;
        bytes32 s;
    }
```
