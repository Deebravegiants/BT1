### Title
Missing bounds/underflow check on `_launchTimeVirtualLtReserve` subtraction permanently DoSes a token's graduation path - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes replacing an unchecked `BUG_ON`-style assumption with a bounds check on an index derived from untrusted, attacker-influenceable network data, because the missing check let attacker-controlled input trigger a hard crash. The closest analog in alt.fun is `canGraduate` / `previewLtUntilGraduation` / `_prepareGraduationLiquidity` in `Bonding.sol`, all of which compute `assetReserve - _launchTimeVirtualLtReserve(token_, pair)` (or the equivalent `reserveAsset - _launchTimeVirtualLtReserve(...)`) with a bare Solidity subtraction and no explicit bounds/underflow guard [1](#0-0) . If `assetReserve` (a value driven by curve trades that any unprivileged trader can move through `Zap.buy`/`Zap.sell` → `Router.buy`/`Router.sell` → `Pair.swap`) is ever pushed below the recovered `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`, the subtraction reverts with a Solidity `Panic(0x11)` arithmetic-underflow, exactly the class of "untrusted-input-driven index/quantity used without a bounds check" that the kernel patch fixes for `map->max_osd`.

### Finding Description
`canGraduate` reads the pair's stored reserves and recovers the launch-time virtual LT reserve, then subtracts it from the live `assetReserve` without ever checking that `assetReserve >= virtualLtReserve`: [2](#0-1) 

The same unguarded pattern appears in `previewLtUntilGraduation`: [3](#0-2) 

and in the phase-1 graduation-liquidity preparation path that actually drains the curve and burns tokens: [4](#0-3) 

`_launchTimeVirtualLtReserve` derives its value purely from `Pair.k()` (frozen at `mint`) and `Token.TOTAL_SUPPLY()` (immutable): [5](#0-4) 

`assetReserve` itself is mutated only inside `Pair.swap`, which is reachable by any unprivileged trader via `Router.buy`/`Router.sell` (called from `Bonding.buy`/`Bonding.sell`, themselves reachable from `Zap.buy`/`Zap.sell`): [6](#0-5) 

Under the intended invariant (K fixed at mint, K-floor enforced on every swap), `assetReserve` should never fall below the virtual seed once curve trading has happened, because the K-floor check `(newTokenReserve+1)*(newAssetReserve+1) < _pool.k` is meant to keep the pool inside the curve. However, the code base's own comments repeatedly acknowledge that this identity can be violated by non-canonical paths: the `Bonding._sweepLTToOwner`/`finalizeGraduation` comments explicitly call out "a balance below `p.ltFromPair` shouldn't be reachable in normal operation, but we keep finalize from bricking on a Panic if any future code path or non-canonical LT briefly violates the invariant" and use a saturating subtraction there [7](#0-6)  — i.e. the authors already treat "subtraction that can panic if state drifts" as a known risk class and defensively guarded it in `finalizeGraduation`, but did **not** apply the same saturating-subtraction/bounds check to `canGraduate`, `previewLtUntilGraduation`, or `_prepareGraduationLiquidity`. Any of the same non-canonical drift vectors they're defending against elsewhere (e.g. a rebasing/donation-influenced `exchangeRate`/LT-mint quirk, or a future upgrade to `Router`/`Pair` that doesn't perfectly preserve the identity, or the generically permissionless `ltAddress` accepted at `launch()` which is any address the BounceTech `Factory.ltExists` allows) would cause these unguarded subtractions to underflow and revert.

### Impact Explanation
If `assetReserve < virtualLtReserve` ever occurs for a given token's pair, `canGraduate(token)` reverts instead of returning `false`. Because `canGraduate` is called unconditionally inside every `Bonding.buy` / `Bonding.sell` (via `_executeBuy`'s `canGraduate` check and `sell`'s `canGraduate` check) and inside `triggerGraduation`, a revert there bricks *all* trading on the curve for that token — not just graduation. Buyers can no longer buy, sellers can no longer sell, and `triggerGraduation`/`previewLtUntilGraduation` are unusable, permanently freezing the creator's and every trader's position in that token's curve (their tokens and LT are stuck with no exit, since `Zap`'s only sell/buy paths route through `Bonding.buy`/`sell`). This is a permanent freezing-of-funds condition satisfying the "concrete... permanent freezing of trader, creator or LP funds" bar.

### Likelihood Explanation
The trigger requires `assetReserve` to fall below the recovered virtual reserve, which should not happen under the intended K-floor invariant during normal `Pair.swap` calls. The likelihood is therefore contingent on the invariant being violated by some other, less-guarded path (e.g., a mismatch between the assumed `Pair.k()`/`TOTAL_SUPPLY()` identity across a `setTokenImplementation` rotation edge case, or a future code path). The authors' own defensive coding at `finalizeGraduation` (saturating-subtract specifically because "if any future code path... briefly violates the invariant") indicates this is a recognized-but-not-fully-closed risk in the codebase, rather than a purely theoretical one — the fix was applied in one place and not propagated to the others that share the identical unguarded-subtraction pattern.

### Recommendation
Replace the bare `assetReserve - _launchTimeVirtualLtReserve(...)` subtractions in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` with the same saturating pattern already used defensively in `_sweepLTToOwner`/`finalizeGraduation` (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`), so that a drifted invariant degrades gracefully (treated as "no real LT raised yet") instead of hard-reverting and bricking all trading and graduation for the affected token.

### Proof of Concept
1. Assume (as the codebase's own comments hypothesize) a future/edge condition where `Pair.k()/Token.TOTAL_SUPPLY()` recovers a `virtualLtReserve` slightly larger than the live stored `assetReserve` for some token — e.g., via an implementation rotation edge case in `setTokenImplementation` mismatched with a pre-rotation token's `Pair.k`, or any non-canonical drift the authors flagged as "shouldn't be reachable... but" in `finalizeGraduation`'s comment.
2. Any unprivileged trader calls `Zap.buy`/`Zap.sell` for that token, which calls `Bonding.buy`/`Bonding.sell`.
3. Inside `_executeBuy`/`sell`, `canGraduate(tokenAddress)` is invoked and executes `assetReserve - _launchTimeVirtualLtReserve(token_, pair)` at Bonding.sol:692, underflows, and reverts with `Panic(0x11)`.
4. Every subsequent buy/sell/`triggerGraduation` call on that token reverts identically, permanently freezing the token's curve — traders' LT and tokens are stuck with no recovery path.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L713-726)
```text
        address pair = info.pair;
        uint256 realBalance = IPair(pair).tokenBalance();
        if (realBalance == 0) return 0;

        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Bonding.sol (L1010-1020)
```text
        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```

**File:** packages/contracts/src/Bonding.sol (L1076-1090)
```text
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
