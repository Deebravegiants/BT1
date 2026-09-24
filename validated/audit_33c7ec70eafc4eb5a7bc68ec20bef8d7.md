### Title
Fee-less rounding drift on the curve AMM can underflow `canGraduate`'s virtual-reserve subtraction and permanently brick a token's buy/sell path - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Pair.sol])

### Summary
CVE-2017-17912 is a class of bug where code reads/derives a value assuming an invariant about buffer bounds that is never actually enforced, so the read walks past the allocated region. Alt.fun has a structurally analogous assumption: `Bonding.canGraduate` (and its callers on every buy/sell) subtract a "recovered" launch-time virtual LT reserve from the pair's live `assetReserve`, assuming `assetReserve` can never fall below that virtual baseline. That assumption is not enforced anywhere — the curve's fee-less, floor-rounded AMM math in `Router._computeBuy`/`_computeSell` combined with `Pair.swap`'s `+1` K-invariant slack lets an unprivileged trader extract reserve value on every round-trip trade, which can drive the stored `assetReserve` below the virtual baseline and cause a Solidity underflow revert in a path that fires on *every* subsequent buy and sell for that token.

### Finding Description
`Bonding.canGraduate` computes: [1](#0-0) 

`realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` assumes `assetReserve` (the pair's stored, non-virtual-adjusted LT reserve) is always `>=` the recovered launch-time virtual reserve (`Pair.k() / TOTAL_SUPPLY()`). This function is invoked unconditionally on **every** curve buy via `_executeBuy` and on **every** curve sell via `sell()`: [2](#0-1) [3](#0-2) 

The curve itself has no trading fee (`Router.sol` header: "No fees here — `Zap` handles fees") and both trade legs use floor division that rounds in the trader's favor: [4](#0-3) [5](#0-4) 

`_computeBuy` gives `tokensOut = reserveToken - k/newReserveAsset` (floor-division makes the subtrahend smaller, so `tokensOut` is rounded up — a token-side subsidy to the buyer), and `_computeSell` gives `assetOut = reserveAsset - k/newReserveToken` (same floor-division bias — an LT-side subsidy to the seller). `Pair.swap` only enforces the invariant with a `+1` grace band on each side: [6](#0-5) 

`(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` permits the post-trade product to sit strictly below `k`, i.e. it does not re-mint the leaked value back into the pool. Because there is no fee to counteract this drift, a trader who repeatedly round-trips small buy-then-sell pairs on the curve extracts a small amount of real LT out of `_pool.assetReserve` on each cycle at negligible net cost (rounding favors the trader on both legs). Over enough round trips this can push `assetReserve` below the recovered virtual reserve. At that point the subtraction in `canGraduate` (`assetReserve - _launchTimeVirtualLtReserve`) underflows and reverts under Solidity 0.8's overflow checks.

Since `canGraduate` is called unconditionally inside `_executeBuy` (post-buy) and `sell()` (pre-sell), every subsequent `Bonding.buy`/`Bonding.sell` call for that token — and therefore every `Zap.buy`/`Zap.sell` — reverts. `triggerGraduation` also calls `canGraduate` and would revert. The token is left permanently stuck in `Lifecycle.Curve` with no reachable exit: it can never trade, never graduate, and any LT/tokens already deposited in `Pair` for that market are permanently frozen.

### Impact Explanation
This is a permanent freezing of trader/creator funds: once the underflow condition is triggered, the affected `Pair` for that token becomes permanently untradeable (no buy, no sell, no graduation path), stranding whatever real LT and launched tokens sit in the `Pair` and cutting off further `FeeVault` accrual for that market. This matches the "Accept only concrete theft or permanent freezing of trader, creator or LP funds" bar for a valid analog.

### Likelihood Explanation
Reachable purely through unprivileged `Zap.buy` / `Zap.sell` calls (or `Bonding.buy`/`sell` through any allowlisted router) — no privileged role required. The trigger requires enough round-trip volume to erode `assetReserve` below the virtual baseline, which is gated by BounceTech's live `minTransactionSize()` floor on each leg (`Zap._buyInternal`/`_sellInternal` enforce `minUsdcAmount()`), so the number of round trips needed and the gas/LT-redemption-fee cost of each cycle bound the practicality of a full drain. The bug is nonetheless real and code-provable: the underflow-guarding invariant is never checked or restored anywhere in `Router` or `Pair`, so the DoS is only a matter of degree, not of reachability.

### Recommendation
- Clamp the subtraction in `canGraduate` / `previewLtUntilGraduation`: treat `assetReserve <= _launchTimeVirtualLtReserve` as `realLtRaised = 0` instead of allowing the raw subtraction to underflow-revert.
- Consider removing (or re-minting) the rounding subsidy in `Router._computeBuy`/`_computeSell` — e.g. round in the protocol's favor instead of the trader's — so the curve cannot be drained via fee-less round-trip arbitrage.
- Add an invariant test/property (e.g. Foundry invariant or fuzz test) asserting `assetReserve >= _launchTimeVirtualLtReserve` holds after arbitrary sequences of buys/sells for a given `k`.

### Proof of Concept
1. Launch a token via `Zap.createToken`, seeding the curve as usual (`VIRTUAL_LIQUIDITY_USD` virtual LT reserve baked into `Pair.k()`).
2. Repeatedly call `Zap.buy(token, minUsdcAmount(), 0, address(0))` immediately followed by `Zap.sell(token, tokensOut, 0)` in a loop from an unprivileged EOA, each cycle sized at (or just above) the BounceTech mint/redeem floor to stay legal.
3. Because `Router._computeBuy`/`_computeSell` round in the trader's favor and `Pair.swap`'s `+1` slack never claws the difference back, each cycle leaks a small amount of real LT out of `_pool.assetReserve` while leaving `_pool.k` (and thus the recovered virtual reserve) unchanged.
4. After sufficient cycles, `_pool.assetReserve` drops below `_launchTimeVirtualLtReserve(token, pair)`.
5. The next `Zap.buy` or `Zap.sell` call reverts inside `Bonding.canGraduate`'s `assetReserve - _launchTimeVirtualLtReserve(...)` subtraction (Solidity 0.8 underflow revert), permanently bricking that token's curve — no further trade or graduation is possible, freezing any LT/tokens still held by the `Pair`.

*Note: exact per-cycle leakage magnitude and the total number of cycles required depend on `_launchTimeVirtualLtReserve`'s implementation, which is defined later in `Bonding.sol` beyond the portion retrieved here; the index truncated the file at 1000 of 1534 lines, so this detail could not be directly confirmed and should be verified in a full read of `packages/contracts/src/Bonding.sol` (and `_prepareGraduationLiquidity`) before treating the exact cycle count as established.*

### Citations

**File:** packages/contracts/src/Bonding.sol (L583-606)
```text
    function sell(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();

        (, uint256 assetOut) = $.router.sell(amountIn, tokenAddress, msg.sender);
        if (assetOut < amountOutMin) revert SlippageExceeded();

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, false, assetOut, amountIn, newCurveSupply, newLtReserve);
        return assetOut;
    }
```

**File:** packages/contracts/src/Bonding.sol (L689-695)
```text
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L918-932)
```text
    function _executeBuy(
        address tokenHolder,
        address trader,
        uint256 amountIn,
        address tokenAddress
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
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

**File:** packages/contracts/src/Router.sol (L172-182)
```text
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
