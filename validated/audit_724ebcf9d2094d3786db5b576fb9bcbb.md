### Title
Unguarded `assetReserve - virtualLtReserve` subtraction in `canGraduate`/`_prepareGraduationLiquidity` can underflow-Panic and permanently brick a token's curve - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes an OOB memory read triggered by a corrupted/degenerate index structure that a local user can reach simply by having a broken directory present, crashing the affected subsystem. The alt.fun analog is a Solidity arithmetic-underflow "crash" (a `Panic(0x11)` revert) reachable by an unprivileged trader through ordinary buy/sell traffic on the bonding curve. `Bonding.canGraduate` and `Bonding._prepareGraduationLiquidity` both compute `realLtRaised`/`ltFromPair` as `assetReserve - _launchTimeVirtualLtReserve(token_, pair)` with a bare Solidity `-`, unlike the sibling computation in `finalizeGraduation` which explicitly uses a saturating subtract and documents *why* ("keep finalize from bricking on a Panic if any future code path... briefly violates the invariant").

### Finding Description
`canGraduate` reads the pair's stored reserves and subtracts the immutable, derived launch-time virtual LT reserve to get the real LT raised on the curve: [1](#0-0) 

The same unguarded pattern is used in `_prepareGraduationLiquidity`, which runs unconditionally at the buy that crosses graduation and inside `triggerGraduation`: [2](#0-1) 

`_launchTimeVirtualLtReserve` recovers the initial virtual reserve purely from `Pair.k() / TOTAL_SUPPLY()`, a value fixed forever at `mint`: [3](#0-2) 

`Pair.swap` itself only enforces a `+1`-slack floor on the invariant, not exact conservation, on every buy/sell: [4](#0-3) 

and `Router._computeBuy` rounds the capped-buy `amountInUsed` up while `_computeSell` rounds `assetOut` down: [5](#0-4) 

Because the `+1` K-slack lets each swap settle marginally in the trader's favor, and buy/sell rounding is asymmetric (ceil on buy-cap, floor on sell), repeated round-trip buy/sell cycles by a single unprivileged trader can drift the stored `assetReserve` down relative to the fixed `virtualLtReserve` baseline. Once a swap lands `assetReserve` at or fractionally below `_launchTimeVirtualLtReserve(...)`, the bare subtraction in `canGraduate` (and `_prepareGraduationLiquidity`) reverts with an arithmetic-underflow Panic instead of the intended `false`/zero result.

The developers were clearly aware of this exact underflow-brick risk class — `finalizeGraduation`'s comment on its own (unrelated) subtraction explicitly calls out "keep finalize from bricking on a Panic" — but did not apply the same saturating-subtract defense to the `assetReserve - virtualLtReserve` computation used on the hot buy/sell path.

`canGraduate` is invoked on every buy via `_executeBuy` and on every sell via `Bonding.sell`: [6](#0-5) [7](#0-6) 

A Panic in `canGraduate` therefore reverts the enclosing `buy`/`sell`/`triggerGraduation` transaction, and — because the underlying trigger condition (`assetReserve` sitting at/near the virtual floor) is a persistent state of the `Pair`, not a transient one — every subsequent `buy`, `sell`, and `triggerGraduation` call for that token reverts identically. There is no other code path that can move `Pair`'s reserves for a `Lifecycle.Curve` token (only `Router.buy`/`sell`, both of which call the now-permanently-reverting `canGraduate`), so the token is frozen permanently in `Lifecycle.Curve` with no way to trade out or reach graduation.

### Impact Explanation
This permanently freezes every trader's LT and every unsold token balance held inside that token's `Pair`, and freezes the creator's ability to graduate the token to HyperSwap V2 — no rescue path exists because `Pair`/`Router`/`Bonding` expose no privileged or fallback mechanism to adjust reserves outside the buy/sell/graduate flow, which is itself the mechanism bricked. This satisfies "permanent freezing of trader, creator or LP funds."

### Likelihood Explanation
Reachable by a single unprivileged wallet issuing ordinary `Zap.buy`/`Zap.sell` calls (or their permit variants) that round-trip through `Bonding.buy`/`Bonding.sell` → `Router._computeBuy`/`_computeSell` → `Pair.swap`; no special LT behavior, admin action, or off-chain component is required — only enough round-trip cycles to accumulate the rounding drift permitted by the `+1` K-slack and the ceil/floor asymmetry between buy-cap and sell math.

### Recommendation
Replace the bare subtraction in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` (`assetReserve - _launchTimeVirtualLtReserve(...)`) with the same saturating-subtract pattern already used in `finalizeGraduation` (`ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0`), so `realLtRaised`/`ltFromPair` floor at zero instead of reverting when `assetReserve` transiently sits at or below the virtual-reserve baseline.

### Proof of Concept
1. Launch a token via `Zap.createToken`; `Bonding._deployAndSeed` sets `Pair._pool.k = TOTAL_SUPPLY * virtualLtReserve`, so initially `assetReserve == virtualLtReserve` and `_launchTimeVirtualLtReserve(...) == assetReserve` (subtraction is exactly 0, safe).
2. Attacker (any unprivileged wallet) repeatedly calls `Zap.buy` followed by `Zap.sell` (round-tripping the same notional amount) on the token. Each `Pair.swap` only needs `(newTokenReserve+1)*(newAssetReserve+1) >= k` (`Pair.sol:73`), and `Router._computeBuy`'s ceil-rounded `amountInUsed` on the capped branch vs. `Router._computeSell`'s floor-rounded `assetOut` (`Router.sol:127-182`) let each cycle settle marginally in the attacker's favor, nudging stored `assetReserve` down relative to the fixed `virtualLtReserve`.
3. After enough cycles, `assetReserve` lands at or fractionally below `_launchTimeVirtualLtReserve(token_, pair)` on a subsequent `buy`/`sell`. The next call into `canGraduate` (invoked from `_executeBuy` after every buy, and explicitly from `Bonding.sell`) executes `assetReserve - _launchTimeVirtualLtReserve(...)` and reverts with `Panic(0x11)` (arithmetic underflow).
4. Because this state is persisted in `Pair._pool`, every future `buy`, `sell`, and `triggerGraduation` call on that token now reverts identically at the same `canGraduate` call site, permanently freezing all LT and token liquidity held in that `Pair` with no admin or fallback recovery path.

### Citations

**File:** packages/contracts/src/Bonding.sol (L592-598)
```text
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();
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

**File:** packages/contracts/src/Bonding.sol (L1073-1090)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;
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

**File:** packages/contracts/src/Router.sol (L125-182)
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
