### Title
`ChainlinkPriceOracle.getAssetPrice()` Accepts Stale Prices Without Freshness Validation, Enabling Incorrect rsETH Minting - (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards the `updatedAt` timestamp and `answeredInRound` fields. This is the direct structural analog to the PythOracle `commit()` bug: both functions consume oracle price data without verifying temporal ordering or freshness. A stale LST price fed into `LRTOracle._updateRsETHPrice()` produces an incorrect rsETH exchange rate, which any unprivileged depositor can exploit to mint excess rsETH at the expense of existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads from Chainlink but only extracts the raw `price` value:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract ignores `updatedAt` (the timestamp of the last price update) and `answeredInRound` (the round in which the answer was computed). No maximum staleness window is enforced. [2](#0-1) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used in the L2 pool path — does check `answeredInRound < roundID` and `timestamp == 0`, demonstrating the protocol is aware of the pattern but did not apply it consistently: [3](#0-2) 

The stale price flows into `LRTOracle._updateRsETHPrice()` via `_getTotalEthInProtocol()`, which aggregates asset values using `getAssetPrice()` for each supported LST. The resulting `newRsETHPrice` is then stored and used to determine how many rsETH tokens to mint per deposited asset: [4](#0-3) [5](#0-4) 

`updateRSETHPrice()` is a public, permissionless function: [6](#0-5) 

---

### Impact Explanation

LSTs such as stETH and ETHx are monotonically appreciating tokens — their ETH price only increases over time. When Chainlink's feed for such an asset is stale (i.e., `updatedAt` is old), the reported price is **lower** than the true current price. This causes `_getTotalEthInProtocol()` to underestimate the protocol's TVL, which in turn lowers the computed `newRsETHPrice`. A lower rsETH price means each unit of deposited asset mints **more rsETH** than it should. The excess rsETH dilutes all existing holders — their proportional claim on the underlying ETH is reduced. This constitutes theft of yield from existing rsETH holders.

**Impact classification**: High — theft of unclaimed yield / dilution of existing holders.

---

### Likelihood Explanation

Chainlink price feeds can become stale during:
- Network congestion (gas spikes preventing keeper updates)
- Oracle node outages
- Rapid price movements that outpace the heartbeat interval

For LSTs, the heartbeat is typically 24 hours with a 0.5% deviation threshold. A stale feed is a realistic, historically observed condition. The attack requires no special privileges — any user can call `updateRSETHPrice()` followed by `depositAsset()` in the same transaction.

**Likelihood classification**: Medium — requires an external condition (stale feed) but that condition is realistic and has occurred on mainnet.

---

### Recommendation

Add staleness and round-completeness checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS` should be set per-asset based on the Chainlink feed's documented heartbeat interval.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed becomes stale (e.g., `updatedAt` is 25 hours old, price is 1.050 ETH/stETH, but true current price is 1.052 ETH/stETH).
2. Attacker calls `LRTOracle.updateRSETHPrice()`. Inside `_updateRsETHPrice()`, `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` which returns the stale 1.050 value. The computed `newRsETHPrice` is lower than it should be (e.g., 1.049 ETH/rsETH instead of 1.051 ETH/rsETH).
3. Attacker calls `LRTDepositPool.depositAsset(stETH, amount, ...)`. The mint calculation uses the artificially low `rsETHPrice`, so the attacker receives more rsETH than the deposited stETH is worth at the true current rate.
4. When the Chainlink feed updates and `updateRSETHPrice()` is called again with the correct price, the attacker's excess rsETH now represents a larger-than-deserved claim on the protocol's TVL, at the expense of all prior holders. [1](#0-0) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L11-18)
```text
interface AggregatorV3Interface {
    function decimals() external view returns (uint8);

    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}
```

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

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```
