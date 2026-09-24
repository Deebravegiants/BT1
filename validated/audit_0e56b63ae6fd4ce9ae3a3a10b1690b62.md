Given the report's bug class — code proceeding to *use* an external return value without validating it is non-degenerate, causing DoS — the closest reachable analog in alt.fun's contracts is in `Bonding.canGraduate` / `Bonding.previewLtUntilGraduation`, which consume `IBounceLeveragedToken.exchangeRate()` without the sanity check the code enforces everywhere else that value is used at launch time.

### Title
Unvalidated `exchangeRate()` return value in `canGraduate` permanently disables the USD graduation trigger - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._deployAndSeed` explicitly guards against a degenerate `exchangeRate()` return (`0`) from the BounceTech LT before using it to size the curve's virtual LT reserve [1](#0-0) . `canGraduate` and `previewLtUntilGraduation`, however, consume the *same* external call later in the token's life without any equivalent validation of the returned value before using it in the USD-denominated graduation math [2](#0-1) .

### Finding Description
`canGraduate` computes the USD-trigger leg as:
```
uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
return valueUsd >= $.graduationThresholdUsd;
``` [3](#0-2) 

If `exchangeRate()` returns `0` — a state the BounceTech LT can legitimately reach (the protocol's own NatSpec elsewhere calls `ZeroExchangeRate` a real, checked-for condition at launch, see `error ZeroExchangeRate()` and its use in `_deployAndSeed`) [4](#0-3)  — `valueUsd` collapses to `0` regardless of how much real LT has been raised on the curve, and the USD leg of `canGraduate` can never return `true`. `previewLtUntilGraduation` has the same blind spot: it only special-cases `exchangeRate == 0` by disabling the USD leg (`ltUntilThreshold = type(uint256).max`), silently deferring entirely to the supply leg (`tokenBalance() == 0`) [5](#0-4) .

The supply-side trigger requires the pair's real token balance to hit exactly zero, which the code's own comments acknowledge is hard to land precisely — the cap-binding buy can miss by "1-2 wei of LT" and float-rounding leaves the last dust of curve supply unsellable via `Zap.buy`'s pre-sizing logic [6](#0-5) . With the USD leg permanently zeroed by a degenerate `exchangeRate()`, the token is left depending solely on this hard-to-hit exact-sellout condition to ever reach `Lifecycle.Graduating`.

### Impact Explanation
While `exchangeRate()` reads `0`, every LT unit raised on the curve is trapped: `triggerGraduation` reverts with `NotGraduatable` [7](#0-6) , and the automatic post-buy check in `_executeBuy` never flips the token into graduation [8](#0-7) . The curve-raised LT and the 250M/750M token split can never be handed to `finalizeGraduation`/`LPLock`, permanently freezing trader and creator funds on the curve for that token — a DoS with fund-freezing impact, matching the CVE's "proceeds without validating a return value... denial of service or possibly other unspecified impact" class.

### Likelihood Explanation
This requires the paired BounceTech LT to actually return `exchangeRate() == 0` (or a value low enough to make `valueUsd` round to a value permanently below `graduationThresholdUsd` even as `realLtRaised` grows unboundedly) at some point after a token has raised significant real LT but before it hits exact sellout. Given creators freely choose which BounceTech LT to pair a launch with, and leveraged tokens are inherently volatile/liquidatable instruments, this is a plausible, externally-triggerable state rather than a purely theoretical one.

### Recommendation
Mirror the `_deployAndSeed` guard in `canGraduate` and `previewLtUntilGraduation`: explicitly revert or otherwise fail closed (rather than silently returning `false`/deferring to the supply-only trigger) when `exchangeRate() == 0`, or add an owner-gated / permissionless escape hatch that lets a token graduate purely on real-LT-raised once it has cleared the threshold under a last-known-good rate, so a transient or terminal zero exchange rate cannot indefinitely brick graduation for tokens that have already raised sufficient value.

### Proof of Concept
1. Creator launches a token paired to a BounceTech LT via `Zap.createToken` → `Bonding.launch` (`exchangeRate()` is nonzero and passes the `_deployAndSeed` check at that time) [1](#0-0) .
2. Traders buy on the curve via `Zap.buy` → `Bonding.buy`, raising real LT reserve past what would normally satisfy `graduationThresholdUsd` at the LT's original rate, but the curve is not yet fully sold out (`IPair.tokenBalance() != 0`).
3. The underlying BounceTech LT's `exchangeRate()` subsequently reads `0` (e.g., following a liquidation/de-peg event in the leveraged position it tracks).
4. Any caller invokes `Bonding.triggerGraduation(tokenAddress)`; `canGraduate` computes `valueUsd = realLtRaised * 0 / 1e18 = 0 < graduationThresholdUsd`, so it reverts with `NotGraduatable` [7](#0-6) .
5. Since exact sellout is the only remaining path and is difficult to hit precisely, the token's curve-raised LT and reserved tokens remain stuck in `Lifecycle.Curve` indefinitely, with no path to `finalizeGraduation` and `LPLock`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L315-319)
```text
    error ZeroExchangeRate();
    /// @dev Launch-time `exchangeRate` so low the curve's LT reserve would
    ///      overflow the HyperSwap V2 pair's `uint112` reserve slot at
    ///      graduation, bricking `finalizeGraduation`.
    error ExchangeRateTooLow();
```

**File:** packages/contracts/src/Bonding.sol (L477-484)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
```

**File:** packages/contracts/src/Bonding.sol (L689-694)
```text
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L719-726)
```text
        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Bonding.sol (L929-932)
```text
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

**File:** packages/contracts/src/Zap.sol (L330-341)
```text
                // `ltToBaseAmount` floors. Bump up so `mint(baseToConvert)`
                // yields ≥ `ltUntilGraduation` and the cap-binding buy
                // actually flips `canGraduate` true — otherwise the
                // closing buy can miss graduation by 1-2 wei of LT.
                if (ltUntilGraduation > 0) {
                    baseToConvert = IBounceLeveragedToken(lt).ltToBaseAmount(ltUntilGraduation);
                    if (IBounceLeveragedToken(lt).baseToLtAmount(baseToConvert) < ltUntilGraduation) {
                        baseToConvert += 1;
                    }
                }
                if (baseToConvert > netUsdc) baseToConvert = netUsdc;

```
