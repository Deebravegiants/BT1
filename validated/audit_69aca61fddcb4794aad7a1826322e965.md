### Title
Stale Chainlink Price Accepted Without Any Validation in `ChainlinkPriceOracle.getAssetPrice()` Allows Attacker to Mint rsETH at Artificially Deflated Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` reads Chainlink price data with **zero staleness validation**. Because `LRTOracle.updateRSETHPrice()` is a `public` function callable by any address, an attacker can trigger a protocol-wide rsETH price update during a period of Chainlink feed staleness. The resulting undervalued `rsETHPrice` allows the attacker to deposit and receive more rsETH than the true TVL warrants, diluting existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and immediately returns the price with no validation of any kind:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol:49-54
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

No check is performed on `answeredInRound`, `updatedAt`, or any heartbeat threshold. This is in stark contrast to the protocol's own `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which at minimum checks `answeredInRound < roundID` and `timestamp == 0`:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol:26-36
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The call chain from the public entry point is:

1. `LRTOracle.updateRSETHPrice()` — `public whenNotPaused`, no access control
2. → `_updateRsETHPrice()`
3. → `_getTotalEthInProtocol()`
4. → `getAssetPrice(asset)` for every supported L1 asset (stETH, rETH, cbETH, etc.)
5. → `ChainlinkPriceOracle.getAssetPrice()` — stale price accepted silently

The stale `totalETHInProtocol` value is then used to compute and **persist** `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol:250,313
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;
```

This stored `rsETHPrice` is subsequently consumed by `LRTDepositPool` to determine how many rsETH tokens to mint per deposited asset, and is also propagated to all L2 chains via `RSETHMultiChainRateProvider` and `RSETHRateProvider`, which both read `ILRTOracle(rsETHPriceOracle).rsETHPrice()`.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / share mis-accounting**

If a Chainlink feed for any supported L1 asset (e.g., stETH/ETH) becomes stale and its last reported price is lower than the true market price:

- `totalETHInProtocol` is underestimated.
- `newRsETHPrice` is set below its true value.
- Any depositor who calls `LRTDepositPool.depositAsset()` or `depositETH()` immediately after receives **more rsETH than the true TVL warrants**.
- When the Chainlink feed resumes and `updateRSETHPrice()` is called again with the correct price, `rsETHPrice` rises — but the attacker's excess rsETH is already minted and represents a permanent dilution of all existing holders.

The `pricePercentageLimit` guard only triggers on deviations exceeding the configured threshold. A feed that has simply not updated within its heartbeat window (e.g., a 1-hour heartbeat feed that last updated 59 minutes ago) will pass all existing checks while potentially reflecting a materially stale price.

---

### Likelihood Explanation

**Likelihood: Medium**

Chainlink feeds go stale in documented, recurring scenarios:
- Network congestion causing keeper transactions to fail.
- Price deviation threshold not met (feed only updates on >0.5% moves; a slow drift is not captured).
- Sequencer downtime on L2 (though this oracle is L1-side).

No special privileges are required. Any externally owned account can call `LRTOracle.updateRSETHPrice()`. The attacker only needs to observe that a feed's `updatedAt` timestamp is aging and act before the feed self-corrects.

---

### Recommendation

Add both a round-completeness check and a heartbeat staleness check in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
uint256 public constant MAX_STALENESS = 3600; // configure per feed

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundID, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Each supported asset's feed should have its own `MAX_STALENESS` value matching the Chainlink-documented heartbeat for that feed.

---

### Proof of Concept

1. The stETH/ETH Chainlink feed has a 24-hour heartbeat and 0.5% deviation threshold. The price has not moved more than 0.5% for 23 hours, so the feed has not updated.
2. The true stETH/ETH rate is 1.08 ETH but the last reported price is 1.07 ETH (a 0.93% understatement).
3. Attacker calls `LRTOracle.updateRSETHPrice()` (no access control).
4. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)`, which returns 1.07 ETH — accepted without any staleness check.
5. `totalETHInProtocol` is underestimated by ~0.93% of the stETH TVL.
6. `rsETHPrice` is written to storage at a value ~0.93% below its true value.
7. Attacker immediately calls `LRTDepositPool.depositETH()` and receives ~0.93% more rsETH than the true exchange rate warrants.
8. The Chainlink feed updates the next block. A keeper calls `updateRSETHPrice()` again; `rsETHPrice` rises to its correct value.
9. Attacker's rsETH is now worth more than what they paid. The loss is borne proportionally by all existing rsETH holders.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
