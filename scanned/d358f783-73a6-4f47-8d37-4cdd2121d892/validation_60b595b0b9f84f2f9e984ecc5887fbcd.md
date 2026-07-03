### Title
Unsafe `int256` → `uint256` Cast Without Negativity Check Causes Deposit DoS - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by Chainlink's `latestRoundData()` directly to `uint256` without first verifying `price > 0`. This is the same vulnerability class as the reference report: an unsafe narrowing/reinterpretation cast that silently produces a wildly incorrect value. In Solidity 0.8.x the cast itself does not revert; the resulting enormous `uint256` then causes an arithmetic overflow revert in the subsequent multiplication, freezing all deposit and oracle-dependent paths for any affected asset.

---

### Finding Description

In `ChainlinkPriceOracle.sol` line 54:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`latestRoundData()` returns `int256 answer`. Chainlink feeds can legitimately return `0` or negative values during circuit-breaker events, oracle malfunction, or extreme market conditions. The code performs no guard (`require(price > 0, ...)`) before the cast.

When `price` is negative (e.g., `-1`):

1. `uint256(-1)` silently wraps to `type(uint256).max` — **no revert at the cast site** (explicit casts in Solidity 0.8.x are always silent).
2. `type(uint256).max * 1e18` overflows → **reverts** under Solidity 0.8.x checked arithmetic.

The function therefore reverts for any asset whose Chainlink feed returns a non-positive answer, making `getAssetPrice()` permanently unusable for that asset until the feed recovers. [1](#0-0) 

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` is the price source consumed by `LRTOracle`, which is called during every deposit and rsETH-minting operation in `LRTDepositPool`. A revert here propagates up and freezes all deposits for the affected asset for as long as the Chainlink feed returns a non-positive value. This constitutes **temporary freezing of funds** (users cannot deposit or receive rsETH).

**Severity: Medium** — Temporary freezing of funds.

---

### Likelihood Explanation

Chainlink price feeds have historically returned `0` or negative answers during:
- Aggregator circuit-breaker events (price hits `minAnswer`/`maxAnswer` bounds).
- Feed deprecation or migration periods.
- Extreme market dislocations.

No special attacker action is required; the condition can arise from normal oracle behavior. Any unprivileged depositor calling `depositETH` or `depositAsset` on `LRTDepositPool` triggers the path.

---

### Recommendation

Add an explicit positivity check before the cast, mirroring the pattern recommended in the reference report:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
// Analog to the reference report's overflow guard
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Alternatively, use OpenZeppelin's `SafeCast.toUint256(int256)`, which reverts on negative input, making the failure explicit and auditable rather than silent. [2](#0-1) 

---

### Proof of Concept

```solidity
// Simulated Chainlink feed returning -1
// price = -1 (int256)
int256 price = -1;

// Step 1: silent cast — no revert
uint256 castedPrice = uint256(price); // == type(uint256).max

// Step 2: arithmetic overflow — REVERTS in Solidity 0.8.x
uint256 result = castedPrice * 1e18; // overflow revert

// Effect: getAssetPrice() reverts → LRTOracle reverts →
// LRTDepositPool.depositETH / depositAsset reverts →
// all deposits for this asset are frozen
```

The cast on line 54 of `ChainlinkPriceOracle.sol` is the necessary vulnerable step: it silently converts a negative `int256` into a huge `uint256` (identical in mechanism to the reference report's silent `uint128` truncation), and the downstream multiplication then causes a revert that freezes the deposit path. [1](#0-0)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```
