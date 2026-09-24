Analog vulnerability found, mapped onto alt.fun's LT-price-dependent sell/graduation gate.

### Title
Curve sells are permanently blocked if `exchangeRate()` reverts, even for tokens far from the graduation threshold - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Zap.sol])

### Summary
`Bonding.sell` and `Zap._sellInternal` both unconditionally re-derive `canGraduate(tokenAddress)` on every curve sell, which internally calls `IBounceLeveragedToken(info.ltAddress).exchangeRate()` [1](#0-0) . This mirrors the reported Blueberry pattern exactly: a "risk" check that requires successful pricing is run on every exit path even when the position (here, a curve token holder with no debt/leverage) has no risk that actually requires that price read. If the LT's `exchangeRate()` transiently reverts, every curve seller is frozen out, with no way to withdraw/exit regardless of how far the token is from graduation.

### Finding Description
`Bonding.sell` gates every curve-side sale behind `canGraduate`: [2](#0-1) . `canGraduate` only skips the pricing read when `IPair(pair).tokenBalance() == 0` (full sellout); in every other case — including a token that just launched and is nowhere near the graduation threshold — it unconditionally calls `exchangeRate()` on the LT to value the raised reserve: [3](#0-2) .

`Zap._sellInternal` calls the same `canGraduate` gate a second time before even reaching the curve/redeem logic: [4](#0-3) . A third, independent `exchangeRate()` read happens afterward purely to size the pre-flight minimum-amount check on the sell proceeds: [5](#0-4) .

None of these three `exchangeRate()` reads are load-bearing for a plain curve sell that is far from the graduation threshold — the actual value transfer is `Router.sell` (constant-product AMM math using stored reserves, not `exchangeRate()`) followed by `IBounceLeveragedToken(lt).redeem(...)`, which is an entirely separate call that does not depend on `exchangeRate()` succeeding. Yet the seller cannot reach `redeem` at all if any of the upstream `exchangeRate()` reads revert, because both `Zap._sellInternal`'s `canGraduate` pre-check and `Bonding.sell`'s internal `canGraduate` re-check happen strictly before the curve swap and before `redeem` is ever invoked.

### Impact Explanation
Any transient failure of the LT's `exchangeRate()` — a pause, a bad price-source read, or any other revert condition on the reserve asset — permanently freezes every holder's ability to exit a `Lifecycle.Curve` token via `Zap.sell`/`Bonding.sell`, no matter how small their position or how far the token is from graduating. Because `Router.sell`'s AMM math and `IBounceLeveragedToken.redeem` do not themselves need `exchangeRate()` to succeed, this is an unnecessary coupling that traps trader funds precisely the way the reported Blueberry bug traps collateral: a risk/threshold check that gates withdrawal is evaluated even when it has no bearing on the actual operation being performed.

### Likelihood Explanation
Reachable by any unprivileged holder calling `Zap.sell`/`sellWithPermit` on a `Lifecycle.Curve` token — no privileged role or unusual setup required. The only precondition is that the LT's `exchangeRate()` view reverts or otherwise fails at call time (e.g., due to a pause or upstream failure on the leveraged-token side); once that happens, the freeze is total and immediate for every trader still on the curve for that token, and persists for as long as the LT's rate feed is unavailable.

### Recommendation
Short-circuit `canGraduate` (and the derived `Bonding.sell` gate) to skip the `exchangeRate()`-dependent USD leg whenever the realLtRaised amount is provably far below any plausible threshold, or restructure `Bonding.sell` so the `canGraduate` check is evaluated only after confirming the sell would otherwise succeed, wrapping the `exchangeRate()` read in a way that degrades to "not graduatable" rather than reverting the whole sell. At minimum, decouple the pre-flight `grossUsdcEstimate` sanity check in `Zap._sellInternal` (lines 444-445) from the critical path so a failed `exchangeRate()` read doesn't block `redeem`, mirroring the Blueberry fix of skipping the price-dependent risk computation when it isn't actually needed to protect the operation being performed.

### Proof of Concept
1. A token is launched via `Zap.createToken` and trades on the curve well below `graduationThresholdUsd` (`Lifecycle.Curve`, `canGraduate` normally false).
2. The paired BounceTech LT's `exchangeRate()` begins reverting (e.g., paused by BounceTech, or any transient failure on their price source) — this is an external state change, not caused by alt.fun.
3. Any holder calls `Zap.sell(tokenAddress, tokenAmount, minUsdcOut)`.
4. `Zap._sellInternal` calls `bonding_.canGraduate(tokenAddress)` (packages/contracts/src/Zap.sol:430), which calls `IBounceLeveragedToken(info.ltAddress).exchangeRate()` inside `Bonding.canGraduate` (packages/contracts/src/Bonding.sol:693) — this reverts.
5. The entire `sell` transaction reverts. The same happens for every other holder and for direct calls to `Bonding.sell`, since it re-runs `canGraduate` internally (packages/contracts/src/Bonding.sol:598).
6. No holder can exit their curve position via the intended interface until the LT's `exchangeRate()` recovers, even though the actual sell (AMM math + `redeem`) never needed that value.

### Citations

**File:** packages/contracts/src/Bonding.sol (L591-601)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L680-694)
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
```

**File:** packages/contracts/src/Zap.sol (L424-434)
```text
        // LT appreciation can push a curve token past the graduation threshold
        // with no buy. Selling now would drag the raised reserve back below it,
        // so graduate the token instead. The holder keeps their tokens and
        // exits on the graduated pool. Nothing is sold, so this fills `0` — only
        // take it when the caller set no floor; a positive `minUsdcOut` reverts
        // so the `usdcOut >= minUsdcOut` guarantee is never silently broken.
        if (bonding_.canGraduate(tokenAddress)) {
            if (minUsdcOut != 0) revert TokenIsGraduating();
            bonding_.triggerGraduation(tokenAddress);
            return 0;
        }
```

**File:** packages/contracts/src/Zap.sol (L444-445)
```text
        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
```
