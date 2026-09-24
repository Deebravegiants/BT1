### Title
Bonding curve and Zap math hardcode the BounceTech LT reserve asset as 18-decimal with no on-chain check - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Zap.sol])

### Summary
`Bonding.sol` and `Zap.sol` treat every BounceTech leveraged token (LT) used as a curve's reserve asset as an 18-decimal token and hardcode `1e18` scaling factors throughout the graduation math, the virtual-reserve math, and the buy/sell conversion math. Nothing in `IBounceLeveragedToken` or in `Bonding.launch`/`_deployAndSeed` calls `decimals()` on the LT or otherwise validates that the LT is actually 18-decimal before wiring it into a curve. This is the same bug class as the Earthquake `previewEmissionsWithdraw` finding: arithmetic that silently assumes 18 decimals on an externally-supplied token breaks by orders of magnitude if that assumption is false.

### Finding Description
The reserve asset for every bonding curve is an externally supplied BounceTech LT, specified by the creator/caller as `ltAddress` in `Bonding.LaunchParams` and consumed by `Zap.createToken` → `Bonding.launch` → `_deployAndSeed`. `IBounceLeveragedToken` documents `exchangeRate()` as "USDC per LT unit, 18-dp" [1](#0-0)  but the interface never surfaces or checks the LT's own `decimals()`, and none of the consuming contracts call it.

Every place that converts between "real LT units" and "USD value" hardcodes `1e18` as if the LT is always 18-decimal:

- Launch-time virtual reserve derivation divides the USD virtual liquidity by `exchangeRate()` and scales by `1e18`: [2](#0-1) 

- The dual graduation trigger's USD leg computes `valueUsd = (realLtRaised * exchangeRate()) / 1e18`, assuming `realLtRaised` (raw LT-token units transferred into the `Pair`) is scaled at 1e18: [3](#0-2) 

- `previewLtUntilGraduation` repeats the same `1e18`-scaled USD-leg math to size the graduation-crossing buy: [4](#0-3) 

- `Zap._sellInternal` computes the USD value of redeemed LT the same way, then converts from an assumed-18dp USD figure to 6dp USDC via a hardcoded `/1e12`: [5](#0-4) 

If the LT actually deployed at a given `ltAddress` has decimals other than 18 (e.g. 6, matching many stablecoin-referencing leveraged tokens, or any value BounceTech chooses for a given underlying), every one of these computations is wrong by a factor of `10^(18-actualDecimals)`. This is functionally identical to the reported Earthquake bug: `entitledAmount = _assets.mulDivDown(emissions[_id], finalTVL[_id])` silently assumed 18-decimal emissions tokens; here `valueUsd`, `virtualLtReserve`, `ltUntilThreshold`, and `grossUsdcEstimate` all silently assume an 18-decimal LT.

### Impact Explanation
A wrong decimals assumption on the reserve asset is not a cosmetic bug — it corrupts the two core protocol invariants:
- **Graduation timing/threshold** (`canGraduate`, `previewLtUntilGraduation`) would trigger orders of magnitude too early or effectively never, letting curves graduate with a tiny fraction of the intended raised value (unbacked LP seeding, permanent value leakage to whoever buys the mispriced closing trade) or get permanently stuck unable to graduate (funds locked in `Bonding`/`Pair` since the USD leg can never numerically reach `graduationThresholdUsd`).
- **Launch-time virtual reserve** (`virtualLtReserve`) sizing the curve's `K` would be off by the same factor, meaning `Router._computeBuy/_computeSell` prices trade against a curve seeded at the wrong scale relative to the LT's real value, letting early buyers extract value disproportionate to what they paid, or making the curve un-tradeable at sane sizes.
- **Zap sell path** `grossUsdcEstimate` gating (`BelowMinAmount`) would be miscalibrated, either blocking legitimate small sells or letting sub-floor sells slip through and interact incorrectly with BounceTech's own `minTransactionSize` floor.

Any of these directly causes theft/mispricing of trader and creator funds or permanent freezing of curve-raised value, satisfying the High-severity bar.

### Likelihood Explanation
This is reachable by design, not by a privileged action: `Bonding.launch` (via `Zap.createToken`) accepts an arbitrary `ltAddress` supplied by the token creator, an unprivileged actor. Nothing in `_deployAndSeed` validates the LT's decimals before it becomes the permanent reserve asset for that curve's `K` and all subsequent buys/sells. The severity is entirely conditional on BounceTech ever deploying (or the creator pointing at) a non-18-decimal LT; I could not find any on-chain enforcement in `packages/contracts/src` that guarantees 18 decimals, nor could I find external documentation in-repo proving BounceTech LTs are contractually fixed at 18 decimals — the interface only asserts it in a comment, not in code. This uncertainty (whether BounceTech's real deployed LTs are always 18-decimal in practice) is the main caveat on likelihood; if that external invariant always holds off-chain, the bug is latent rather than actively exploitable today, but the contract itself provides no defense if it doesn't.

### Recommendation
Read `decimals()` from the LT at `_deployAndSeed` time (with a `try/catch` fallback, mirroring the pattern already used for OZ's `ERC4626._tryGetAssetDecimals`) and either (a) revert `Bonding.launch` if `decimals() != 18`, or (b) generalize every `1e18`-scaled conversion in `Bonding.sol` (`_deployAndSeed`, `canGraduate`, `previewLtUntilGraduation`) and `Zap.sol` (`_executeBuy`, `_sellInternal`) to scale by `10 ** ltDecimals` instead of a hardcoded `1e18`.

### Proof of Concept
Conceptual (cannot be executed without a non-18-decimal LT mock, which the test suite's `MockLeveragedToken` does not provide — it is always deployed as a standard OZ `ERC20` with default 18 decimals):
1. Deploy a `MockLeveragedToken`-like contract but override `decimals()` to return `6`.
2. Call `Zap.createToken` with `ltAddress` pointing at this LT; `_deployAndSeed` computes `virtualLtReserve = (3000e18 * 1e18) / exchangeRate` — a value scaled as if 1 LT unit == 1e18 wei, when in reality 1 LT unit == 1e6 wei for this LT, inflating the effective virtual reserve by `1e12`.
3. Perform buys via `Zap.buy`; observe that `Bonding.canGraduate`'s USD leg (`realLtRaised * exchangeRate() / 1e18`) computes a `valueUsd` that is `1e12`x too small relative to the real dollar value actually raised (since `realLtRaised` is expressed in 6-decimal LT units, not 18-decimal), making the USD graduation trigger effectively unreachable while real economic value has already far exceeded `graduationThresholdUsd`.

### Citations

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L28-29)
```text
    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);
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

**File:** packages/contracts/src/Bonding.sol (L705-736)
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

        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
    }
```

**File:** packages/contracts/src/Zap.sol (L440-445)
```text
        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
```
