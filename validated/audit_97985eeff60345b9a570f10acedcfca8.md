Audit Report

## Title
`confidenceParam` Defaults to Zero, Collapsing Oracle Spread Fee to `marginStep`-Only and Enabling Oracle-Update Front-Running — (File: `smart-contracts-poc/contracts/PriceProvider.sol`, `ProtectedPriceProvider.sol`, `PriceProviderL2.sol`, `ProtectedPriceProviderL2.sol`)

## Summary
All four price-provider contracts declare `confidenceParam` as a plain `uint256` storage slot that Solidity initialises to `0`. When `confidenceParam == 0`, the oracle's own spread is multiplied to zero inside `_getBidAndAskPrice`, so the bid/ask pair delivered to the pool carries only the immutable `marginStep` separation. The pool's swap fee (`baseFeeX64`) is derived entirely from that residual spread, and any oracle price movement exceeding `2 × marginStep` can be profitably sandwiched by an unprivileged trader, draining LP balances.

## Finding Description

**Root cause — `confidenceParam` is never set at construction.**

All four providers declare:

```solidity
uint256 public confidenceParam;   // Solidity default: 0
``` [1](#0-0) [2](#0-1) [3](#0-2) 

The constructor accepts no `_confidenceParam` argument and stores nothing, so the slot remains `0` until the provider owner explicitly calls `setConfidence` on the factory.

**`createPriceProvider` does not call `setConfidenceParam`.**

`PriceProviderFactory.createPriceProvider` deploys the contract and registers it, but never initialises `confidenceParam`: [4](#0-3) 

`setConfidence` is a separate, optional call that the provider owner must make after deployment: [5](#0-4) 

**Zero confidence collapses the oracle spread.**

Inside `_getBidAndAskPrice` (identical across all four providers):

```solidity
uint256 adjustedSpread = spread * confidenceParam;   // = spread * 0 = 0
(uint256 bid, uint256 ask) = _getBidAskFrom(mid, adjustedSpread);
``` [6](#0-5) 

Inside `_getBidAskFrom`:

```solidity
uint256 delta = midPrice * confidence / CONFIDENCE_BASE;  // = 0
bid = midPrice - 0;   // = mid
ask = midPrice + 0;   // = mid
``` [7](#0-6) 

After `_applyBidAdjustments` / `_applyAskAdjustments`, the only separation remaining is from the immutable `marginStep`:

```
bid  = mid × (BPS_BASE − marginStep) / BPS_BASE
ask  = mid × (BPS_BASE + marginStep) / BPS_BASE
``` [8](#0-7) 

**The pool's swap fee is derived from this collapsed spread.**

`MetricOmmPool.swap` calls:

```solidity
(uint256 midPriceX64, uint256 baseFeeX64) =
    SwapMath.midAndSpreadFeeX64FromBidAsk(uint256(bidPriceX64), uint256(askPriceX64));
``` [9](#0-8) 

`midAndSpreadFeeX64FromBidAsk` computes:

```solidity
baseFeeX64 = Math.mulDiv(askPriceX64, ONE_X64, midPriceX64, Math.Rounding.Ceil) - ONE_X64;
// ≈ sqrt(ask/bid) − 1  ≈  marginStep  (when confidenceParam == 0)
``` [10](#0-9) 

For `marginStep = 5 bps`, `baseFeeX64 ≈ 0.05%`. The oracle's own spread (e.g., 25 bps from Pyth) is completely absent from the fee.

**Existing guards are insufficient.**

The only invariant check is `bidOut >= askOut` (returns stale marker), which passes whenever `marginStep > 0`. Staleness and price-guard checks are orthogonal and do not protect against a correctly-priced but under-spread quote. [11](#0-10) 

## Impact Explanation

LP token balances are directly drained. Each successful sandwich extracts `(Δ − 2 × marginStep) × notional` from the pool's bin balances. For a pool with `marginStep = 5 bps` and a Pyth update moving price by 25 bps, the attacker nets ~15 bps per round trip on the full notional. With $10 M TVL this is ~$15,000 per oracle update. The loss is permanent and accrues to the attacker, not to LPs. This constitutes a direct loss of LP principal above Sherlock thresholds and qualifies as bad-price execution (oracle spread absent from the fee quote reaching a live swap).

## Likelihood Explanation

- `confidenceParam == 0` is the **default state** of every deployed price provider; no malicious action is required.
- `createPriceProvider` is permissionless; any user can deploy a provider and attach it to a pool without ever calling `setConfidence`.
- Even for diligent provider owners, a deployment window exists between `createPriceProvider` and the subsequent `setConfidence` call (two separate transactions).
- Oracle price movements exceeding `2 × marginStep` are routine for any non-trivial asset pair with small `marginStep`.
- The attack requires only a standard `swap` call — no special role or permission.

## Recommendation

1. **Require non-zero `confidenceParam` at construction.** Accept it as a constructor argument and validate `newValue > 0 && newValue <= CONFIDENCE_MAX` before storing it. Pass it through `PriceProviderFactory.createPriceProvider` as well. This eliminates the zero-default window entirely.
2. **Alternatively, enforce a minimum effective spread.** In `_getBidAndAskPrice`, revert (return stale marker) if `ask − bid` (before Q64 conversion) is below a constructor-set floor, ensuring the fee always covers the oracle's own deviation band.
3. **Long-term:** integrate the `PriceVelocityGuardExtension` as a mandatory extension for pools using price providers with mutable `confidenceParam`, so rapid oracle moves pause swaps until the fee can be recalibrated.

## Proof of Concept

```
State:
  marginStep      = 5e15  (5 bps, i.e. 0.05% of BPS_BASE = 1e18)
  confidenceParam = 0     (Solidity default; factory has not called setConfidence)
  oracle mid      = 100_000_000 (1.00 USD, 8-decimal Pyth feed)
  oracle spread   = 250   (25 bps — ignored because confidenceParam == 0)

Computed bid/ask delivered to pool:
  bid = 100_000_000 × (1e18 − 5e15) / 1e18 = 99_500_000
  ask = 100_000_000 × (1e18 + 5e15) / 1e18 = 100_500_000
  baseFeeX64 ≈ sqrt(100_500_000 / 99_500_000) − 1 ≈ 0.05%

Attacker observes pending Pyth update: mid will move to 100_250_000 (+25 bps).

Tx 1 (before update, buy token0 with 1_000_000 token1):
  token0 out = 1_000_000 / (1.00 × 1.0005) ≈ 999_500 token0

Oracle update lands: mid = 100_250_000

Tx 2 (after update, sell 999_500 token0):
  token1 out = 999_500 × 1.0025 / 1.0005 ≈ 1_001_497 token1

Profit = 1_001_497 − 1_000_000 = 1_497 token1 (≈ 0.15% on 1M notional)
LP balances are drained by 1,497 token1 per oracle update.
```

Foundry test plan: deploy `PriceProvider` with `marginStep = 5e15`, do not call `setConfidence`, set oracle mid to `100_000_000` with spread `250`, call `getBidAndAskPrice`, assert `ask − bid` equals only the `marginStep` separation, then simulate two swaps bracketing an oracle update and assert attacker profit > 0.

### Citations

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L40-41)
```text
    uint256 public confidenceParam;
    uint256 public lastConfidenceUpdate;
```

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L137-141)
```text
    function _getBidAskFrom(uint256 midPrice, uint256 confidence) internal pure returns (uint256 bid, uint256 ask) {
        uint256 delta = midPrice * confidence / CONFIDENCE_BASE;
        bid = delta >= midPrice ? 0 : midPrice - delta;
        ask = midPrice + delta;
    }
```

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L147-158)
```text
    function _applyBidAdjustments(
        uint256 price
    ) internal view returns (uint256 out, bool ok) {
        return _applyStepAdjustment(price, stepBidFactor, Math.Rounding.Floor);
    }

    /// @notice Ask adjustment: rounds UP (ceil).
    ///         out = price * Q64 * stepAskFactor / 1e26
    function _applyAskAdjustments(
        uint256 price
    ) internal view returns (uint256 out, bool ok) {
        return _applyStepAdjustment(price, stepAskFactor, Math.Rounding.Ceil);
```

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L214-217)
```text
        // 5. Compute bid/ask from mid + confidence-adjusted spread
        //    confidenceParam multiplies oracle spread; 0 means no spread
        uint256 adjustedSpread = spread * confidenceParam;
        (uint256 bid, uint256 ask) = _getBidAskFrom(mid, adjustedSpread);
```

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L226-228)
```text
        // 7. Hard invariant: bid must be strictly less than ask.
        //    Can be violated when marginStep < 0 and confidence is too small.
        if (bidOut >= askOut) return (0, type(uint128).max);
```

**File:** smart-contracts-poc/contracts/ProtectedPriceProvider.sol (L44-45)
```text
    uint256 public confidenceParam;
    uint256 public lastConfidenceUpdate;
```

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L44-45)
```text
    uint256 public confidenceParam;
    uint256 public lastConfidenceUpdate;
```

**File:** smart-contracts-poc/contracts/PriceProviderFactory.sol (L41-76)
```text
    function createPriceProvider(
        address _oracle,
        bytes32 _feedId,
        int256  _marginStep,
        uint256 _maxTimeDelta,
        address _baseToken,
        address _quoteToken
    ) external override returns (address provider) {
        PriceProvider p = new PriceProvider(
            address(this),
            _oracle,
            _feedId,
            _marginStep,
            _maxTimeDelta,
            _baseToken,
            _quoteToken
        );

        provider = address(p);
        address creator = msg.sender;

        _providers.add(provider);
        _providersByCreator[creator].add(provider);
        providerOwner[provider] = creator;

        emit ProviderDeployed(
            provider,
            creator,
            _feedId,
            _oracle,
            p.baseToken(),
            p.quoteToken(),
            _marginStep,
            _maxTimeDelta
        );
    }
```

**File:** smart-contracts-poc/contracts/PriceProviderFactory.sol (L130-142)
```text
    function setConfidence(
        address[] calldata providers,
        uint256[] calldata values
    ) external override {
        uint256 l = providers.length;
        if (l != values.length) revert LengthMismatch();

        for (uint256 i; i < l; ++i) {
            require(_providers.contains(providers[i]), ProviderNotTracked());
            _requireUpdater(providers[i]);
            PriceProvider(providers[i]).setConfidenceParam(values[i]);
        }
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L242-245)
```text
    (uint256 midPriceX64, uint256 baseFeeX64) =
      SwapMath.midAndSpreadFeeX64FromBidAsk(uint256(bidPriceX64), uint256(askPriceX64));
    SwapMath.InternalSwapParams memory params =
      SwapMath.InternalSwapParams({midPriceX64: midPriceX64, baseFeeX64: baseFeeX64, priceLimitX64: priceLimitX64});
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L64-72)
```text
  /// @notice Geometric mid price (Q64.64) and spread fee in Q64.64 from bid/ask oracle quotes.
  function midAndSpreadFeeX64FromBidAsk(uint256 bidPriceX64, uint256 askPriceX64)
    internal
    pure
    returns (uint256 midPriceX64, uint256 baseFeeX64)
  {
    midPriceX64 = Math.sqrt(bidPriceX64 * askPriceX64);
    baseFeeX64 = Math.mulDiv(askPriceX64, ONE_X64, midPriceX64, Math.Rounding.Ceil) - ONE_X64;
  }
```
