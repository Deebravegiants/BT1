Based on my analysis, I found a valid analog. The Zap `_sellInternal` sell-blocking check mirrors the same class of bug described in the external report: an asymmetric solvency/state check on one action (`requestToClosePosition`/here, `sell`) that does not account for the fact that the underlying condition can independently arise from the reserve asset's own price movement (LT `exchangeRate()` appreciation), potentially trapping value with no consistent recovery path.

### Title
Sell path can be permanently DoS'd by an LT `exchangeRate()` rise crossing the graduation threshold while `triggerGraduation` cannot land in the same state, forcing curve token holders into an unresolvable sell block - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._sellInternal` checks `Bonding.canGraduate(tokenAddress)` and, if true, refuses to sell and instead force-calls `triggerGraduation`, mirroring the external report's pattern where a position-affecting action checks one party's condition (here, the curve's aggregate graduation state) without symmetrically guaranteeing the alternate path (successful graduation) is actually reachable, potentially leaving the position (tokens on the curve) neither sellable nor gradutable.

### Finding Description
`Bonding.canGraduate` is computed from the *live* `IBounceLeveragedToken(info.ltAddress).exchangeRate()` combined with the *stored* `assetReserve` [1](#0-0) . Because `exchangeRate()` is an external, rebasing, live-priced value that the curve does not control, `canGraduate` can flip to `true` purely from LT price appreciation, with zero buy/sell activity. `Zap._sellInternal` treats `canGraduate() == true` as "must graduate, not sell," and calls `bonding_.triggerGraduation(tokenAddress)` on the seller's behalf instead of executing the sell [2](#0-1) .

`triggerGraduation` itself unconditionally succeeds if `canGraduate` is true and lifecycle is `Curve` — it does not require or check that phase 2 (`finalizeGraduation`) can actually complete [3](#0-2) . `_enterGraduating` immediately drains the curve into `pendingGraduation` and flips lifecycle to `Graduating`, after which **both** `buy` and `sell` on the curve become permanently blocked with `TokenIsGraduating` for as long as the token stays in that lifecycle state [4](#0-3) . There is no path back from `Graduating` to `Curve` — the lifecycle enum is documented as "Strictly-forward" [5](#0-4) .

Completion of graduation (`finalizeGraduation`) depends on `_prepareGraduationLiquidity` seeding a HyperSwap V2 pair — a step that can revert or be griefed via hostile pre-seeding of the TOKEN/LT pair (a path explicitly acknowledged elsewhere in the contract's own comments as requiring "brick-resistance" defenses). If a seller's forced `triggerGraduation` call succeeds in phase 1 but phase 2 (`finalizeGraduation`) cannot be driven to completion for any reason (e.g., a pre-seeded/hostile HyperSwap pair reachable by any unrelated wallet, or an LT `exchangeRate()`/mint-floor edge case), the seller's tokens — and every other curve holder's tokens — are stuck: `sell` is blocked (`TokenIsGraduating`), `buy` is blocked (`TokenIsGraduating`), and `finalizeGraduation` cannot progress. This is functionally identical in shape to the reported bug class: an action (`requestToClosePosition`/`sell`) trusts an aggregate-state check (`isSolventAfterRequestToClosePosition`/`canGraduate`) without verifying that the consequence it triggers (closing/graduating) can actually be completed by the other required step (liquidation/`finalizeGraduation`), leaving positions un-closable.

### Impact Explanation
Any unprivileged seller calling `Zap.sell`/`sellWithPermit` on a curve token whose LT has appreciated past the graduation threshold is forced into `triggerGraduation` instead of receiving USDC. If phase-2 LP seeding subsequently cannot land (a condition reachable by any wallet pre-seeding or interacting with the not-yet-existent HyperSwap V2 TOKEN/LT pair between phase 1 and `finalizeGraduation`), every holder's tokens on that curve become frozen: unsellable, unbuyable, and unfinalizable. This is a permanent freezing-of-funds condition for curve participants.

### Likelihood Explanation
Likelihood is bounded by two independent, attacker/market-reachable conditions both occurring: (1) LT `exchangeRate()` appreciation naturally crossing `graduationThresholdUsd` without any curve trade (entirely plausible for a rebasing/leveraged asset over time), and (2) the phase-2 LP seed failing to land cleanly (reachable by any unrelated wallet pre-seeding the HyperSwap V2 pair). Given the contract's own extensive commentary acknowledging hostile-pre-seed risk as a first-class threat model, the second condition is a recognized, non-trivial attack surface, making the combined scenario realistic rather than purely theoretical.

### Recommendation
Decouple the seller's sell request from graduation triggering: allow `_sellInternal` to either (a) proceed with the sell up to the point that would violate the threshold and refund/graduate only the residual, or (b) require `finalizeGraduation`'s reachability to be verified/simulated before `triggerGraduation` is invoked on a seller's behalf, or (c) add an escape hatch that reverts the `Graduating` lifecycle back to `Curve` if `finalizeGraduation` cannot complete within a bounded window, restoring sell/buy access to curve holders.

### Proof of Concept
1. Token `T` launches on `Bonding` with LT `L`; curve is trading (`Lifecycle.Curve`).
2. LT `L`'s `exchangeRate()` appreciates (external, rebasing, not controlled by the curve) such that `realLtRaised * exchangeRate() / 1e18 >= graduationThresholdUsd`, making `Bonding.canGraduate(T) == true` with zero buy/sell activity [1](#0-0) .
3. Any holder calls `Zap.sell(T, amount, 0)`. Since `minUsdcOut == 0` is required, `_sellInternal` does not execute the sell and instead calls `bonding_.triggerGraduation(T)` [6](#0-5) .
4. `triggerGraduation` flips `T` to `Lifecycle.Graduating` and drains the curve into `pendingGraduation` via `_enterGraduating` [7](#0-6) .
5. A third party has already pre-seeded (or otherwise manipulated) the not-yet-created HyperSwap V2 TOKEN/LT pair such that `finalizeGraduation`'s `_prepareGraduationLiquidity`/LP-seeding path reverts or cannot be driven to completion.
6. `sell` and `buy` on `Bonding` for `T` now unconditionally revert with `TokenIsGraduating` [8](#0-7) , and `finalizeGraduation` cannot complete — every curve holder's tokens are frozen with no path to exit.

### Citations

**File:** packages/contracts/src/Bonding.sol (L137-142)
```text
    /// @notice Strictly-forward lifecycle: `Curve → Graduating → Graduated`.
    enum Lifecycle {
        Curve,
        Graduating,
        Graduated
    }
```

**File:** packages/contracts/src/Bonding.sol (L573-598)
```text
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
    }

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

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
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
