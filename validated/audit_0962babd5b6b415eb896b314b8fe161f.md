### Title
Unchecked zero `exchangeRate()` in `Zap._executeBuy`'s `baseToLtAmount`/`ltToBaseAmount` calls permanently DoSes curve buys and traps curve funds - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._executeBuy` calls the external LT's `baseToLtAmount`/`ltToBaseAmount` on every curve (pre-graduation) buy without ever checking that `exchangeRate()` is non-zero, unlike other call sites in the codebase that explicitly guard against this exact value. If the LT's `exchangeRate()` ever reads `0` (a value the contracts elsewhere treat as a real, reachable state for this external rebasing-priced asset), every curve buy for that token reverts on division-by-zero inside the LT, and — because the sell path's exit is gated by a USD-floor check that also degenerates to `0` at that rate — both buy and sell become permanently blocked, stranding the token in `Lifecycle.Curve` with its curve-raised LT and tokens locked forever.

### Finding Description
`Bonding._deployAndSeed` explicitly guards against a zero exchange rate: [1](#0-0) 

and `Bonding.previewLtUntilGraduation` likewise guards its own division by exchange rate: [2](#0-1) 

Both show the protocol's own code recognizes `exchangeRate() == 0` as a real, reachable state for a BounceTech LT (a live, externally-priced leveraged token, per `IBounceLeveragedToken`), and that any *division* by it must be checked.

However, `Zap._executeBuy` — the only entry point that drives every pre-graduation curve buy — never applies that guard before calling the LT's `baseToLtAmount`, which internally divides by `exchangeRate()` (see the mock's implementation, mirroring the real BounceTech LT's division-based formula): [3](#0-2) [4](#0-3) 

If `exchangeRate()` returns `0` at the moment a user calls `Zap.buy` / `Zap.buyWithPermit` on a still-curve (non-graduated) token, `baseToLtAmount(netUsdc)` reverts on division by zero, and the entire buy call reverts. This is the same bug class as CVE-2018-7731: a value read from an external/untrusted source (`exchangeRate()` in this contract, the WEBP bitstream in Exempi) is dereferenced/divided without a `!= 0` check, and the missing check turns into an unconditional crash on that code path.

The resulting freeze is durable, not transient:
- `Bonding.canGraduate`'s USD leg multiplies by `exchangeRate()` (line 693), so at `exchangeRate() == 0` it always evaluates to `0`, and the USD trigger can never fire.
- The supply trigger (`IPair(pair).tokenBalance() == 0`) can only be satisfied by more curve buys draining the pair — but curve buys are exactly what's reverting.
- `Zap._sellInternal`'s exit path computes `grossUsdcEstimate = ltReceived * exchangeRate() / 1e18` (line 444); at rate `0` this is always `0`, so `grossUsdcEstimate / 1e12 < minUsdcAmount()` reverts `BelowMinAmount` for essentially any sell size, blocking exits too.

With both the buy path (hard revert) and sell path (floor check that can never be satisfied at rate `0`) blocked, and graduation unreachable via either trigger, the token's curve-held tokens, the trader-held tokens, and the curve's raised LT reserve are permanently stranded — no unprivileged caller (trader, creator, or otherwise) can move the state forward.

### Impact Explanation
This is a permanent freeze of trader and creator funds: all tokens still on the curve (unsold curve supply plus the real LT the curve has raised, sitting in `Pair`) become permanently untradeable and ungraduatable the moment the paired LT's `exchangeRate()` reads `0`. Impact is medium-severity because it depends on a specific external-price condition (rate collapsing to zero) that is outside the protocol's control but explicitly anticipated elsewhere in its own code (`ZeroExchangeRate`, the `previewLtUntilGraduation` guard) — showing the developers already know this state is reachable, just not that it's unguarded on this particular path.

### Likelihood Explanation
BounceTech leveraged tokens are volatile, rebasing-priced instruments whose `exchangeRate()` can in principle decay toward zero under adverse underlying price moves or liquidation of the leverage position — the same class of "external rebasing-priced LT" the codebase's own comments flag repeatedly as a live risk surface (`_deployAndSeed`, `canGraduate`, `previewLtUntilGraduation`). Any curve token paired with an LT that reaches (or is manipulated/degrades to) `exchangeRate() == 0` hits this path with a single ordinary `Zap.buy` call from any unprivileged trader — no special permissions or crafted inputs are required, only the pre-existing external state.

### Recommendation
Add an explicit `exchangeRate() != 0` (or equivalent) guard in `Zap._executeBuy` before calling `baseToLtAmount`/`ltToBaseAmount` on the curve path, mirroring the guard already used in `Bonding.previewLtUntilGraduation` and `Bonding._deployAndSeed`. On a zero rate, either revert with a clear, catchable error (so the UI/keeper can react) or route the token straight into `triggerGraduation`/an emergency-exit path instead of leaving it silently unreachable. Consider also hardening `Bonding.canGraduate`'s supply-trigger reachability so a token cannot become permanently stuck in `Lifecycle.Curve` purely because its priced-in reserve asset's rate collapsed to zero.

### Proof of Concept
1. Launch a token via `Zap.createToken` paired with an LT whose `exchangeRate()` is currently non-zero; the seed buy succeeds and the token sits in `Lifecycle.Curve`.
2. The LT's `exchangeRate()` subsequently degrades to `0` (adverse underlying move / liquidation, external to `alt.fun`).
3. Any unprivileged trader calls `Zap.buy(tokenAddress, usdcAmount, minTokensOut, referrer)`. Inside `Zap._executeBuy`, `IBounceLeveragedToken(lt).baseToLtAmount(netUsdc)` (`Zap.sol:324`) divides by `exchangeRate()` and reverts on division-by-zero — the buy fails.
4. A trader holding curve tokens calls `Zap.sell`; `grossUsdcEstimate = ltReceived * exchangeRate() / 1e18` evaluates to `0` (`Zap.sol:444`), so `grossUsdcEstimate / 1e12 < minUsdcAmount()` reverts `BelowMinAmount` — the sell fails too.
5. `Bonding.triggerGraduation` requires `canGraduate(tokenAddress)`, whose USD leg is `realLtRaised * exchangeRate() / 1e18` (`Bonding.sol:693`), which is `0` at this rate, and the supply leg can never be reached because buys revert — graduation is unreachable.
6. The token is now permanently stuck in `Lifecycle.Curve` with all curve-side tokens and the raised LT reserve frozen, with no unprivileged caller able to unstick it.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-478)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
```

**File:** packages/contracts/src/Bonding.sol (L720-726)
```text
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Zap.sol (L323-340)
```text
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);

            if (ltUntilGraduation >= ltIfFull) {
                baseToConvert = netUsdc;
            } else {
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

**File:** packages/contracts/test/mocks/MockLeveragedToken.sol (L67-77)
```text
    function baseToLtAmount(
        uint256 baseAmount
    ) public view returns (uint256) {
        return (baseAmount * 1e18) / _exchangeRate;
    }

    function ltToBaseAmount(
        uint256 ltAmount
    ) public view returns (uint256) {
        return (ltAmount * _exchangeRate) / 1e18;
    }
```
