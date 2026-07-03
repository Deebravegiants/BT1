### Title
Stale Chainlink Price Accepted Without Any Staleness Validation in `ChainlinkPriceOracle` — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except `price`. No `updatedAt` timestamp check, no `answeredInRound` vs `roundId` comparison, and no maximum-age guard are performed. This stale price propagates directly into rsETH minting amounts for depositors and into the rsETH price update mechanism.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` is used. [1](#0-0) 

The missing checks are:
- `updatedAt < block.timestamp - MAX_STALENESS` — price age limit
- `answeredInRound < roundId` — round completeness
- `price <= 0` — negative/zero price guard

By contrast, `ChainlinkOracleForRSETHPoolCollateral` (used for pool collateral) does implement `answeredInRound < roundID` and `timestamp == 0` checks, confirming the project is aware of the pattern but failed to apply it to the core oracle. [2](#0-1) 

---

### Impact Explanation

The stale price from `ChainlinkPriceOracle.getAssetPrice()` flows into two critical paths:

**Path 1 — rsETH minting (depositor over/under-mint):**
`LRTOracle.getAssetPrice()` delegates to `ChainlinkPriceOracle.getAssetPrice()`. [3](#0-2) 

`LRTDepositPool.getRsETHAmountToMint()` uses this price to compute how many rsETH tokens a depositor receives:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [4](#0-3) 

A stale inflated LST price causes depositors to receive more rsETH than their deposit is worth, diluting existing holders (theft of yield / protocol insolvency). A stale deflated price causes depositors to receive fewer rsETH tokens than deserved.

**Path 2 — rsETH price update (incorrect TVL, fee minting, pause trigger):**
`LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice()` for every supported asset to compute total protocol TVL: [5](#0-4) 

This TVL feeds `_updateRsETHPrice()`, which computes the new rsETH price, mints protocol fees, and may trigger an emergency pause if the price appears to drop beyond the threshold. [6](#0-5) 

A stale low price can artificially depress the computed TVL, triggering a false emergency pause of the deposit pool and withdrawal manager — a temporary freeze of funds.

---

### Likelihood Explanation

Chainlink feeds can go stale during network congestion, oracle node downtime, or L2 sequencer issues. The `updateRSETHPrice()` function is publicly callable by anyone, meaning any user can trigger a price update using a stale feed at any time without special access. [7](#0-6) 

---

### Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
uint256 constant MAX_STALENESS = 1 hours; // tune per feed heartbeat

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt < block.timestamp - MAX_STALENESS) revert PriceOutdated();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Chainlink's LST/ETH feed (e.g., stETH/ETH) stops updating due to network congestion. The last reported price is from 4 hours ago and is 2% higher than the current market price.
2. Any user calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice()` → returns the stale inflated price with no revert.
4. The inflated TVL causes `newRsETHPrice` to be computed higher than it should be.
5. A depositor then calls `LRTDepositPool.depositAsset(stETH, amount)`, which calls `getRsETHAmountToMint()` using the stale inflated `getAssetPrice(stETH)` — the depositor receives more rsETH than their deposit is worth, at the expense of existing rsETH holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L231-251)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
