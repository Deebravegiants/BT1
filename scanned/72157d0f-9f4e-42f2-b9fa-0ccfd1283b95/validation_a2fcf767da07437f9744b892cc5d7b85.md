### Title
Stale rsETH/ETH Rate in `CrossChainRateReceiver` Allows Over-Minting of rsETH on L2 — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` stores the rsETH/ETH exchange rate pushed from L1 via LayerZero and records `lastUpdated` when the rate arrives. However, `getRate()` returns the stored `rate` unconditionally, with no staleness check against `lastUpdated`. `RSETHPoolV3` uses this oracle directly to price every deposit. If the cross-chain rate update is delayed or fails, the stale (lower) rate causes the pool to over-mint `wrsETH` to depositors, who can then redeem the excess on L1 at the correct higher rate, extracting value from the protocol.

---

### Finding Description

`CrossChainRateReceiver` is the abstract base for `RSETHRateReceiver`, which is the `rsETHOracle` wired into `RSETHPoolV3` on every L2 deployment. [1](#0-0) 

When a LayerZero message arrives from L1, `lzReceive` stores the rate and timestamps it: [2](#0-1) 

`getRate()` then returns the stored value with no freshness guard: [3](#0-2) 

`RSETHPoolV3.getRate()` delegates directly to this oracle: [4](#0-3) 

Both deposit paths use this rate to compute how many `wrsETH` tokens to mint: [5](#0-4) 

The minting formula is `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`. A stale (lower) rate produces a larger `rsETHAmount` for the same ETH input. The `lastUpdated` field is stored but never consulted anywhere in the read path.

The rate is pushed from L1 by `RSETHRateProvider`, which reads `LRTOracle.rsETHPrice()` — a value that increases over time as staking rewards accrue: [6](#0-5) 

If the LayerZero relay or the off-chain keeper calling `updateRate()` on `MultiChainRateProvider` stalls, the L2 receiver holds a rate that is lower than the true L1 rate for an unbounded period. [7](#0-6) 

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / protocol insolvency.**

An attacker who deposits 1 ETH when the stale rate is `1.00e18` instead of the true `1.05e18` receives `1.0 wrsETH` instead of `0.952 wrsETH`. After bridging back to L1 and redeeming at the correct rate, the attacker extracts ~0.048 ETH of value per ETH deposited. Scaled across the daily mint limit, this drains yield that belongs to existing rsETH holders and can push the protocol toward insolvency.

---

### Likelihood Explanation

**Likelihood: Low.**

The rate update depends on an off-chain keeper calling `updateRate()` and LayerZero successfully relaying the message. Network congestion, keeper downtime, or LayerZero delivery failures are realistic but not routine. The window of exploitability grows with the duration of the stale period, and the rsETH rate increases monotonically, so any prolonged outage creates a profitable gap.

---

### Recommendation

Add a configurable `maxStaleness` duration to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

This mirrors the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`, which checks `answeredInRound < roundID` and `timestamp == 0` before returning a price: [8](#0-7) 

---

### Proof of Concept

1. On L1, `LRTOracle.rsETHPrice` is updated to `1.05e18` (rsETH has appreciated 5% from staking rewards).
2. The off-chain keeper or LayerZero relay fails; `RSETHRateReceiver.rate` on Arbitrum remains at the old value `1.00e18`. `lastUpdated` is hours old but `getRate()` returns `1.00e18` without complaint.
3. Attacker calls `RSETHPoolV3.deposit{value: 1 ether}("")` on Arbitrum.
4. `viewSwapRsETHAmountAndFee(1e18)` computes `rsETHAmount = 1e18 * 1e18 / 1.00e18 = 1.0 wrsETH` instead of the correct `~0.952 wrsETH`.
5. Attacker bridges `wrsETH` to L1 and redeems at the true rate of `1.05e18`, receiving `~1.05 ETH` for the `1 ETH` deposited — a ~5% profit extracted from existing holders.
6. The protocol has issued more rsETH claims than the ETH it received, degrading the backing ratio for all holders. [3](#0-2) [9](#0-8)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-17)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-99)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L235-237)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L258-264)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-113)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;
```

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
