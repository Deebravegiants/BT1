## Analysis

The reported bug class — an external price-oracle call without a try/catch that can DoS a critical function — maps onto alt.fun's dependency on the external BounceTech LT's `exchangeRate()`. Unlike Chainlink's `latestRoundData`, alt.fun's "oracle" is `IBounceLeveragedToken.exchangeRate()`, called live and unprotected in both the buy and sell paths.

`Bonding.canGraduate` reads `exchangeRate()` on essentially every call while a token is pre-graduation (whenever `IPair(pair).tokenBalance() != 0`): [1](#0-0) 

`Zap._sellInternal` calls `bonding_.canGraduate(tokenAddress)` unconditionally at the top of every sell, and separately calls `IBounceLeveragedToken(lt).exchangeRate()` again to compute `grossUsdcEstimate`: [2](#0-1) 

`Zap._executeBuy` also depends on `Bonding.previewLtUntilGraduation`, which likewise reads `exchangeRate()`: [3](#0-2) 

Crucially, pre-graduation the `Pair` is only reachable through `Router`, gated by `BONDING_ROLE`, so `Zap.buy`/`Zap.sell` are the only paths an ordinary holder can use to convert `Token` ↔ LT ↔ USDC. There is no unprivileged bypass. The codebase's own comments explicitly acknowledge and accept that a paused `mint()` DoSes buys while leaving sells functional via `redeem()`: [4](#0-3) 

But that accepted tradeoff assumes `exchangeRate()` itself never reverts. None of the four `exchangeRate()`/`ltToBaseAmount`/`baseToLtAmount` call sites in `Bonding.canGraduate`, `Bonding.previewLtUntilGraduation`, or `Zap._executeBuy`/`_sellInternal` are wrapped in try/catch, so a revert on that single external view call breaks **both** buy and sell simultaneously — a strictly worse outcome than the documented mint-pause tradeoff, and one the team's own design note ("holders can always exit via redeem") does not anticipate for the pre-graduation `Zap`-only path.

### Title
Unprotected external `IBounceLeveragedToken.exchangeRate()` call in `Bonding.canGraduate`/`previewLtUntilGraduation` and `Zap` can freeze both buy and sell for a curve-stage token - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Zap.sol`)

### Summary
Every `Zap.buy` and `Zap.sell` on a pre-graduation token unconditionally calls the external BounceTech LT's `exchangeRate()` (directly, or transitively via `Bonding.canGraduate`/`previewLtUntilGraduation`), with no try/catch. If that single external view reverts — e.g. BounceTech pauses/deprecates the LT's price accessor, or the LT enters an error state — both trading directions revert, because the internal curve `Pair` is only reachable through `Router` under `BONDING_ROLE`, leaving `Zap` as the sole unprivileged entry point.

### Finding Description
`Bonding.canGraduate` is invoked at the start of `Zap._sellInternal` for every sell attempt while the pair still holds real token balance (the common case), and it calls `IBounceLeveragedToken(info.ltAddress).exchangeRate()` unconditionally: [5](#0-4) 

`Zap._sellInternal` then independently calls `exchangeRate()` a second time to size the sell-floor guard: [6](#0-5) 

On the buy side, `Zap._executeBuy` calls `Bonding.previewLtUntilGraduation`, which also reads `exchangeRate()` unconditionally when the token is on-curve: [3](#0-2) [7](#0-6) 

None of these four sites wrap the external call in try/catch. Since a curve-stage `Token`/LT pair is exposed only via `Router`, gated by `BONDING_ROLE` (only `Bonding` holds it), an ordinary trader has no way to reach `Pair.swap` or the LT's `redeem()` except through `Zap`. If BounceTech's `exchangeRate()` reverts persistently for a given LT, both `Zap.buy` and `Zap.sell` for every token paired to that LT revert on every call, with no fallback.

### Impact Explanation
This is a stronger DoS than the one the codebase already documents and accepts (mint-pause blocking only buys while sells remain live via `redeem()`). Here, both sides freeze simultaneously, and — unlike the documented case — the protocol's stated invariant that "holders can always exit via redeem" does not hold for pre-graduation tokens, since holders hold `Token`, not LT, and the only path to convert `Token → LT → USDC` is `Zap.sell`, which itself depends on the same unprotected `exchangeRate()` call. Curve-stage traders' and creators' funds (locked in `Token`) become inaccessible for as long as the external call reverts, which can constitute permanent freezing if the LT is deprecated or its rate accessor is disabled indefinitely.

### Likelihood Explanation
`exchangeRate()` is an external call into a third-party contract (BounceTech LT) outside alt.fun's control, invoked on every single buy and sell for every curve-stage token. Any BounceTech-side pause, upgrade, deprecation, or bug affecting this view is sufficient to trigger the condition — no attacker action or privileged alt.fun action is required, matching the "unrelated wallet reachable" criterion (any trader's `Zap.buy`/`Zap.sell` call is affected the moment the external call starts reverting).

### Recommendation
Wrap the `exchangeRate()` (and related `baseToLtAmount`/`ltToBaseAmount`) calls in `Bonding.canGraduate`, `Bonding.previewLtUntilGraduation`, and `Zap._executeBuy`/`_sellInternal` in try/catch, with a defensive fallback (e.g., treat the USD graduation leg as unavailable and fall back to the supply-only trigger, or allow a direct-redeem path in `Zap` that does not depend on the graduation-check leg) so a single external oracle-style revert cannot simultaneously disable both buy and sell for a token.

### Proof of Concept
1. A token is launched and trading on-curve, paired to LT `L`.
2. BounceTech pauses/breaks `L.exchangeRate()` (reverts on every call) — an event outside alt.fun's control.
3. Any trader calls `Zap.sell(token, amount, 0)`: `_sellInternal` calls `bonding_.canGraduate(token)`, which calls `IBounceLeveragedToken(L).exchangeRate()` and reverts; the whole sell reverts.
4. Any trader calls `Zap.buy(token, usdcAmount, 0, ref)`: `_executeBuy` calls `bonding_.previewLtUntilGraduation(token)`, which calls `exchangeRate()` and reverts; the whole buy reverts.
5. With `Pair` reachable only via `Router`'s `BONDING_ROLE`, no unprivileged address has any alternative path to exit `Token` for USDC — funds are frozen for the duration of the external outage.

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

**File:** packages/contracts/src/Bonding.sol (L705-726)
```text
    function previewLtUntilGraduation(
        address token_
    ) external view returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return 0;
        if (info.lifecycle != Lifecycle.Curve) return 0;

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

**File:** packages/contracts/src/Zap.sol (L304-314)
```text
        // BounceTech LTs are mint-pausable (but NOT redeem-pausable). When
        // the LT operator pauses minting, this call reverts, so every buy
        // through Zap — bonding curve and post-graduation alike — DoSes for
        // that token while sells keep working (sells go through `redeem`,
        // not `mint`). This is an accepted v1 tradeoff: a sell-only market
        // is preferable to freezing both sides, since holders can still
        // exit to USDC. Post-graduation, anyone holding LT directly can
        // also still buy by swapping on the HyperSwap TOKEN/LT pair,
        // bypassing Zap. We do not mirror BounceTech's pause flag in
        // `Zap` (it would couple our pausing surface to theirs and add
        // storage with no security gain).
```

**File:** packages/contracts/src/Zap.sol (L323-325)
```text
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);
```

**File:** packages/contracts/src/Zap.sol (L430-445)
```text
        if (bonding_.canGraduate(tokenAddress)) {
            if (minUsdcOut != 0) revert TokenIsGraduating();
            bonding_.triggerGraduation(tokenAddress);
            return 0;
        }

        address lt = bonding_.ltOf(tokenAddress);

        IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), tokenAmount);

        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
```
