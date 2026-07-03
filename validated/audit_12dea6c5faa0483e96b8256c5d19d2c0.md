### Title
`RSETHPriceFeed.getRoundData` Uses Global Current rsETH Rate Instead of Round-Specific Historical Rate, Returning Fabricated Cross-Price for Every Historical Query - (File: contracts/oracles/RSETHPriceFeed.sol)

---

### Summary

`RSETHPriceFeed.getRoundData` implements the Chainlink `AggregatorV3Interface` to expose an rsETH/USD price feed. When a caller queries a specific historical round, the function correctly fetches the ETH/USD price at that round from the underlying Chainlink feed, but then multiplies it by the **global current** `rsETHPrice()` from `LRTOracle` rather than the rsETH/ETH rate that was valid at that round. Every historical round query therefore returns a fabricated answer: `current_rsETH_rate × historical_ETH_USD_price`. The `latestRoundData` path is internally consistent (both legs are "current"), but `getRoundData` is not, creating the same global-vs-specific mismatch as the reference bug.

---

### Finding Description

`contracts/oracles/RSETHPriceFeed.sol` implements the full Chainlink `AggregatorV3Interface`, including `getRoundData`:

```solidity
function getRoundData(uint80 _roundId)
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;   // ← always uses global current rate
}
``` [1](#0-0) 

`RS_ETH_ORACLE.rsETHPrice()` reads the single stored value in `LRTOracle`:

```solidity
uint256 public override rsETHPrice;
``` [2](#0-1) 

`LRTOracle` stores only the most recently computed rsETH/ETH rate; no historical series is kept. `_updateRsETHPrice` overwrites `rsETHPrice` in place on every call. [3](#0-2) 

By contrast, `latestRoundData` is self-consistent: it fetches the current ETH/USD round and multiplies by the current rsETH rate — both legs refer to "now." [4](#0-3) 

`getRoundData` fetches a **historical** ETH/USD price but still multiplies by the **current** rsETH rate. The two legs are temporally mismatched. Additionally, the `updatedAt` field returned is the ETH/USD round's timestamp, not the timestamp of the last rsETH price update, so any staleness check a consumer performs on `updatedAt` reflects only the ETH/USD heartbeat (every few minutes on Chainlink) and silently ignores how stale the rsETH component is.

---

### Impact Explanation

Any protocol that integrates `RSETHPriceFeed` as a standard Chainlink feed and calls `getRoundData` — for TWAP computation, round-consistency validation, or historical price auditing — receives a fabricated answer. The magnitude of the error equals the drift in the rsETH/ETH rate between the queried round and the present. Because rsETH accrues EigenLayer rewards continuously, this drift grows monotonically over time, making older rounds increasingly wrong. A protocol computing a TWAP over N rounds will produce a result that is uniformly biased upward (since the current rsETH rate is always ≥ any historical rate), potentially allowing a borrower to obtain more credit than their collateral warrants. The `updatedAt` staleness bypass means a consumer cannot detect that the rsETH component of the answer is stale even if the ETH/USD leg was updated seconds ago.

**Impact: Low — Contract fails to deliver promised returns (incorrect historical cross-price data); escalates toward Medium/High in any downstream protocol that uses `getRoundData` for TWAP-based collateral valuation.**

---

### Likelihood Explanation

`RSETHPriceFeed` is deployed as a drop-in Chainlink-compatible feed (description field, full `AggregatorV3Interface` implementation). Any lending protocol, DEX, or aggregator that plugs it in and calls `getRoundData` — a standard interface method — is immediately affected. No special attacker action is required; the incorrect data is returned on every historical round query by any caller.

---

### Recommendation

Because `LRTOracle` stores only the current `rsETHPrice` and no historical series, there is no on-chain source of truth for the rsETH/ETH rate at an arbitrary past round. Two remediation paths exist:

1. **Revert on `getRoundData`**: Since correct historical data cannot be provided, revert with a descriptive error (e.g., `HistoricalDataUnavailable()`). This prevents consumers from silently receiving wrong data.
2. **Store a historical rate ring-buffer in `LRTOracle`**: Record `(timestamp → rsETHPrice)` on every `_updateRsETHPrice` call, then binary-search for the rate closest to the queried round's `updatedAt` timestamp inside `getRoundData`.

Option 1 is the minimal safe fix; option 2 is the correct long-term solution.

---

### Proof of Concept

Assume:
- rsETH/ETH rate at time T₁ (6 months ago): **1.00**
- ETH/USD at Chainlink round R₁ (6 months ago): **$3,000**
- rsETH/ETH rate today (current, stored in `LRTOracle`): **1.05**
- ETH/USD today (latest round): **$2,500**

**`latestRoundData()` (correct):**
`answer = 1.05 × $2,500 = $2,625` ✓

**`getRoundData(R₁)` (incorrect):**
`answer = 1.05 × $3,000 = $3,150` ✗
Correct answer should be: `1.00 × $3,000 = $3,000`

A protocol computing a 2-point TWAP over rounds R₁ and latest:
- **Incorrect TWAP**: `(1.05 × $3,000 + 1.05 × $2,500) / 2 = $2,887.50`
- **Correct TWAP**: `(1.00 × $3,000 + 1.05 × $2,500) / 2 = $2,812.50`

The inflated TWAP (+2.7%) allows a borrower to extract ~2.7% more credit than their rsETH collateral actually supports, constituting a direct loss to lenders in any protocol that uses this feed for collateral valuation.

### Citations

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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
