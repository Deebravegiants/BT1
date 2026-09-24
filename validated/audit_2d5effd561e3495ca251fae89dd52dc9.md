### Title
Underflow panic in `_prepareGraduationLiquidity` lets an unprivileged trader permanently brick a token's graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._prepareGraduationLiquidity` computes the real LT raised by the curve as an unchecked subtraction, `ltFromPair = assetReserve - virtualLtReserve`, with no floor/clamp. `assetReserve` is the pair's live stored asset reserve and `virtualLtReserve` is the launch-time virtual seed recovered from the immutable `k()`. `Pair.swap`'s K-invariant check uses a `+1` slack (`(newTokenReserve+1)*(newAssetReserve+1) >= k`) and `Router._computeSell` computes `assetOut` via floor division, both of which let a seller extract slightly more value per trade than exact curve math would allow. Repeated dust sells routed through the permissionless `Zap.sell`/`Bonding.sell` path can therefore push the pair's real `assetReserve` down to (or below) `virtualLtReserve`, causing the subtraction to underflow (Solidity Panic `0x11`) the moment `_enterGraduating` runs — whether fired inline from a graduating buy or from the fully permissionless `triggerGraduation`. [1](#0-0) 

### Finding Description
`_prepareGraduationLiquidity` is the single place that turns the frozen curve state into the LP-seeding amounts for graduation: [2](#0-1) 

`virtualLtReserve` is derived from the pair's immutable `k` and the token's `TOTAL_SUPPLY`, and is asserted by the codebase's own comments to be constant for the pair's lifetime: [3](#0-2) 

`assetReserve` is only mutated by `Pair.swap`, which enforces the K-invariant with an explicit `+1` slack on both sides rather than the exact product: [4](#0-3) 

`Router._computeSell` computes the LT paid out to a seller via floor division of `k / newReserveToken`; because integer division truncates, the resulting `assetOut` is rounded slightly in the seller's favor relative to the exact curve, and the `+1` slack check in `Pair.swap` does not reject this: [5](#0-4) 

Both `sell` and `buy` are reachable by any unprivileged wallet through `Zap`'s public entry points, which forward into `Bonding.sell`/`Bonding.buy` → `Router.sell`/`Router.buy`. By repeatedly submitting minimum-size sells (bounded below only by `minTransactionSize`), a trader can accumulate the per-trade rounding slack until the pair's stored `assetReserve` is driven down to/below the immutable `virtualLtReserve` floor. At that point, any subsequent call that reaches `_prepareGraduationLiquidity` — either the inline call inside `_executeBuy` at the end of a threshold-crossing buy, or the standalone permissionless `triggerGraduation` — reverts with an arithmetic underflow Panic instead of a typed, recoverable error: [6](#0-5) [7](#0-6) 

This mirrors the external report's bug class: an unprivileged, low-privilege actor triggers a crash/DoS specifically at the unpredictable moment a system is being promoted (there: replica set → sharded cluster; here: `Curve` → `Graduating`/`Graduated`). Unlike MongoDB, where the crash is "only" a primary restart, here the underflow is unrecoverable by design: `_enterGraduating` is the sole gateway into graduation, so once `assetReserve` is stuck at or under `virtualLtReserve`, `canGraduate`'s own USD-trigger arithmetic (which the codebase's `AGENTS.md` documents as the identical `storedAssetReserve - virtualLtReserve` expression) and `_prepareGraduationLiquidity` both revert forever, and there is no other path to drain the curve or move the token to `Graduated`.

### Impact Explanation
Once a token's pair reaches this state, graduation becomes permanently unreachable: every `buy` that would cross the graduation threshold reverts inside `_executeBuy`'s inline `_enterGraduating` call, and the standalone `triggerGraduation` entry point reverts identically. The 250M `LP_RESERVE` tokens parked in `Bonding` for that token, plus all curve-raised LT sitting in the pair, are permanently stranded — they can only be moved out via `Router.graduate`, which is only called from `_prepareGraduationLiquidity`. This is a permanent freeze of both creator/LP-bound token supply and trader-raised LT for the affected token, matching the "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
The attack requires no privilege — any wallet can call `Zap.sell`/`Bonding.sell` repeatedly. Because the exploitable slack is on the order of rounding-error magnitude per trade (bounded by the `+1` K slack and floor division in `_computeSell`), a large number of minimum-size sells would be needed to walk `assetReserve` down to the `virtualLtReserve` floor, so the attack is economically expensive in gas relative to the tiny per-trade edge extracted. This lowers likelihood from "trivial" to "feasible but costly," which is why this is rated Medium rather than High/Critical — consistent with the source advisory's own Medium severity for the analogous "unpredictable window" crash class.

### Recommendation
Clamp the subtraction in `_prepareGraduationLiquidity` (and the identical expression used by `canGraduate`) with a saturating subtract, e.g. `ltFromPair = assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`, mirroring the saturating-subtract pattern already used elsewhere in the same file (e.g. `finalizeGraduation`'s `protectedLT` computation). Separately, tighten `Pair.swap`'s K-invariant check to remove or bound the `+1` slack, and/or round `_computeSell`'s `assetOut` down (ceil the subtracted term) so sells cannot systematically extract value beyond the exact curve, eliminating the underlying drift that lets `assetReserve` cross below `virtualLtReserve` at all.

### Proof of Concept
1. Launch a token normally via `Zap.createToken` (creator seed buy establishes `assetReserve = virtualLtReserve_init + seedLt`).
2. As an unprivileged trader, repeatedly call `Zap.sell` (or `Bonding.sell` if router-allowlisted) with dust-sized token amounts at/near `minTransactionSize`. Each sell's `Router._computeSell` floor-division and `Pair.swap`'s `+1` K-slack allow the trader to receive marginally more LT than the exact curve would imply, incrementally reducing stored `assetReserve` faster than the true curve price would dictate.
3. Continue until `assetReserve` (as tracked by `Pair.getReserves()`) reaches at or below `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`.
4. Trigger any path into `_enterGraduating` — either a buy that crosses `canGraduate`'s threshold (via `Bonding._executeBuy`) or a direct call to `Bonding.triggerGraduation(tokenAddress)`.
5. Observe the call reverts with an arithmetic underflow Panic (`0x11`) at `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(...)` in `_prepareGraduationLiquidity`, and that this revert is permanent and reproducible for that token going forward, since the underlying reserve state never recovers.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
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

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
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
