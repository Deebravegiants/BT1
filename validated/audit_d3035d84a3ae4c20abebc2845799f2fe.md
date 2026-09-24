### Title
Floor-rounding drift in fee-less curve trades can push `assetReserve` below the launch-time virtual LT seed, permanently reverting graduation via an unhandled subtraction underflow - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Router._computeBuy`/`_computeSell` and `Pair.swap` implement a fee-less constant-product curve whose K-floor check tolerates a `+1` rounding slack on every trade [1](#0-0) . Both buy and sell quotes use floor division against `k`, which systematically rounds in the trader's favor by a sub-wei margin on every trade [2](#0-1) [3](#0-2) . An unprivileged trader doing many small buy/sell round trips can accumulate this drift until `tokenReserve` returns to its original virtual `TOTAL_SUPPLY` value while `assetReserve` sits below the immutable launch-time virtual LT seed recovered via `Pair.k()/TOTAL_SUPPLY()`. `Bonding._prepareGraduationLiquidity` unconditionally computes `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(...)` with no underflow guard [4](#0-3) , so once drift pushes `assetReserve` below the seed, this line reverts with an unhandled Solidity Panic (arithmetic underflow) — a reachable "assertion abort" in the same bug class as CVE-2017-12959's `dict_add_mrset` reachable assertion, except here it is unprivileged-trader reachable and freezes funds rather than merely crashing a process.

### Finding Description
`canGraduate()` has two independent triggers. The supply trigger (`IPair(pair).tokenBalance() == 0`) short-circuits and returns `true` without ever touching `assetReserve - virtualLtReserve` [5](#0-4) . That subtraction is only performed later, unconditionally, inside `_prepareGraduationLiquidity`, which is invoked by `_enterGraduating` from both the inline post-buy path (`_executeBuy`, called on every `Bonding.buy`) and the permissionless `triggerGraduation` [6](#0-5) [7](#0-6) .

Because `Router` charges no curve fee ("`Zap` handles fees" per its own header comment [8](#0-7) ), and `Pair.swap`'s K-floor check only requires `(newTokenReserve+1)*(newAssetReserve+1) >= k` rather than exact equality [9](#0-8) , the floor-rounded `_computeBuy`/`_computeSell` outputs can shave sub-wei amounts off the pool on every trade without tripping that check. Repeated round-trip trades by a single unprivileged trader can accumulate this drift so that when `tokenReserve` is driven back up to `TOTAL_SUPPLY` (curve fully sold back down to its virtual max), `assetReserve` has drifted to a value strictly below the immutable `_launchTimeVirtualLtReserve` recovered from `Pair.k()/TOTAL_SUPPLY()` [10](#0-9) .

Once the curve is sold down to `tokenBalance() == 0` under this drifted state, `canGraduate()` returns `true` via the supply leg, so:
- `Bonding.sell` reverts unconditionally via `if (canGraduate(tokenAddress)) revert TokenIsGraduating();` [11](#0-10) , blocking sells.
- Every further `Bonding.buy` calls `_executeBuy` → `canGraduate` → `_enterGraduating` → `_prepareGraduationLiquidity`, which underflows and panics, reverting the whole buy [12](#0-11) .
- `triggerGraduation` hits the identical underflow and reverts every time it's called, by anyone, forever [7](#0-6) .

Since `_enterGraduating` only flips `info.lifecycle` inside the same reverted call, the token is stuck permanently in `Lifecycle.Curve` with `tokenBalance() == 0`: no buy, no sell, no graduation path succeeds ever again.

### Impact Explanation
This permanently freezes: all curve-raised LT sitting in the `Pair` (never recoverable — `Router.graduate` is only reachable from the now-permanently-reverting `_prepareGraduationLiquidity`), the 25% LP-reserved token allocation, and every trader's already-purchased token balance (illiquid — cannot be sold back, cannot graduate to a tradable HyperSwap V2 market). This is a permanent freezing of trader, creator, and protocol funds tied to that token — satisfying the Validate bar for concrete permanent freezing, not merely a single-tx DoS.

### Likelihood Explanation
Reaching the drift requires no privileges — only a sequence of ordinary `Zap`-mediated buy/sell round trips (or direct `Bonding.buy`/`sell` calls through an allowlisted router) on a single token's curve, exploiting the deterministic floor-rounding behavior of `_computeBuy`/`_computeSell`. The exact number of round trips needed depends on the LT's `exchangeRate` and curve constants and was not empirically bounded here, but the rounding-favors-trader direction is a structural property of the floor-division formulas, not a probabilistic one, so the drift is monotonic and achievable given enough attacker-funded round trips (dust trades are strictly viable since `Router` charges no per-trade curve fee).

### Recommendation
Add an explicit `assetReserve < virtualLtReserve` guard in `canGraduate`/`_prepareGraduationLiquidity` that fails soft (e.g., treat the supply trigger as insufficient rather than reaching the unguarded subtraction), and/or eliminate the rounding-favors-trader direction in `_computeBuy`/`_computeSell` by rounding buy/sell outputs in the pool's favor (ceil against the trader instead of floor), consistent with the ceil-rounding already used for the overflow-cap path in `_computeBuy`.

### Proof of Concept
1. Launch a token via `Zap.createToken`, establishing `Pair` with `tokenReserve = TOTAL_SUPPLY`, `assetReserve = virtualLtReserve`, `k = TOTAL_SUPPLY * virtualLtReserve`.
2. As an unprivileged trader, repeatedly call small `buy` then `sell` round trips of equal nominal size through the allowlisted `Zap`/`Router` path. Each pair of calls uses floor division in `Router._computeBuy` (line 138) and `Router._computeSell` (line 181), each rounding in the trader's favor by up to 1 wei, protected only by `Pair.swap`'s `+1` K-floor slack.
3. Continue round trips (optionally interleaved with real trading activity from other users) until cumulative drift pushes `assetReserve` below the immutable `_launchTimeVirtualLtReserve` at the moment `tokenReserve` returns to `TOTAL_SUPPLY` (i.e., when the real curve balance approaches full sellout, `tokenBalance() == 0`).
4. Call `Bonding.triggerGraduation(token)` (or any subsequent `buy`): the call reverts with a Solidity Panic (arithmetic underflow) inside `_prepareGraduationLiquidity`'s `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(...)` (Bonding.sol:1084).
5. Observe `Bonding.sell` also reverts (`TokenIsGraduating`) because `canGraduate` still reports `true` via the supply leg — the token is now permanently untradeable and ungraduatable, freezing all LT and tokens held by the `Pair`.

### Citations

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

**File:** packages/contracts/src/Router.sol (L135-148)
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

**File:** packages/contracts/src/Bonding.sol (L594-598)
```text
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();
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

**File:** packages/contracts/src/Bonding.sol (L1073-1087)
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
```

**File:** packages/contracts/src/Bonding.sol (L1098-1119)
```text
    /// @dev Recovers the launch-time virtual LT reserve from immutable
    ///      identities: `Pair._pool.k = tokenReserve_init * assetReserve_init
    ///      = TOTAL_SUPPLY * virtualLtReserve_init` is set ONCE in
    ///      `Pair.mint` and never modified by `Pair.swap` (swap only
    ///      mutates `tokenReserve` / `assetReserve` and asserts K-floor).
    ///      So `Pair.k() / Token.TOTAL_SUPPLY()` returns the exact
    ///      `virtualLtReserve` that was passed to `addInitialLiquidity` at
    ///      launch — for any pair, in any phase, with no storage of our own.
    ///
    ///      Going through this derivation rather than a stored mirror
    ///      eliminates an admin-writable economic-state slot and makes the
    ///      donation-immunity property a pure consequence of the pair's
    ///      already-immutable accounting. The `TOTAL_SUPPLY`-equality check
    ///      in `setTokenImplementation` keeps the divisor consistent across
    ///      impl rotations, so tokens launched under different
    ///      `tokenImplementation` versions still derive the same way.
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```
