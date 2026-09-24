### Title
Unguarded `IBounceLeveragedToken.exchangeRate()` calls with no try/catch or fallback permanently freeze buy/sell/graduation for a curve token if the LT reverts - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Zap.sol`)

### Summary
Every trade and graduation check for a still-curve-stage token depends on a live, unguarded call to the external LT's `exchangeRate()` (or the `baseToLtAmount`/`ltToBaseAmount` wrappers around it). None of these call sites use try/catch or have a fallback price source. If the LT's `exchangeRate()` ever reverts for any reason — a bug in BounceTech's own rate math, an access-control/circuit-breaker flip, a paused state that also blocks the view, or any other failure mode outside alt.fun's control — every buy, every sell, and the graduation check for that token become permanently un-callable while the token still has curve supply remaining.

### Finding Description
`Bonding.canGraduate` reads `IBounceLeveragedToken(info.ltAddress).exchangeRate()` directly whenever the pair still holds real token supply: [1](#0-0) 

`Bonding.previewLtUntilGraduation` does the same: [2](#0-1) 

`Zap._executeBuy` calls `baseToLtAmount`/`ltToBaseAmount` on the LT (which read the same rate) on every curve-stage buy: [3](#0-2) 

`Zap._sellInternal` unconditionally calls `bonding_.canGraduate(tokenAddress)` before executing any sell of a curve-stage token, and separately calls `IBounceLeveragedToken(lt).exchangeRate()` again after the swap to enforce the dust floor: [4](#0-3) 

None of these four call sites wrap the external call in try/catch or provide any fallback if the LT's `exchangeRate()` reverts. Since the LT is an untrusted, externally-deployed BounceTech contract, alt.fun has no control over its availability. The documentation for "Retired LTs" only covers a *graceful* deprecation path (`exchangeRate` keeps returning a stale-but-non-reverting value): [5](#0-4) 

but a genuinely reverting `exchangeRate()` (as opposed to a merely stale one) is not handled anywhere — it is a distinct failure mode the protocol's own "retired LT" safeguard does not address.

### Impact Explanation
For any token still in `Lifecycle.Curve` with `tokenBalance() != 0` (i.e., not yet fully sold out — the only case where the supply trigger's short-circuit in `canGraduate` avoids the rate read), an `exchangeRate()` revert on the paired LT:
- Blocks all buys (`_executeBuy` reverts).
- Blocks all sells (`_sellInternal`'s `canGraduate` pre-check reverts before the token transfer even happens).
- Blocks the USD graduation trigger (`canGraduate`/`previewLtUntilGraduation` revert), leaving only the unreachable supply trigger as an escape hatch.

The token's raised LT and unsold real token supply sit locked in the `Pair` with no route to buy, sell, or force graduation — funds are trapped for as long as the LT's `exchangeRate()` reverts, which for a genuinely broken/bricked LT (not merely "retired") is indefinite/permanent, since alt.fun has no fallback oracle or LT-swap mechanism for a curve already in flight.

### Likelihood Explanation
Likelihood depends entirely on the external LT's reliability, which is outside alt.fun's control — the protocol's own documentation already acknowledges BounceTech LTs can be mint-paused and can be retired, showing the team anticipates LT-side failure modes. A revert in `exchangeRate()` (as opposed to graceful staleness) is a realistic failure class (e.g., a bug or intentional circuit-breaker in BounceTech's rate computation, or an upgrade that temporarily reverts views) that the current code has zero resilience against.

### Recommendation
Wrap `exchangeRate()` (and derivative `baseToLtAmount`/`ltToBaseAmount` calls) in `try/catch` at the `canGraduate`, `previewLtUntilGraduation`, `_executeBuy`, and `_sellInternal` call sites. On revert, at minimum allow sells to proceed via a safe fallback path (e.g., skip the `canGraduate` USD-leg check and go straight to the curve/graduated swap, since the dust-floor check in `_sellInternal` is not essential to correctness) so that holders always retain an exit, mirroring the protocol's own stated design goal that "a sell-only market is preferable to freezing both sides."

### Proof of Concept
1. A token is launched and partially sold on the bonding curve (`tokenBalance() > 0`, `Lifecycle.Curve`).
2. The paired LT's `exchangeRate()` starts reverting (e.g., BounceTech pauses the rate oracle or hits an internal computation bug).
3. Any user calls `Zap.buy(...)` → `_executeBuy` calls `IBounceLeveragedToken(lt).baseToLtAmount(netUsdc)` → reverts → buy fails.
4. Any user calls `Zap.sell(...)` → `_sellInternal` calls `bonding_.canGraduate(tokenAddress)` → `Bonding.canGraduate` calls `IBounceLeveragedToken(info.ltAddress).exchangeRate()` → reverts → sell fails before the token transfer.
5. No route exists to graduate the token via the USD trigger, and the supply trigger cannot be reached because no more buys can execute.
6. All USDC/LT/tokens associated with this curve are frozen until the external LT's `exchangeRate()` resumes functioning, which alt.fun cannot control or work around.

### Citations

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L717-726)
```text
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

**File:** packages/contracts/src/Zap.sol (L324-340)
```text
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

**File:** docs/contracts-scope.md (L77-77)
```markdown
**Retired LTs.** The reserve asset is an external BounceTech LT. If BounceTech de-registers it (it redeploys a fresh LT at a new address and flips the old address's `ltExists` to `false`), bonding curves already pointing at the old LT keep trading — `mint` / `redeem` / `exchangeRate` still work — but its `exchangeRate` stops tracking the underlying, so leverage is effectively frozen. The USD trigger above then can't ripen further; the supply trigger still graduates the token, and holders can always exit via `redeem`, so no funds are stranded. `Bonding.launch` rejects new bonding curves against a retired LT (its `ltExists` gate), so only pre-existing bonding curves are affected. See root `AGENTS.md` for the full note.
```
