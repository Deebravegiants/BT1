### Title
`ChainlinkPriceOracle.getAssetPrice()` Missing Staleness Validation Returns Incorrect Price Breaking rsETH Share-Price Invariant - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` silently discards all Chainlink staleness fields and returns a potentially stale or zero price without any freshness check. This incorrect price propagates into `LRTOracle._updateRsETHPrice()`, corrupting the stored `rsETHPrice` and breaking the protocol's share-price invariant — the same structural flaw as the external report's unconverged Newton solver: a computation returns an incorrect value without validation, and that value is used directly in share/asset accounting.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every validation field:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`roundId`, `updatedAt`, and `answeredInRound` are all silently dropped. The sibling contract `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository explicitly guards against exactly these failure modes:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The stale price returned by `ChainlinkPriceOracle` flows through the following call chain:

1. `LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported LST
2. The incorrect `totalETHInProtocol` is fed into `_updateRsETHPrice()`, which computes `newRsETHPrice = (totalETHInProtocol − protocolFeeInETH) / rsethSupply` and writes it to the public `rsETHPrice` storage slot
3. `rsETHPrice` is then consumed by:
   - `LRTDepositPool.getRsETHAmountToMint()` → `depositAsset()` / `depositETH()`: `rsethAmountToMint = (amount × getAssetPrice(asset)) / rsETHPrice`
   - `LRTWithdrawalManager.getExpectedAssetAmount()` → `initiateWithdrawal()`: `underlyingToReceive = amount × rsETHPrice / getAssetPrice(asset)`

### Impact Explanation
When a Chainlink LST feed (e.g., stETH/ETH or ETHx/ETH) becomes stale with a price lower than the true value:

- `totalETHInProtocol` is underestimated → `rsETHPrice` is set below its true value
- A depositor calling `depositETH()` immediately after receives `rsethAmountToMint = ethAmount / rsETHPrice` — more rsETH than their ETH is worth at the true price
- When `rsETHPrice` is later corrected upward, the attacker's rsETH is worth more than deposited, diluting all existing rsETH holders

This is **theft of unclaimed yield** from existing rsETH holders (High impact). In the opposite direction (stale price too high), depositors receive fewer rsETH tokens than entitled — the contract fails to deliver promised returns (Low impact).

### Likelihood Explanation
`updateRSETHPrice()` is a public, permissionless function callable by any address. Chainlink feeds can become stale during L2 sequencer downtime, network congestion, or oracle node failures. The `pricePercentageLimit` guard in `_updateRsETHPrice()` only triggers on large deviations; a moderate staleness (e.g., 0.3–0.5% drift within the configured threshold) passes silently. The inconsistency with `ChainlinkOracleForRSETHPoolCollateral` — which does perform staleness checks — confirms this is an unintentional omission in the mainnet oracle path.

### Recommendation
Apply the same staleness and validity guards already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(price > 0, "Invalid price");
// Optionally: require(block.timestamp - updatedAt <= HEARTBEAT, "Price too old");
```

### Proof of Concept
1. The stETH/ETH Chainlink feed becomes stale (e.g., last update 4 hours ago during L2 sequencer downtime), reporting a price 0.4% below the true value — within the `pricePercentageLimit` threshold.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale low price; no revert.
4. `totalETHInProtocol` is underestimated → `newRsETHPrice` is set ~0.4% below true value → stored as `rsETHPrice`.
5. Attacker calls `LRTDepositPool.depositETH{value: 100 ether}(0, "")`.
6. `getRsETHAmountToMint` computes `rsethAmountToMint = 100e18 × 1e18 / rsETHPrice` — attacker receives ~0.4% more rsETH than entitled.
7. Chainlink feed updates; next `updateRSETHPrice()` call corrects `rsETHPrice` upward.
8. Attacker's rsETH is now worth more than deposited; existing holders' share value is diluted by the excess minted rsETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L329-349)
```text
    /// @notice get total ETH in protocol
    /// @return totalETHInProtocol total ETH in protocol (normalized to 1e18)
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
