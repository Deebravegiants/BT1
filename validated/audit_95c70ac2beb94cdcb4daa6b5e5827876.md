### Title
Bonding hardcodes an 18-decimal reserve-asset assumption when converting `exchangeRate()` into LT amounts, unchecked across pluggable BounceTech LTs - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding` treats every BounceTech Leveraged Token (LT) it can be launched against as an implicit 18-decimal asset when converting the LT's `exchangeRate()` (a USD-per-LT rate, itself documented as "18-dp") into a raw LT-unit reserve amount. This is the same bug class as the external report: a fixed decimal assumption baked into cross-asset conversion math, with no check that the actual asset conforms to that assumption.

### Finding Description
`_deployAndSeed` derives the launch-time virtual LT reserve directly from the LT's `exchangeRate()`: [1](#0-0) 

and the identical `USD × 1e18 / exchangeRate` pattern recurs in `canGraduate` and `previewLtUntilGraduation`: [2](#0-1) [3](#0-2) 

`IBounceLeveragedToken.exchangeRate()` is documented only as "USDC per LT unit, 18-dp" - a statement about the *rate's* precision, not about the LT token's own `decimals()`: [4](#0-3) 

The `(usd18dp * 1e18) / exchangeRate` formula only yields a correct amount of raw LT base units (wei) if one "whole" LT equals `1e18` base units, i.e. the LT has 18 decimals. Nowhere in `Bonding.sol` (nor in `Zap.sol`) is `IERC20Metadata.decimals()` queried on the LT, and nowhere does `launch`/`createToken` gate on it - the only whitelist check is `ltExists` on BounceTech's own `GlobalStorage`, which is a registration flag, not a decimals guarantee. Any unprivileged creator can call `Zap.createToken` against any LT address BounceTech has registered: [5](#0-4) 

If BounceTech ever registers (or already has registered) an LT whose `decimals()` is not 18, every USD↔LT conversion that anchors the bonding curve's `K` (`VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate`), the graduation threshold (`realLtRaised * exchangeRate / 1e18 >= graduationThresholdUsd`), and the pre-sizing cap in `Zap._executeBuy` (`baseToLtAmount`/`ltToBaseAmount`, themselves LT-side functions relying on the same 18-dp assumption per `MockLeveragedToken.baseToLtAmount`) is off by `10^(18 - actualDecimals)`. [6](#0-5) 

### Impact Explanation
- If the paired LT has **fewer than 18 decimals** (e.g. 6), `virtualLtReserve` is computed `10^(18-decimals)`-times too large in the LT's actual base units. Since `K = TOTAL_SUPPLY * virtualLtReserve` and the curve requires raising real LT proportional to that inflated virtual reserve to move price meaningfully, the curve becomes permanently unmovable/bricked relative to any realistic LT supply - a **permanent freezing of the launch** (creator's seed and all subsequent buyer funds become effectively stuck behind a curve that can never graduate or drain).
- If the paired LT has **more than 18 decimals**, the reverse happens: `virtualLtReserve` collapses toward zero, making `K` collapse toward zero. The bonding curve then dispenses almost the entire 750M curve-token supply for a vanishingly small amount of real LT - an **unbacked token payout** to the first buyer(s), at the expense of later buyers, the creator's fee split, and the eventual HyperSwap LP, which would be seeded off a curve close price that was never actually backed by proportional value raised.

Both outcomes are concrete fund-loss/freezing scenarios reachable purely from `Zap.createToken` + `Zap.buy`, matching the report's "High" impact framing.

### Likelihood Explanation
Low, matching the external report's own likelihood rating: it requires BounceTech to register (or have already registered) an LT with non-18 decimals, which alt.fun does not control and does not validate against at `launch`/`createToken` time. This is analogous to the original report's "if OrbitProxyOFT1_2 is deployed on both EVM and non-EVM chains" precondition - the vulnerability is latent and depends on the shape of a pluggable, out-of-repo asset, but the root-cause arithmetic in `packages/contracts/src/Bonding.sol` provides zero defense-in-depth against it.

### Recommendation
Query `IERC20Metadata(ltAddress).decimals()` in `Bonding.launch`/`_deployAndSeed` and either (a) revert if it is not exactly 18, matching every other hardcoded `1e18` conversion in the codebase, or (b) generalize all USD↔LT conversions (`_deployAndSeed`, `canGraduate`, `previewLtUntilGraduation`, and the `Zap._executeBuy`/`_sellInternal` estimate) to scale by the LT's actual `10**decimals()` rather than a hardcoded `1e18`.

### Proof of Concept
1. BounceTech registers `LT_6` with `decimals() == 6` and sets `ltExists[LT_6] = true`, `exchangeRate() == 1e18` ($1/LT).
2. Attacker (any unprivileged wallet) calls `Zap.createToken({..., ltAddress: LT_6}, seed)`.
3. `Bonding._deployAndSeed` computes `virtualLtReserve = (3000e18 * 1e18) / 1e18 = 3000e18` - but `LT_6` only has 6 decimals, so `3000e18` raw units represents `3e15` "whole" LT tokens, several orders of magnitude beyond any plausible LT supply.
4. `K = TOTAL_SUPPLY * 3000e18` is baked in permanently at `Pair.mint` (per `docs/contracts-scope.md` and `Router.sol`), so the curve can never be moved by any realistic amount of real `LT_6` - the token is permanently un-tradeable/un-graduatable, freezing the creator's seed funds and any subsequent buyer's USDC/LT on the curve.
   - (Conversely, an `LT` with >18 decimals collapses `virtualLtReserve` toward `0`, letting the first buyer drain the 750M curve supply for near-zero real LT via `Zap.buy` → `Bonding.buy` → `Router._computeBuy`, an unbacked payout.)

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-480)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
```

**File:** packages/contracts/src/Bonding.sol (L690-695)
```text

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
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

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L28-35)
```text
    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);

    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);
```

**File:** packages/contracts/src/Zap.sol (L279-302)
```text
    function _executeBuy(
        address tokenAddress,
        uint256 usdcAmount
    ) internal returns (uint256 tokensOut, uint256 amountInUsed, uint256 actualFee) {
        ZapStorage storage $ = _s();
        address lt = $.bonding.ltOf(tokenAddress);

        // Fee is charged on EVERY buy — bonding curve AND post-graduation.
        // This is intentional. Lifting the fee post-grad would silently
        // halve protocol+creator revenue the moment a token graduates and is
        // the opposite of what we want. The `if (isGraduated) ...` branch
        // below selects the venue (HyperSwap V2 vs. internal AMM `Router.sol`),
        // not the fee policy.
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
        // The LT floor applies to the post-fee amount forwarded to `mint`, not
        // the gross input — `_buyInternal`'s pre-check on `usdcAmount` leaves a
        // ~5-cent dirty band (`[MIN, MIN / (1 − buyFeeBps/BPS_DENOM)]`) where
        // the gross passes but `mint` reverts with the undecodable
        // `0x05eb05ac` selector that the pre-check exists to suppress.
        if (netUsdc < minUsdcAmount()) revert BelowMinAmount();

        $.usdc.safeTransferFrom(msg.sender, address(this), usdcAmount);
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
