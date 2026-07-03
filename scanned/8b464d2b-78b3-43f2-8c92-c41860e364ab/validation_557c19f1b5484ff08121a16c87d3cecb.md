### Title
`RSETHPriceFeed` Returns ETH/USD `updatedAt` Timestamp, Permanently Masking Staleness of the rsETH Price Component - (File: `contracts/oracles/RSETHPriceFeed.sol`)

### Summary
`RSETHPriceFeed.latestRoundData()` and `getRoundData()` compose a derived rsETH/USD price by multiplying the ETH/USD Chainlink answer by `LRTOracle.rsETHPrice`. However, the `updatedAt` timestamp returned is sourced entirely from the ETH/USD Chainlink feed — it never reflects when `rsETHPrice` was last written in `LRTOracle`. Because `LRTOracle` stores no `lastUpdatedAt` field, the correct timestamp is structurally unavailable, and the feed permanently reports the ETH/USD heartbeat timestamp as if it were the rsETH price freshness timestamp. Any integrator that performs a standard Chainlink staleness check on `updatedAt` will be misled into treating a potentially stale rsETH price as fresh.

### Finding Description
`RSETHPriceFeed` implements `AggregatorV3Interface` and is deployed in production (README lists `RSETHPriceFeed (Morph)` at `0x4B9C66c2C0d3706AabC6d00D2a6ffD2B68A4E383`). Both of its data-returning functions delegate all five return fields to the ETH/USD feed and then overwrite only `answer`:

```solidity
// contracts/oracles/RSETHPriceFeed.sol L63-70
function latestRoundData()
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    // updatedAt is left as ETH_TO_USD's timestamp — never corrected
}
```

`RS_ETH_ORACLE.rsETHPrice()` reads `LRTOracle.rsETHPrice`, a storage variable that is only updated when `updateRSETHPrice()` or `updateRSETHPriceAsManager()` is called:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`LRTOracle` stores no `lastUpdatedAt` field — there is no on-chain record of when `rsETHPrice` was last written. The ETH/USD Chainlink feed has a ~1-hour heartbeat, so `updatedAt` from that feed will always appear fresh to any staleness guard of the form `block.timestamp - updatedAt < threshold`. The rsETH price component, however, can be arbitrarily old.

This is structurally identical to the reference bug: a data-composition function always populates a time-related field from the wrong source (full duration / ETH/USD heartbeat), making the derived value's freshness unverifiable by downstream consumers.

### Impact Explanation
Any protocol that integrates `RSETHPriceFeed` as a standard Chainlink feed and applies a staleness check on `updatedAt` will silently accept a stale rsETH price as current. In a slashing or depeg scenario where `rsETHPrice` has not been updated, the feed will report an inflated rsETH/USD price while `updatedAt` appears fresh, allowing borrowers to obtain more credit than the actual collateral value warrants, creating bad debt for lenders. In the normal (upward-drifting) case the price is understated, causing the contract to fail to deliver the promised accurate rate — the feed cannot be relied upon by integrators.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value** (in the normal upward-drift case); escalates toward Medium in a slashing/depeg scenario where the stale price is inflated.

### Likelihood Explanation
`updateRSETHPrice()` is permissionless but not automatic; it depends on off-chain keepers or manual calls. Any gap between keeper runs (maintenance windows, keeper failures, protocol pause triggered by `_pause()` which blocks `updateRSETHPrice` via `whenNotPaused`) leaves `rsETHPrice` stale while `updatedAt` from ETH/USD continues to appear fresh. The feed is already deployed and integrated with at least one external lending protocol (Morph), so the exposure is live.

### Recommendation
1. Add a `rsETHPriceUpdatedAt` storage variable to `LRTOracle` and set it to `block.timestamp` inside `_updateRsETHPrice()` at the point where `rsETHPrice` is written.
2. Expose it via `ILRTOracle`.
3. In `RSETHPriceFeed.latestRoundData()` and `getRoundData()`, override `updatedAt` with `IRSETHOracle(RS_ETH_ORACLE).rsETHPriceUpdatedAt()` instead of leaving it as the ETH/USD timestamp.
4. Consider adding a revert if `rsETHPriceUpdatedAt` is older than an acceptable threshold (e.g., 24 hours) so the feed fails loudly rather than silently returning stale data.

### Proof of Concept
1. `updateRSETHPrice()` is called at time `T`. `LRTOracle.rsETHPrice` is set; no timestamp is stored.
2. 48 hours pass. The ETH/USD Chainlink feed continues to update every ~1 hour; its `updatedAt` is always within the last hour.
3. A lending protocol calls `RSETHPriceFeed.latestRoundData()`. It receives `updatedAt = block.timestamp - 30 minutes` (from ETH/USD) and `answer = rsETHPrice_at_T * ethPrice_now / 1e18`.
4. The lending protocol's staleness guard (`block.timestamp - updatedAt < 3600`) passes.
5. The rsETH price used for collateral valuation is 48 hours old. If rsETH has depegged or been slashed in that window, the collateral is overvalued and the loan is under-collateralized.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L313-315)
```text
        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
```
