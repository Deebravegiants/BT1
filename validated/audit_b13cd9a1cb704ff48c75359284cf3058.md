### Title
Cumulative K-invariant rounding slack drains `Pair.assetReserve` below the launch-time virtual LT baseline, causing `canGraduate`'s subtraction to underflow and permanently brick the curve - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Pair.sol])

### Summary
The GLib advisory's bug class is a state-confusion/arithmetic error in a stateful accounting routine (nested-element counters overflowing during introspection) that leads to an out-of-bounds read and DoS. The alt.fun analog is a state-confusion arithmetic error in the bonding-curve reserve accounting: `Router._computeBuy`/`_computeSell` round every trade in the trader's favor and `Pair.swap`'s `+1` K-invariant slack lets that rounding persist, letting `assetReserve` drift below the immutable launch-time virtual LT baseline recovered in `Bonding._launchTimeVirtualLtReserve`. When that happens, `Bonding.canGraduate`'s unchecked subtraction `assetReserve - _launchTimeVirtualLtReserve(...)` underflows and reverts (Solidity Panic 0x11), and because `canGraduate` is invoked on every buy, every sell, and `triggerGraduation`, the token's curve becomes permanently unusable.

### Finding Description
`Router._computeBuy` computes `tokensOut = reserveToken - (k / newReserveAsset)`, where `k / newReserveAsset` is floor-divided — this rounds `tokensOut` up (in the buyer's favor) relative to the exact constant-product break-even. [1](#0-0) 

Symmetrically, `Router._computeSell` computes `assetOut = reserveAsset - (k / newReserveToken)`, again floor-dividing, which rounds `assetOut` up (in the seller's favor). [2](#0-1) 

Both roundings extract slightly more value from the pool than the exact invariant allows. `Pair.swap` tolerates this via an explicit `+1` slack on both sides of the K check: `(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` reverts only if the *padded* product falls below `k` — it does not require reserves to stay above their initial values. [3](#0-2) 

Because a buy followed by a sell of the tokens just bought each round rounds in the trader's favor and the slack check never restores the lost wei, repeated buy/sell round trips monotonically drain `_pool.assetReserve` below its launch value over time — this is the "state confusion" analog: the stored reserve state silently diverges from what the recovered virtual baseline assumes.

`Bonding.canGraduate` (and `previewLtUntilGraduation`) recover that launch-time virtual LT baseline purely from the immutable identity `Pair.k() / Token.TOTAL_SUPPLY()`, then subtract it from the live stored `assetReserve` with no floor/clamp: [4](#0-3) [5](#0-4) 

Once accumulated rounding drift pushes `assetReserve` below `_launchTimeVirtualLtReserve(...)`, this subtraction underflows in checked Solidity arithmetic and reverts with a Panic, exactly mirroring the "unsigned integer overflow" mechanism in the GLib CVE but manifesting as a hard revert instead of an OOB read, because Solidity 0.8.x traps rather than wraps.

`canGraduate` is not an isolated view — it is called unconditionally inside every buy via `_executeBuy`, inside every `sell()`, and directly by the permissionless `triggerGraduation`: [6](#0-5) [7](#0-6) [8](#0-7) 

Once the underflow condition is reached, all three entry points revert unconditionally for that token, permanently bricking its curve.

### Impact Explanation
Any curve token whose `assetReserve` has drifted to/below the launch-time virtual baseline becomes permanently untradeable: `Zap.buy`/`Zap.sell` (via `Bonding.buy`/`Bonding.sell`) and `Bonding.triggerGraduation` all revert with an arithmetic Panic. Traders holding curve tokens can no longer sell them back for LT, the creator can never graduate the token to the DEX, and any LT already raised on the curve (held virtually inside `Pair`) becomes permanently frozen — there is no admin recovery path since `Pair`/`Bonding` expose no rescue for a bricked curve. This is a permanent freezing of trader and creator funds, satisfying the Critical bar.

### Likelihood Explanation
The attack requires only ordinary, permissionless actions any trader can already perform: repeated `Zap.buy`/`Zap.sell` round trips (or direct `Bonding.buy`/`sell` if the caller is an allow-listed router) on the same token. No privileged role, oracle manipulation, or upgrade is needed — only enough LT capital and gas to execute many round trips, and the rounding direction is deterministic and always favors the trader on both legs, so the drift accumulates monotonically rather than requiring luck. The exact number of round trips needed depends on the token's specific `virtualLtReserve` (derived from `VIRTUAL_LIQUIDITY_USD` and the LT's launch-time `exchangeRate()`), so magnitude of effort is token-dependent but the mechanism itself is unconditional and reproducible.

### Recommendation
- Clamp `realLtRaised` in `canGraduate` and `previewLtUntilGraduation` to `0` when `assetReserve <= _launchTimeVirtualLtReserve(...)` instead of subtracting unchecked, so a rounding-driven reserve dip degrades gracefully (defers graduation) rather than reverting and bricking the curve.
- Reconsider the `+1` K-invariant slack in `Pair.swap` (or tighten `_computeBuy`/`_computeSell` rounding direction) so it cannot be exploited via repeated round trips to monotonically drain `assetReserve`; consider rounding trades against the trader instead of in their favor, or bounding cumulative slack loss.
- Add a regression test that performs many buy/sell round trips and asserts `canGraduate`, `buy`, and `sell` never revert with an arithmetic Panic regardless of trade history.

### Proof of Concept
1. Launch a token via `Zap.createToken`, establishing `Pair._pool` with `tokenReserve = TOTAL_SUPPLY`, `assetReserve = virtualLtReserve`, `k = TOTAL_SUPPLY * virtualLtReserve` (`Pair.mint`, `Bonding._deployAndSeed`).
2. Repeatedly call `Zap.buy` for a small LT amount, then immediately `Zap.sell` the exact `tokensOut` just received, for many iterations. Each `_computeBuy`/`_computeSell` floor-division rounds in the trader's favor [9](#0-8) , and `Pair.swap`'s `+1`-padded K check permits the resulting reserves [10](#0-9) , so `_pool.assetReserve` trends strictly downward across iterations.
3. Once `_pool.assetReserve` (as read by `getReserves()`) falls to or below `Pair.k() / Token.TOTAL_SUPPLY()` (the recovered `virtualLtReserve`), any subsequent call to `Bonding.canGraduate` reverts with a Panic(0x11) on the subtraction [11](#0-10) .
4. Because `_executeBuy`, `sell()`, and `triggerGraduation` all call `canGraduate` unconditionally, every subsequent buy, sell, and graduation attempt on this token now reverts, permanently freezing all LT and token value already committed to that curve.

### Citations

**File:** packages/contracts/src/Router.sol (L135-182)
```text
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

**File:** packages/contracts/src/Bonding.sol (L588-606)
```text
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

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
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

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1114-1119)
```text
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```
