### Title
`getRoundData` Ignores `_roundId` for rsETH Price Component, Returning Incorrect Historical Price — (File: `contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed.getRoundData(_roundId)` is documented (via the `AggregatorV3Interface` it implements) to return the rsETH/USD price at a specific historical round. However, while it correctly fetches the historical ETH/USD price for the given `_roundId`, it always uses the **current** rsETH/ETH price from `RS_ETH_ORACLE.rsETHPrice()`, ignoring the historical context of `_roundId`. This is a direct analog to the reported mismatch between a function's documented parameter semantics and its actual implementation.

---

### Finding Description

`RSETHPriceFeed` implements `AggregatorV3Interface` and is deployed as a Chainlink-compatible price feed for rsETH/USD. The interface contract defines `getRoundData(uint80 _roundId)` as returning the price data **at a specific historical round**.

The implementation is:

```solidity
function getRoundData(uint80 _roundId)
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
``` [1](#0-0) 

The `answer` is computed as:

```
answer = ETH/USD_price_at_roundId  ×  CURRENT_rsETH/ETH_price
```

But the correct semantics require:

```
answer = ETH/USD_price_at_roundId  ×  rsETH/ETH_price_at_roundId
```

`RS_ETH_ORACLE.rsETHPrice()` always returns the **current** stored rsETH/ETH exchange rate — it has no concept of historical round data. [2](#0-1) 

The `latestRoundData` function has the same structural pattern but is semantically correct for its purpose (returning the latest price). The bug is exclusive to `getRoundData`, where `_roundId` is partially used (for the ETH/USD leg) but silently ignored for the rsETH/ETH leg. [3](#0-2) 

---

### Impact Explanation

Any external protocol that integrates `RSETHPriceFeed` as a Chainlink-compatible oracle and calls `getRoundData` for historical price verification (e.g., TWAP calculations, dispute resolution, historical auditing) will receive a **hybrid price**: the ETH/USD component is historical, but the rsETH/ETH component is current. The returned rsETH/USD price for past rounds is therefore incorrect whenever the rsETH/ETH rate has changed since that round.

This means the contract fails to deliver its promised return (accurate historical rsETH/USD price) without directly losing user funds in the LRT-rsETH protocol itself.

**Impact: Low** — Contract fails to deliver promised returns, but doesn't lose value directly.

---

### Likelihood Explanation

`RSETHPriceFeed` is a production contract explicitly designed for external protocol integration as a Chainlink-compatible feed. Any integrator that calls `getRoundData` — a standard part of `AggregatorV3Interface` — will receive incorrect data. The likelihood depends on whether downstream integrators use historical round queries, which is a common pattern in DeFi (e.g., for TWAP, dispute windows, or fallback checks).

---

### Recommendation

Since `RSETHPriceFeed` cannot reconstruct the historical rsETH/ETH rate for an arbitrary past round (no checkpoint storage exists), the correct fix is to **revert in `getRoundData`** with a clear error indicating that historical round data is not supported for the rsETH component:

```solidity
function getRoundData(uint80 /*_roundId*/) external pure override returns (...) {
    revert("RSETHPriceFeed: historical round data not supported");
}
```

Alternatively, if historical accuracy is required, the contract must store rsETH/ETH price snapshots keyed by round ID at the time `updateRSETHPrice()` is called on `LRTOracle`.

---

### Proof of Concept

1. At round `R`, ETH/USD = $2,000 and rsETH/ETH = 1.05. Correct rsETH/USD at round `R` = $2,100.
2. Time passes; rsETH/ETH rises to 1.10 (stored in `LRTOracle.rsETHPrice`).
3. An integrator calls `RSETHPriceFeed.getRoundData(R)`.
4. The function fetches ETH/USD = $2,000 from `ETH_TO_USD.getRoundData(R)` (correct), then multiplies by `RS_ETH_ORACLE.rsETHPrice()` = 1.10 (current, not historical).
5. Returned `answer` = $2,000 × 1.10 = $2,200 — **incorrect by $100 (≈4.8%)**.
6. Any protocol using this for historical price validation receives a materially wrong value. [1](#0-0)

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
