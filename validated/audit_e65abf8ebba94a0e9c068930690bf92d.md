### Title
Rounding slack in the bonding-curve AMM lets repeated buy/sell round-trips push `assetReserve` below the launch-time virtual LT floor, permanently bricking `canGraduate` with an underflow revert - ([File: packages/contracts/src/Bonding.sol])

### Summary
The GLib report describes a state-producing function (`g_date_time_add_full`) that can leave an object in an invalid state, which a later decomposition function (`g_date_time_get_ymd`) reads without validation, causing an out-of-bounds read/corrupted output and a logic-error DoS. The alt.fun analog is the bonding-curve math in `Router._computeBuy`/`_computeSell` (state-producing) combined with `Pair.swap`'s `+1` K-invariant slack, which can leave the pair's stored `assetReserve` below the launch-time virtual LT reserve floor. That "invalid" reserve state is then decomposed by `Bonding.canGraduate` via an unchecked subtraction, causing a permanent arithmetic-underflow revert that bricks buying, selling, and graduation for the token.

### Finding Description
`Router._computeBuy` and `Router._computeSell` implement a fee-less constant-product curve using floor (`/`) integer division on both sides: [1](#0-0) [2](#0-1) 

In both `_computeBuy` and `_computeSell`, the trader-favorable rounding (`tokensOut`/`assetOut` computed as `reserve - floor(k/newReserve)`) means the resulting `(newTokenReserve, newAssetReserve)` pair can produce a product strictly less than `k`. `Pair.swap` tolerates this via an explicit `+1` slack in its invariant check instead of requiring `newTokenReserve * newAssetReserve >= k`: [3](#0-2) 

`(newTokenReserve+1)*(newAssetReserve+1) < _pool.k` only reverts once the product falls short of `k` by more than `newTokenReserve + newAssetReserve + 1`. Every buy/sell (or matched buy-then-sell round trip) is therefore permitted to leak a small amount of value out of the curve's stored `k`-consistent reserves, moving `_pool.assetReserve` slightly further away from what it would be under an exact invariant. Because there is no curve fee to offset this (per the contract's own design notes: "No fees here — `Zap` handles fees"), this leak is monotonic and compounds over many trades — it isn't self-correcting.

`Bonding.canGraduate` recovers the launch-time virtual LT reserve from immutable `Pair.k()` / `Token.TOTAL_SUPPLY()` and subtracts it from the *live* stored `assetReserve` without a floor/underflow guard: [4](#0-3) [5](#0-4) 

If enough rounding-favorable buy/sell round trips accumulate such that `assetReserve` drifts below `_launchTimeVirtualLtReserve(token_, pair)`, the subtraction `assetReserve - _launchTimeVirtualLtReserve(...)` underflows and reverts with a Solidity Panic(0x11).

This is exactly analogous to the GLib bug class: a state-producing path (`_computeBuy`/`_computeSell` + `Pair.swap`'s slack) can leave the "object" (`Pool.assetReserve`) in a state inconsistent with the invariant its consumer assumes, and the consumer (`canGraduate`'s unchecked subtraction) corrupts/crashes instead of validating.

The blast radius is severe because `canGraduate` is not an isolated view — it is invoked unconditionally on every trade and on the permissionless graduation trigger:
- `Bonding._executeBuy` calls `canGraduate(tokenAddress)` after every buy: [6](#0-5) 
- `Bonding.sell` calls `canGraduate(tokenAddress)` before allowing a sell: [7](#0-6) 
- `Bonding.triggerGraduation` calls `canGraduate` directly: [8](#0-7) 

Once the underflow condition is reached, all three entry points revert unconditionally for that token — there is no other path to advance the token to `Lifecycle.Graduating`/`Graduated`, and no rescue function exists for a `Lifecycle.Curve` token stuck this way.

### Impact Explanation
Once `assetReserve` drifts below the recovered virtual floor, the affected token's curve is permanently bricked:
- No further `buy()` succeeds (every buy ends by calling `canGraduate`, which reverts).
- No further `sell()` succeeds (it calls `canGraduate` up front).
- `triggerGraduation()` also reverts, so the token can never reach `Lifecycle.Graduating`/`Graduated`.

This permanently freezes: (a) all real LT already raised and held in the `Pair` (unreachable — `Router.graduate` is only callable from `Bonding._prepareGraduationLiquidity`, itself only reachable via `_enterGraduating`, which is now unreachable), and (b) all tokens still held by traders/creator on that curve, since they can no longer be sold. This satisfies the "permanent freezing of trader, creator or LP funds" bar for Medium/High severity.

### Likelihood Explanation
The leak per trade is bounded by the `+1` slack (at most `newTokenReserve + newAssetReserve` wei-scale units of `k` per swap), so a single trade is very unlikely to trip the underflow on a curve with large reserves. However, the leak is monotonic and fee-less, and any unprivileged trader can repeatedly buy and sell back into the curve (self-funding both legs, since tokens/LT return to the same wallet each round trip, modulo any BounceTech LT streaming-fee drift) to accumulate the rounding leak over many iterations without needing any other party's cooperation. This makes the DoS end-state reachable purely through repeated public `buy`/`sell` calls, at a gas cost proportional to the number of round trips required — no privileged role, no external price manipulation, and no cooperation from other actors are needed.

### Recommendation
- Add fee-favoring (protocol-favoring) rounding to `Router._computeBuy`/`_computeSell` so `k` can only increase or stay equal after a swap, eliminating the leak that `Pair.swap`'s `+1` slack currently tolerates, or tighten `Pair.swap`'s invariant to `newTokenReserve * newAssetReserve >= _pool.k` without slack.
- In `Bonding.canGraduate` (and `previewLtUntilGraduation`), replace the raw subtraction `assetReserve - _launchTimeVirtualLtReserve(...)` with a saturating subtraction (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`), matching the saturating-subtract pattern already used defensively in `finalizeGraduation` (`packages/contracts/src/Bonding.sol:1019-1020`), so a reserve dip below the virtual floor degrades gracefully instead of permanently reverting every trade.

### Proof of Concept
Conceptual sequence (exact iteration count depends on live reserves and is not derivable without on-chain values, but the mechanism is deterministic):
1. Attacker/trader calls `Zap.buy` (routes to `Bonding.buy` → `Router.buy` → `Pair.swap`) for a small `amountIn`, receiving `tokensOut` computed by `Router._computeBuy`'s floor-rounding.
2. Attacker immediately calls `Zap.sell` (routes to `Bonding.sell` → `Router.sell` → `Pair.swap`) selling back the same `tokensOut`, receiving `assetOut` computed by `Router._computeSell`'s floor-rounding.
3. Each such round trip is accepted by `Pair.swap`'s `(newTokenReserve+1)*(newAssetReserve+1) < _pool.k` check even though the true product after rounding is slightly below `_pool.k`, so `_pool.assetReserve` ends up marginally lower than before the round trip while `_pool.tokenReserve` returns close to its starting value.
4. Repeating steps 1–2 enough times monotonically drains `_pool.assetReserve` toward, and eventually below, `_launchTimeVirtualLtReserve(token, pair) = Pair.k() / Token.TOTAL_SUPPLY()`.
5. The next call to any of `Bonding.buy`, `Bonding.sell`, or `Bonding.triggerGraduation` invokes `canGraduate`, which executes `assetReserve - _launchTimeVirtualLtReserve(...)` in [9](#0-8)  and reverts with Panic(0x11), permanently bricking the token's curve.

### Citations

**File:** packages/contracts/src/Router.sol (L130-148)
```text
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

**File:** packages/contracts/src/Bonding.sol (L582-606)
```text
    /// @notice Sell tokens on the curve. Router-only.
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

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
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
