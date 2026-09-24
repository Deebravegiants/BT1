## Analysis

I've confirmed a strong analog. `canGraduate()` unconditionally calls `IBounceLeveragedToken(info.ltAddress).exchangeRate()` whenever the pair still has real token balance [1](#0-0) . There is no try/catch or fallback around this external call. `canGraduate()` is reached from **both** trade directions with no way to bypass it:

- Every curve buy calls it inline at the end of `Bonding._executeBuy` — `if (canGraduate(tokenAddress)) { _enterGraduating(tokenAddress); }` [2](#0-1) .
- Every curve sell calls it unconditionally at the top of `Zap._sellInternal` before any tokens are pulled: `if (bonding_.canGraduate(tokenAddress)) { ... }` [3](#0-2) .
- `Bonding.sell` itself also calls `canGraduate(tokenAddress)` directly as a guard [4](#0-3) .

If `exchangeRate()` on the paired BounceTech LT reverts (offline/paused pricing state, analogous to the Chainlink-offline scenario in the report), `canGraduate()` bubbles the revert, and **both `Zap.buy` and `Zap.sell` revert for every pre-graduation token on that LT** — unlike the already-documented, accepted mint-pause tradeoff where sells still work via `redeem`. This is a stronger, non-accepted freeze: it blocks exits (sell) as well as entries (buy), with no fallback path, exactly mirroring the reported bug class (unprotected price-read revert freezing a critical state-changing/exit function).

### Title
Unguarded `exchangeRate()` call in `canGraduate` freezes both buy and sell when the paired LT reverts - (File: packages/contracts/src/Bonding.sol)

### Summary
`canGraduate()` reads `IBounceLeveragedToken(info.ltAddress).exchangeRate()` with no try/catch, and this view is invoked unconditionally on every curve buy and sell path (`Bonding._executeBuy`, `Bonding.sell`, `Zap._sellInternal`). A revert from the external LT's `exchangeRate()` — e.g., the LT contract pausing or entering an error state that reverts its price view, the on-chain analog of an oracle going offline — propagates up and reverts the entire trade, freezing all trading (not just buys) for that token.

### Finding Description
`canGraduate` is a `public view` used as a gate inside the hot trading path:
- Buys: `Bonding._executeBuy` calls `canGraduate(tokenAddress)` at the end of every curve buy [2](#0-1) .
- Sells: `Bonding.sell` calls `canGraduate(tokenAddress)` as a pre-check that reverts with `TokenIsGraduating` if true [5](#0-4) , and `Zap._sellInternal` separately calls `bonding_.canGraduate(tokenAddress)` before pulling the seller's tokens [6](#0-5) .

Inside `canGraduate`, once `IPair(pair).tokenBalance() != 0` (curve not yet exhausted — the common case for most of a token's life), the function unconditionally calls the external LT's `exchangeRate()`:
```solidity
address pair = info.pair;
if (IPair(pair).tokenBalance() == 0) return true;

(, uint256 assetReserve) = IPair(pair).getReserves();
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
return valueUsd >= $.graduationThresholdUsd;
``` [7](#0-6) 

There is no try/catch, no cached/stale fallback price, and no bypass. If `exchangeRate()` reverts for any reason on the BounceTech LT side (paused pricing, a stuck checkpoint, an internal computation failure — the functional equivalent of "the oracle goes offline"), `canGraduate` reverts, which reverts every caller: `Bonding.buy`, `Bonding.sell`, and by extension `Zap.buy`/`Zap.sell` for that token.

This differs from the project's own accepted tradeoff around mint-pausable LTs. The docs explicitly note that when `mint` is paused, only buys are blocked and sells still succeed because they go through `redeem`, not `mint`, so "holders can still exit to USDC" [8](#0-7) . That exit-preserving guarantee is broken by the `exchangeRate()` dependency in `canGraduate`, because `Zap.sell`'s very first check on every graduatable-eligible curve token calls `canGraduate` before `redeem` is ever reached — so a reverting `exchangeRate()` blocks sells too, with no accepted fallback documented anywhere for this specific call site.

### Impact Explanation
While the curve for a token is un-graduated and the paired LT's `exchangeRate()` reverts, all buy and sell activity for that token is frozen. Traders cannot exit their curve positions, and the creator/protocol cannot generate fee revenue on it. This is a full, protocol-level DoS on a token's entire trading lifecycle (not merely a degraded-quality read), with no admin lever, fallback price, or unaffected exit path — a direct parallel to the cited report's "liquidations frozen when oracle goes offline," here manifesting as "buys and sells frozen when the reserve-asset's price view goes offline."

### Likelihood Explanation
Likelihood is low, matching the "Impact high, likelihood low → Medium" framing of the original report: the LT is an external, trusted BounceTech contract, and its `exchangeRate()` is expected to normally succeed. However, BounceTech's own automation, pausability, or an implementation bug in its price-settlement path (streaming fee checkpoint, leverage rebalance) could cause a transient or persistent revert, and the protocol has no defenses against this specific failure mode despite explicitly designing around the analogous mint-pause case.

### Recommendation
Wrap the `exchangeRate()` call inside `canGraduate` (and the equivalent call in `previewLtUntilGraduation`) in a try/catch. On failure, fall back to treating the USD-graduation leg as not yet met (return `false`/skip that leg) rather than reverting the whole call, so the supply-based graduation trigger and — critically — ordinary buys/sells can proceed uninterrupted even while the LT's price view is unavailable. This mirrors the existing philosophy of preferring degraded (sell-only or buy-only) availability over full freezing that the codebase already applies to the mint-pause case.

### Proof of Concept
1. Launch a token and buy partway toward the graduation threshold so `IPair(pair).tokenBalance() != 0` (curve not yet exhausted) — this is the normal state for most of a token's trading life.
2. Cause (or simulate, e.g., via `vm.mockCallRevert` against the paired LT's `exchangeRate()` selector) the LT's `exchangeRate()` to revert.
3. Call `zap.buy(tokenAddress, usdcAmount, 0, address(0))` — the call reverts because `_executeBuy` → `canGraduate` → `exchangeRate()` reverts.
4. Call `zap.sell(tokenAddress, tokenAmount, 0)` — the call also reverts, because `_sellInternal`'s unconditional `bonding_.canGraduate(tokenAddress)` check reverts before the seller's tokens are even pulled, or `Bonding.sell`'s own `canGraduate` guard reverts.
5. Both entry and exit for the token are frozen for as long as the external LT's `exchangeRate()` keeps reverting, with no way for any unprivileged caller to route around it.

### Citations

**File:** packages/contracts/src/Bonding.sol (L583-599)
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

**File:** packages/contracts/src/Zap.sol (L412-434)
```text
    function _sellInternal(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut
    ) internal returns (uint256 usdcOut) {
        if (tokenAmount == 0) revert InvalidInput();
        if (tokenAddress == address(0)) revert InvalidInput();
        ZapStorage storage $ = _s();
        Bonding bonding_ = $.bonding;
        if (bonding_.creatorOf(tokenAddress) == address(0)) revert TokenNotTrading();
        if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();

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
