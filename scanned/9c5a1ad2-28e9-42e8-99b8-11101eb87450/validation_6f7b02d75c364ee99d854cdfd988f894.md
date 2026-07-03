### Title
Missing Time-Based Staleness Check Allows Stale Chainlink Prices to Be Accepted as Valid - (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral` fetches `updatedAt` from Chainlink's `latestRoundData()` but never compares it against `block.timestamp`. The only staleness guard used is the deprecated `answeredInRound < roundID` check, which Chainlink itself no longer guarantees to be meaningful. This is a direct analog to M-6: instead of a constant threshold that is too large for some tokens, this contract has **no time-based threshold at all** — effectively an infinite staleness window.

---

### Finding Description

In `getRate()`, the oracle calls `latestRoundData()` and receives `updatedAt` (aliased as `timestamp`). The only checks performed are:

- `if (answeredInRound < roundID) revert StalePrice()` — deprecated Chainlink pattern, not a reliable freshness guarantee
- `if (timestamp == 0) revert IncompleteRound()` — only catches a completely missing timestamp

There is no check of the form `if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice()`. [1](#0-0) 

This means a price last updated hours, days, or weeks ago passes all validation and is returned as current. The `updatedAt` value is fetched but silently discarded. [2](#0-1) 

This oracle is consumed by `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `RSETHPoolNoWrapper`, and `AGETHPoolV3` as the collateral pricing oracle. The rate it returns feeds directly into the rsETH minting calculation. [3](#0-2) 

---

### Impact Explanation

When the Chainlink feed for a collateral asset goes stale (e.g., during network congestion or a feed outage), the oracle continues to return the last known price. If the true market price has moved significantly:

- **Price dropped**: collateral is overvalued → users receive more rsETH than the collateral is worth → protocol insolvency risk / theft of yield from existing rsETH holders.
- **Price risen**: collateral is undervalued → users receive fewer rsETH tokens than they are entitled to → loss of value for depositors.

This maps to **Low: Contract fails to deliver promised returns** at minimum, and **Medium: Temporary freezing / incorrect minting** in adverse market conditions.

---

### Likelihood Explanation

Chainlink feeds do go stale during network congestion or sequencer outages (especially relevant on L2 deployments where these pool contracts operate). The pool contracts are publicly callable by any depositor with no access restriction, making this reachable by any unprivileged user.

---

### Recommendation

Add a configurable per-oracle `MAX_STALENESS` parameter (analogous to the per-token threshold recommended in M-6) and enforce it in `getRate()`:

```solidity
uint256 public immutable maxStaleness;

constructor(address _oracle, uint256 _maxStaleness) {
    oracle = _oracle;
    maxStaleness = _maxStaleness;
}

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 updatedAt, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > maxStaleness) revert StalePrice(); // <-- add this
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

Different collateral assets have different Chainlink heartbeat intervals (e.g., ETH/USD updates every 1 hour on mainnet, but other feeds may differ), so `maxStaleness` must be set per oracle instance — exactly the lesson from M-6.

---

### Proof of Concept

1. Chainlink's ETH/USD feed (or any collateral feed) goes stale — last `updatedAt` is 4 hours ago.
2. Any user calls `deposit()` on `RSETHPoolV3` with collateral.
3. The pool calls `collateralOracle.getRate()` → `ChainlinkOracleForRSETHPoolCollateral.getRate()`.
4. `answeredInRound >= roundID` (passes), `updatedAt != 0` (passes) — stale price is returned.
5. rsETH is minted at the stale rate, over- or under-valuing the deposited collateral. [4](#0-3)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
