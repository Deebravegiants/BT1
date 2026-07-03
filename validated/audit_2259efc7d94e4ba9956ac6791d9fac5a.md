### Title
`RSETHPriceFeed` Returns ETH/USD `updatedAt` Instead of Composite Staleness, Masking Stale rsETH Oracle Prices — (File: `contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed` is a Chainlink-compatible composite price feed that multiplies the ETH/USD Chainlink price by the rsETH/ETH rate from `LRTOracle`. Both `latestRoundData()` and `getRoundData()` correctly compute the `answer` (rsETH/USD price), but they return `updatedAt`, `startedAt`, `roundId`, and `answeredInRound` exclusively from the ETH/USD Chainlink feed. The rsETH/ETH component's staleness is never surfaced to consumers.

---

### Finding Description

`RSETHPriceFeed.latestRoundData()` and `getRoundData()` follow this pattern:

```solidity
// contracts/oracles/RSETHPriceFeed.sol  lines 63–70
function latestRoundData()
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;   // ✓ answer is updated
    // updatedAt, answeredInRound, roundId are still from ETH_TO_USD only ✗
}
``` [1](#0-0) 

The same pattern appears in `getRoundData()`: [2](#0-1) 

The `answer` is correctly updated to the rsETH/USD composite price. However, `updatedAt` and `answeredInRound` are left as the values returned by the ETH/USD Chainlink feed. The rsETH/ETH rate comes from `RS_ETH_ORACLE.rsETHPrice()`, which is the `rsETHPrice` state variable in `LRTOracle`, updated only when `updateRSETHPrice()` is called: [3](#0-2) 

`LRTOracle` stores no timestamp alongside `rsETHPrice`, and the `IRSETHOracle` interface exposed to `RSETHPriceFeed` only declares `rsETHPrice()`: [4](#0-3) 

This means `RSETHPriceFeed` structurally cannot propagate the rsETH oracle's last-update time into `updatedAt`. The returned `updatedAt` reflects only when the ETH/USD Chainlink round was last updated — which can be very recent even when the rsETH/ETH rate is days old.

---

### Impact Explanation

Any protocol (lending market, vault, AMM) that consumes `RSETHPriceFeed` as a Chainlink-compatible feed will perform the standard staleness check:

```
require(updatedAt > block.timestamp - maxStaleness, "stale price");
```

Because `updatedAt` is sourced from the ETH/USD feed (which is updated every few minutes), this check will always pass — even if `rsETHPrice` in `LRTOracle` has not been updated for hours or days. The composite rsETH/USD price returned in `answer` will be stale without any on-chain signal of staleness.

- **If rsETH/ETH has fallen** (e.g., slashing event) and `updateRSETHPrice()` has not been called: the feed returns an inflated rsETH/USD price. Borrowers can over-borrow against rsETH collateral, leaving the lending protocol under-collateralized — **temporary or permanent freezing of funds / theft of yield**.
- **If rsETH/ETH has risen** and the oracle is stale: the feed returns a deflated price, causing incorrect liquidations — **temporary freezing of user funds**.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

`updateRSETHPrice()` is a public, permissionless function, but there is no on-chain enforcement of a maximum update interval. If the off-chain keeper fails, is delayed, or is front-run during a volatile period, the rsETH oracle can lag. The ETH/USD Chainlink feed will continue updating independently, making the staleness invisible to consumers. This is a realistic operational scenario, especially during market stress when timely updates matter most.

---

### Recommendation

1. Add a `lastUpdated` timestamp to `LRTOracle` that is written every time `rsETHPrice` is updated.
2. Expose it via `IRSETHOracle` (e.g., `function rsETHPriceLastUpdated() external view returns (uint256)`).
3. In `RSETHPriceFeed`, return `min(ethToUSD_updatedAt, rsETH_lastUpdated)` as `updatedAt`:

```solidity
function latestRoundData()
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
+   uint256 rsETHUpdatedAt = RS_ETH_ORACLE.rsETHPriceLastUpdated();
+   if (rsETHUpdatedAt < updatedAt) updatedAt = rsETHUpdatedAt;
}
```

---

### Proof of Concept

1. `LRTOracle.rsETHPrice` is last updated at `T=0` (e.g., rsETH/ETH = 1.05).
2. At `T = 25 hours`, a slashing event drops the true rsETH/ETH rate to 0.95, but `updateRSETHPrice()` is not called.
3. The ETH/USD Chainlink feed updates normally; its `updatedAt` is `T = 25 hours`.
4. A lending protocol calls `RSETHPriceFeed.latestRoundData()`:
   - `answer` = `1.05e18 * ethUSDPrice / 1e18` (stale, inflated)
   - `updatedAt` = `T = 25 hours` (fresh, from ETH/USD feed)
5. The lending protocol's staleness check passes. It accepts the inflated rsETH/USD price.
6. A borrower deposits rsETH and borrows at the inflated valuation, leaving the protocol under-collateralized. [1](#0-0) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L22-24)
```text
interface IRSETHOracle {
    function rsETHPrice() external view returns (uint256);
}
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L53-61)
```text
    function getRoundData(uint80 _roundId)
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);

        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L311-315)
```text
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
```
